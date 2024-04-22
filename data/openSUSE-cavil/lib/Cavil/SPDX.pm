# Copyright (C) 2023 SUSE LLC
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <http://www.gnu.org/licenses/>.

package Cavil::SPDX;
use Mojo::Base -base, -signatures;

use Cavil::Checkout;
use Cavil::Licenses qw(lic);
use Cavil::Util     qw(read_lines);
use Digest::SHA1;
use Mojo::File qw(path tempfile);
use Mojo::JSON qw(from_json);
use Mojo::Date;
use Mojo::Util qw(decode scope_guard);

use constant NO_ASSERTION => 'NOASSERTION';

my $SPDX_VERSION = '2.2';

has 'app';

my @FLAGS = qw(trademark patent export_restricted);

sub generate_to_file ($self, $id, $file) {
  path($file)->remove if -e $file;

  my $app             = $self->app;
  my $log             = $app->log;
  my $config          = $app->config->{spdx} || {};
  my $namespace       = $config->{namespace} || 'http://legaldb.suse.de/spdx/';
  my $dir             = $app->packages->pkg_checkout_dir($id);
  my $checkout        = Cavil::Checkout->new($dir);
  my $reports         = $app->reports;
  my $specfile_report = $reports->specfile_report($id);
  my $db              = $app->pg->db;
  my $license_ref_num = 0;

  my $spdx_tmp_file = "$file.tmp";
  my $refs_tmp_file = "$file.refs.tmp";
  my $spdx_handle   = path($spdx_tmp_file)->open('>');
  my $spdx          = _SPDXWriter->new(handle => $spdx_handle);
  my $refs          = _SPDXWriter->new(handle => path($refs_tmp_file)->open('>'));
  my $cleanup       = scope_guard sub { -e $_ && path($_)->remove for $spdx_tmp_file, $refs_tmp_file };

  # Document
  $spdx->tag(SPDXVersion => "SPDX-$SPDX_VERSION");
  $spdx->tag(DataLicense => 'CC0-1.0');
  $spdx->br();
  $spdx->box('Document Information');
  $spdx->tag(DocumentNamespace => "$namespace$id");
  $spdx->tag(DocumentName      => 'report.spdx');
  $spdx->tag(SPDXID            => 'SPDXRef-DOCUMENT');
  $spdx->br();

  # Creation
  $spdx->box('Creation Information');
  $spdx->tag(Creator => 'Tool: Cavil');
  $spdx->tag(Created => Mojo::Date->new->to_datetime);
  $spdx->br();

  # Scan files (needed for verification)
  my (%files, %paths, @checksums, %original_files);
  for my $unpacked (@{$checkout->unpacked_files}) {
    my ($file, $mime) = @$unpacked;
    $file = decode('UTF-8', $file) // $file;

    # The indexer pre-processes certain files to allow for them to be scanned (and we want the original checksum)
    my $checksum_path = $dir->child('.unpacked', $file)->to_string;
    if ($file =~ /^(.+)\.processed(?:\.(\w+)|$)/) {
      my $original      = defined $2 ? "$1.$2" : $1;
      my $original_path = $dir->child('.unpacked', $original)->to_string;
      if (-e $original_path) {
        $paths{$file}          = $checksum_path;
        $checksum_path         = $original_path;
        $original_files{$file} = $original;
      }
    }
    $paths{$file} //= $checksum_path;

    # Make sure encoding errors are logged for debugging
    if (-e $checksum_path) {
      push @checksums, $files{$file} = Digest::SHA->new('1')->addfile($checksum_path)->hexdigest;
    }
    else {
      $log->error("Non-existing path in SPDX report $id: $checksum_path");
    }
  }
  my $verification_code = Digest::SHA->new('1')->add(join('', sort @checksums))->hexdigest;

  # Package
  my $pkg = $db->query('SELECT * FROM bot_packages WHERE id = ?', $id)->hash;
  $spdx->box('Package Information');
  $spdx->tag(PackageName             => $pkg->{name});
  $spdx->tag(SPDXID                  => "SPDXRef-pkg-$id");
  $spdx->tag(PackageDownloadLocation => NO_ASSERTION);
  $spdx->tag(PackageVerificationCode => $verification_code);
  if (my $main = $specfile_report->{main}) {
    my $version = $main->{version} // '';
    $spdx->tag(PackageVersion => $version) if $version =~ /^[0-9.]+$/;
    my $license = lic($main->{license} // '');
    $spdx->tag(PackageLicenseDeclared => $license->is_valid_expression ? $license->to_string : NO_ASSERTION);
    if (my $summary = $main->{summary}) { $spdx->tag(PackageDescription => $summary) }
    if (my $url     = $main->{url})     { $spdx->tag(PackageHomePage    => $url) }
  }
  $spdx->tag(PackageLicenseInfoFromFiles => NO_ASSERTION);
  $spdx->tag(PackageLicenseConcluded     => NO_ASSERTION);
  $spdx->tag(PackageCopyrightText        => NO_ASSERTION);
  $spdx->tag(PackageChecksum             => 'MD5: ' . $pkg->{checkout_dir});
  $spdx->tag(Relationship                => "SPDXRef-DOCUMENT DESCRIBES SPDXRef-pkg-$id");
  $spdx->br();

  # Files
  $spdx->box('File Information');
  my $matched_files = {};
  for my $matched ($db->query('SELECT * FROM matched_files WHERE package = ?', $id)->hashes->each) {
    $matched_files->{$matched->{filename}} = $matched->{id};
  }
  my $file_num = 0;
  for my $file (sort keys %files) {
    $file_num++;

    my $real_name = $original_files{$file} // $file;
    $spdx->comment('File');
    $spdx->br();
    $spdx->tag(FileName         => "./$real_name");
    $spdx->tag(SPDXID           => "SPDXRef-item-$id-$file_num");
    $spdx->tag(FileChecksum     => 'SHA1: ' . $files{$file});
    $spdx->tag(LicenseConcluded => NO_ASSERTION);

    # Matches
    if (my $file_id = $matched_files->{$file}) {
      my (@copyright, %duplicates, %matched_lines, %ignored_lines, %similarity);

      my $snippet_sql = qq{
        SELECT f.sline, f.eline, s.license, s.like_pattern, s.likelyness
        FROM file_snippets f LEFT JOIN snippets s ON f.snippet = s.id
        WHERE file = ? AND classified = true
      };
      for my $snippet ($db->query($snippet_sql, $file_id)->hashes->each) {

        # Snippets the AI lawyer does not think are license text
        if (!$snippet->{license}) {
          _matched_lines(\%ignored_lines, $snippet->{sline}, $snippet->{eline}, 1);
        }

        # Snippets the AI lawyer thinks are similar to an exising license pattern
        if ($snippet->{like_pattern}) {
          _matched_lines(\%similarity, $snippet->{sline}, $snippet->{eline},
            [$snippet->{like_pattern}, $snippet->{likelyness}]);
        }
      }

      my $match_sql = qq{
        SELECT m.*, p.spdx, p.license, p.risk, p.unique_id, p.trademark, p.patent, p.export_restricted
        FROM pattern_matches m LEFT JOIN license_patterns p ON m.pattern = p.id
        WHERE file = ? AND ignored = false ORDER BY p.license, p.id DESC
      };
      for my $match ($db->query($match_sql, $file_id)->hashes->each) {

        # Remove keyword matches when possible
        my $similar;
        if ($match->{license} eq '') {

          # Ignored keyword matches that the AI lawyer does not consider license text
          next if $ignored_lines{$match->{sline}} && $ignored_lines{$match->{eline}};

          # Ignore keyword matches that overlap with other pattern matches
          next if $matched_lines{$match->{sline}};

          # Keyword match is similar to an existing license pattern
          if (my $similarity = $similarity{$match->{sline}}) {
            my ($id, $likelyness) = @$similarity;
            if ($similar = $db->query('SELECT license, risk FROM license_patterns WHERE id = ?', $id)->hash) {
              $similar->{likelyness} = int($likelyness * 100);
            }
          }
        }
        _matched_lines(\%matched_lines, $match->{sline}, $match->{eline}, 1);

        my $snippet = read_lines($paths{$file}, $match->{sline}, $match->{eline});
        push @copyright, grep { /copyright.*\d+/i && !$duplicates{$_} } split("\n", $snippet);

        # License
        if (my $license = $match->{spdx}) {
          $spdx->tag(LicenseInfoInFile => $license);
        }

        # Non-SPDX license or keyword
        else {
          my $unknown = $match->{license};
          $license_ref_num++;
          my $license = "LicenseRef-$unknown-$id-$license_ref_num";
          $license =~ s/[^A-Za-z0-9.]+/-/g;

          $spdx->tag(LicenseInfoInFile => $license);

          $refs->comment('License Reference');
          $refs->br();
          $refs->tag(LicenseID   => $license);
          $refs->tag(LicenseName => $unknown || NO_ASSERTION);
          my $flags = '';
          if (grep { $match->{$_} } @FLAGS) {
            my @flags = map { $match->{$_} ? ("\@$_") : () } @FLAGS;
            $flags = '; Flags: ' . join(', ', @flags);
          }
          my $risk = $unknown eq '' ? 9 : $match->{risk};
          $refs->tag(LicenseComment => "Risk: $risk$flags ($match->{unique_id}:$match->{id})");
          $refs->tag(LicenseComment =>
              "Similar: $similar->{license} ($similar->{likelyness}% similarity, estimated risk $similar->{risk})")
            if $similar;
          $refs->text(ExtractedText => $snippet);
          $refs->br();
        }
      }

      if (@copyright) {
        $spdx->text(FileCopyrightText => join("\n", @copyright));
      }
      else {
        $spdx->tag(FileCopyrightText => NO_ASSERTION);
      }
    }

    # No matches
    else {
      $spdx->tag(LicenseInfoInFile => NO_ASSERTION);
      $spdx->tag(FileCopyrightText => NO_ASSERTION);
    }

    $spdx->br();
  }

  # Merge license references and main SPDX file
  if (-s $refs_tmp_file) {
    $spdx->box('Other Licensing Information');
    my $tmp_handle = path($refs_tmp_file)->open('<');
    my $buffer;
    $spdx_handle->syswrite($buffer) while $tmp_handle->sysread($buffer, 1024);
  }

  path($spdx_tmp_file)->move_to($file);
}

sub _matched_lines ($matched_lines, $start, $end, $value) {
  for (my $i = $start; $i <= $end; $i++) {
    $matched_lines->{$i} ||= $value;
  }
}

package _SPDXWriter;
use Mojo::Base -base, -signatures;

use Mojo::Util qw(encode);

sub append ($self, $text) { $self->{handle}->syswrite(encode('UTF-8', $text)) }

sub br ($self) { $self->append("\n") }

sub tag ($self, $name, $value) {
  if ($value =~ /\n/) {
    $self->text($name, $value);
  }
  else {
    $self->append("$name: $value\n");
  }
}

sub text ($self, $name, $value) {
  $self->append("$name: <text>$value</text>\n");
}

sub comment ($self, $text) { $self->append("##$text\n") }

sub box ($self, $text) {
  $self->comment('-----------------------------');
  $self->comment(" $text");
  $self->comment('-----------------------------');
  $self->br();
}

1;
