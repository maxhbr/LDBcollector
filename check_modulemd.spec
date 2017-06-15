Name:           check_modulemd
Version:        0.1.0
Release:        1%{?dist}
Summary:        Checks the validity of a modulemd file

License:        GPLv3+
URL:            https://github.com/fedora-modularity/check_modulemd
Source0:        https://github.com/fedora-modularity/check_modulemd/releases/%{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python2-setuptools
Requires:       python2-aexpect
Requires:       python2-avocado
Requires:       python2-modulemd
Requires:       python2-requests
Requires:       python-enchant
Requires:       hunspell-en-US

%description
%{summary}.

%prep
%autosetup
# Remove bundled egg-info
rm -rf %{name}.egg-info

%build
%py2_build

%install
%py2_install
install -d -p -m 755 %{buildroot}%{_datadir}/%{name}
install -d -p -m 755 %{buildroot}%{_bindir}
mv examples-{modulemd,repo,testdata} Dockerfile %{buildroot}%{_datadir}/%{name}/
mv process_avocado_results.py check_modulemd.py %{buildroot}%{_bindir}/
mv run-checkmmd.sh %{buildroot}%{_bindir}/

%files
%license LICENSE
%doc README.md
%{_bindir}/check_modulemd.py
%{_bindir}/run-checkmmd.sh
%{_bindir}/process_avocado_results.py
%{_datadir}/%{name}/examples-{modulemd,repo,testdata}
%{_datadir}/%{name}/Dockerfile
%{python2_sitelib}/check_modulemd-*.egg-info/

%changelog
* Mon Jun 12 2017 Petr Hracek <phracek@redhat.com> - 0.1.0-1
- Initial version

