<!-- SPDX-FileCopyrightText: © Fossology contributors

     SPDX-License-Identifier: GPL-2.0-only
-->
# Changelog of LicenseDb

### 1.0.0 (Jul 10th 2025)

LicenseDb is an open-source project designed to simplify license and obligation management for tools such as FOSSology and SW360. 
Its purpose is to streamline the workflow for legal and compliance teams by providing a centralized interface,
eliminating the need to log into and navigate multiple tools manually.

This initial release lays the foundation for a unified compliance workflow platform.

##### Main Features of LicenseDb

* LicenseDB provides a centralized interface to streamline the workflow for legal teams, eliminating the need to log into and navigate multiple tools to manage licenses and obligations.
* APIs for full license lifecycle management including retrieval with filtering, creation, import/export and updates.
* APIs for full obligation lifecycle management including retrieval with filtering, creation, import/export and updates.
* Gives changelogs and analytics about licenses and obligations.


#### Credits to contributors for 1.0.0

```
> Anupam <ag.4ums@gmail.com>
> Avinal Kumar <avinal.xlvii@gmail.com>
> chayandass <daschayan8837@gmail.com>
> deo002 <oberoidearsh@gmail.com>
> Divij Sharma <divijs75@gmail.com>
> Gaurav Mishra <gmishx@gmail.com>
> Kaushlendra Pratap Singh <kaushlendrapratap.9837@gmail.com>
> Kavya Shukla <kavyuushukla59@gmail.com>
> Shaheem Azmal M MD <shaheem.azmal@gmail.com>
> Sourav Bhowmik <sourav.bhowmik@siemens.com>
> Vaibhav <sahusv4527@gmail.com>

```

#### Features

* `62ee51ab3` add(e2e): add e2e testing infrastructure for local and github action
* `4a10a0d74` feat(dashboard): Dashboard api returning different analytics
* `38a725137` feat: added user/createdBy when creating new license
* `8b25459cc` feat: added new category field in obligations
* `965fa5aba` feat: added user json as createdBy field in getLicense
* `9191a517e` feat(spdx_validation): Add validation for spdx id
* `f2f1bdd11` feat(user_profile): Add endpoint to fetch user profile
* `7fc8fee18` feat(oidc_auth): Add backend support for OIDC Auth
* `b220cf463` feat(obligation_classifications): Add admin apis for creating, listing and deleting obligation classifications
* `2127a66b0` feat(admin_obligation_types): Admin apis to create, delete and get obligation types
* `bdb1a2d4d` feat(external_ref): Make external_ref fields configurable
* `82b0c3256` feat(auth): Enable/disable authentication for READ apis via env variable
* `708d56359` feat(changelog): Add changelog entries for creation of entities
* `cc6c8e59b` feat(sort_obligations): Add sorting of obligations by topic
* `e4c4f0e2d` feat(license_sorting): Enable sorting in licenses by spdx_id, fullname and shortname
* `bcab679aa` feat(license_preview): Created an endpoint to fetch all license shortnames
* `40fd7ac11` feat: Introduce Stage to Build and Push Docker Image
* `735497109` feat(obligations_preview): Create an endpoint to fetch topic and type of all obligations
* `d4f8f4fc6` feat: Docker Support for license DB
* `98c3e4790` feat(ci): use CodeQL analysis
* `f501e396e` feat(license): add /export endpoint
* `0609c47bc` feat(license_import): Add endpoint to import licenses via a json file
* `ecd39e5f4` feat(obligations_export): Add functionality to export obligations
* `9db5946ba` feat(obligation_import): Add functionality to import obligations via json file
* `e21c1aa9e` feat(external_references): Integrated external references in db schema and enabled filtering and update on them
* `a7178cb30` feat(obligation_audits): Create endpoint to fetch audits of an obligation
* `39392115a` feat(api): add pagination capabilities with middleware
* `0e8228d6f` feat(ci): Github Workflow for Golang static checks and linting
* `dba59dc87` feat(auth): use JWT tokens
* `c42633253` feat(auth): user bcrypt to encrypt user password
* `988b0b80d` feat(api): add /health endpoint
* `f0ba49024` feat(api): add endpoints to modify obligation maps
* `f33887921` feat(api): add endpoints to get obligation maps
* `9fad40c8f` feat: added obligation endpoints.
* `1df70a575` feat: added audit and change history endpoints.
* `570e8ab10` feat: added authentication in API and search api
* `993ecc438` feat(api): add CORS headers
* `ddccd788f` feat(ci): GitHub Workflow for Swagger APIs doc checks
* `64659f61f` feat: add populating of database from json file
* `e95a79e64` feat: updated the project structure and added test case
* `c6c6d4e6b` feat: added authentication in API and search api
* `554165e97` feat: added two api endpoints i.e, create and update
* `084f8e0dc` feat: added GET endpoints

#### Corrections

* `aeeae43c5` fix(docker): update to go 1.23
* `5a74a8891` fix(obligations):align Swagger docs with existing implementation for obligations endpoint
* `1a9063d13` fix(license): optimize schema export for better performance and consistency
* `2362481ac` refactor(db): rename fossology to licensedb (#105)
* `c8b3d7991` fix(api): correct health API response
* `c0813a2dd` fix(update_license): License update endpoint and it's documentation fixed
* `d5cf63b45` fix(obligation_apis): Make GET obligation classifications and types unauthorized
* `83d2f4269` fix(deps): update golang.org/x/net/html
* `a2daf914a` refactor(obligations): Make separate database tables for classification and type
* `97b885c09` fix(rf): Remove rf prefix from license fields in json
* `e7a4827d2` refactor(licenses): Add validation to license requests and code refactor
* `594643218` fix(doc): fix typo in same external_ref_field
* `6faf87a6b` fix(import_licenses): New licenses were not being created on import
* `e99d788c5` fix(changelog): add changelog entries for type and classification during populatedb
* `fb1e5aa10` refactor(user): Remove password from user response and get rid of redundant structs
* `8c9699056` fix(auditResponse): Add user and obligation or license data to audit response
* `a2caaafa5` refactor(external_ref): Remove unnecessary UpdateExternalRefsJSONPayload type
* `58ca6bb1e` fix(content_disposition): Expose header content-disposition to the browser
* `7eaca0aab` fix(license_obligations): Add type field to response
* `f722ce087` fix(jwt): Add user information in jwt for showing UI according to user permission level
* `62abda08f` fix(license_list): Order licenses by shortname
* `db6b3f31e` fix(users_pagination): Paginate /users endpoint
* `db1ec0a77` refactor(obligation_maps): Add transactions and refactor code
* `7cc95f232` fix(api): check field name before running query
* `26816327e` fix(search): check column name before searching
* `93dc745e3` fix(docs): Fix errors in compilation of docs of struct LicensePATCHRequestJSONSchema
* `29e20be34` fix(license_patch): Fix bug in license patch request
* `9ecd629cd` fix(patch_obligation): Fix patch request bugs in obligation
* `24f99a0f5` fix(license_update_transaction): Enclose the update license functionality in a transaction
* `984bd59f9` fix(required_fields): Make text, topic and type optional in update obligation
* `c560b27ce` fix(update_license): Create audit only if changes are there
* `254a6b6df` fix(transaction): Enclose update obligation in a transaction
* `0fd3aa5ee` fix(bug): Minor bug fixes in audit endpoints
* `e4325eae6` fix(audits): Order audits in descending order by id
* `0e851d4d5` fix(copyright): fix Siemens AG copyrights
* `b08411ac2` fix(lint): Fixed golang linting errors
* `0f04b9558` fix(obligation): fix FirstOrCreate in obligation creation
* `76ce02742` fix(api): fixed error handeling in authentication middleware
* `e701f4701` fix(db): fix DB schema types
* `e725b8390` fix(types): remove space
* `6b4f9615b` fix(obligations): filter active/inactive
* `08fdf8b25` fix(obligations): check if obligation text is updatable

#### Infrastructure

* `64b4e53cc` chore(contributing): add CONTRIBUTING.md file
* `30abaa4fc` chore(notices): add notice files to licenseDb
* `2ab973c08` chore(migration): setup golang-migrate and replace GORM AutoMigrate
* `c7d8e1219` chore(deps): bump golang.org/x/net
* `f962a2285` chore(deps): update Go version and dependencies
* `f78ffc8eb` chore(deps): bump golang.org/x/net
* `45af91942` chore(deps): bump golang.org/x/crypto in the go_modules group
* `7a25d0908` chore(deps): bump github.com/golang-jwt/jwt/v4 in the go_modules group
* `600d240ca` misc: add pull request template
* `456431c83` chore(deps): bump golang.org/x/net from 0.19.0 to 0.23.0
* `7dad7ce3a` chore(deps): bump github.com/jackc/pgx/v5 from 5.4.3 to 5.5.4
* `7db746e1d` chore(deps): bump google.golang.org/protobuf from 1.30.0 to 1.33.0
* `e7c8d90cb` docs(swagger): Make port in swagger docs configurable
* `89641c9fd` chore(readme): update README with new JWT changes
* `ad5e40176` chore(reuse): set reuse lint in CI
* `6cae220f7` chroe: updated README.md and added basic CI
* `1a1a70b4a` chore: added project structure and initial files.
* `4eaf6f6b8` Update README.md
* `dcf82cde5` Update README.md
* `9f5357115` chore(deps): bump golang.org/x/crypto from 0.14.0 to 0.17.0
* `eddff78bb` chore(api): divide API code into different files
* `f14f0721c` chore(api): unify API input/output
* `92caebadb` doc(swagger): add Swagger doc for all endpoints and reorganize routing
* `7c6b28d4a` chore(deps): bump golang.org/x/net from 0.10.0 to 0.17.0
* `49ddeb27e` docs: added documentation and updated readme.md
* `f96cb3ad6` chore: add go format check and update go version
