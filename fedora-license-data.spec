%global forgeurl https://gitlab.com/fedora/legal/fedora-license-data
%if 0%{?fedora} || 0%{?rhel} >= 10
%bcond_without  rpmlint
%else
%bcond_with     rpmlint
%endif

Name:           fedora-license-data
Version:        1.28
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
BuildRequires:  python3-devel
%if 0%{?fedora} || 0%{?rhel} >= 8
BuildRequires:  (python%{python3_pkgversion}-tomli if python%{python3_pkgversion} < 3.11)
%else
BuildRequires:  python%{python3_pkgversion}-tomli
%endif
# grammar
%if 0%{?fedora} || 0%{?rhel} > 8
BuildRequires:  python3dist(lark-parser)
%endif

%if %{with rpmlint}
BuildRequires:  python%{python3_pkgversion}-tomli-w
%endif

%description
This project contains information about licenses used in the Fedora
Linux project.  Licenses are categorized by their approval or
non-approval and may include additional notes.  The data files provide
mappings between the SPDX license expressions and the older Fedora
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
%make_build spec-validate json grammar %{?with_rpmlint:rpmlint}

%install
make DESTDIR=%{buildroot} install-json install-grammar %{?with_rpmlint:install-rpmlint}

%check
%if 0%{?fedora} || 0%{?rhel} > 8
# the grammar cannot be parsed on rhel8 and older
make check-grammar
%endif

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
* Sat Aug 19 2023 Miroslav Suchý <msuchy@redhat.com> 1.28-1
- Add TU-Berlin-2.0 license
- Add HPLIP nonfree licenses
- Add LicenseRef-libzmq
- Add CCLP content licenses
- add LicenseRef-Waqf as not-allowed
- Add LicenseRef-Bacula as allowed
- Add some allowed licenses
- Reformat REUSE licenses
- Add autoconf public domain declaration
- Update MIT-testregex.toml to delete [fedora] block
- add MIT-testregex license
- add GPL-3.0-or-later WITH Texinfo-exception
- add usage notes to LicenseRef-TCGL
- Add hpcdtoppm as not allowed
- add Zeeff license

* Fri Aug 04 2023 Miroslav Suchý <msuchy@redhat.com> 1.27-1
- Add TCGL as not allowed
- Add GPL-2.0-or-later WITH GCC-exception-2.0
- Add Soundex License
- Add HP-1989
- add GPL-3.0-or-later WITH Autoconf-exception-generic-3.0
- Add SL license
- Add check-cvs license
- add John Walker to ultrapermissive collection
- Add Artistic-1.0 as not allowed.
- Add BSD-3-Clause-Clear as not allowed.
- Add LicenseRef-JasPer as not allowed.
- Revert "Remove AFL-2.0 since it is probably not in Fedora"
- Add LicenseRef-rdist-Cooper as not allowed
- Add public domain license in Ruby
- add information about license to README

* Thu Jul 20 2023 Miroslav Suchý <msuchy@redhat.com> 1.26-1
- add not-allowed LicenseRef-verbatim
- Add Apache-2.0 WITH Swift-exception
- document timing of releases
- mark HPND-sell-variant as variant of MIT in legacy system
- Add source-highlight public domain delcarations
- Add usage note for CC0-1.0 addressing liboqs issue
- Add gdb/GNU libiberty public domain delcarations
- Add CFITSIO license
- add licenses *GPL*WITH Linux-syscall-note

* Thu Jul 06 2023 Miroslav Suchý <msuchy@redhat.com> 1.25-1
- Add legacy attributes to HP-1986 - variant of legacy MIT license
- Add dtoa
- Add MulanPSL-2.0
- Add Boehm-GC
- add LLGPL
- public-domain-text.txt: Add a perl-Barcode-Code128 dedication
- Add new file: GPL-2.0-only_WITH_Asterisk-exception

* Thu Jun 22 2023 Miroslav Suchý <msuchy@redhat.com> 1.24-1
- Add new file: Inner-Net-2.0
- Add Linux-man-pages-copyleft-2-para
- Add Linux-man-pages-1-para
- Add Linux-man-pages-copyleft-var
- Remove AFL-2.0 since it is probably not in Fedora
- Make REUSE conformant
- Add GPL-2.0-or-later WITH Bison-exception-2.2
- Add new file: AFL-2.1

* Sun Jun 11 2023 Miroslav Suchý <msuchy@redhat.com> 1.23-1
- Update public-domain-text.txt
- Add new file: CECILL-2.1
- Add new file: TermReadKey
- Add new file: LicenseRef-Sleepycat-HtDig
- Add new file: Xfig
- Add new file: GPL-2.0-or-later WITH WxWindows-exception-3.1
- Add new file: LicenseRef-Array

* Sat May 27 2023 Miroslav Suchý <msuchy@redhat.com> 1.22-1
- Add cryptsetup GPL/LGPL licenses with OpenSSL exceptions.
- Add new file for the BSD-3-Clause-Open-MPI variant
- Add new files for the GPL-3.0-interface-exception
- Add new file for GPL-3.0-or-later_WITH_cryptsetup-OpenSSL-exception

* Wed May 17 2023 Miroslav Suchý <msuchy@redhat.com> 1.21-1
- Ensure all text files end with newlines
- Add GPL-2.0-only WITH libpri-OpenH323-exception as allowed
- Consolidate text in public-domain-text.txt
- Add LicenseRef-LDP-1 as not-allowed

* Mon May 08 2023 Miroslav Suchý <msuchy@redhat.com> 1.20-1
- Add HP-1986
- Add public domain notices from the tzdata data files
- Add man-pages public domain notices
- Add new file: SGP4
- Add new file: metamail
- Add automake to public-domain-text.txt
- Add public-domain text for words
- Add man-pages ultra permissive licenses

* Thu Apr 20 2023 Miroslav Suchý <msuchy@redhat.com> 1.19-1
- fix el7 build failure

* Thu Apr 20 2023 Miroslav Suchý <msuchy@redhat.com> 1.18-1
- add BNF grammar
- Add BSD-4.3TAHOE
- Add Latex2e-translated-notice
- Update UnixCrypt.toml since we don't use legacy Fedora URLs for SPDX (license
  list) identifiers
- Add new file: UnixCrypt
- Add new file: LicenseRef-Schematron-schema
- After the MIT-Festival license was accepted by SPDX, add it to the data
- add field to template to warn about automatic conversion
- Add jisksp16-1990-fonts to public-domain-text.txt
- Add groff public domain notice
- Add public-domain texts for libinstpatch
- Update to correct SPDX id: eCos-exception-2.0
- Update QPL-1.0-INRIA-2004 WITH QPL-1.0-INRIA-2004-exception.toml
- Add new file: QPL-1.0-INRIA-2004 WITH QPL-1.0-INRIA-2004-exception
- Add new file: Xdebug-1.03
- Add new file: NIST-Software

* Wed Apr 05 2023 Miroslav Suchý <msuchy@redhat.com> 1.17-1
- Add dnsmasq po files public domain notice
- add schema of fedora-license.json
- Add hanamin-fonts to UltraPermissive.txt
- Add fontconfig to public-domain-text.txt
- Add HPND-Markus-Kuhn
- Add BSD-Advertising-Acknowledgement
- Add Kazlib
- Add CMU-Mach
- Add perl-doc to UltraPermissive
- Add public-domain text for perl-libs
- Add public-domain text for perl-Test-Simple

* Fri Mar 24 2023 Miroslav Suchý <msuchy@redhat.com> 1.16-1
- Add public-domain text for python-multiprocess
- Add public domain text for versioneer in python-llvmlite
- Add Martin-Birgmeier
- Add public domain license in perl-libxml-perl
- Add public domain license in perl-Math-Int64
- Add public domain license in perl-Net-OpenID-Consumer
- Add public domain license in perl-Net-OpenID-Server
- Add public domain license in perl-perlfaq
- Update GPL-2.0-only_WITH_389-exception.toml
- Add new file: GPL-2.0-only WITH 389-exception
- Add public-domain text for jo
- Add public-domain license texts for abseil-cpp
- Update public-domain-text.txt for ecl
- Update public-domain-text.txt for gap-pkg-profiling
- Update public-domain-text.txt for icu4j
- Update public-domain-text.txt for mona
- Update public-domain-text.txt for pl
- Update public-domain-text.txt for pvs-sbcl
- Add Blessing
- Add new file: HPND-sell-variant-MIT-disclaimer
- Add new file: OFFIS
- Add new file: UCAR
- Add new file: TPL-1.0
- Add new file: Brian-Gladman-3-Clause
- Add new file: OpenPBS.toml
- Update public-domain-text.txt for python-pdfminer
- Add MagniComp-EULA as not-allowed

* Sun Mar 12 2023 Miroslav Suchý <msuchy@redhat.com> 1.15-1
- Update Spencer-94.toml
- Add Spencer-94
- Update public-domain-text.txt for ImageJ
- Add GPL-2.0-or-later WITH SWI-exception
- Add Info-ZIP

* Mon Feb 27 2023 Miroslav Suchý <msuchy@redhat.com> 1.14-1
- Add GPL-3.0-or-later WITH Autoconf-exception-macro
- Add GNAT-exception.
- Add AdaCore-doc.
- combine gdouros fonts entry
- Add public domain text covering gdouros-*-fonts
- Add GPL-2.0-or-later WITH Autoconf-exception-generic
- Add JPL-image license
- Update mkdsv.py to replace "notes" with "usage" for not allowed table
- Update not-allowed-licenses.adoc.j2 to have usage
- add text of BUSL-1.1.toml
- Update LPPL-1.3a.toml

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
