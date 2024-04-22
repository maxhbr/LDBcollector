/**
 *   This file is part of wald:find.
 *   Copyright (C) 2015  Kuno Woudt <kuno@frob.nl>
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of copyleft-next 0.3.0.  See LICENSE.txt.
 */

'use strict';

var React = require('react');
var _ = require('underscore');
var httpinvoke = require('httpinvoke/httpinvoke-browser');
var s = require('underscore.string');
var wald = require('wald/jsx');

var Heading = React.createClass({
    propTypes: {
        model: React.PropTypes.instanceOf(wald.view.Model).isRequired
    },
    render: function () {
        var license = this.props.model;
        var hasVersion = license.literal('dc:hasVersion');
        var versionString = null;
        if (hasVersion) {
            versionString = <span>version {hasVersion}</span>;
        }

        return (
            <h1>{license.literal('dc:title')} {versionString} </h1>
        );
    }
});

var License = React.createClass({
    propTypes: {
        model: React.PropTypes.instanceOf(wald.view.Model).isRequired
    },
    render: function () {
        var license = this.props.model;

        return (
            <section className="license-metadata">
                <h2>Metadata</h2>
                <wald.view.Image src={license.links('foaf:logo')} />
                <wald.view.KeyValue subject={license} predicate="li:id" />
                <wald.view.KeyValue subject={license} predicate="li:name" />
                <hr />
                <wald.view.KeyValue subject={license} predicate="dc:title" />
                <wald.view.KeyValue subject={license} predicate="dc:identifier" />
                <wald.view.KeyValue subject={license} predicate="dc:hasVersion" />
                <wald.view.KeyValue subject={license} predicate="dc:creator" />
                <hr />
                <wald.view.KeyValue subject={license} predicate="li:plaintext" />
                <wald.view.KeyValue subject={license} predicate="cc:legalcode" />
                <wald.view.KeyValue subject={license} predicate="li:libre" />
                <hr />
                <wald.view.KeyValue subject={license} predicate="cc:permits" />
                <wald.view.KeyValue subject={license} predicate="cc:requires" />
                <hr />
                <wald.view.KeyValue subject={license} predicate="dc:replaces" />
                <hr />
                <wald.view.KeyValue subject={license} predicate="spdx:licenseId" />
            </section>
        );
    }
});

var PlainText = React.createClass({
    getInitialState: function () {
        return { body: 'Loading...' };
    },
    componentDidMount: function () {
        if (this.props) {
            this.loadDocument(this.props);
        }
    },
    componentWillReceiveProps: function (nextProps) {
        this.loadDocument(nextProps);
    },
    loadDocument: function (props) {
        var self = this;
        var values = props.model.list('li:plaintext');

        var plaintext = _(values).find(function (iri) {
            return s(iri).startsWith('https://licensedb.org/id/');
        });

        if (plaintext) {
            httpinvoke(plaintext, 'GET').then(function (data) {
                self.setState({ body: data.body });
            });
        } else {
            self.setState({ body: 'Full license text not available' });
        }
    },
    render: function () {
        return (
            <section className="license-plaintext">
                <h2>License text</h2>
                <pre>{this.state.body}</pre>
            </section>
        );
    }
});

exports.Heading = Heading;
exports.License = License;
exports.PlainText = PlainText;

// -*- mode: web -*-
// -*- engine: jsx -*-
