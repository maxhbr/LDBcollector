# Fedora License Data Project

This project contains data for licenses that have been reviewed
for use in the Fedora Linux project. For more on the criteria 
Fedora applies for such review, see [License Approval(https://docs.fedoraproject.org/en-US/legal/license-approval)

Licenses are categorized by their status of allowed (generally, or for specific uses) 
or not-allowed and published to [Fedora Docs Legal](https://docs.fedoraproject.org/en-US/legal).
The data may include additional notes and provides
mappings between the [SPDX license expressions](https://spdx.org/licenses/) and the older Fedora
"Callaway" short license names.

To request review of a new license for use in Fedora Linux, follow the process described
at https://docs.fedoraproject.org/en-US/legal/license-review-process

The project also intends to publish the combined license information
in a number of data file formats and provide a package in Fedora for
other projects to reference, such as package building tools and
package checking tools.

The Fedora Legal team is responsible for this project.

## Contribution

To create a merge request to this project you must log in using Fedora OpenID. You can do that on [SSO page](https://gitlab.com/groups/fedora/-/saml/sso).

The source about licenses is stored in `data/` directory. One file per license.
The source data are stored in [TOML](https://toml.io/en/) format. This was agreed as a simplest format for even non-technical contributors.

The RPM package contains the data in JSON format. If you need the data in a different format, you can send a merge request that converts the TOML data to a different format. We can have multiple output formats, but the source format has to be preserved.

## License

License data: CC0-1.0
Scripts: BSD-3-Clause
