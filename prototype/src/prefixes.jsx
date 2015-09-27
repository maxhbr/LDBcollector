/**
 *   This file is part of wald:find.
 *   Copyright (C) 2015  Kuno Woudt <kuno@frob.nl>
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of copyleft-next 0.3.0.  See LICENSE.txt.
 */

'use strict';

var prefixes = function (datastore) {
    datastore.addPrefix('lidb', 'https://licensedb.org/id/');
    datastore.addPrefix('cc', 'http://creativecommons.org/ns#');
    datastore.addPrefix('dbr', 'http://dbpedia.org/resource/');
    datastore.addPrefix('dc', 'http://purl.org/dc/terms/');
    datastore.addPrefix('dc1', 'http://purl.org/dc/elements/1.1/');
    datastore.addPrefix('dc11', 'http://purl.org/dc/elements/1.1/');
    datastore.addPrefix('foaf', 'http://xmlns.com/foaf/0.1/');
    datastore.addPrefix('frbr', 'http://purl.org/vocab/frbr/core#');
    datastore.addPrefix('li', 'https://licensedb.org/ns#');
    datastore.addPrefix('md', 'http://www.w3.org/ns/md#');
    datastore.addPrefix('owl', 'http://www.w3.org/2002/07/owl#');
    datastore.addPrefix('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#');
    datastore.addPrefix('rdfs', 'http://www.w3.org/2000/01/rdf-schema#');
    datastore.addPrefix('schema', 'http://schema.org/');
    datastore.addPrefix('spdx', 'http://spdx.org/rdf/terms#');
    datastore.addPrefix('xhv', 'http://www.w3.org/1999/xhtml/vocab#');
    datastore.addPrefix('xml', 'http://www.w3.org/XML/1998/namespace');
    datastore.addPrefix('xsd', 'http://www.w3.org/2001/XMLSchema#');
}

module.exports = prefixes;
