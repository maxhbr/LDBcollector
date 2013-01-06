
var assert = require('assert');
var main = require('../main');

var redirect_test = function (mimetype, suffix) {
    var request = {
        url: 'https://licensedb.org/id/Apache-2',
        headers: { 'Accept': mimetype },
    };

    var expected = {
        status: 303,
        headers: { 'Location': 'https://licensedb.org/id/Apache-2.' + suffix }
    };

    var message = "Accept " + mimetype + " redirects to " + suffix;

    assert.response (main.http, request, expected, message);
};


exports['test 404'] = function () {
    assert.response(
        main.http,
        { url: 'https://licensedb.org/does/not/exist' },
        { status: 404 },
        "Non-existant url results in 404");
};

exports['test redirects'] = function () {
    redirect_test( '*/*',                 'html'   );
    redirect_test( 'text/html',           'html'   );
    redirect_test( 'application/json',    'json'   );
    redirect_test( 'application/ld+json', 'jsonld' );
    redirect_test( 'application/rdf+xml', 'rdf'    );
};
