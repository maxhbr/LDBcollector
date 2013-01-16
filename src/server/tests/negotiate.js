/*

tests/negotiate.js -- this file is part of the licensedb.org server.
copyright 2012,2013 Kuno Woudt

Licensed under the Apache License, Version 2.0 (the "License"); you
may not use this file except in compliance with the License.  You may
obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied.  See the License for the specific language governing
permissions and limitations under the License.

*/

var assert = require ('assert');
var main = require ('../main');
var request = require ('supertest');

var redirect_test = function (mimetype, suffix) {
    describe ('Accept: ' + mimetype, function () {
        it ('responds with ' + suffix, function (done) {
            request(main.server)
                .get('/id/Apache-2')
                .set('Accept', mimetype)
                .expect('Location', 'https://licensedb.org/id/Apache-2.' + suffix)
                .expect(303, done);
        });
    });
};

describe('Content Negotiation', function () {
    describe ('/does/not/exist', function () {
        it ('responds with 404', function(done) {
            request(main.server)
                .get('/does/not/exist')
                .expect(404, done);
        });
    });

    redirect_test('*/*', 'html');
    redirect_test('text/html', 'html');
    redirect_test('application/json', 'json');
    redirect_test('application/ld+json', 'jsonld');
    redirect_test('application/rdf+xml', 'rdf');
});
