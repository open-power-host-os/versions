%if 0%{?fedora} >= 15 || 0%{?rhel} >= 7
%global with_systemd 1
%endif

Name:       ginger-base
Version:    2.2.1
Release:    4%{?dist}
Summary:    Wok plugin for base host management
BuildRoot:  %{_topdir}/BUILD/%{name}-%{version}-%{release}
BuildArch:  noarch
Group:      System Environment/Base
License:    LGPL/ASL2
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
* Thu Nov 3 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 2.2.1-4
- spec cleanup

* Wed Nov 02 2016 user - 2.2.1-3
- 56913b3 Merge remote-tracking branch upstream/master into hostos-devel
ff00717 Bug fix #135: Add/Edit repository should consider host OS to ask user input
964cdbc Issue # 146 : Miscellaneous UI issue in SMT functionality
51b4b86 Issue # 146 : Miscellaneous UI issue in SMT functionality
2767b78 Remove URI configuration from gingerbase.conf file
747cb75 Fix for Multi-Culture Dashboard UI issue
2be034d Wok issue #173: Set tab color on tab-ext.xml and update SCSS files
f5bc5d0 Wok issue #174: Let Wok create the whole navigation bar
cd1334d Issue #140 - Fedora 24: Bug when try to rename multiple debug reports
d4e4d35 Issue #137 - Update All button should be disabled when the update successfully finished.
c071b52 test_rest.py: changing generated reports name
fbfe853 Improve the way Updates tab is loaded
1d2027d Rpmlint spec file fixes
75b71fc Issue #118: Suggestion to check spec guidelines
a8f5fdd Adding pt-br translations in fuzzy statements
722d0c0 Updating po files
fffc8f9 Merge branch next
d286125 Issue #108: Update APT packges list after update.
34daea3 Bug fix: Log message got truncated because of \ on message
c4cfbd0 Fix for adding capabilities for smt and modified UT.
2fcf6d0 Fix issue #131: Update README to add python-mock as dependency to run tests
457e2cc Fix PEP8 1.5.7 issues on next
ca451c8 Fixing copyright date of test_storage_devs.py
fbc1d06 Introducing SMT feature
1df5936 Introducing SMT feature
021ce3e Introducing SMT feature
e7cc035 Added docs ,error messages and UT for SMT.
801063e Backend code implementation for SMT
a025aae test_rest.py: changing generated reports name

* Wed Oct 26 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 2.2.1-2
- a025aae test_rest.py: changing generated reports name
0f9bf86 Improve the way Updates tab is loaded

* Wed Oct 05 2016 user - 2.0.0-7
- 2bc859f Rpmlint spec file fixes
fe9f4fb Issue #118: Suggestion to check spec guidelines
36dc0ab Adding pt-br translations in fuzzy statements
394938f Updating po files
9769bc3 ChangeLog for 2.2.1
82a79fc Updating VERSION to 2.2.1
d8fe260 ChangeLog and VERSION changes for 2.2.1-rc1
5fbea64 Issue #108: Update APT packges list after update.
4422805 Bug fix: Log message got truncated because of \ on message

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
