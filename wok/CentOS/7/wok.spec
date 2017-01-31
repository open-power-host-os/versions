Name:       wok
Version:    2.3.0
Release:    9%{?dist}
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
* Tue Jan 31 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 2.3.0-9
- 0489d72cbf7f3f33da304ae83a7bacedcc1bb7d5 Make sure nginx is running before reloading its config
- fc225d7cdaa7d6938eee7c9b5d04153d645b45ea Generate dhparams in post-install and development mode
- 26d66e1ec07ed69d2a3a36c8750858950055769e reload API: adding user log messages
- fee0e09d43b11e5674ab342c1c81aeb8ba93f9bf reload API: adding notification before reloading operation
- 85b5f894acd08435abd5322b87139aabe12bfb0c reload API: added rest API tests
- 0b4ae68134607bb716a423d6a33c14affef2cdd3 reload API: new file tests/test_config_model.py
- b8d5e2df203c5821c846b84a2dac32f1325d63f2 reload API: control and model changes
- db95e238b5a54523042936b1dc35a1b738cc55ee reload API: doc changes
- a6994dbd6507cb21f1dc59ec2ac7170d8ddabccd Do not link user role with UI tabs
- 448a94268a8553521c586ff4e98d7c7a738f082d Readd dependency on firewalld needed for HostOS

* Wed Jan 25 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.3.0-9
- d21e3f6d8db014f2c7100f93f1686afa3a437a84 Remove whitespace from COPYING file
- 9c07e522851ce0242c1cf7ef1d3582e9111d1188 Add Documentation for systemd service
- 50bf5286258f865b42433d5a955f24c7eea40e0b Fix typo in license header
- fb3b616c0fa7b18263c0d7303114e0fa4ba13bc3 Update man page document
- 490b22cd77758ea031b22b624918d32f59c4bd2d Update COPYING file to reflect all the imported code
- 5569693af1367d4cd33d1f31ab713e2cc8bd1403 Update AUTHORS content according to git-log command
- d52f90617b0e4e51c27d0be28953cea945286895 Use underscore in all wokd command options
- 8fba89d2a370cf5a4cd7929248b778f6d74ee48b Remove --access-log and --error-log options from wokd command
- 7feae0471826b36b330ec34fbc1ddeed3ce736b5 Issue #160: Fedora 25: Make check breaks on wok
- 7835c18d8462b489dc092ba3028b2a8bcdef0ae8 Remove spice-html5 references from Wok build
- 72377b6ec5b25e267b2d0c52226446d0f476a882 Fix issue #40: Improve WOKAUTH0002E error message and remove references to Kimchi
- 852c8501dc24f7816d0dd8c16637497884d307ae Always install firewalld conf for all distributions
- 3fcb8c544a2aac9ba03edb657765946b01a103a9 Update Copyright date
- 001456bfb26c9f2b43e12f8fb16f647a020edd2b Remove execution permission from css files
- 4adf824cf12397428f7ad2eb6134ae2508fae671 Fix typo in settings.css

* Wed Dec 21 2016 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.3.0-8
- 7173a7979648fad2e3a8355b15b94addbb4cc949 Bug fix #163: make check-local: whitespace verification is not excluding imported files
- af84a916765d6aa5ce6207fa7450804f46007b3a Bug fix #130: Wok does not support multiple words in plugin tag name
- b1f1fc774953d0a70bc2608569358a8de76a87ad Bug fix #144: The filter of of the user activity log shows loading forever
- d728a98ade06d4c4f1b6a1524bb75abcd78a156f Bug fix #168: check_ui_code_errors.sh not found by make check on dist tarball (RHEL 7.2)
- 5e205b319a0d19b10f4437ea9cab6a9cb2f4360e Bug fix #186: make check-local fails inside tarball
- ecf1f2f281ae012fd895f9c8462dfdc76af04e07 Bug fix #187: wok.main.js: parseTabs does not consider none mode tabs
- da171fdf5edfc53ad15adc459f93d6d5ab9f15b7 Bug fix #191: Break lines content to be smaller than 512 characters
- eaf4c93f38049366832928691ed98bc4b7371722 Bug fix #191: Add updated lodash.min.js file
- 0cdf5bbbf34d0b30caa11bc8a3ad95d5d3d0ff4a Bug fix #185: make rpm fails on CentOS when firewalld isnt installed
- 55bb83d99d4bcf243f2c2103a2c45751172bacc7 Fix non-relative paths

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
