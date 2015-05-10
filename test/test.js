/**
 *   This file is part of wald:find.
 *   Copyright (C) 2015  Kuno Woudt <kuno@frob.nl>
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of copyleft-next 0.3.0.  See LICENSE.txt.
 */

'use strict';

/* global suite test */

var assert = require ('assert');
var qs = require ('querystring');
var rp = require ('request-promise').defaults({ resolveWithFullResponse: true });

var baseIRI = 'http://' + process.env.CONTAINER_IP + '/';

var testRequest = function (path, conneg, expected) {
    var options = {
        headers: {},
        url: baseIRI + path
    };

    if (expected.statusCode === undefined) {
        expected.statusCode = 200;
    }

    switch (conneg) {
        case 'html':
        options.headers.Accept = 'text/turtle;q=0.3,text/html;q=0.7';
        break;

        case 'turtle':
        options.headers.Accept = 'text/turtle;q=0.9,text/html;q=0.7';
        break;

        case 'jsonld':
        options.headers.Accept = 'text/turtle;q=0.3,application/ld+json;q=0.8,text/html;q=0.7';
        break;
    }

    return rp(options).then (function (response) {
        var key;

        assert.equal (response.statusCode, expected.statusCode);
        assert.equal (response.headers['content-type'], expected.contentType);

        if (expected.hasOwnProperty('startsWith')) {
            assert.strictEqual (
                response.body.slice(0, expected.startsWith.length),
                expected.startsWith,
                'body starts with "' + expected.contains + '"'
            );
        }

        if (expected.hasOwnProperty('contains')) {
            var contains = expected.contains;
            if (typeof expected.contains === 'string') {
                contains = [ expected.contains ];
            }

            for (key in contains) {
                if (contains.hasOwnProperty(key)) {
                    var idx = response.body.indexOf(contains[key]);
                    assert.ok(idx >= 0, 'body contains "' + contains[key] + '"');
                }
            }
        }

        if (expected.hasOwnProperty('regex')) {
            var regexes = expected.regex;
            if (typeof expected.regex === 'string') {
                regexes = [ expected.regex ];
            }

            for (key in regexes) {
                if (regexes.hasOwnProperty (key)) {
                    var r = new RegExp(regexes[key]);
                    assert.ok(r.test(response.body), 'body matches "' + regexes[key] + '"');
                }
            }
        }

        return response;
    });
};

suite ('Main site', function () {

    test ('vocabulary (content negotiate html)', function () {
        return testRequest('ns', 'html', {
            contentType: 'text/html',
            startsWith: '<!DOCTYPE html>'
        });
    });

    test ('vocabulary (content negotiate turtle)', function () {
        return testRequest('ns', 'turtle', {
            contentType: 'text/turtle',
            startsWith: '@prefix'
        });
    });

    test ('vocabulary (content negotiate json-ld)', function () {
        return testRequest('ns', 'jsonld', {
            contentType: 'application/ld+json',
            startsWith: '{'
        });
    });

    test ('vocabulary (.html)', function () {
        return testRequest('ns.html', null, {
            contentType: 'text/html',
            startsWith: '<!DOCTYPE html>'
        });
    });

    test ('vocabulary (.ttl)', function () {
        return testRequest('ns.ttl', null, {
            contentType: 'text/turtle',
            startsWith: '@prefix'
        });
    });

    test ('vocabulary (.jsonld)', function () {
        return testRequest('ns.jsonld', null, {
            contentType: 'application/ld+json',
            startsWith: '{'
        });
    });

    test ('vocabulary (trailing slash redirect)', function () {
        return testRequest('ns/', 'html', {
            contentType: 'text/html',
            startsWith: '<!DOCTYPE html>'
        });
    });

    test ('license', function () {
        return testRequest('license', null, {
            contentType: 'text/html',
            startsWith: '<!DOCTYPE html>'
        });
    });

    test ('license (trailing slash redirect)', function () {
        return testRequest('license/', null, {
            contentType: 'text/html',
            startsWith: '<!DOCTYPE html>'
        });
    });

    test ('AGPL-3 (content negotiate html)', function () {
        return testRequest('id/AGPL-3', 'html', {
            contentType: 'text/html',
            startsWith: '<!DOCTYPE html>'
        });
    });

    test ('AGPL-3 (content negotiate turtle)', function () {
        return testRequest('id/AGPL-3', 'turtle', {
            contentType: 'text/turtle',
            startsWith: '@prefix'
        });
    });

    test ('AGPL-3 (content negotiate json-ld)', function () {
        return testRequest('id/AGPL-3', 'jsonld', {
            contentType: 'application/ld+json',
            startsWith: '{'
        });
    });

    test ('AGPL-3 (.html)', function () {
        return testRequest('id/AGPL-3.html', null, {
            contentType: 'text/html',
            startsWith: '<!DOCTYPE html>'
        });
    });

    test ('AGPL-3 (.ttl)', function () {
        return testRequest('id/AGPL-3.ttl', null, {
            contentType: 'text/turtle',
            startsWith: '@prefix'
        });
    });

    test ('AGPL-3 (.jsonld)', function () {
        return testRequest('id/AGPL-3.jsonld', null, {
            contentType: 'application/ld+json',
            startsWith: '{'
        });
    });

    test ('AGPL-3 (trailing slash redirect)', function () {
        return testRequest('id/AGPL-3/', 'html', {
            contentType: 'text/html',
            startsWith: '<!DOCTYPE html>'
        });
    });

    test ('HDT download', function () {
        return testRequest('dl/', 'html', {
            contentType: 'text/html',
            regex: 'licensedb\.[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].hdt'
        });
    });

    test ('TTL download', function () {
        return testRequest('dl/', 'html', {
            contentType: 'text/html',
            regex: 'licensedb\.[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].ttl'
        });
    });

});

suite ('Linked Data Fragments server', function () {

    test ('LDF list of datasets', function () {
        return testRequest('data', 'html', {
            contentType: 'text/html;charset=utf-8',
            contains: [ 'Available datasets', 'https://licensedb.org/data/licensedb' ]
        });
    });

    test ('LDF LicenseDB index', function () {
        return testRequest('data/licensedb', 'html', {
            contentType: 'text/html;charset=utf-8',
            contains: [ 'Matches in LicenseDB', 'CC0 1.0 Universal' ]
        });
    });

    test ('Search for AGPLv3 (html)', function () {
        var query = qs.stringify({
            subject: 'https://licensedb.org/id/AGPL-3',
            predicate: '',
            object: ''
        });

        return testRequest('data/licensedb?' + query, 'html', {
            contentType: 'text/html;charset=utf-8',
            contains: [
                'agplv3-155x51.png',
                'GNU Affero General Public License',
                '?predicate=http%3A%2F%2Fcreativecommons.org%2Fns%23legalcode'
            ]
        });
    });

    test ('Search for AGPLv3 (turtle)', function () {
        var query = qs.stringify({
            subject: 'https://licensedb.org/id/AGPL-3',
            predicate: '',
            object: ''
        });

        return testRequest('data/licensedb?' + query, 'turtle', {
            contentType: 'text/turtle;charset=utf-8',
            contains: [
                'agplv3-155x51.png',
                'GNU Affero General Public License',
                '<http://creativecommons.org/ns#legalcode>',
            ]
        });
    });

    test ('Search for FSF approved free licenses (html)', function () {
        var query = qs.stringify({
            subject: '',
            predicate: 'https://licensedb.org/ns#libre',
            object: 'http://fsf.org/'
        });

        return testRequest('data/licensedb?' + query, 'html', {
            contentType: 'text/html;charset=utf-8',
            contains: [
                'AGPL-3',
                'Apache-2',
                'CC-BY-SA-4.0'
            ]
        });
    });

});
