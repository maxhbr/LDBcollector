#!/usr/bin/env node

var fs = require ('fs');
var _  = require ('underscore');

_.mixin(require('underscore.string').exports());

var data = fs.readFileSync (process.argv[2]);
var parsed = JSON.parse (data);

process.stdout.write ("rapper --quiet --input ntriples --output rdfxml-abbrev ");
process.stdout.write (process.argv[3]);

_(parsed["@context"]).each (function (val, key) {
    if (_(val).startsWith ('http'))
    {
        process.stdout.write (" -f \'xmlns:" + key + "=\"" + val + "\"\'");
    }
});




