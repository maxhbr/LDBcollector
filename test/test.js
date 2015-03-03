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

var baseIRI = 'http://www.frob.mobi/';

// var accept = [
//     'application/ld+json;q=1.0',
//     'application/trig;q=0.9',
//     'application/n-quads;q=0.7',
//     'text/turtle;q=0.6',
//     'application/n-triples;q=0.5',
//     'text/n3;q=0.4',
//     'text/html;q=0.3'
// ].join (',');

suite ('Apache configuration', function () {

    test ('vocabulary (content negotiate html)', function () {
        return rp({
            url: baseIRI + 'ns',
            headers: {
                Accept: 'text/turtle;q=0.3,text/html;q=0.7'
            }
        }).then (function (response) {
            assert.equal (response.statusCode, 200);
            assert.equal (response.headers['content-type'], 'text/html');
            assert.equal (response.body.slice(0, 15), '<!DOCTYPE html>');
        });
    });

    test ('vocabulary (content negotiate turtle)', function () {
        return rp({
            url: baseIRI + 'ns',
            headers: {
                Accept: 'text/turtle;q=0.9,text/html;q=0.7'
            }
        }).then (function (response) {
            assert.equal (response.statusCode, 200);
            assert.equal (response.headers['content-type'], 'text/turtle');
            assert.equal (response.body.slice(0, 7), '@prefix');
        });
    });

    test ('vocabulary (content negotiate json-ld)', function () {
        return rp({
            url: baseIRI + 'ns',
            headers: {
                Accept: 'text/turtle;q=0.3,application/ld+json;q=0.8,text/html;q=0.7'
            }
        }).then (function (response) {
            assert.equal (response.statusCode, 200);
            assert.equal (response.headers['content-type'], 'application/ld+json');
            assert.equal (response.body.slice(0, 1), '{');
        });
    });

    test ('vocabulary (.html)', function () {
        return rp({ url: baseIRI + 'ns.html' }).then (function (response) {
            assert.equal (response.statusCode, 200);
            assert.equal (response.headers['content-type'], 'text/html');
            assert.equal (response.body.slice(0, 15), '<!DOCTYPE html>');
        });
    });

    test ('vocabulary (.ttl)', function () {
        return rp({ url: baseIRI + 'ns.ttl' }).then (function (response) {
            assert.equal (response.statusCode, 200);
            assert.equal (response.headers['content-type'], 'text/turtle');
            assert.equal (response.body.slice(0, 7), '@prefix');
        });
    });

    test ('vocabulary (.jsonld)', function () {
        return rp({ url: baseIRI + 'ns.jsonld' }).then (function (response) {
            assert.equal (response.statusCode, 200);
            assert.equal (response.headers['content-type'], 'application/ld+json');
            assert.equal (response.body.slice(0, 1), '{');
        });
    });

    test ('vocabulary (trailing slash redirect)', function () {
        return rp({
            url: baseIRI + 'ns/',
            headers: {
                Accept: 'text/turtle;q=0.3,text/html;q=0.7'
            }
        }).then (function (response) {
            assert.equal (response.statusCode, 200);
            assert.equal (response.headers['content-type'], 'text/html');
            assert.equal (response.body.slice(0, 15), '<!DOCTYPE html>');
        });
    });

    test ('license', function () {
        return rp({ url: baseIRI + 'license' }).then (function (response) {
            assert.equal (response.statusCode, 200);
            assert.equal (response.headers['content-type'], 'text/html');
            assert.equal (response.body.slice(0, 15), '<!DOCTYPE html>');
        });
    });

    test ('license (trailing slash redirect)', function () {
        return rp({ url: baseIRI + 'license/' }).then (function (response) {
            assert.equal (response.statusCode, 200);
            assert.equal (response.headers['content-type'], 'text/html');
            assert.equal (response.body.slice(0, 15), '<!DOCTYPE html>');
        });
    });

});
