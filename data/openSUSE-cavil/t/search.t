# Copyright (C) 2018-2020 SUSE LLC
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

use Mojo::Base -strict;

use FindBin;
use lib "$FindBin::Bin/lib";

use Test::More;
use Test::Mojo;
use Cavil::Test;

plan skip_all => 'set TEST_ONLINE to enable this test' unless $ENV{TEST_ONLINE};

my $cavil_test = Cavil::Test->new(online => $ENV{TEST_ONLINE}, schema => 'search_test');
my $t          = Test::Mojo->new(Cavil => $cavil_test->default_config);
$cavil_test->mojo_fixtures($t->app);

# Modify fixtures so there are packages with different names to search for
my $pkgs = $t->app->packages;
$pkgs->update(
  {id => 1, state => 'correct', result => 'Perfect', checksum => 'Artistic-2.0-3:Hsyo', review_timestamp => 1});
$pkgs->update(
  {id => 2, state => 'correct', result => 'The best', checksum => 'Artistic-1.0-3:PeRl', review_timestamp => 1});
$t->app->pg->db->update('bot_packages', {name => 'perl'}, {id => 2});

subtest 'Basic search with suggestion' => sub {
  $t->get_ok('/')->status_is(200)->element_exists('form[action=/search] input[name=q]');
  $t->get_ok('/search?q=perl')->status_is('200')->element_exists('form[action=/search] input[name=q][value=perl]')
    ->element_exists('#review-search')->text_like('#suggestions td a', qr/perl-Mojolicious/);
  $t->get_ok('/search?q=perl-Mojolicious')->status_is('200')->element_exists('#review-search')
    ->element_exists_not('#suggestions');
};

done_testing();
