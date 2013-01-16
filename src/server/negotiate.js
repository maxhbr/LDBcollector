/*

negotiate.js -- this file is part of the licensedb.org server.
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

var _ = require ('underscore');
var fs = require ('fs');
var url = require ('url');
var Negotiator = require ('negotiator');

_.mixin(require('underscore.string').exports());

var MimeType = function (type, suffix) {
    return { 'type': type, 'suffix': suffix };
};

var _types = _([
    MimeType("text/html", "html"),
    MimeType("application/rdf+xml", "rdf"),
    MimeType("application/json", "json"),
    MimeType("application/ld+json", "jsonld"),
]);

var typemap = _types.reduce (function (memo, val) {
    memo[val.type] = val.suffix;
    return memo;
}, {});

var available_types = _types.map (function (val) { return val.type; });
var base_location = {};

var error404 = function (response) {
    response.writeHead (404, { 'Content-Type': 'text/plain' });
    response.end('Not Found\n');
};

exports.init = function (base_url) {
    base_location = url.parse (base_url);
};

exports.content = function (request, response) {
    var negotiator = new Negotiator (request);
    var content_type = negotiator.preferredMediaType (available_types);

    if (!content_type) {
        return error404(response);
    }

    var location = url.parse(request.url);

    location.pathname = location.pathname + '.' + typemap[content_type];

    if (!fs.existsSync('production.www' + location.pathname)) {
        return error404(response);
    }

    var location_str = url.format(_(location).defaults(base_location));

    response.writeHead (303, {
        'Content-Type': 'text/plain',
        'Location': location_str
    });
    response.end('see: ' + location_str + '\n');
};
