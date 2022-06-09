# Fedora License Data Project

This project contains information about licenses used in the Fedora
Linux project.  Licenses are categorized by their approval or
non-approval and may include additional notes.  The data files provide
mappings between the [SDPX license expressions](https://spdx.org/licenses/) and the older Fedora
license abbreviations.

The project also intends to publish the combined license information
in a number of data file formats and provide a package in Fedora for
other projects to reference, such as package building tools and
package checking tools.

The [Fedora Legal team](https://fedoraproject.org/wiki/Legal:Main) is responsible for this project.

## Contribution

To create a merge request to this project you must log in using Fedora OpenID. You can do that on [SSO page](https://gitlab.com/groups/fedora/-/saml/sso).

The source about licenses is stored in `data/` directory. One file per license.
The source data are stored in [TOML](https://toml.io/en/) format. This was agreed as a simplest format for even non-technical contributors.

The RPM package contains the data in JSON format. If you need the data in a different format, you can send a merge request that converts the TOML data to a different format. We can have multiple output formats, but the source format has to be preserved.

## License

CC0-1.0

