%if 0%{?fedora} >= 15 || 0%{?rhel} >= 7
%global with_systemd 1
%endif

%define ibm_release .1

Name:       ginger-base
Version:    2.0.0
Release:    6%{?dist}
Summary:    Wok plugin for base host management
BuildRoot:  %{_topdir}/BUILD/%{name}-%{version}-%{release}
BuildArch:  noarch
Group:      System Environment/Base
License:    LGPL/ASL2
#Source0:   %{name}-%{version}.tar.gz
Source0:    %{name}.tar.gz
Requires:   wok >= 2.1.0
Requires:   pyparted
Requires:   python-cherrypy
Requires:   python-configobj
Requires:   python-lxml
Requires:   python-psutil >= 0.6.0
Requires:   rpm-python
Requires:   gettext
Requires:   git
Requires:   sos
BuildRequires:  gettext-devel
BuildRequires:  libxslt
BuildRequires:  python-lxml
BuildRequires: autoconf
BuildRequires: automake

%if 0%{?fedora} >= 23
Requires:   python2-dnf
%endif

%if 0%{?fedora} >= 15 || 0%{?rhel} >= 7
%global with_systemd 1
%endif

%if 0%{?rhel} == 6
Requires:   python-ordereddict
BuildRequires:    python-unittest2
%endif

%description
Ginger Base is an open source base host management plugin for Wok
(Webserver Originated from Kimchi), that provides an intuitive web panel with
common tools for configuring and managing the Linux systems.

%prep
%setup -n %{name}

%build
./autogen.sh --system
make


%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install


%clean
rm -rf $RPM_BUILD_ROOT

%files
%attr(-,root,root)
%{python_sitelib}/wok/plugins/gingerbase
%{_datadir}/gingerbase
%{_prefix}/share/locale/*/LC_MESSAGES/gingerbase.mo
%{_datadir}/wok/plugins/gingerbase
%{_datadir}/wok/plugins/gingerbase/ui/pages/tabs/host-dashboard.html.tmpl
%{_datadir}/wok/plugins/gingerbase/ui/pages/tabs/host-update.html.tmpl
%{_sysconfdir}/wok/plugins.d/gingerbase.conf
%{_sharedstatedir}/gingerbase/


%changelog
* Thu Sep 29 2016 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 2.0.0-6
- 4422805 Bug fix: Log message got truncated because of \ on message
70b7eed Fix issue #131: Update README to add python-mock as dependency to run tests
c13abf8 Fix PEP8 version 1.5.7 issues on master

* Thu Sep 22 2016 user - 2.0.0-5
- c13abf8 Fix PEP8 version 1.5.7 issues on master
9274de8 Fixing copyright date of test_storage_devs.py
b51c6ae Extending Kimchi Peers to Host Dashboard

* Wed Sep 07 2016 user - 2.0.0-3.pkvm3_1_1
- b51c6ae Extending Kimchi Peers to Host Dashboard
6875c55 Moving storage device listing from ginger to gingerbase
2fa4618 Update usage of add_task() method.

* Thu Sep 01 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 2.0.0-2.pkvm3_1_1
- Build August, 31st, 2016

* Wed Mar 23 2016 Daniel Henrique Barboza <dhbarboza82@gmail.com>
- Added wok version restriction >= 2.1.0

* Tue Aug 25 2015 Chandra Shehkhar Reddy Potula <chandra@linux.vnet.ibm.com> 0.0-1
- First build
