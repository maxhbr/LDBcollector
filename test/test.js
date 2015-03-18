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
var rp = require ('request-promise').defaults({ resolveWithFullResponse: true });

var baseIRI = 'http://10.237.180.17/';

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
        assert.equal (response.statusCode, expected.statusCode);
        assert.equal (response.headers['content-type'], expected.contentType);
        assert.equal (response.body.slice(0, expected.startsWith.length), expected.startsWith);
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

});
