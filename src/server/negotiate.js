/*

negotiate.js -- this file is part of the licensedb.org server.
copyright 2013 Kuno Woudt

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

var _types = _([
    [ "text/html",           "html"   ],
    [ "application/rdf+xml", "rdf"    ],
    [ "application/json",    "json"   ],
    [ "application/ld+json", "jsonld" ]
]);

var typemap = _types.reduce (function (memo, val) {
    memo[val[0]] = val[1];
    return memo;
}, {});

var available_types = _types.map (function (val) { return val[0]; });

var base_url = process.argv[2] ? process.argv[2] : "";

function error404 (response)
{
    response.writeHead(404, {'Content-Type': 'text/plain'});
    response.end('Not Found\n');
}

exports.content = function (request, response)
{
    var negotiator = new Negotiator(request);
    var content_type = negotiator.preferredMediaType(available_types);

    if (!content_type)
        return error404 (response);

    var location = url.parse(request.url);
    location.pathname = location.pathname + '.' + typemap[content_type]

    if (!fs.existsSync('production.www'+location.pathname))
        return error404 (response)

    var location_str = base_url + url.format (location);

    response.writeHead(303, {
        'Content-Type': 'text/plain',
        'Location': location_str,
    });
    response.end('see: ' + location_str + '\n');
};
