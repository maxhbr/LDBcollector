#!/usr/bin/env node

var _ = require ('underscore');
var fs = require ('fs');
var url = require ('url');
var http = require ('http');
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

function server (request, response) {

    var negotiator = new Negotiator(request);
    var content_type = negotiator.preferredMediaType(available_types);

    if (!content_type)
        return error404 (response);

    var location = url.parse(request.url);
    location.pathname = location.pathname + '.' + typemap[content_type]

    if (!fs.existsSync('www'+location.pathname))
        return error404 (response)

    var location_str = base_url + url.format (location);

    response.writeHead(303, {
        'Content-Type': 'text/plain',
        'Location': location_str,
    });
    response.end('see: ' + location_str + '\n');
};

function main (port) {

    console.log('Server running at http://127.0.0.1:' + port.toString () + '/');
    http.createServer(server).listen(port);

};

main (26553);

