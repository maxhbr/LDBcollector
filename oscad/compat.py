try:
    from urllib.parse import urljoin, urlparse  # noqa
except ImportError:
    from urlparse import urljoin, urlparse  # noqa

try:
    from collections import OrderedDict  # noqa
except ImportError:
    from ordereddict import OrderedDict  # noqa
