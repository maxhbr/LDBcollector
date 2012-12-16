#!/usr/bin/env node

var fs     = require ('fs');
var Lazy   = require ("lazy");
var _      = require ('underscore');
var jsonld = require ('./jsonld');

_.mixin(require('underscore.string').exports());

// The normalizations done here are as follows:
//
// 1. http://purl.org/dc/elements/1.1/title is replaced with
//    http://purl.org/dc/terms/title if the object is a literal.  The
//    only difference between the two is that dcterms:title has a range
//    specified.
//
// 2. http://purl.org/dc/elements/1.1/creator is replaced with
//    http://purl.org/dc/terms/creator if the object is not a literal.
//    The difference here is that the range for dcterms:creator is
//    dcterms:agent, which should be a resource or blank node.
//
// see:
// http://dublincore.org/usage/decisions/2010/dcterms-changes/
//
// 3. http://purl.org/dc/elements/1.1/description is replaced with
//    http://purl.org/dc/terms/description.
//
// 4. http://purl.org/dc/elements/1.1/identifier is replaced with
//    http://purl.org/dc/terms/identifier if the object is a literal.
//    The only difference between the two is that dcterms:identifier
//    has a range specified.
//
// 5. http://purl.org/dc/elements/1.1/source is replaced with
//    http://purl.org/dc/terms/source.
//
// see:
// http://dublincore.org/usage/decisions/2008/dcterms-changes/

function normalize (statements) {
    var default_titles = {};
    var english_titles = {};
    var dc11 = 'http://purl.org/dc/elements/1.1/';
    var dct = 'http://purl.org/dc/terms/';

    var output = [];
    for (var i in statements) {
        if (statements.hasOwnProperty (i)) {
            var s = statements[i];

            if (s.property.nominalValue == dc11+'title'
               && s.object.interfaceName == 'LiteralNode')
            {
                s.property.nominalValue = dct+'title';
            }

            if (s.property.nominalValue == dc11+'creator'
               && s.object.interfaceName != 'LiteralNode')
            {
                s.property.nominalValue = dct+'creator';
            }

            if (s.property.nominalValue == dc11+'description')
            {
                s.property.nominalValue = dct+'description';
            }

            if (s.property.nominalValue == dc11+'identifier')
            {
                s.property.nominalValue = dct+'identifier';
            }

            if (s.property.nominalValue == dc11+'source')
            {
                s.property.nominalValue = dct+'source';
            }

            if (s.property.nominalValue == dct+'title')
            {
                if (s.object.language)
                {
                    if (_(s.object.language).startsWith ('en')) {
                        english_titles[s.subject] = s.object.nominalValue;
                    }
                }
                else
                {
                    if (! _(s.object.nominalValue).isEmpty ()) {
                        default_titles[s.subject] = s.object.nominalValue;
                    }
                }
            }

            // Skip empty values.
            if (! _(s.object.nominalValue).isEmpty ())
            {
                output.push (s);
            }
        }
    }

    return output;
};

function main (quiet) {

    new Lazy(process.stdin).lines.forEach(function(line) {

        var statements = [];
        try {
            statements = statements.concat (jsonld.parseNQuads (line.toString ()))
        }
        catch (e) {
            if (!quiet)
            {
                console.warn ("WARNING: " + e.toString ());
                console.warn ("-> " + line);
            }
        }

        _.chain(normalize (statements)).map (jsonld.toNQuad).map (function (val) {
            process.stdout.write (val);
        });
    });

    process.stdin.resume();
};

function usage () {
    console.log ("normalize.js - perform normalizations for The License Database.");
    console.log ("copyright 2012  Kuno Woudt");
    console.log ("");
    console.log ("usage:  normalize.js [--quiet]");
};


if (process.argv[2] == "--help")
{
    usage ();
}
else
{
    main (process.argv[2] == "--quiet");
}