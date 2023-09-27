# Changelog

## 0.2.0

BREAKING CHANGES:
* fix: add file upload limit (10 MO) ([9408282](https://gitlab.com/hermine-project/hermine/commit/9408282))
* feat: clarify config and README ([e1e65b4](https://gitlab.com/hermine-project/hermine/commit/e1e65b4))
    * user config is moved to `config.py` file which replaces `mysecrets.py`
    * HOST is no longer defined by an environment variable and must be defined in `config.py`
* feat: pick version from pyproject.toml (not from VERSION.txt file) ([0fbe0ba](https://gitlab.com/hermine-project/hermine/commit/0fbe0ba))
* feat: don't flatten project structure in docker (changes default static file directory) ([537c6f2](https://gitlab.com/hermine-project/hermine/commit/537c6f2))

FEATURES:
* feat: spdx lookup for licenses endpoints ([7802baa](https://gitlab.com/hermine-project/hermine/commit/7802baa))
* feat: display last consulted release in dashboard ([b4a3f35](https://gitlab.com/hermine-project/hermine/commit/b4a3f35))
* feat: all forms accessible from several pages now return to original page on success ([7ebd7dc](https://gitlab.com/hermine-project/hermine/commit/7ebd7dc))
* feat: add specific obligations to generics/sbom endpoint ([14d13d3](https://gitlab.com/hermine-project/hermine/commit/14d13d3))

* fix: Choose auto_now over auto_now_add in ReleaseConsultation.date ([b2c8698](https://gitlab.com/hermine-project/hermine/commit/b2c8698))
* fix: handling of ExpressionError in license_expression lib ([df65e34](https://gitlab.com/hermine-project/hermine/commit/df65e34))
* fix: hardening on sensible spots (no exploitable security risk at the moment) ([7e05f38](https://gitlab.com/hermine-project/hermine/commit/7e05f38))
* fix: hide "shared reference" entry from menu if shared data is not initialized ([7dd7821](https://gitlab.com/hermine-project/hermine/commit/7dd7821))
* fix: licensechoice rule form ([e3a7c05](https://gitlab.com/hermine-project/hermine/commit/e3a7c05))
* fix: licenses/id/obligations nested endpoint ([f4bf100](https://gitlab.com/hermine-project/hermine/commit/f4bf100))
* fix: missing redirection after exploitation edition ([9d7ec9a](https://gitlab.com/hermine-project/hermine/commit/9d7ec9a))
* fix: remove last hardcoded urls ([353b8b2](https://gitlab.com/hermine-project/hermine/commit/353b8b2))
* fix: swagger api doc errors ([220e533](https://gitlab.com/hermine-project/hermine/commit/220e533))
* fix: replace blockquote with linebreaks filter ([b29417b](https://gitlab.com/hermine-project/hermine/commit/b29417b))
* docs(fix):remove trailing comment ([2e1b7b2](https://gitlab.com/hermine-project/hermine/commit/2e1b7b2))
* docs: complete doc for manual install ([27c89dd](https://gitlab.com/hermine-project/hermine/commit/27c89dd))
* docs: Fix url for health checks to get 200 not 301 ([b5665ad](https://gitlab.com/hermine-project/hermine/commit/b5665ad))
* doc: reference data ([a8c1701](https://gitlab.com/hermine-project/hermine/commit/a8c1701))
* doc: Details on reference data text ([2cfc658](https://gitlab.com/hermine-project/hermine/commit/2cfc658))

## 0.0.1

Legacy version tag before version 0.0.2, setting up
project releases.