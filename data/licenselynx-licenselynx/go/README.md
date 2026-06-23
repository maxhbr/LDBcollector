# LicenseLynx for Go

The Go library for LicenseLynx provides a `Map` function that allows mapping of strings to canonical license identifiers.
The return value is a `LicenseObject` together with a boolean indicating whether a match was found.

## Installation

To install the library, run the following command:

```shell
go get github.com/licenselynx/licenselynx/go
```

## Usage

```go
package main

import (
	"fmt"

	"github.com/licenselynx/licenselynx/go"
)

func main() {
	licenseObject, ok := licenselynx.Map("MIT")
	if !ok {
		panic("license not found")
	}

	fmt.Println(licenseObject.ID)
	fmt.Println(licenseObject.Src)

	riskyLicenseObject, ok := licenselynx.Map("License :: LGPLv3", licenselynx.WithRisky())
	if ok {
		fmt.Println(riskyLicenseObject.ID)
	}
}
```

## Organization Licenses

Organizations can register internal or proprietary license identifiers that are kept separate from OSS licenses.
To look up an organization license, pass `WithOrganization`:

```go
licenseObject, ok := licenselynx.Map("SISL 1.5", licenselynx.WithOrganization(licenselynx.OrgSiemens))
```

Helper methods on the returned object:

```go
licenseObject.IsSpdxId()
licenseObject.IsScancodeLicenseId()
licenseObject.IsCustomId()
licenseObject.IsOrganizationSource()
licenseObject.IsOrganizationSourceOf(licenselynx.OrgSiemens)
```

## Development

### Regenerating mapping tables

One important caveat for the go library, compared to the other library implementations, is that the generated mapping tables are checked into the repository.  
This is necessary as go, unlike the other ecosystems, does not have a concept of publishing packages to some registry and, instead, the git repo housing the go module itself is the ground truth.  
As a result the repo must contain the generated files.

This also means that, if a new mapping is added in `data/` the go files MUST be regenerated and committed.  
The actions workflow has a check in place that verifies that the checked in generated files are not stale.

Generating the lookup tables can be done like so:

```shell
mkdir -p _support
python3 scripts/src/load/merge_data.py -o _support/merged_data.build.json
cd go
go generate ./...
```

### Local validation  

In order to run pre-flight checks locally before passing to CI, you can run the following commands:  

1. Run `golangci-lint run ./...` - this requires you to install `golangci-lint` first, see details for your environment [here](https://golangci-lint.run/docs/welcome/install/local/)
2. Run go static checks: `go vet ./...`
3. Execute the test suite: `go test -race ./...`

## License

This project is licensed under the [BSD 3-Clause "New" or "Revised" License](../LICENSE) (SPDX-License-Identifier: BSD-3-Clause).

Copyright (c) Siemens AG 2026 ALL RIGHTS RESERVED
