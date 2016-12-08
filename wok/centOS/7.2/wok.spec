Name:       wok
Version:    2.3.0
Release:    7%{?dist}
Summary:    Wok - Webserver Originated from Kimchi
BuildRoot:  %{_topdir}/BUILD/%{name}-%{version}-%{release}
BuildArch:  noarch
Group:      System Environment/Base
License:    LGPL/ASL2
Source0:    %{name}.tar.gz
Requires:   gettext
Requires:   python-cherrypy >= 3.2.0
Requires:   python-cheetah
Requires:   m2crypto
Requires:   PyPAM
Requires:   python-jsonschema >= 1.3.0
Requires:   python-lxml
Requires:   nginx
Requires:   python-ldap
Requires:   python-psutil >= 0.6.0
Requires:   fontawesome-fonts
Requires:   open-sans-fonts
Requires:   logrotate
Requires:	policycoreutils
Requires:	policycoreutils-python

Requires(post): policycoreutils
Requires(post): policycoreutils-python
Requires(post): selinux-policy-targeted
Requires(postun): policycoreutils
Requires(postun): policycoreutils-python
Requires(postun): selinux-policy-targeted

BuildRequires:	gettext-devel
BuildRequires:	libxslt
BuildRequires:	openssl
BuildRequires:	python-lxml
BuildRequires:	selinux-policy-devel
BuildRequires:	policycoreutils-devel

%if 0%{?fedora} >= 15 || 0%{?rhel} >= 7
%global with_systemd 1
%endif

%if 0%{?rhel} == 6
Requires:   python-ordereddict
Requires:   python-imaging
BuildRequires:    python-unittest2
%endif

%if 0%{?with_systemd}
Requires:   systemd
Requires:   firewalld
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%endif

%if 0%{?with_systemd}
BuildRequires: systemd-units
%endif

BuildRequires: autoconf
BuildRequires: automake

%description
Wok is Webserver Originated from Kimchi.


%prep
%setup -n %{name}


%build
./autogen.sh --system
make
cd src/selinux
make -f /usr/share/selinux/devel/Makefile


%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install

%if 0%{?rhel} == 6
# Install the upstart script
install -Dm 0755 contrib/wokd-upstart.conf.fedora %{buildroot}/etc/init/wokd.conf
%endif
%if 0%{?rhel} == 5
# Install the SysV init scripts
install -Dm 0755 contrib/wokd.sysvinit %{buildroot}%{_initrddir}/wokd
%endif

install -Dm 0640 src/firewalld.xml %{buildroot}%{_prefix}/lib/firewalld/services/wokd.xml

# Install script to help open port in firewalld
install -Dm 0744 src/wok-firewalld.sh %{buildroot}%{_datadir}/wok/utils/wok-firewalld.sh

# Install SELinux policy
install -Dm 0744 src/selinux/wokd.pp %{buildroot}%{_datadir}/wok/selinux/wokd.pp

%post
if [ $1 -eq 1 ] ; then
    /bin/systemctl enable wokd.service >/dev/null 2>&1 || :
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :

    # Add wokd as default service into public chain of firewalld
    %{_datadir}/wok/utils/wok-firewalld.sh public add wokd
fi

# Install SELinux policy
semodule -i %{_datadir}/wok/selinux/wokd.pp

%preun

if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable wokd.service > /dev/null 2>&1 || :
    /bin/systemctl stop wokd.service > /dev/null 2>&1 || :

    # Remove wokd service from public chain of firewalld
    %{_datadir}/wok/utils/wok-firewalld.sh public del wokd
    firewall-cmd --reload >/dev/null 2>&1 || :
fi

exit 0


%postun
if [ "$1" -ge 1 ] ; then
    /bin/systemctl try-restart wokd.service >/dev/null 2>&1 || :
fi
if [ $1 -eq 0 ]; then
    # Remove the SELinux policy, only when uninstall the package
    semodule -r wokd
fi
exit 0

%clean
rm -rf $RPM_BUILD_ROOT

%files
%attr(-,root,root)
%{_bindir}/wokd
%{python_sitelib}/wok/*.py*
%{python_sitelib}/wok/control/*.py*
%{python_sitelib}/wok/model/*.py*
%{python_sitelib}/wok/xmlutils/*.py*
%{python_sitelib}/wok/API.json
%{python_sitelib}/wok/plugins/*.py*
%{python_sitelib}/wok/
%{_prefix}/share/locale/*/LC_MESSAGES/wok.mo
%{_datadir}/wok/ui/
%{_datadir}/wok
%{_sysconfdir}/wok/wok.conf
%{_sysconfdir}/wok/
%{_sysconfdir}/logrotate.d/wokd
%{_mandir}/man8/wokd.8.gz

%if 0%{?with_systemd}
%{_sysconfdir}/nginx/conf.d/wok.conf
%{_sharedstatedir}/wok/
%{_localstatedir}/log/wok/*
%{_localstatedir}/log/wok/
%{_unitdir}/wokd.service
%{_prefix}/lib/firewalld/services/wokd.xml
%endif
%if 0%{?rhel} == 6
/etc/init/wokd.conf
%endif
%if 0%{?rhel} == 5
%{_initrddir}/wokd
%endif

%changelog
* Thu Dec 08 2016 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.3.0-7
- 55bb83d99d4bcf243f2c2103a2c45751172bacc7 Fix non-relative paths
- 43d73d0f087ffb09f6528f1fe3485a7457d0b8e9 Fix ip-address.js directory
- 53ee603d62815818636b5b9550090413f8532c07 Do not install firewalld conf in Debian
- e8d1bfe1fae19bbda8bdd17edc3981caa124911b Bug fix #151: Wok settings page not working when locale not set

* Fri Nov 25 2016 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.3.0-6
- e8d1bfe1fae19bbda8bdd17edc3981caa124911b Bug fix #151: Wok settings page not working when locale not set
- a682998c917b7ce18eb60b12c8801556673259ae Remove nginx-specific parameters from wok.conf file
- 1b6c8110d802d06ba38e2f02e6ad4997868bec81 Bug fix #175: Do not generate nginx configuration file on the fly
- 118d3562f067640353cc7fb58f722b412a58f27f Generate SSL self signed certificate on package post installation script
- 9180d4809968c8e2e1a63076647039460b2ea652 Add nginx.service as wokd.service dependency
- e3916814f1823a98e69a67ccb49b52f22b85d4a4 Remove log size information from Wok config
- 48ebb52b572f3fa7cf30fa647b1d00318086f42b Fix make check issues
- 8d8db1384e01224de28944330da5541bd99ac3f0 Merge remote-tracking branch upstream/master into hostos-devel

* Wed Nov 09 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 2.3.0-5
- wok rebase

* Thu Nov 3 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 2.3.0-4
- Spec cleanup

* Wed Nov 02 2016 user - 2.3.0-3
- 5443d11 Merge remote-tracking branch upstream/master into host-devel
80b5bab Fix pep8 issues caused by 2a7b3c6
768cf29 Issue #116: Suggestion to check spec guidelines
2a7b3c6 Issue #139: Do not generate logrotate config file on the fly
6bf4254 Bug fix #176: Assume plugin URI is /plugins/<plugin-name>
0efaeae Remove Ginger Base specific CSS from Wok source code
64860ba Remove build warning message from Wok
1cd86b9 Remove non-Wok strings from Wok source code
504c67e Align _wok-variables.scss content for visual matters
2738686 Remove unused SCSS variables
0ccd581 Update Wok variables names for better meaning
289af10 Bug fix #173: Get plugin color to set user log data
e16bd91 Bug fix #173: Get color tab from tab-ext.xml file
652c59b Bug fix #174: Automatic create navigation toolbar when loading plugin
5fc9899 Updating css files to latest UI libs versions
9eb347a Github #143: non-ASCII characters in the password field
eb2118f Fix Ginger Base issue #122: Get immediate children while looking for selected options
306dae0 Bug fix #169: Display user log date in numeric format
d84f137 Bug fix #146: Do not display Wok tab for non-admin users
d62440c Update tests with relative path support
5ffb7fe CSS updates to handle relative path support.
f1453e5 Fix UI to handle relative paths.
78f218d Add support to relative paths.
71ffa96 Update ChangeLog, VERSION and po files to 2.3 release
bfdbb68 Fix make-rpm target
ea8a2d4 Issue #166: wok is pointing to /etc/nginx/conf.d which does not exists on OpenSuse 42.1
4bbfcd1 Fix Kimchi issue #1032: Remove Peers dropdown from Wok header
50065e0 Github #143: non-ASCII characters in the password field

* Wed Oct 26 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 2.3.0-2
- 50065e0 Github #143: non-ASCII characters in the password field
680eb9f Fix Ginger Base issue #122: Get immediate children while looking for selected options

* Wed Oct 05 2016 user - 2.2.0-8
- bd24776 Update ChangeLog, VERSION and po files to 2.3 release
646941d Fix make-rpm target

* Thu Sep 29 2016 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 2.2.0-7
- 646941d Fix make-rpm target
cad930b Issue #166: wok is pointing to /etc/nginx/conf.d which does not exists on OpenSuse 42.1
e80f9e3 Fix Kimchi issue #1032: Remove Peers dropdown from Wok header
5c62e4c Merge remote-tracking branch upstream/master into powerkvm-v3.1.1
1f2eec3 Issue #155: make clean does not revert its changes from make rpm
2e99b4f Fix issue #159: Fix user log filter parameters to allow user does advanced search
918911e Merge remote-tracking branch upstream/master into powerkvm-v3.1.1

* Thu Sep 22 2016 user - 2.2.0-6
- 918911e Merge remote-tracking branch upstream/master into powerkvm-v3.1.1
a14cda7 Add ui/libs/datatables/js/plugins/ip-address/* files to IBM-license-blacklist
69743f8 Remove obsolete message WOKUTILS0001E
bea70fc Merge remote-tracking branch upstream/master into powerkvm-v3.1.1

* Wed Sep 07 2016 user - 2.2.0-4.pkvm3_1_1
- bea70fc Merge remote-tracking branch upstream/master into powerkvm-v3.1.1
8e5a84d Change location of User Requests Log
d164293 Save log entry IDs for requests that generate tasks
2ae31d2 Log AsyncTask success or failure
d25d822 Update Request Logger to handle AsyncTask status
0767b4b Create log_request() method for code simplification
cdb3c4e Blink dialog session timeout
86514d0 Minor fixes in form fields
bc54058 Removing Kimchi Peers dropdown from Wok navbar
b1f0fef Issue #122 - Add unit test to stop AsyncTask.
9a00bff Issue #122 - Make AsyncTask stoppable.
240f449 Merge remote-tracking branch upstream/master into powerkvm-v3.1.1

* Thu Sep 01 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 2.2.0-3.pkvm3_1_1
- Build August, 31st, 2016

* Thu Aug  4 2016 Paulo Vital <pvital@linux.vnet.ibm.com> 2.3
- Add SELinux policy to allow http context

* Fri Jun 19 2015 Lucio Correia <luciojhc@linux.vnet.ibm.com> 2.0
- Rename to wokd
- Remove kimchi specifics

* Thu Feb 26 2015 Frédéric Bonnard <frediz@linux.vnet.ibm.com> 1.4.0
- Add man page for kimchid

* Tue Feb 11 2014 Crístian Viana <vianac@linux.vnet.ibm.com> 1.1.0
- Add help pages and XSLT dependency

* Tue Jul 16 2013 Adam Litke <agl@us.ibm.com> 0.1.0-1
- Adapted for autotools build

* Thu Apr 04 2013 Aline Manera <alinefm@br.ibm.com> 0.0-1
- First build
