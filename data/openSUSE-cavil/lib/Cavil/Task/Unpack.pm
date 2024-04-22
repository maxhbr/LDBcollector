# Copyright (C) 2018 SUSE Linux GmbH
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

package Cavil::Task::Unpack;
use Mojo::Base 'Mojolicious::Plugin', -signatures;

use Cavil::Checkout;
use Cavil::Util qw(parse_exclude_file);

sub register ($self, $app, $config) {
  $app->minion->add_task(unpack => \&_unpack);
}

sub _unpack ($job, $id) {
  my $app    = $job->app;
  my $minion = $app->minion;
  my $log    = $app->log;
  my $pkgs   = $app->packages;

  # Protect from race conditions
  return $job->finish("Package $id is already being processed")
    unless my $guard = $minion->guard("processing_pkg_$id", 172800);
  return $job->fail("Package $id is not imported yet") unless $pkgs->is_imported($id);

  # Exclude file
  my $exclude = [];
  if (my $exclude_file = $app->config->{exclude_file}) {
    my $name = $app->packages->find($id)->{name};
    $exclude = parse_exclude_file($exclude_file, $name);
  }

  # Unpack the package
  my $dir = $pkgs->pkg_checkout_dir($id);
  Cavil::Checkout->new($dir)->unpack({exclude => $exclude});
  $pkgs->unpacked($id);
  $log->info("[$id] Unpacked $dir");

  # Next step
  undef $guard;
  $pkgs->index($id, $job->info->{priority} + 1, [$job->id]);
}

1;
