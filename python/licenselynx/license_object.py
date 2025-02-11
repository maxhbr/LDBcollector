class LicenseObject(object):
    def __init__(self, canonical, src):
        self._canonical = canonical
        self._src = src

    @property
    def canonical(self):
        return self._canonical

    @property
    def src(self):
        return self._src
