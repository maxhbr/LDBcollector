# Copyright (C) 2019 SUSE Linux GmbH
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

package Cavil::Task::ClosestMatch;
use Mojo::Base 'Mojolicious::Plugin', -signatures;

use Mojo::JSON 'encode_json';
use Cavil::Util;
use Spooky::Patterns::XS 1.54;
use Mojo::File qw(path);

sub register ($self, $app, $config) {
  $app->minion->add_task(pattern_stats => \&_pattern_stats);
}

sub _pattern_stats ($job) {
  my $app = $job->app;
  my $db  = $app->pg->db;

  my $rows = $db->select('license_patterns', 'id,pattern')->hashes;

  my $bag = Spooky::Patterns::XS::init_bag_of_patterns;
  my %patterns;
  $patterns{$_->{id}} = $_->{pattern} for $rows->each;
  $bag->set_patterns(\%patterns);

  my $dir   = path($app->config->{cache_dir});
  my $cache = $dir->child('cavil.pattern.bag.new.' . $job->id);
  $bag->dump($cache);
  rename($cache, $dir->child('cavil.pattern.bag'));

  $rows = $db->select('snippets', 'id,text', {like_pattern => undef});
  while (my $next = $rows->hash) {
    my $best_pattern = $bag->best_for($next->{text}, 1)->[0];
    $db->update(
      'snippets',
      {likelyness => $best_pattern->{match}, like_pattern => $best_pattern->{pattern},},
      {id         => $next->{id}}
    );
  }
}

1;
