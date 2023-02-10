%global forgeurl https://gitlab.com/fedora/legal/fedora-license-data
%if 0%{?fedora} || 0%{?rhel} >= 10
%bcond_without  rpmlint
%else
%bcond_with     rpmlint
%endif

Name:           fedora-license-data
Version:        1.13
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

%if %{with rpmlint}
BuildRequires:  python%{python3_pkgversion}-tomli-w
%endif

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


%if %{with rpmlint}
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
%make_build spec-validate json %{?with_rpmlint:rpmlint}

%install
make DESTDIR=%{buildroot} install-json %{?with_rpmlint:install-rpmlint}


%files
%license LICENSES/*
%doc AUTHORS README.md
%{_datadir}/%{name}/


%if %{with rpmlint}
%files -n rpmlint-%{name}
%license LICENSES/CC0-1.0.txt
%doc AUTHORS README.md
%config(noreplace) %{_sysconfdir}/xdg/rpmlint/*.toml
%endif


%changelog
* Fri Feb 10 2023 Miroslav Suchý <msuchy@redhat.com> 1.13-1
- Fix erroneous substitutions of legacy-name for name
- Add NIST Public Domain license as approved
- Add Blue Oak Model License 1.0.0 as approved

* Sat Jan 28 2023 Miroslav Suchý <msuchy@redhat.com> 1.12-1
- address change in LICENSING structure in spec file
- Make REUSE conformant
- Use revised LicenseRef-Not-Copyrightable
- Revise usage note for CC0-1.0

* Thu Jan 19 2023 Fedora Release Engineering <releng@fedoraproject.org> - 1.11-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Thu Jan 12 2023 Miroslav Suchý <msuchy@redhat.com> 1.11-1
- Add BSD-1-Clause license as an approved license
- add perl-XML-Writer to Update UltraPermissive.txt
- move TTWL and add extension
- Move TPDL.toml
- Add new file: HPND-export-US
- Update Bitstream-Charter.toml

* Mon Dec 26 2022 Miroslav Suchý <msuchy@redhat.com> 1.10-1
- Add GPL-2.0-only WITH GCC-exception-2.0
- Update LicenseRef-HSNCL.toml - remove usage
- Update UltraPermissive.txt: add for texlive-kix
- add for texlive-docbytex
- Update UltraPermissive.txt: add texlive-courseoutline
- Add new file: LicenseRef-CoreMark-Pro
- Add new file: LOOP
- Add new file: TTWL
- Add new file: TPDL
- Add new file: MIT-Wu
- Add new file: SunPro
- remove Fedora block
- Add new file: IJG-short
- Add new file: Bitstream-Charter
- Add new file: Knuth-CTAN
- Add new file: libutil-David-Nugent
- Add new file: W3C-19980720
- Add Symlinks
- add link to legal-doc artifacts
- Old "Python" could be either "Python-2.0.1" or "PSF-2.0"

* Sun Dec 11 2022 Miroslav Suchý <msuchy@redhat.com> 1.9-1
- Add ibus-table-chinese FRWR statement to UltraPermissive
  (rfontana@redhat.com)
- Update UltraPermissive.txt (jlovejoy@redhat.com)
- Add new file for collecting Freely Redistributable (jlovejoy@redhat.com)
- Add BSD-3-Clause-Modification (code@musicinmybrain.net)
- Add public domain license in perl-IO-HTML (mspacek@redhat.com)
- Add GPL-3.0-only WITH Qt-GPL-exception-1.0 (arthur@bols.dev)
- packaging: Don't unnecessarily generate rpmlint data (gotmax@e.email)
- Add public domain text found in .NET 7 source code (omajid@redhat.com)
- data: add HSNCL license (dcavalca@fedoraproject.org)
- Add the OCaml LGPL linking exception (loganjerry@gmail.com)

* Thu Nov 24 2022 Miroslav Suchý <msuchy@redhat.com> 1.8-1
- Add Public Domain license text used in libselinux (plautrba@redhat.com)
- Make LicenseRef for GPLv2 with UPX exception more SPDX-confrmant
  (rfontana@redhat.com)
- Add the equivalent LicenseRef-UPX and LicenseRef-GPL-2.0-or-later WITH UPX
  (rfontana@redhat.com)

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
