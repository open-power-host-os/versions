Name:           ppc64-diag
Version:        2.7.1
Release:        2%{?dist}
Summary:        PowerLinux Platform Diagnostics
URL:            http://sourceforge.net/projects/linux-diag/files/ppc64-diag/
Group:          System Environment/Base
License:        GNU General Public License (GPL)
ExclusiveArch:  ppc64 ppc64le
BuildRequires:  libservicelog-devel, flex, perl, byacc, librtas-devel >= 1.4.0
BuildRequires:  libvpd-devel, systemd, systemd-devel
BuildRequires:  ncurses-devel
Requires(post): systemd
Requires(preun): systemd
Requires:       servicelog, lsvpd >= 1.7.1
# PRRN RTAS event notification handler depends on below librtas
# and powerpc-utils versions.
Requires:	librtas
# License change
Requires:	powerpc-utils >= 1.3.2

Source0:        %{name}.tar.gz
Source1:        rtas_errd.service
Patch0:         ppc64-diag-2.4.2-messagecatalog-location.patch
Patch1:         ppc64-diag-2.4.2-chkconfig.patch
Patch2:         ppc64-diag-2.4.3-scriptlocation.patch
Patch3:         ppc64-diag-unusedvar.patch
Patch4:         ppc64-diag-2.6.1-lpdscriptloc.patch
Patch5:         ppc64-diag-2.6.1-verbose-build.patch

# patch from https://bugzilla.novell.com/show_bug.cgi?id=882667
# attachment https://bugzilla.novell.com/attachment.cgi?id=599147
# resolving https://bugzilla.redhat.com/show_bug.cgi?id=1109371
Patch10:        ppc64-diag-tmpraces.patch


%description
This package contains various diagnostic tools for PowerLinux.
These tools captures the diagnostic events from Power Systems
platform firmware, SES enclosures and device drivers, and
write events to servicelog database. It also provides automated
responses to urgent events such as environmental conditions and
predictive failures, if appropriate modifies the FRUs fault
indicator(s) and provides event notification to system
administrators or connected service frameworks.

# BZ#860040:
%global __requires_exclude %{?__requires_exclude:%__requires_exclude|}\/usr\/libexec\/ppc64-diag\/servevent_parse.pl

%prep
%setup -q -n %{name}
%patch0 -p1 -b .msg_loc
%patch1 -p1 -b .chkconfig
%patch2 -p1 -b .script_loc
%patch3 -p1 -b .unusevar
%patch4 -p1 -b .lpdscriptloc
%patch5 -p1 -b .verbose

%patch10 -p1 -b .tmpraces

%build
CFLAGS="%{optflags} -fno-strict-aliasing" CXXFLAGS="%{optflags} -fno-strict-aliasing" make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT
chmod 644 COPYING
rm -f $RPM_BUILD_ROOT/usr/share/doc/packages/ppc64-diag/COPYING
mkdir -p $RPM_BUILD_ROOT/%{_unitdir}
install -m644 %{SOURCE1} $RPM_BUILD_ROOT/%{_unitdir}
mkdir $RPM_BUILD_ROOT/%{_sysconfdir}/%{name}/ses_pages
mkdir -p $RPM_BUILD_ROOT/%{_var}/log/dump
ln -sfv %{_sbindir}/usysattn $RPM_BUILD_ROOT/%{_sbindir}/usysfault

%files
%doc COPYING
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/ses_pages
%dir %{_var}/log/dump
%{_mandir}/man8/*
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/%{name}/ppc64-diag.config
%attr(755,root,root) %{_sbindir}/*
%dir %{_datadir}/%{name}
%dir %attr(755,root,root) %{_datadir}/%{name}/message_catalog/
%attr(755,root,root) %{_libexecdir}/%{name}/ppc64_diag_migrate
%attr(755,root,root) %{_libexecdir}/%{name}/ppc64_diag_mkrsrc
%attr(755,root,root) %{_libexecdir}/%{name}/ppc64_diag_notify
#%attr(755,root,root) %{_libexecdir}/%{name}/ppc64_diag_servagent
%attr(755,root,root) %{_libexecdir}/%{name}/ppc64_diag_setup
%attr(755,root,root) %{_libexecdir}/%{name}/lp_diag_setup
%attr(755,root,root) %{_libexecdir}/%{name}/lp_diag_notify
%attr(644,root,root) %{_libexecdir}/%{name}/servevent_parse.pl
%attr(644,root,root) %{_datadir}/%{name}/message_catalog/cxgb3
%attr(644,root,root) %{_datadir}/%{name}/message_catalog/e1000e
%attr(644,root,root) %{_datadir}/%{name}/message_catalog/exceptions
%attr(644,root,root) %{_datadir}/%{name}/message_catalog/gpfs
%attr(644,root,root) %{_datadir}/%{name}/message_catalog/reporters
%attr(644,root,root) %{_datadir}/%{name}/message_catalog/with_regex/*
%attr(755,root,root) %{_sysconfdir}/rc.powerfail
%attr(755,root,root) %{_libexecdir}/%{name}/rtas_errd
%attr(755,root,root) %{_libexecdir}/%{name}/opal_errd
%attr(644,root,root) %{_unitdir}/rtas_errd.service
%attr(644,root,root) %{_unitdir}/opal_errd.service

%post
# Post-install script --------------------------------------------------
%{_libexecdir}/%{name}/lp_diag_setup --register >/dev/null
%{_libexecdir}/%{name}/ppc64_diag_setup --register >/dev/null
systemctl daemon-reload >/dev/null 2>&1 || :
if [ "$1" = "1" ]; then # first install
    systemctl -q enable opal_errd.service >/dev/null 2>&1 || :
    systemctl -q enable rtas_errd.service >/dev/null 2>&1 || :
    systemctl start opal_errd.service >/dev/null 2>&1 || :
    systemctl start rtas_errd.service >/dev/null 2>&1 || :
elif [ "$1" = "2" ]; then # upgrade
    systemctl try-restart opal_errd.service >/dev/null 2>&1 || :
    systemctl try-restart rtas_errd.service >/dev/null 2>&1 || :
fi

%preun
# Pre-uninstall script -------------------------------------------------
if [ "$1" = "0" ]; then # last uninstall
    systemctl stop opal_errd.service >/dev/null 2>&1 || :
    systemctl stop rtas_errd.service >/dev/null 2>&1 || :
    systemctl -q disable opal_errd.service >/dev/null 2>&1 || :
    systemctl -q disable rtas_errd.service >/dev/null 2>&1 || :
    %{_libexecdir}/%{name}/ppc64_diag_setup --unregister >/dev/null
    %{_libexecdir}/%{name}/lp_diag_setup --unregister >/dev/null
fi

%triggerin -- librtas
# trigger on librtas upgrades ------------------------------------------
if [ "$2" = "2" ]; then
    systemctl try-restart opal_errd.service >/dev/null 2>&1 || :
    systemctl try-restart rtas_errd.service >/dev/null 2>&1 || :
fi


%changelog
* Mon May 9 2016 - Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 2.7.1
- Fixed endianness issues in diagnostics code

* Tue Jan 19 2016 - Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 2.7.0
- Move from EPL to the GNU GPL license

* Sat Nov 7 2015 - Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 2.6.10
- LED support on FSP based PowerNV platform
- Few minor bugs fixes

* Thu Aug 27 2015 Jakub Čajka <jcajka@redhat.com> - 2.6.9-2
- Resolves: #1257504 - opal-elog-parse -a does not display any results

* Tue Jun 30 2015 Jakub Čajka <jcajka@redhat.com> - 2.6.9-1
- Resolves: #1182027 - [7.2 FEAT] ppc64-diag package update - ppc64/ppc64le

* Tue Jun 16 2015 Jakub Čajka <jcajka@redhat.com> - 2.6.8-1
- Resolves: #1182027 - [7.2 FEAT] ppc64-diag package update - ppc64/ppc64le

* Fri Jan 02 2015 Jakub Čajka <jcajka@redhat.com> - 2.6.7-6
- Resolves: #1175808 - missing /var/log/dump directory

* Thu Dec 04 2014 Jakub Čajka <jcajka@redhat.com> - 2.6.7-5
- Resolves: #1170146 - ppc64-diag: rtas_errd is not started by default

* Fri Nov 14 2014 Jakub Čajka <jcajka@redhat.com> - 2.6.7-4
- Resolves: #1164148 - CVE-2014-4039 CVE-2014-4038 ppc64-diag: multiple temporary file races [rhel-7.1]

* Mon Nov 10 2014 Jakub Čajka <jcajka@redhat.com> - 2.6.7-3
- Related: #1160352 - use -fno-strict-aliasing during build

* Mon Nov 10 2014 Jakub Čajka <jcajka@redhat.com> - 2.6.7-2
- Resolves: #1160352 - ppc64-diag: please integrate additional LE fixes

* Mon Aug 25 2014 Jakub Čajka <jcajka@redhat.com> - 2.6.7-1
- Resolves: #1088493 - [7.1 FEAT] ppc64-diag package update - ppc64
- Resolves: #1084062 - ppc64-diag: add support for hotplugging of qemu pci virtio devices
- Resolves: #1124007 - ppc64-diag needs ppc64le added to ExclusiveArch

* Mon Mar 03 2014 Dan Horák <dhorak@redhat.com> - 2.6.1-4
- modernize spec a bit and switch to verbose build in Makefiles
- use system-wide CFLAGS during build (#1070784)
- Resolves: #1070784

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 2.6.1-3
- Mass rebuild 2013-12-27

* Tue May 21 2013 Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 2.6.1-2
- Add ncurses-devel as build dependency
- Fix script location issue

* Mon May 20 2013 Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 2.6.1
- Update to latest upstream 2.6.1

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.3-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Sep 26 2012 Karsten Hopp <karsten@redhat.com> 2.4.3-6
- revert permissions fix, filter requirement instead

* Mon Sep 24 2012 karsten Hopp <karsten@redhat.com> 2.4.3-4
- fix permissions of servevent_parse.pl

* Fri Jul 27 2012 Lukáš Nykrýn <lnykryn@redhat.com> - 2.4.3-3
- rename .service file
- auto start rtas_errd (#843471)

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri May 04 2012 Karsten Hopp <karsten@redhat.com> 2.4.3-1
- update to 2.4.3

* Wed Feb 15 2012 Karsten Hopp <karsten@redhat.com> 2.4.2-5
- don't strip binaries
- fix some build issues

* Thu Sep 22 2011 Karsten Hopp <karsten@redhat.com> 2.4.2-4
- fix preun and post install scriptlets

* Fri Sep 09 2011 Karsten Hopp <karsten@redhat.com> 2.4.2-3
- add buildrequirement systemd-units for _unitdir rpm macro
- move helper scripts to libexecdir/ppc64-diag

* Wed Sep 07 2011 Karsten Hopp <karsten@redhat.com> 2.4.2-2
- additional fixes for Fedora package review (bugzilla #736062)

* Wed Aug 17 2011 Karsten Hopp <karsten@redhat.com> 2.4.2-1
- initial Fedora version, based on IBM spec file with rpmlint cleanups
  - move scripts to /usr/share/ppc-diag
  - don't start service automatically after install
