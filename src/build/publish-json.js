#!/usr/bin/env node

var _      = require ('underscore');
var fs     = require ('fs');
var jsonld = require ('jsonld');
var path   = require ('path');
var t2j    = require ('turtle-to-jsonld');

_.mixin(require('underscore.string').exports());

var exception = function (name, message) {
    var e = function () { this.name = name,  this.message = message };
    e.prototype = new Error ();

    return new e ();
};

function usage () {
    console.log ("publish-json.js - ntriples to json-ld conversion");
    console.log ("copyright 2012  Kuno Woudt");
    console.log ("");
    console.log ("usage:  publish-json.js <CONTEXT> <SRC>");
};

function save_to (filename, data) {
    fs.writeFileSync(filename, JSON.stringify (data, null, 4));
};

function main (ctx, src, dst) {
    if (!src) {
        return usage ();
    }

    if (!dst) {
        dst = src.replace (/\.[^.]+$/, '.jsonld');
    }

    var id = path.basename(src, '.turtle');
    var root = 'https://licensedb.org/id/' + id;
    var data = fs.readFileSync (src).toString ();
    var context = JSON.parse (fs.readFileSync (ctx).toString ());

    t2j.compactFromTurtle (data, context, root)
        .then (function (result) {
            save_to(dst, result);
        })
        .catch (function (err) {
            console.log("ERROR: " + err);
        });
};

main (process.argv[2], process.argv[3], process.argv[4]);
