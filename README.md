<!-- SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>

     SPDX-License-Identifier: GPL-2.0-only
-->
# LicenseDb

License as a service provides a convenient and effective way for organizations to
manage their use of open-source licenses. With the growing popularity of open-source
software, organizations are finding it more difficult to keep track of the various
licenses and terms under which they are permitted to use open-source components.
Open-source licenses can be complicated, making it difficult to understand how they
apply to a specific piece of software or interact with other licenses. It can be
used for various purposes by organizations and tools like [FOSSology](https://fossology.org)
and [SW360](https://eclipse.org/sw360) like license identification, filtering, and
managing licenses. There are benefits of this service such as increasing flexibility,
a faster time-to-access, and managing the database.

## Database

Licensedb database has licenses, obligations, obligation map, users, their audits
and changes.

- **license_dbs** table has list of licenses and all the data related to the licenses.
- **obligations** table has the list of obligations that are related to the licenses.
- **obligation_maps** table that maps obligations to their respective licenses.
- **users** table has the user that are associated with the licenses.
- **audits** table has the data of audits that are done in obligations or licenses
- **change_logs** table has all the change history of a particular audit.

![ER Diagram](./docs/assets/licensedb_erd.png)

## APIs

There are multiple API endpoints for licenses, obligations, user and audit
endpoints.

### API endpoints

Check the OpenAPI documentation for the API endpoints at
[cmd/laas/docs/swagger.yaml](https://github.com/fossology/LicenseDb/blob/main/cmd/laas/docs/swagger.yaml).

The same can be viewed by Swagger UI plugin after installing and running the
tool at [http://localhost:8080/swagger/index.html](http://localhost:8080/swagger/index.html).

### Authentication

To get the access token, send a POST request to `/api/v1/login` with the
username and password.

```bash
curl -X POST "http://localhost:8080/api/v1/login" \
-H "accept: application/json" -H "Content-Type: application/json" \
-d "{ \"username\": \"<username>\", \"password\": \"<password>\"}"
```

As the response of the request, a JWT will be returned. Use this JWT with the
`Authorization` header (as `-H "Authorization: <JWT>"`) to access endpoints
requiring authentication.

## Prerequisite

Please [install and set-up Golang](https://go.dev/doc/install) on your system
in advance.

## How to run this project?

- Clone this Project and Navigate to the folder.

``` bash
git clone https://github.com/fossology/LicenseDb.git
cd LicenseDb
```

- Create the `external_ref_fields.yaml` file in the root directory of the project and change the
  values of the extra license json keys as per your requirement.

```bash
cp external_ref_fields.yaml.example external_ref_fields.yaml
vim external_ref_fields.yaml
```

- Generate Go struct for the extra fields listed in the external_ref_fields.yaml.

```bash
go generate ./...
```

- Build the project using following command.

```bash
go build ./cmd/laas
```

- Create the `.env` file in the root directory of the project and change the
  values of the environment variables as per your requirement.

```bash
cp .env.example .env
vim .env
```

- Run the executable.

```bash
./laas
```

- You can directly run it by the following command.

```bash
go run ./cmd/laas
```

### Create first user
Connect to the database using `psql` with the following command.
```bash
psql -h localhost -p 5432 -U fossy -d fossology
```

Run the following query to create the first user.
```sql
INSERT INTO users (username, userpassword, userlevel) VALUES ('<username>', '<password>', 'admin'); 
```

### Generating Swagger Documentation
1. Install [swag](https://github.com/swaggo/swag) using the following command.
    ```bash
    go install github.com/swaggo/swag/cmd/swag@latest
    ```
2. Run the following command to generate swagger documentation.
    <!-- https://github.com/swaggo/swag/issues/817#issuecomment-730895033 -->
    ```bash
    swag init --parseDependency --generalInfo api.go --dir ./pkg/api,./pkg/auth,./pkg/db,./pkg/models,./pkg/utils --output ./cmd/laas/docs
    ```
3. Swagger documentation will be generated in `./cmd/laas/docs` folder.
4. Run the project and navigate to `http://localhost:8080/swagger/index.html` to view the documentation.
5. Optionally, after changing any documentation comments, format them with following command.
    ```bash
    swag fmt --generalInfo ./pkg/api/api.go --dir ./pkg/api,./pkg/auth,./pkg/db,./pkg/models,./pkg/utils
    ```
