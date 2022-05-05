%global forgeurl https://gitlab.com/fedora/legal/fedora-license-data
%global tag HEAD

Name:           fedora-license-data
Release:        1%{?dist}
Summary:        Fedora Linux license data

License:        BSD-3-Clause AND CC0-1.0
URL:            %{forgeurl}
Source0:        %{forgesource}

BuildRequires:  make
BuildRequires:  python3

%description
This project contains information about licenses used in the Fedora
Linux project.  Licenses are categorized by their approval or
non-approval and may include additional notes.  The data files provide
mappings between the SDPX license expressions and the older Fedora
license abbreviations.

The project also intends to publish the combined license information
in a number of data file formats and provide a package in Fedora for
other projects to reference, such as package building tools and
package checking tools.

The Fedora Legal team is responsible for this project.


%prep
%forgesetup


%build
%make_build


%install
%make_install


%files
%license LICENSE LICENSE.BSD-3-Clause LICENSE.CC0-1.0
%doc AUTHORS README
/usr/share/rpminspect/licenses/fedora-licenses.json


%changelog
* Mon May 02 2022 David Cantrell <dcantrell@redhat.com> - 1.0-1
- Initial build
