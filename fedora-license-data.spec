%global forgeurl https://gitlab.com/fedora/legal/fedora-license-data

Name:           fedora-license-data
Version:        1.0
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
%if 0%{?fedora} || 0%{?rhel} >= 9
BuildRequires:  (python%{python3_pkgversion}-toml if python%{python3_pkgversion} < 3.11)
BuildRequires:  python%{python3_pkgversion}-tomli-w
%else
BuildRequires:  python%{python3_pkgversion}-toml
%endif

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
%setup -q -n %{name}-%{version}


%build
%make_build


%install
%make_install


%files
%license LICENSE LICENSE.BSD-3-Clause LICENSE.CC0-1.0
%doc AUTHORS README.md
%{_datadir}/%{name}/
# co-own the rpmlint directory not to depend on rpmlint
%dir %{_sysconfdir}/xdg/rpmlint/
%config(noreplace) %{_sysconfdir}/xdg/rpmlint/licenses.toml


%changelog
* Mon May 02 2022 David Cantrell <dcantrell@redhat.com> - 1.0-1
- Initial build
