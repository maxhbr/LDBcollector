#!/usr/bin/env node

var fs     = require ('fs');
var clone  = require ('clone');
var Lazy   = require ("lazy");
var _      = require ('underscore');
var jsonld = require ('./jsonld');

_.mixin(require('underscore.string').exports());

function derive (statements) {
    var default_titles = {};
    var english_titles = {};
    var dct = 'http://purl.org/dc/terms/';

    var output = [];
    _(statements).each (function (s, i) {

        // Look for dc:title entries with and without a language tag.
        // If when we're done, we have not found a title without a lanugage tag,
        // use the first english title found.
        if (s.property.nominalValue == dct+'title')
        {
            if (s.object.language)
            {
                if (_(s.object.language).startsWith ('en')) {
                    english_titles[s.subject.nominalValue] = s;
                }
            }
            else
            {
                if (! _(s.object.nominalValue).isEmpty ()) {
                    default_titles[s.subject.nominalValue] = s;
                }
            }
        }

        // Generate a owl:sameAs link with the fully-qualified licensedb identifier.
        if (s.property.nominalValue == 'https://licensedb.org/ns#id')
        {
            sameas_obj = 'https://licensedb.org/id/' + s.object.nominalValue;

            /* Don't output if subject and object are identical. */
            if (s.subject.nominalValue != sameas_obj)
            {
                output.push ({
                    'subject': clone (s.subject),
                    'property': {
                        'nominalValue': 'http://www.w3.org/2002/07/owl#sameAs',
                        'interfaceName': 'IRI'
                    },
                    'object': {
                        'nominalValue': sameas_obj,
                        'interfaceName': 'IRI'
                    }
                });
            }
        }
    });


    _(english_titles).each (function (statement, subject_str) {
        if (! _(default_titles).has (subject_str))
        {
            var newstatement = clone(statement);
            delete newstatement.object["language"];
            output.push (newstatement);
        }
    });

    return output;
};

function read_stdin (callback) {
    var data = "";
    process.stdin.resume ();
    process.stdin.setEncoding ('UTF-8');
    process.stdin.on ('data', function (chunk) { data += chunk; });
    process.stdin.on ('end', function () { callback(data); });
};

function write_statement (statement) {
    process.stdout.write (jsonld.toNQuad (statement));
};

function main (all) {

    read_stdin (function (data) {

        var cc4deed = /4.0\/deed/;

        var statements = _(jsonld.parseNQuads (data)).filter (function (triple) {
            /* HACK: skip the CC 4.0 deeds as subject, as it confuses
             * publish-json.js. */
            return ! cc4deed.test (triple["subject"].nominalValue);
        });

        if (all) {
            _(statements).map (write_statement);
        }

        _(derive (statements)).map (write_statement);
    });
};

function usage () {
    console.log ("derived.js - derive new statements for the License Database.");
    console.log ("copyright 2012  Kuno Woudt");
    console.log ("");
    console.log ("usage:  derive.js [--all]");
};

if (process.argv[2] == "--help")
{
    usage ();
}
else
{
    main (process.argv[2] == "--all");
}
