from oscad.util import is_url_prefix


def test_is_url_prefix():
    for a, b, r in [
        ('/foo', '/foo', True),
        ('/foo', '/foo/bar', True),
        ('/foo', '/foobar', False),
        ('/bar', '/foo', False),
        ('/foo/', '/foo/', True),
        ('/foo/', '/foo/bar', True),
        ('/foo/', '/foobar', False),
        ('/', '/foo', True),
        ('', '/foo', True),
    ]:
        assert is_url_prefix(a, b) == r
