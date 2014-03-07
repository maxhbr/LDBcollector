class InvalidParameterCombination(Exception):
    pass


class InvalidLicense(Exception):
    def __init__(self, license):
        self.license = license


class MissingParameter(Exception):
    def __init__(self, param):
        self.param = param


class UtilException(Exception):
    pass
