class LicenseObject(object):
    def __init__(self, canonical: str, src: str):
        self._canonical = canonical
        self._src = src

    @property
    def canonical(self) -> str:
        return self._canonical

    @property
    def src(self) -> str:
        return self._src
