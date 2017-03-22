%if 0%{?fedora} >= 15 || 0%{?rhel} >= 7
%global with_systemd 1
%endif

%global commit          %{?git_commit_id}
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitcommittag    .git%{shortcommit}

Name:       ginger-base
Version:    2.2.1
Release:    13%{gitcommittag}%{?dist}
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
%setup -q -n %{name}

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
* Wed Mar 01 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.2.1-13.git109815c
- 109815ccb5bbcbdc5dc5cef847accf9a3b9083d4 Merge remote-tracking branch upstream/master into hostos-devel
- 4b90d6cbfccace5fa9528e57acfa046d4c523d40 Fix patch_auth() call according to Wok changes

* Wed Feb 15 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.2.1-12.gitbe727f1
- be727f1f3fec4d551802940dff09fcaf061ed6e4 Merge remote-tracking branch upstream/master into hostos-devel
- 676b5ff056c867c04d564538a06b8afd90d8e5e2 Remove unused temporary directory
- 79275c2a5f7cee458a892cf2cd99a5aea837e1ce Merge remote-tracking branch upstream/master into hostos-devel
- 2971b2f384bf66af94c2efa1e463702d2fa62935 Update run_server() calls to do not pass model instance
- b4ca94343a04bc75e1680a08816570c56b526fdd Specify objectstore location when running on test mode

* Thu Feb 02 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.2.1-11
- 593bf276645a98717586c2b532e379b3cf050810 Merge remote-tracking branch upstream/master into hostos-devel
- 5dda16ea5f2692d792cb70fe9dab67895e3ec707 Typo at API.json
- 6f114040fbe03bcd38c21a3f82c6d622f9d97e58 Bug fix #136: Add filter for repositories
- ac9565153fdd6ff6b165bfd3c8e1b2e6892f01d2 Remove role_key parameter

* Wed Jan 25 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.2.1-10
- 2de55c275f473eafc053c5b804af8f204810164f Merge remote-tracking branch upstream/master into hostos-devel
- 33e9bf1a765e573fef2f2463987ab73a1e51b50a Fix available flag for multipath lun
- 414f80520b70de50dbe088a9df2853a8e9b39269 Merge remote-tracking branch upstream/master into hostos-devel
- 20a95807564b5d588dc8ca3ba4915b041f67c45b pep8 compatible, copyright notice added
- 14d460e7f360120a26c01d9f5d40458a239449cc initial gentoo Linux support
- 162f7ecab31c5a41692ebd9cc68307bab6b584cb Fixing copyright year of model/smt.py
- efcf7e10c43ee0d744fd7742aeb60fcd34d1c75c Fix for issue #156
- eff99e3c66b999ef7e4b5497c480487b90d223f5 fix for parsing issue of pvs command output

* Wed Dec 21 2016 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.2.1-9
- 82dd2bea6900e3bda3cd14ef6835586b773fc6c8 Merge remote-tracking branch upstream/master into hostos-devel
- d8b9b8c08952a4e1f298a352113e7570ad299bc8 Bug fix #134: Allow user enable/disable multiple repositories at once
- 9c61cfd1a1d3dc3a8f88e957cae5a08045354bb7 Bug fix: Merge repo data with the user changes to update repo information
- a06fecdf7f92909373f280cdb2c6d7e3b083f2c6 Add error message equivalent to WOKUTILS0001E
- 109b9cc0be4305b0478cd73a3eba31b8f252263e Bug fix #152: Only serialize visible form inputs when editing repository
- 90c3d1d170f43c54121fb43786f8f374c4e93ce4 Fix checking for Apt tool
- c84dc833cbab89f92bc4aeb1c73023d4f74fb504 Merge remote-tracking branch upstream/master into hostos-devel

* Thu Dec 08 2016 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.2.1-8
- c84dc833cbab89f92bc4aeb1c73023d4f74fb504 Merge remote-tracking branch upstream/master into hostos-devel
- 0ac1d6b34bb208a29950c89cad6d76f53ea04a15 Fix for gingerbase issue #156
- dc57f3ad06882c1a452a0e60467ca34fe75eec02 Fix for ginger issue #489 - Introduced new method for getting physical volumes and associated volume groups
- da13715ce50e844537b9de39b76a3bf7607a292b Fix for ginger issue #484
- 0f006534e799ba44ccfee5cb3af186b2998db9fa Merge remote-tracking branch upstream/master into hostos-devel

* Wed Nov 30 2016 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.2.1-7
- 0f006534e799ba44ccfee5cb3af186b2998db9fa Merge remote-tracking branch upstream/master into hostos-devel
- 1201b6bc602ca214fb976cfd007f9a79df142477 Bug fix #111: Do not return package dependencies on package lookup()
- a4525c3ea0802f111e55612542bd4bccbb58b7c6 Update UI to use /host/packagesupdate/<pkg>/deps API to get the package dependencies
- e31f3f165c4498f4a739781b420ec858ad9167c2 Create a new API to return the package dependencies
- f481c2c2f6b31d8b1607f815bb297b3bdf2155cc Merge remote-tracking branch upstream/master into hostos-devel

* Sat Nov 26 2016 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.2.1-6
- f481c2c2f6b31d8b1607f815bb297b3bdf2155cc Merge remote-tracking branch upstream/master into hostos-devel
- b55043cb6e3cba5b4ea0b0260be7f3509eb60090 Bug fix #123: Do not make requests when repositories/software update section is collapsed
- 5fd9447b44c62806342dd3f973e374fd9fd06662 Update Ginger Base code due chnages on Wok configuration parameters
- 8296bfafd142fe2486f9d4935f098584cdd1b6a1 Merge remote-tracking branch upstream/master into hostos-devel

* Wed Nov 09 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 2.2.1-5
- ginger-base rebase

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
