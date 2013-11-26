#!/usr/bin/env node

var fs     = require ('fs');
var jsonld = require ('jsonld');
var _      = require ('underscore');

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

function walk (obj, key, list, action) {
    var _obj = _(obj);
    if (_obj.isArray () || _obj.isObject ())
    {
        _obj.each (function (val, key, list) {
            walk (val, key, list, action);
        });
    }

    action (obj, key, list);
};

function directGraph (compacted)
{
    var objects = {};
    var used = {};
    var toplevel = {};

    if (! compacted.hasOwnProperty ("@graph"))
        return compacted;

    _(compacted["@graph"]).each (function (val, key, list) {
        objects[val["@id"]] = val;
    });

    _(objects).each (function (toplevel_object, toplevel_id, list) {
        walk (toplevel_object, null, null, function (val, key, list) {

            if (val.hasOwnProperty ("@id") && !_(list).isEmpty ())
            {
                id = val["@id"];
                if (objects.hasOwnProperty (id))
                {
                    toplevel[toplevel_id] = true;
                    used[id] = true;
                    list[key] = objects[id];
                }
            }
            else
            {
                if (objects.hasOwnProperty (val) && val != toplevel_id)
                {
                    toplevel[toplevel_id] = true;
                    used[val] = true;
                }
            }
        });
    });

    if (_(toplevel).size () != 1)
    {
        throw exception("Multiple top-level objects left after directing the graph");
    }

    var directed = objects[_(toplevel).keys ()[0]];
    directed["@context"] = compacted["@context"];

    return directed;
};

function main (ctx, src, dst) {
    if (!src)
        return usage ();

    if (!dst)
        dst = src.replace (/\.[^.]+$/, '.jsonld')

    var data = fs.readFileSync (src).toString ();
    var context = JSON.parse (fs.readFileSync (ctx).toString ());

    jsonld.fromRDF (data, function (err, parsed) {
        jsonld.compact (parsed, context, { optimize: true }, function (err, compacted) {
            if (compacted)
            {
                save_to(dst, directGraph (compacted));
            }
            else
            {
                console.error ("Error during compaction:", err);
            }
        });
    });
};

main (process.argv[2], process.argv[3], process.argv[4]);
