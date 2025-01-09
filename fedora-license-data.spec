%global forgeurl https://gitlab.com/fedora/legal/fedora-license-data
%if 0%{?fedora} || 0%{?rhel} >= 10
%bcond_without  rpmlint
%else
%bcond_with     rpmlint
%endif
%if 0%{?fedora} > 39
%bcond_without  scancode
%else
%bcond_with     scancode
%endif

Name:           fedora-license-data
Version:        1.64
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
%if 0%{?fedora} > 39
BuildRequires:  scancode-toolkit
%endif
BuildRequires:  python3-devel
%if 0%{?fedora} || 0%{?rhel} >= 8
BuildRequires:  (python%{python3_pkgversion}-tomli if python%{python3_pkgversion} < 3.11)
%else
BuildRequires:  python%{python3_pkgversion}-tomli
%endif
# grammar
%if 0%{?fedora} || 0%{?rhel} > 8
BuildRequires:  (python3dist(lark) or python3dist(lark-parser))
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
Summary:        Rpmlint configuration with valid SPDX license identifiers
# this package does not need to depend on the main one
Requires:       rpmlint >= 2
Supplements:    rpmlint >= 2

# Require the legacy subpackage for backwards compatibility
%if 0%{?fedora} && 0%{?fedora} < 41
Requires:       rpmlint-%{name}-legacy = %{version}-%{release}
%endif

%description -n rpmlint-%{name}
This package contains information about licenses used in the Fedora
Linux project. The licenses are stored in a way that makes rpmlint read it.
Only the SPDX license identifiers are listed in this package.
The legacy (callaway) identifiers are listed in rpmlint-%{name}-legacy.

The Fedora Legal team is responsible for the content.


%package -n rpmlint-%{name}-legacy
Summary:        Rpmlint configuration with legacy (callaway) license identifiers
Requires:       rpmlint >= 2

%description -n rpmlint-%{name}-legacy
This package contains information about licenses used in the Fedora
Linux project. The licenses are stored in a way that makes rpmlint read it.
Only the legacy (callaway) identifiers are listed in this package.
The SPDX identifiers are listed in rpmlint-%{name}.

The Fedora Legal team is responsible for the content.
%endif


%prep
%setup -q -n %{name}-%{version}


%build
%make_build spec-validate json grammar %{?with_scancode:scancode} %{?with_rpmlint:rpmlint}

%install
make DESTDIR=%{buildroot} install-json install-grammar %{?with_scancode:install-scancode} %{?with_rpmlint:install-rpmlint}

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
%config(noreplace) %{_sysconfdir}/xdg/rpmlint/fedora-spdx-licenses.toml

%files -n rpmlint-%{name}-legacy
%license LICENSES/CC0-1.0.txt
%doc AUTHORS README.md
%config(noreplace) %{_sysconfdir}/xdg/rpmlint/fedora-legacy-licenses.toml
%endif


%changelog
* Thu Jan 09 2025 Miroslav Suchý <msuchy@redhat.com> 1.64-1
- add copyleft-next-0.3.1 license
- Add public-domain text for llvm-test-suite
- document usage exception for fedora-remix-logos
- add MIPS and ThirdEye licenses
- add libcsv UltraPermissive dedication
- Add public-domain text for stb

* Fri Dec 06 2024 Miroslav Suchý <msuchy@redhat.com> 1.63-1
- add LICENSE.Sigma from sigrok-firmware
- Add public-domain text for python-zmq
- add public domain for mg

* Fri Nov 22 2024 Miroslav Suchý <msuchy@redhat.com> 1.62-1
- add Avasys public license as allowed-firmware
- add public domain dedication for python-hexdump
- add public domain dedication for allegro (loadpng addon)
- add LicenseRef-soundfont as not-allowed
- add broadcom firmware license
- Reclassify LicenseRef-qmail as allowed (deprecated)
- add GPL-2.0-only WITH CGAL-linking-exception
- add firmware licensing terms for atmel-firmware
- add wwl license
- add generic-xts license
- add LicenseRef-Mod-Archive as not-allowed
- add public domain dedication for perl-Math-Expression-Evaluator
- add public domain dedication for perl-MaxMind-DB-Reader-XS
- add public domain dedication for python-django-pdb
- add UltraPermissive dedication of package python-utmp
- add public domain dedication for re2c
- add public domain dedication for python-nine
- add public domain dedication for perl-Devel-Trace
- add LGPL-3.0-or-later WITH LGPL-3.0-linking-exception

* Thu Nov 07 2024 Miroslav Suchý <msuchy@redhat.com> 1.61-1
- Revert "add LicenseRef-BSD-3-Clause-firmware"

* Thu Nov 07 2024 Miroslav Suchý <msuchy@redhat.com> 1.60-1
- add LicenseRef-Intel-firmware
- add public domain dedication for oflb-goudy-bookletter-1911-fonts
- add public domain dedication for nacl
- add Apache-2.0 WITH mxml-exception
- add public domain dedication for nec2c
- add any-OSI-perl-modules
- add public domain dedication for ogre
- add text of Unsplash license
- add LicenseRef-Intel-firmware
- add SGI-B-1.1 as not-allowed
- add public domain dedication for libgenht
- add ultra permissive findings for lyx
- add public domain findings for golang-github-xi2-xz
- add UltraPermissive dedication of package samcoupe-rom
- add UltraPermissive dedication of package radial
- add LicenseRef-MIT-CRL-Xim license as not-allowed
- add public domain findings for icon
- add public domain findings for jhead
- add public domain findings for mingw-pdcurses
- add LicenseRef-BASS (beneath a steel sky) as not-allowed
- add public domain and ultra permissive findings for rubygem-ruby-shadow

* Thu Oct 24 2024 Miroslav Suchý <msuchy@redhat.com> 1.59-1
- add public domain findings for sdl-telnet
- add public domain findings for libmodplug
- add public domain findings for mb2md
- add public domain findings for perl-DateTime-Precise
- add public domain findings for gimpfx-foundry
- add public domain findings for gnome-valgrind-session
- add public domain findings for sqlite2
- Blessing.toml -> blessing.toml
- add public domain findings for surfraw
- add GPL-3.0-or-later WITH GPL-3.0-389-ds-base-exception
- add public domain findings for klt
- add public domain findings for libb64
- add public domain dedication of emacs-slime
- add public domain dedication of cproto
- add public domain dedication for cockatrice
- add LGPL-2.1-or-later WITH Independent-modules-exception

* Thu Oct 10 2024 Miroslav Suchý <msuchy@redhat.com> 1.58-1
- add Ultra permissive dedication of docbook5-schemas
- add public domain dedication for clc
- add Sendmail-Open-Source-1.1 license
- add public domain dedication for biblesync
- add public domain dedication for BareBonesBrowserLaunch
- add public domain dedication for astronomy-menus
- add LGPL-2.1-only WITH OCCT-exception-1.0
- add CERN-OHL-P-2.0
- add Jam license
- add public domain dedication for ants

* Fri Sep 27 2024 Miroslav Suchý <msuchy@redhat.com> 1.57-1
- add filedrop public domain dedication
- add ddate public domain dedication
- Add wgrib license text
- add zork public domain dedication
- add AGPL-3.0-or-later WITH GPL-3.0-linking-source-exception
- allow CC-BY-SA 3.0 for fonts
- add Boehm-GC-without-fee license
- add LicenseRef-Julius as not allowed

* Fri Sep 13 2024 Miroslav Suchý <msuchy@redhat.com> 1.56-1
- add public domain dedication in package calf
- add public domain dedication for btop
- add public domain dedication for upx
- add DocBook-Stylesheet
- add LGPL-2.1-only WITH WxWindows-exception-3.1
- add public domain dedication for bsh
- Add vim into OPUBL-1.0 exceptions
- add GPL-1.0-or-later WITH Autoconf-exception-generic
- LicenseRef-Fedora-Public-Domain: Add perlmulticore.h
- add MIT-Click

* Fri Aug 30 2024 Miroslav Suchý <msuchy@redhat.com> 1.55-1
- Split rpmlint-fedora-license-data-legacy from rpmlint-fedora-license-
  data
- add LicenseRef-IUPAC-InChI-Trust as not allowed
- add TrustedQSL
- add TU-Berlin-1.0 license
- add DocBook-XML license
- add DocBook-Schema license
- add AGPL-3.0-or-later WITH PS-or-PDF-font-exception-20170817
- Extend ISO-8879 exception to dotnet9.0

* Fri Aug 16 2024 Miroslav Suchý <msuchy@redhat.com> 1.54-1
- public domain dedication found in mailcap
- public domain dedications found in web server icons
- replaced obsolescent command with modern equivalent
- add LicenseRef-compface
- Add rijndael from sdl-crypto to public domain
- add public domain dedication for xz
- Add sha1 from sdl-crypto to public domain
- correct location of HPND-Netrek.toml

* Wed Jul 31 2024 Miroslav Suchý <msuchy@redhat.com> 1.53-1
- add HPND-Netrek license
- Add license text for py-sdl2 Public Domain license
- remove LicenseRef-framed as ulem license was extended to allow LicenseRef-
  framed variation
- add HIDAPI license
- add Ruby-pty license
- add LicenseRef-OASIS-spec

* Fri Jul 19 2024 Miroslav Suchý <msuchy@redhat.com> 1.52-1
- Add LicenseRef-Frontier-Artistic-1.0 as not-allowed
- Add LicenseRef-JasPer-1.0 as not-allowed
- Create missing TOML for Callaway Nmap but reclassify as not-allowed, with
  usage exception
- Add LicenseRef-NPSL-0.92 as not-allowed, corresponding to Callaway-era NPSL
- Add LicenseRef-NPSL-0.93 as not-allowed to cover NPSL 0.93 and 0.94
- Correct TOML files for LicenseRef-NPSL-0.94 and LicenseRef-NPSL-0.95
- Add LicenseRef-NPSL-0.95 as not-allowed

* Wed Jul 03 2024 Miroslav Suchý <msuchy@redhat.com> 1.51-1
- add conditions when to use scancode

* Wed Jul 03 2024 Miroslav Suchý <msuchy@redhat.com> 1.50-1
- include scancode-license-policy.yaml in rpm
- add BSD-3-Clause-No-Nuclear-Warranty license
- add unicode-mappiing license as not-allowed
- add LicenseRef-W3C-Document-2023
- add W3C-20150513 license
- add 'make scancode' that produces scancode license policy file
- Add LicenseRef-framed as allowed

* Fri Jun 21 2024 Miroslav Suchý <msuchy@redhat.com> 1.49-1
- add AMD-newlib

* Mon Jun 10 2024 Miroslav Suchý <msuchy@redhat.com> 1.48-1
- Add GPL-2.0-only WITH vsftpd-openssl-exception

* Thu May 23 2024 Miroslav Suchý <msuchy@redhat.com> 1.47-1
- add GPL-2.0-or-later WITH RRDtool-FLOSS-exception-2.0
- add text of ultrapermissive dedication from sublimehq
- add HPND-export2-US license
- add Gutmann license
- add HPND-merchantability-variant license
- fix case in license id of BSD-2-Clause-first-lines
- add HPND-export-US-acknowledgement license
- add HPND-Intel license
- add loguru public domain dedication
- add BSD-3-Clause WITH AdditionRef-OpenEXR-Additional-IP-Rights-Grant
- add HPND-sell-variant-MIT-disclaimer-rev license
- add GD license
- Add crc32 license found in libsurvive to UltraPermissive
- allow lower case variant
- add any-OSI license
- document dotnet* packages as exception for LicenseRef-ISO-8879

* Fri Apr 26 2024 Miroslav Suchý <msuchy@redhat.com> 1.46-1
- rename LicenseRef-Catharon to Catharon
- add NCL license
- add HPND-UC-export-US license
- Add GPL-2.0-only_WITH_cryptsetup-OpenSSL-exception
- add Sun-PPP-2000 license
- add BSD-2-clause-first-lines license
- add pkgconf license

* Fri Apr 12 2024 Miroslav Suchý <msuchy@redhat.com> 1.45-1
- Update public-domain-text.txt for OpenCTM
- lark-parser was renamed to lark, allow both
- public domain dedication for libtcd
- public domain dedication for mopac7
- Public domain for sshguard
- public domain dedication for tcd-utils
- public domain dedication for minicom
- add LicenseRef-Catharon license

* Thu Mar 28 2024 Miroslav Suchý <msuchy@redhat.com> 1.44-1
- add OAR License
- include dictd md5 public domain text
- public domain dedication for libdstr
- Add LicenseRef-RSALv2 (not-allowed)
- add swig to UltraPermissive
- add LGPL-3.0-or-later WITH WxWindows-exception-3.1

* Sat Mar 16 2024 Miroslav Suchý <msuchy@redhat.com> 1.43-1
- rename LicenseRef-Threeparttable to threeparttable
- Add “KST32B” license terms to UltraPermissive.txt
- Add glibc public domain declarations

* Thu Feb 22 2024 Miroslav Suchý <msuchy@redhat.com>
- add CMU-Mach-nodoc license
- add Mackerras-3-Clause-acknowledgment license
- add bcrypt-Solar-Designer license
- add HPND-INRIA-IMAG license
- add OpenVision license
- public domain dedications for irssi
- add MIT-Khronos-old license
- public domain dedications for openshadinglanguage
- public domain dedication for util-linux
- public domain dedications for rrdtool
- public domain dedications for ppp
- Add public domain text from minicom
- add GPL-3.0-or-later WITH Autoconf-exception-generic

* Thu Feb 15 2024 Miroslav Suchý <msuchy@redhat.com>
- add Sun-PPP license
- add CC-BY-SA-3.0 WITH GNOME-examples-exception license
- add GPL-2.0-or-later WITH Gmsh-exception license
- add HPND-Fenneberg-Livingston license
- add Brian-Gladman-2-Clause license
- add gtkbook license
- add UMich-Merit license
- add Mackerras-3-Clause license
- Add legacy name for "LGPL-3.0-or-later WITH openvpn-openssl-exception"
- add softSurfer license
- add LGPL-2.1-or-later WITH GStreamer-exception-2005 license
- add UltraPermissive notice for libpng and perl-Image-PNG-Libpng
- add BSD-3-Clause-acpica license
- add SSLeay-standalone license
- add BSD-2-Clause-Darwin license

* Fri Feb 02 2024 Miroslav Suchý <msuchy@redhat.com> 1.40-1
- add HPND-UC
- add GPL-2.0-or-later WITH GStreamer-exception-2008
- add TGPPL-1.0 (and replace LicenseRef-TGPPL)

* Thu Jan 18 2024 Miroslav Suchý <msuchy@redhat.com> 1.39-1
- add LicenseRef-docbook-dtds
- public domain dedication for iw
- add HPND-MIT-disclaimer
- add Caldera-no-preamble
- Delete TOML files for licenses that cannot be found
- Add xkeyboard-config-Zinoviev
- Add Adobe-Display-Postscript
- Add DEC-3-Clause
- Add HPND-sell-MIT-disclaimer-xserver
- add not allowed license LicenseRef-sph2pipe
- add LGPL-2.1-or-later WITH GNU-compiler-exception
- GNU-compiler-exception: GPL-3.0 -> GPL-2.0
- firmware.txt: add license for microcode_ctl
- firmware.txt: remove trailing whitespace
- public domain dedication for jansson

* Thu Jan 04 2024 Miroslav Suchý <msuchy@redhat.com> 1.38-1
- add GPL-2.0-or-later WITH Bison-exception-1.24
- Add Unicode-3.0 license
- Add ISC-Veillard license
- Add mailprio license
- Add BSD-Systemics-W3Works license
- Modify .reuse/dep5
- Add UltraPermissive notices for libmtp
- public domain dedication for rwhoisd
- public domain dedication for openshadinglanguage
- public domain dedication for remind

* Fri Dec 22 2023 Miroslav Suchý <msuchy@redhat.com> 1.37-1
- add license HPND-Kevlin-Henney
- add license FSFAP-no-warranty-disclaimer
- add not allowed license LicenseRef-Nikto
- add LicenseRef-Fedora-Firmware

* Thu Dec 07 2023 Miroslav Suchý <msuchy@redhat.com> 1.36-1
- new license: TCP-wrappers
- new license: LicenseRef-Not-Copyrightable
- new license: SAX-PD-2.0
- new license: radvd

* Thu Nov 23 2023 Miroslav Suchý <msuchy@redhat.com> 1.35-1
- add argon2 as known exception to CC0-1.0
- new license: LicenseRef-BSD-3-Clause-Clear-WITH-AdditionRef-AOMPL-1.0
- new license: LicenseRef-BSD-2-Clause-WITH-AdditionRef-AOMPL-1.0
- new license: GCR-docs
- new license: AML-glslang
- new license: Pixar

* Fri Nov 10 2023 Miroslav Suchý <msuchy@redhat.com> 1.34-1
- new license: hdparm
- add not allowed license LicenseRef-LLaMA-2

* Fri Oct 27 2023 Miroslav Suchý <msuchy@redhat.com> 1.33-1
- add packages_with_exceptions to JSON schema
- document packages_with_exceptions for LicenseRef-Fedora-Logos
- document packages_with_exceptions for LicenseRef-TCGL
- document packages_with_exceptions for FDK-AAC
- include packages_with_exceptions field in json and in toml validation
- Template - document exception of not-allowed license
- not allowed license LicenseRef-novint

* Thu Oct 12 2023 Miroslav Suchý <msuchy@redhat.com> 1.32-1
- new not allowed license LicenseRef-Riverbank-SIP
- new license: LGPL-2.1-only_WITH_Linux-syscall-note
- new license: LicenseRef-Fedora-Logos
- new license: GPL-3.0-or-later WITH GNU-compiler-exception
- new license: HPND-doc-sell
- new license: BSD-3-Clause-flex
- new license: HPND-doc
- new license: LGPL-2.1-or-later WITH GCC-exception-2.0
- Add GPL-2.0-or-later WITH GPL-3.0-linking-source-exception
- new license: BSD-3-Clause-HP
- new license: GFDL-1.3-no-invariants-only
- new license: OLDAP-2.7
- new license: Adobe-Utopia
- new license: python-ldap
- new license: lsof

* Fri Sep 29 2023 Miroslav Suchý <msuchy@redhat.com> 1.31-1
- new license: GPL-2.0-or-later WITH Autoconf-exception-macro
- new license: LGPL-3.0-or-later WITH Autoconf-exception-macro
- new license: HPND-export-US-modify
- Add a public domain dedication from the SWORD Project
- Add LPPL-1.2 as not-allowed, add LPPL-1.3a+ as allowed
- new license: LGPL-2.1-only WITH Qt-LGPL-exception-1.1
- new license: SGI-OpenGL
- Add jhash public domain dedication for QEMU
- Add QEMU to the rijndael (AES) public domain license reference
- new license: SSH-short
- new license: GPL-2.0-or-later WITH UBDL-exception
- new license: McPhee-slideshow
- new license: HPND-DEC
- new license: magaz
- new license: ulem
- new license: fwlw
- new license: Kastrup
- Fix names of Linux-syscall-note TOML files
- Add reference to EDK2 package public domain code
- new license: HPND-sell-regexpr
- new license: Cronyx
- new license: Lucida-Bitmap-Fonts
- new license: LPPL-1.3c
- new license: swrule
- new license: BSD-Inferno-Nettverk
- Some code in OpenSSH has a Public Domain license
- new license: ssh-keyscan
- new license: HPND-Pbmplus
- Add public domain text from mingw-headers/mingw-winpthreads packages
- Add public domain test from Augeas project
- new license: BSD-Attribution-HPND-disclaimer
- new not allowed license: LicenseRef-Tyrian
- Add public domain entry for squid

* Thu Sep 14 2023 Miroslav Suchý <msuchy@redhat.com> 1.30-1
- new license: LGPL-3.0-or-later WITH openvpn-openssl-exception
- new license: BSD-3-Clause-Sun
- new license: BSD-Systemics
- new license: FBM
- new license: LGPL-2.0-or-later WITH Libtool-exception
- new license: Ferguson-Twofish
- Add Public Domain for varnish
- new license: MPEG-SSG
- Add cursor-misc from xorg-x11-fonts to UltraPermissive
- new not allowed license: MPEG-4 Audio
- new license: pnmstitch
- Add snprintf as allowed
- Add xlock as allowed
- Add BSD-4.3RENO as allowed
- Add public domain entry for winitzki-cyrillic X11 font
- Public Domain: Add mobile-broadband-provider-info
- Add public domain entry used by some xorg-x11-fonts
- Add Volatility Software License 1.0 to Not Allowed Licenses
- Add misc-cyrillic from xorg-x11-fonts to UltraPermissive
- Add public domain entry for aopalliance
- Add public domain entry for plexus-utils
- not allowed license LicenseRef-pgplot
- Fix a typo in xz-java package name

* Thu Aug 31 2023 Miroslav Suchý <msuchy@redhat.com> 1.29-1
- Add byacc public domain declaration
- recognize and allow MPL-2.0+ license
- public-domain-text.txt: Add a dedication found in zpaq
- New license: MMIXware
- not allowed license LicenseRef-Iozone
- new license: Utah Raster Toolkit Run Length Encoded License
- add license GPL-2.0-only WITH x11vnc-openssl-exception
- not allowed license LicenseRef-Misti-Fonts
- new license TTYP0
- add license GPL-2.0-or-later WITH stunnel-exception
- Add GPL-2.0-or-later WITH SANE-exception
- Fix man-pages public-domain and UltraPermissive locations
- generate additional grammar with all licenses inluding not allowed ones
- cleanup: remove mkdsv.py

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
