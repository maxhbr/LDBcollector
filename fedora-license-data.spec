%global forgeurl https://gitlab.com/fedora/legal/fedora-license-data

Name:           fedora-license-data
Version:        1.7
Release:        1%{?dist}
Summary:        Fedora Linux license data

License:        CC0-1.0
URL:            %{forgeurl}
BuildArch:      noarch
# git clone https://gitlab.com/fedora/legal/fedora-license-data.git
# cd fedora-license-data
# packit prepare-sources
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  make
BuildRequires:  python3
%if 0%{?fedora} || 0%{?rhel} >= 8
BuildRequires:  (python%{python3_pkgversion}-tomli if python%{python3_pkgversion} < 3.11)
%else
BuildRequires:  python%{python3_pkgversion}-tomli
%endif
BuildRequires:  python%{python3_pkgversion}-tomli-w

%description
This project contains information about licenses used in the Fedora
Linux project.  Licenses are categorized by their approval or
non-approval and may include additional notes.  The data files provide
mappings between the SDPX license expressions and the older Fedora
license legacy-abbreviations.

The project also intends to publish the combined license information
in a number of data file formats and provide a package in Fedora for
other projects to reference, such as package building tools and
package checking tools.

The Fedora Legal team is responsible for this project.


%if 0%{?fedora} || 0%{?rhel} >= 10
%package -n rpmlint-%{name}
Summary:        Rpmlint configuration with valid license expressions
# this package does not need to depend on the main one
Requires:       rpmlint >= 2
Supplements:    rpmlint >= 2

%description -n rpmlint-%{name}
This package contains information about licenses used in the Fedora
Linux project. The licenses are stored in a way that makes rpmlint read it.
Both the SPDX license expressions and the legacy (callaway) expressions are
allowed.

The Fedora Legal team is responsible for the content.
%endif


%prep
%setup -q -n %{name}-%{version}


%build
%make_build
cp LICENSES/* ./

%install
%make_install


%files
%license LICENSE BSD-3-Clause.txt CC0-1.0.txt
%doc AUTHORS README.md
%{_datadir}/%{name}/


%if 0%{?fedora} || 0%{?rhel} >= 10
%files -n rpmlint-%{name}
%license CC0-1.0.txt
%doc AUTHORS README.md
%config(noreplace) %{_sysconfdir}/xdg/rpmlint/*.toml
%else
%exclude %{_sysconfdir}/xdg/rpmlint/*.toml
%endif


%changelog
* Wed Nov 02 2022 Miroslav Suchý <msuchy@redhat.com> 1.7-1
- redefine JSON format
- Also use rich-deps on EL 8 (miro@hroncok.cz)
- Once again, abandon the toml module, use tomllib/tomli/tomli-w instead
  (miro@hroncok.cz)
- Fix typos in license review template (dcavalca@fedoraproject.org)
- rename [fedora]name to [fedora]legacy-name
- rename [fedora]abbreviation to [fedora]legacy-abbreviation
- Revise toml for GPL-2.0-or-later WITH x11vnc-openssl-exception
  (rfontana@redhat.com)
- Add FSFULLRWD (rfontana@redhat.com)
- Add OFL-1.1-RFN as allowed-fonts (rfontana@redhat.com)
- use tomllib instead of toml
- document availablity of fedora-licenses.json artifact

* Thu Oct 13 2022 Miroslav Suchý <msuchy@redhat.com> 1.6-1
- Add MS-LPL as not-allowed
- Add ISO-8879 to not-allowed with big usage exception
- Delete redundant license info from README.md
- Add LicenseRef-Glyphicons as not-allowed
- Add Spencer-99
- Add LicenseRef-UPX as not-allowed
- Add LicenseRef-STREAM as not-allowed
- Simplify overcomplicated condition to evaluate if a license is approved
- Handle licenses with only SPDX identifier in mkjson.py

* Mon Oct 03 2022 msuchy <msuchy@redhat.com> - 1.5-1
- 1.5 release

* Mon Sep 19 2022 msuchy <msuchy@redhat.com> - 1.4-1
- 1.4 release

* Mon May 02 2022 David Cantrell <dcantrell@redhat.com> - 1.0-1
- Initial build
