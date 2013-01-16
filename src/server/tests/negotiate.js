/*

server.js -- this file is part of the licensedb.org server.
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

function redirect_test (mimetype, suffix) {

    var request = {
        url: 'https://licensedb.org/id/Apache-2',
        headers: { 'Accept': mimetype }
    };

    var expected = {
        status: 303,
        headers: {
            'Location': 'https://licensedb.org/id/Apache-2.' + suffix
        }
    };

    var message = "Accept " + mimetype + " redirects to " + suffix;
    assert.response(main.server, request, expected, message);
}

exports.test_404 = function() {
    assert.response(main.server,
                    { url: 'https://licensedb.org/does/not/exist' },
                    { status: 404 },
                    "Non-existant url results in 404");
}

exports.test_redirects = function() {
    redirect_test('*/*', 'html');
    redirect_test('text/html', 'html');
    redirect_test('application/json', 'json');
    redirect_test('application/ld+json', 'jsonld');
    redirect_test('application/rdf+xml', 'rdf');
}
