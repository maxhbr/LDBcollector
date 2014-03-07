try:
    from urllib.parse import urljoin  # noqa
except ImportError:
    from urlparse import urljoin  # noqa

try:
    from collections import OrderedDict  # noqa
except ImportError:
    from ordereddict import OrderedDict  # noqa
