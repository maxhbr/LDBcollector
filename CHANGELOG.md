# Changelog

## 0.5.0 - RC1

FEATURES :
* [Add step for Outbound license compatibility](https://gitlab.com/hermine-project/hermine/-/merge_requests/582)
* [Hash tokens and set expiry date](https://gitlab.com/hermine-project/hermine/-/merge_requests/605)
* [Allow updating existing components on SBOM import](https://gitlab.com/hermine-project/hermine/-/merge_requests/606)
* [Keep track of and display import history for a release](https://gitlab.com/hermine-project/hermine/-/merge_requests/600)
* [Add API endpoint to add a single dependency to a release](https://gitlab.com/hermine-project/hermine/-/merge_requests/596)
* [Add filters/seach on components, authorized contexts, derogations, licenses choices and curations.](https://gitlab.com/hermine-project/hermine/-/merge_requests/602)

BUGFIXES:
* [Limit default API permissions](https://gitlab.com/hermine-project/hermine/-/merge_requests/605)
* [Create missing teams on the fly when importing Compliance actions](https://gitlab.com/hermine-project/hermine/-/merge_requests/601)
* [Fix edition of authorized context](https://gitlab.com/hermine-project/hermine/-/merge_requests/599)
* [API: Add id field listing exploitations ](https://gitlab.com/hermine-project/hermine/-/merge_requests/595)
*[Allow to set CSRF_TRUSTED_ORIGINS in Docker environment with or without protocols ](https://gitlab.com/hermine-project/hermine/-/merge_requests/594)
*[Set Poetry minimal version to 2.0](https://gitlab.com/hermine-project/hermine/-/merge_requests/597)
* [Set Postgres version in docker compose](https://gitlab.com/hermine-project/hermine/-/merge_requests/587)

## O.4.0:

FEATURES :
* Add filters on release SBOM table [12011ee1](https://gitlab.com/hermine-project/hermine/-/commit/12011ee1beecae5cba63f2bbf2eb4b623de5ef38) [97083969](https://gitlab.com/hermine-project/hermine/-/commit/97083969)
* Create a proper 404 page [7741223a](https://gitlab.com/hermine-project/hermine/-/commit/7741223a)
* Add search in curations page [8510e823](https://gitlab.com/hermine-project/hermine/-/commit/8510e823)
* Derogation can be created from release validation page [c04bdbd8](https://gitlab.com/hermine-project/hermine/-/commit/c04bdbd8)
* Add horizontal scroll on tables [e57a3837](https://gitlab.com/hermine-project/hermine/-/commit/e57a3837)
* Add new links to objects detail page in lists [4c60a007](https://gitlab.com/hermine-project/hermine/-/commit/4c60a007)
* Allow authentification through `HTTP-X-Remote-User` header [c741c3de](https://gitlab.com/hermine-project/hermine/-/commit/c741c3de)
* Add missing native forms and remove links to admin panel [7478c0d8](https://gitlab.com/hermine-project/hermine/-/commit/7478c0d8)
* Display licenses choices explanations in release choices list [1c62b474](https://gitlab.com/hermine-project/hermine/-/commit/1c62b474)
* Add `shared.json` in Docker image if available [c0b17538](https://gitlab.com/hermine-project/hermine/-/commit/c0b17538)
* Allow deploys under subpaths [2620d5b7](https://gitlab.com/hermine-project/hermine/-/commit/2620d5b7)
* Import "description" field with SPDX imports [90b48596](https://gitlab.com/hermine-project/hermine/-/commit/90b48596)
* Create a new export mode to use for [hermine-data](https://gitlab.com/hermine-project/hermine-data) contributions and update UX of import / export [9f8184b5](https://gitlab.com/hermine-project/hermine/-/commit/9f8184b5) [33ac4095](https://gitlab.com/hermine-project/hermine/-/commit/33ac4095)

BUGFIXES:
* List only distinct scopes when creating Authorized contexts [23d9bebf](https://gitlab.com/hermine-project/hermine/-/commit/23d9bebfab0f33f4b1b7225248a0167d28e55f15)
* Allow derogation creation when no product or release in form [f217f2fc](https://gitlab.com/hermine-project/hermine/-/commit/f217f2fc8af1539c7d8e56b50b8a1369b2522fb4) [7861d118](https://gitlab.com/hermine-project/hermine/-/commit/7861d11824108de8680d294a08f0f49716668019)
* Fix autocomplete fields styling [2e28be23](https://gitlab.com/hermine-project/hermine/-/commit/2e28be23)
* Exploitation choices did not transfer to usages when scope or project filters were blank [25d611b7](https://gitlab.com/hermine-project/hermine/-/commit/25d611b7)

BREAKING:
* Separate `LicensePolicy` model from `License` model [440cd374](https://gitlab.com/hermine-project/hermine/-/commit/440cd374) [7b6dbafd](https://gitlab.com/hermine-project/hermine/-/commit/7b6dbafd)
* Remove unused fields (License version, radical, autoupgrade and inspiration) [662a6a4e](https://gitlab.com/hermine-project/hermine/-/commit/662a6a4e31d5a1faedf77db5861f0dcebd5e1551)
* Static files are served by default by [Whitenoise](https://whitenoise.readthedocs.io/) [7698ab33](https://gitlab.com/hermine-project/hermine/-/commit/7698ab33) [44976899](https://gitlab.com/hermine-project/hermine/-/commit/44976899) [0a257499](https://gitlab.com/hermine-project/hermine/-/commit/0a257499)
* Static files in are collected at build time in Dockerfile [a7029ee8](https://gitlab.com/hermine-project/hermine/-/commit/a7029ee8)
* `localhost` docker compose profile is removed. The default profile is now the one to use
  locally or behind a reverse proxy. In this default profile, there is no more Caddy image : the Django
  image now directly binds to $PORT. In order to prevent any conflict when upgrading, you should
  run `docker compose up -d --remove-orphans` .


## 0.3.5

FEATURES:
* Add CycloneDX import [6ad734fa](https://gitlab.com/hermine-project/hermine/-/commit/6ad734fa)
* Add API endpoint to component versions [c7e35f08](https://gitlab.com/hermine-project/hermine/-/commit/c7e35f08)
* Allow custom default sub-project/scope names  [550cd194](https://gitlab.com/hermine-project/hermine/-/commit/550cd194)
* Allow to setup SMTP server in Compose .env [c25da744](https://gitlab.com/hermine-project/hermine/-/commit/c25da744)
* Rename "generic obligations" to "compliance actions" [548ef08d](https://gitlab.com/hermine-project/hermine/-/commit/548ef08d)
* Add a basic profile page  [46def88e](https://gitlab.com/hermine-project/hermine/-/commit/46def88e)

BUGFIXES:

* Disable-docker-snapshot [63d9016](https://gitlab.com/hermine-project/hermine/-/commit/63d9016)
* Take proxy config from user config [df6d8474](https://gitlab.com/hermine-project/hermine/-/commit/df6d8474)
* Show license_expression field in API [2e2eed47](https://gitlab.com/hermine-project/hermine/-/commit/2e2eed47)
* Unbreak api-doc generation [60c3c105](https://gitlab.com/hermine-project/hermine/-/commit/60c3c105)

## 0.3.4

* Technical release.

## 0.3.3

FEATURES:
* Validate license spdx ids ([e8da736](https://gitlab.com/hermine-project/hermine/commit/e8da736))
* Allow deleting all usages for a scope / subproject ([3e2e888](https://gitlab.com/hermine-project/hermine/commit/3e2e888))
* Blank values for scope and project in exploitations ([126763f](https://gitlab.com/hermine-project/hermine/commit/126763f))
* Allow autocomplete on Generic field when adding/editing an obligation ([6c1e43f](https://gitlab.com/hermine-project/hermine/commit/6c1e43f))
* Move warranty and liability to shared fields ([669c3a7](https://gitlab.com/hermine-project/hermine/commit/669c3a7))

BUGFIXES:

* Increase max length for license expressions to accomodate real life cases ([b020f06](https://gitlab.com/hermine-project/hermine/commit/b020f06))
* Add style to button ([206fba9](https://gitlab.com/hermine-project/hermine/commit/206fba9))
* Give variable name more related to their content ([e073dbf](https://gitlab.com/hermine-project/hermine/commit/e073dbf))
* Display project and scope ([28c702f](https://gitlab.com/hermine-project/hermine/commit/28c702f))
* Add hyperlink on licence name to licence page ([6addfce](https://gitlab.com/hermine-project/hermine/commit/6addfce))
* Typo in title ([e52709c](https://gitlab.com/hermine-project/hermine/commit/e52709c))
* Display PURLs in component versions ([541f05a](https://gitlab.com/hermine-project/hermine/commit/541f05a))
* Add breadcrumb to product in release creation form ([0947b2f](https://gitlab.com/hermine-project/hermine/commit/0947b2f))


DOCUMENTATION:

* Update page for REST API ([12ab064](https://gitlab.com/hermine-project/hermine/commit/12ab064))


CI:
* Use to be continuous Docker template ([f29e26a](https://gitlab.com/hermine-project/hermine/commit/f29e26a))
* Use TBC standard stages ([be246a0](https://gitlab.com/hermine-project/hermine/commit/be246a0))
* Fix Trivy's Docker image ([a0c54dd](https://gitlab.com/hermine-project/hermine/commit/a0c54dd))
* Temporary removal to fix the blocking false positives ([7974279](https://gitlab.com/hermine-project/hermine/commit/7974279))
* Delete the apt-get lists after installing ([815efe7](https://gitlab.com/hermine-project/hermine/commit/815efe7))
* Update poetry version to allow package-mode option ([b31489d](https://gitlab.com/hermine-project/hermine/commit/b31489d))

MISC:

## 0.3.2
BUGFIXES:
* Add hlink to projects in dashboard ([d367c3e](https://gitlab.com/hermine-project/hermine/commit/d367c3e))
* Categories widget in product forms ([e41e235](https://gitlab.com/hermine-project/hermine/commit/e41e235)), closes [#284](https://gitlab.com/hermine-project/hermine/issues/284)
* Checking many-to-many relationships in check_liscenses_against_policy duplicates usages ([ee81971](https://gitlab.com/hermine-project/hermine/commit/ee81971))
* Copy generics ([3cf6c16](https://gitlab.com/hermine-project/hermine/commit/3cf6c16))
* Display empty progress bar ([69d7bb6](https://gitlab.com/hermine-project/hermine/commit/69d7bb6)), closes [#213](https://gitlab.com/hermine-project/hermine/issues/213)
* Ensure we don't use external primary key value on import ([da91ef9](https://gitlab.com/hermine-project/hermine/commit/da91ef9))
* Wrong statistics on shared database page ([6c8370c](https://gitlab.com/hermine-project/hermine/commit/6c8370c))
* Adapt form layout to div not table ([7641cfd](https://gitlab.com/hermine-project/hermine/commit/7641cfd)), closes [#287](https://gitlab.com/hermine-project/hermine/issues/287)
* Add link to Dashboard in breadcrumbs ([61c524e](https://gitlab.com/hermine-project/hermine/commit/61c524e))
* Display purl type in component list ([4862f03](https://gitlab.com/hermine-project/hermine/commit/4862f03))
* Restore value for model ([17d66c9](https://gitlab.com/hermine-project/hermine/commit/17d66c9))

FEATURES:
* Add number of scopes in summary ([148f27c](https://gitlab.com/hermine-project/hermine/commit/148f27c))
* Change license comment field label ([85f0421](https://gitlab.com/hermine-project/hermine/commit/85f0421)), closes [#225](https://gitlab.com/hermine-project/hermine/issues/225)
* Duplicate obligations with licenses ([d2ab406](https://gitlab.com/hermine-project/hermine/commit/d2ab406))
* New shared data page ([39753c0](https://gitlab.com/hermine-project/hermine/commit/39753c0))
* Pagination on top and bottom of lists ([9eecd30](https://gitlab.com/hermine-project/hermine/commit/9eecd30)), closes [#241](https://gitlab.com/hermine-project/hermine/issues/241)
* Replace text field by select for scope field on derogation forms ([22a3faf](https://gitlab.com/hermine-project/hermine/commit/22a3faf))
* Use purl name when available ([5503e61](https://gitlab.com/hermine-project/hermine/commit/5503e61))

MISC:
* HERMINE_ prefix for compose config ([510abd6](https://gitlab.com/hermine-project/hermine/commit/510abd6))
* Add docker composer version warning to doc ([0617fca](https://gitlab.com/hermine-project/hermine/commit/0617fca))
* Clarify .gitignore ([f19bc16](https://gitlab.com/hermine-project/hermine/commit/f19bc16))
* Eable error logging in prod ([65b9424](https://gitlab.com/hermine-project/hermine/commit/65b9424))
* Logging config ([884843b](https://gitlab.com/hermine-project/hermine/commit/884843b))
* Reuse linting ([879aad3](https://gitlab.com/hermine-project/hermine/commit/879aad3))
* Djhtml linting ([ef85f45](https://gitlab.com/hermine-project/hermine/commit/ef85f45))
* Document dev container ([5a09973](https://gitlab.com/hermine-project/hermine/commit/5a09973))
* Tun devcontainer settings ([97d896d](https://gitlab.com/hermine-project/hermine/commit/97d896d))


## 0.3.1
MISC:
* Update Django to 5.0.3

## 0.3.0
FEATURES:
* Add purl type in component and curation list ([3328c10](https://gitlab.com/hermine-project/hermine/commit/3328c10))
* Better import error messages ([524a015](https://gitlab.com/hermine-project/hermine/commit/524a015))
* Clarify validation results for authorized contexts licenses ([63831a6](https://gitlab.com/hermine-project/hermine/commit/63831a6))
* Display purl_type in component name ([3ea79af](https://gitlab.com/hermine-project/hermine/commit/3ea79af))
* Export ORT versions constraints ([7908df2](https://gitlab.com/hermine-project/hermine/commit/7908df2))
* Update curation versions ([7a2b739](https://gitlab.com/hermine-project/hermine/commit/7a2b739))
* Import purl from SPDX files ([98a9925](https://gitlab.com/hermine-project/hermine/commit/98a9925))

BUGFIXES:
* Do not strip package names starting with @ ([092dbd2](https://gitlab.com/hermine-project/hermine/commit/092dbd2))
* Don't display reference data column when no ref data ([f9c4e3f](https://gitlab.com/hermine-project/hermine/commit/f9c4e3f))
* Form and table styling with bulma and django 5 ([d5419e2](https://gitlab.com/hermine-project/hermine/commit/d5419e2)) ([210f8dc](https://gitlab.com/hermine-project/hermine/commit/210f8dc))
* Avoid some crashes in AND validation form ([77e9940](https://gitlab.com/hermine-project/hermine/commit/77e9940)), closes [#426](https://gitlab.com/hermine-project/hermine/issues/426)
* Only use concluded_license in ort curations ([6f71a47](https://gitlab.com/hermine-project/hermine/commit/6f71a47)), closes [#252](https://gitlab.com/hermine-project/hermine/issues/252)
* Order license list by SDPX id ([f55f735](https://gitlab.com/hermine-project/hermine/commit/f55f735)), closes [#267](https://gitlab.com/hermine-project/hermine/issues/267)
* Replace NOASSERTION by empty string for package url on import, and hide links for NOASSERTION v ([225c38d](https://gitlab.com/hermine-project/hermine/commit/225c38d))
* Don't display links to NOASSERTION ([49ae040](https://gitlab.com/hermine-project/hermine/commit/49ae040)) ([bffc135](https://gitlab.com/hermine-project/hermine/commit/bffc135))
* Fix form render for release_import ([2d9429f](https://gitlab.com/hermine-project/hermine/commit/2d9429f))
* Replace logout link with form ([c12cb89](https://gitlab.com/hermine-project/hermine/commit/c12cb89))
* Fix a permission name ([5573362](https://gitlab.com/hermine-project/hermine/commit/5573362))
* docker: Handle cases where MAX_UPLOAD_SIZE is not defined ([62be3fd](https://gitlab.com/hermine-project/hermine/commit/62be3fd))
* docker: Set correct path to shared.json in entry point ([8f8cd60](https://gitlab.com/hermine-project/hermine/commit/8f8cd60))

DOCUMENTATION:
* Documentation for using Docker without Docker Compose ([41370e7](https://gitlab.com/hermine-project/hermine/commit/41370e7))
* Add dev container configuration ([5065654](https://gitlab.com/hermine-project/hermine/commit/5065654))
* Update reference data ([da8c9d6](https://gitlab.com/hermine-project/hermine/commit/da8c9d6))
* Add link to documentation to the sidebar ([c9a0e9f](https://gitlab.com/hermine-project/hermine/commit/c9a0e9f))
* Move downloading instructions as first step ([17b7833](https://gitlab.com/hermine-project/hermine/commit/17b7833))

MISC:
* Upgrade django to version 5 and Docker python version to 3.12 ([d9c6a01](https://gitlab.com/hermine-project/hermine/commit/d9c6a01)), closes [#254](https://gitlab.com/hermine-project/hermine/issues/254)
* Better perfs for applying licenses choices ([4d5332c](https://gitlab.com/hermine-project/hermine/commit/4d5332c))

## 0.2.1

FEATURES :
* feat: add max upload size to settings ([4ad96b5](https://gitlab.com/hermine-project/hermine/commit/4ad96b5))
* feat: Auto fill licenses chosen from license expression in usage ([5c73663](https://gitlab.com/hermine-project/hermine/commit/5c73663))
* feat: copy licenses and generics from reference ([a1dc2fa](https://gitlab.com/hermine-project/hermine/commit/a1dc2fa))
* feat: separate license shared fields from internal policy field ([2ed0229](https://gitlab.com/hermine-project/hermine/commit/2ed0229))
* feat:Add possility to list orphan obligations - first step ([5e5acd1](https://gitlab.com/hermine-project/hermine/commit/5e5acd1))
* feat: semver filter for curations choices and derogations ([dc2cf2c](https://gitlab.com/hermine-project/hermine/commit/dc2cf2c))
* feat:Diplay license text for custom licenses ([f4ff5a0](https://gitlab.com/hermine-project/hermine/commit/f4ff5a0))
* feat:Display subproject and scope in component details page ([98aa36f](https://gitlab.com/hermine-project/hermine/commit/98aa36f))
* feat(api): allow to search a component by name ([889f7ef](https://gitlab.com/hermine-project/hermine/commit/889f7ef))
* fix: release licensecuration form with semver ([e3813d9](https://gitlab.com/hermine-project/hermine/commit/e3813d9))

MISC :
* fix:Improve readability of validation page ([3f4d021](https://gitlab.com/hermine-project/hermine/commit/3f4d021))
* fix:Update text describing generic obligations ([b85361b](https://gitlab.com/hermine-project/hermine/commit/b85361b))
* fix(ui):Improve wording for license comparison ([b4abb57](https://gitlab.com/hermine-project/hermine/commit/b4abb57))
* feat: performance improvements for apply_curations ([c147372](https://gitlab.com/hermine-project/hermine/commit/c147372))
* feat: performance improvements for derogations check ([ea3ddc2](https://gitlab.com/hermine-project/hermine/commit/ea3ddc2))
* Add SOCIAL_AUTH_REDIRECT_IS_HTTPS parameter. ([ffe0e26](https://gitlab.com/hermine-project/hermine/commit/ffe0e26))
* Add CSRF_TRUSTED_ORIGINS ([e48d9f2](https://gitlab.com/hermine-project/hermine/commit/e48d9f2))
* docs: Add basic info about groups ([37c89f3](https://gitlab.com/hermine-project/hermine/commit/37c89f3))
* docs: Add some help text ([b1c9ae8](https://gitlab.com/hermine-project/hermine/commit/b1c9ae8))
* docs(fix): add warning a about trailing slash for endpoints ([8ffadbc](https://gitlab.com/hermine-project/hermine/commit/8ffadbc))
* docs(fix): Correct command  for importing shared data ([361e14b](https://gitlab.com/hermine-project/hermine/commit/361e14b))
* doc: add hint on migrations for profiling ([e8aaf7e](https://gitlab.com/hermine-project/hermine/commit/e8aaf7e))
* fix(ui): Display number of usages involved at each validation step ([3e9eebb](https://gitlab.com/hermine-project/hermine/commit/3e9eebb))
* feature: display user's groups in header ([3e1d66c](https://gitlab.com/hermine-project/hermine/commit/3e1d66c))

* docker install improvements :
  * feat: init shared data in docker entrypoint ([c61a058](https://gitlab.com/hermine-project/hermine/commit/c61a058)) ([e830971](https://gitlab.com/hermine-project/hermine/commit/e830971)) ([4030482](https://gitlab.com/hermine-project/hermine/commit/4030482))
  * feat: make threads configurable ([1b74668](https://gitlab.com/hermine-project/hermine/commit/1b74668))
  * fix:Transfer CSRF_TRUSTED_ORIGINS to django container env ([e06402b](https://gitlab.com/hermine-project/hermine/commit/e06402b))
  * improve gunicorn conf ([dc6b257](https://gitlab.com/hermine-project/hermine/commit/dc6b257))
  * switch to python:3.10-slim-bullseye (no secu issues) and add optional pip module to install ([c2fcba5](https://gitlab.com/hermine-project/hermine/commit/c2fcba5))

BUGFIXES :
* fix: raise 404 on shared reference pages when no shared data is loaded ([477d9d2](https://gitlab.com/hermine-project/hermine/commit/477d9d2))
* fix boolean var env when not defined ([8298cd7](https://gitlab.com/hermine-project/hermine/commit/8298cd7))
* fix:Fix 500 error for update funding ([7b3e998](https://gitlab.com/hermine-project/hermine/commit/7b3e998)), closes [#238](https://gitlab.com/hermine-project/hermine/issues/238)
* fix:Handle cases when CSRF_TRUSTED_ORIGINS is not defined in env ([e2f800b](https://gitlab.com/hermine-project/hermine/commit/e2f800b))
* fix:Handle unset CSRF_TRUSTED_ORIGINS with Docker ([b8d87a2](https://gitlab.com/hermine-project/hermine/commit/b8d87a2))
* try without gunicorn ([5bc8900](https://gitlab.com/hermine-project/hermine/commit/5bc8900))
* fix: Add template name for licence choice creation in realease ([b299e5b](https://gitlab.com/hermine-project/hermine/commit/b299e5b))
* fix: add venue_choice field to shared data and example data ([9d097cd](https://gitlab.com/hermine-project/hermine/commit/9d097cd))
* fix: Allow editing of curations in admin ([467e4ed](https://gitlab.com/hermine-project/hermine/commit/467e4ed)), closes [#249](https://gitlab.com/hermine-project/hermine/issues/249) [#248](https://gitlab.com/hermine-project/hermine/issues/248)
* fix: Clarify terminology following 2023/10/2 meeting ([c97039f](https://gitlab.com/hermine-project/hermine/commit/c97039f))
* fix: config for forwarded host and proto ([f62aa6f](https://gitlab.com/hermine-project/hermine/commit/f62aa6f))
* fix: Enable ORT SBOM via API ([0802c01](https://gitlab.com/hermine-project/hermine/commit/0802c01))
* fix: Include actual max size in error message ([c083712](https://gitlab.com/hermine-project/hermine/commit/c083712))
* fix: remove duplicated triggered_by in api/generics/sbom/ endpoint ([5a7c06b](https://gitlab.com/hermine-project/hermine/commit/5a7c06b))
* fix: Remove link to edit user profile in admin ([e85b11d](https://gitlab.com/hermine-project/hermine/commit/e85b11d))
* fix(api): Fix nested api for components/versions ([83049fc](https://gitlab.com/hermine-project/hermine/commit/83049fc))

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
