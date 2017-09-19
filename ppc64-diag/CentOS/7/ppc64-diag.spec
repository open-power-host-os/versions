%global commit          %{?git_commit_id}
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitcommittag    .git%{shortcommit}

Name:           ppc64-diag
Version:        2.7.4
Release:        2%{?extraver}%{gitcommittag}%{?dist}
Summary:	PowerLinux Platform Diagnostics
Group:		System Environment/Base
License:	GNU General Public License (GPL)
URL:		http://sourceforge.net/projects/linux-diag/files/ppc64-diag/
Packager:	IBM Corp.
Vendor:		IBM Corp.
ExclusiveArch:  ppc ppc64 ppc64le
BuildRequires:  libservicelog-devel, flex, perl, /usr/bin/yacc
BuildRequires:  libvpd-devel
BuildRequires:  librtas-devel >= 1.4.0
BuildRequires:	ncurses-devel
BuildRequires:	systemd-devel
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool

Requires:	servicelog
Requires:	systemd
# License change
Requires:	powerpc-utils >= 1.3.2
# Light Path Diagnostics depends on below lsvpd version.
Requires:	lsvpd >= 1.7.1
Source0: %{name}.tar.gz

%description
This package contains various diagnostic tools for PowerLinux.
These tools captures the diagnostic events from Power Systems
platform firmware, SES enclosures and device drivers, and
write events to servicelog database. It also provides automated
responses to urgent events such as environmental conditions and
predictive failures, if appropriate modifies the FRUs fault
indicator(s) and provides event notification to system
administrators or connected service frameworks.

%prep
%setup -q -n %{name}

%build
./autogen.sh
%configure
make

%install
make install DESTDIR=$RPM_BUILD_ROOT
chmod 644 $RPM_BUILD_ROOT/etc/%{name}/servevent_parse.pl
mkdir -p $RPM_BUILD_ROOT/etc/%{name}/ses_pages
mkdir -p $RPM_BUILD_ROOT/%{_libexecdir}/%{name}
mkdir -p $RPM_BUILD_ROOT/%{_unitdir}
mkdir -p $RPM_BUILD_ROOT/var/log/dump
mkdir -p $RPM_BUILD_ROOT/var/log/opal-elog

%files
%defattr (-,root,root,-)
%doc /usr/share/doc/%{name}/COPYING
%doc /usr/share/doc/%{name}/README
%doc /usr/share/man/man8/*
/usr/sbin/*
%dir /etc/%{name}
%dir /etc/%{name}/ses_pages
%dir /var/log/dump
%dir /var/log/opal-elog
%config /etc/%{name}/*
%config /etc/rc.powerfail
%attr(755,root,root) /etc/cron.daily/run_diag_encl
%attr(755,root,root) %{_libexecdir}/%{name}/rtas_errd
%attr(755,root,root) %{_libexecdir}/%{name}/opal_errd
%attr(644,root,root) %{_unitdir}/rtas_errd.service
%attr(644,root,root) %{_unitdir}/opal_errd.service

%post
# Post-install script --------------------------------------------------
# We will install both opal_errd and rtas_errd daemon and during boottime
# daemon will fail gracefully if its not relevant to the running platform
/etc/ppc64-diag/ppc64_diag_setup --register >/dev/null 2>&1
/etc/ppc64-diag/lp_diag_setup --register >/dev/null 2>&1
if [ "$1" = "1" ]; then # first install
    systemctl -q enable opal_errd.service >/dev/null
    systemctl -q enable rtas_errd.service >/dev/null
    systemctl start opal_errd.service >/dev/null
    systemctl start rtas_errd.service >/dev/null
elif [ "$1" = "2" ]; then # upgrade
    systemctl restart opal_errd.service >/dev/null
    systemctl restart rtas_errd.service >/dev/null
fi

%preun
# Pre-uninstall script -------------------------------------------------
if [ "$1" = "0" ]; then # last uninstall
    systemctl stop opal_errd.service >/dev/null
    systemctl stop rtas_errd.service >/dev/null
    systemctl -q disable opal_errd.service
    systemctl -q disable rtas_errd.service
    /etc/ppc64-diag/ppc64_diag_setup --unregister >/dev/null
    /etc/ppc64-diag/lp_diag_setup --unregister >/dev/null
fi

%triggerin -- librtas
# trigger on librtas upgrades ------------------------------------------
if [ "$2" = "2" ]; then
    systemctl restart rtas_errd.service >/dev/null
fi

%changelog
* Tue Sep 19 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 2.7.4-2.git2e89648
- Bump to update shared object dependencies

* Mon Jul 24 2017 - Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 2.7.4
- Move to autotools based build environment
- Run diag_encl automatically (via crontab)
- Added disk diagnostics support
- Test case improvement
- Service script improvement

* Tue Dec 6 2016 - Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 2.7.3
- LED support for Marvell HDD
- Added support to parse new drc-index device tree property
- ela: remove support on PowerVM LPAR

* Mon Sep 19 2016 - Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 2.7.2
- Added slider enclosure diagnostics support
- Added support for eSEL parsing

* Mon May 9 2016 - Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 2.7.1
- Fixed endianness issues in diagnostics code

* Tue Jan 19 2016 - Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 2.7.0
- Move from EPL to the GNU GPL license

* Sat Nov 7 2015 - Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 2.6.10
- LED support on FSP based PowerNV platform
- Few minor bugs fixes

* Mon Jun 29 2015 - Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 2.6.9
- Added Home Run (5887) enclosure diagnostics support
- Added PHB hotplugging support for PowerKVM guest
- Fixed LE issue in rtas_errd
- Fixed memory leak in rtas_errd

* Mon May 11 2015 - Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 2.6.8
- Cpu and memory hotplugging support for PowerKVM guest
- Various fixes to opal-dump-parse tool
- Few LE related fixes
- Several security fixes across tools

* Fri Aug 15 2014 - Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 2.6.7
- Bug fixes in opal_errd and opal-elog-parse
- Added opal-dump-parse tool
- LE support for light path code (usysident, usysattn and lp_diag)
- Switch to systemd based daemon management
- Fixed bashism issues

* Tue Apr 15 2014 - Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 2.6.6
- Log rotator for opal_errd
- Dump retention policy for extract_opal_dump
- Couple of fixes in opal_errd and opal-elog-parse file

* Wed Apr 02 2014 - Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 2.6.5
- Fixed number of issues in opal_errd and opal-elog-parse code
- Bashism fix
- Fixes to comply with hardened build flags

* Fri Mar 21 2014 - Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 2.6.4
- Added support for PowerKVM host (opal_errd, extract_opal_dump)
- Added support to parse PEL format log (opal-elog-parse)

* Fri Mar 07 2014 - Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 2.6.3
- Added platform validation code
- Add support for hotplugging qemu pci devices via RTAS event
- Minor bug fixes in rtas_errd code

* Tue Aug 20 2013 - Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 2.6.2
- Minor bug fix in diag_encl and encl_led

* Fri Feb 08 2013 - Vasant Hegde <hegdevasant@in.ibm.com> - 2.6.1
- Handler to handle PRRN RTAS notification

* Tue Jan 29 2013 - Vasant Hegde <hegdevasant@in.ibm.com> - 2.6.0-3
- rtas_errd segfault fix in test path (bug #88056)

* Fri Jan 18 2013 - Vasant Hegde <hegdevasant@in.ibm.com> - 2.6.0-2
- Updated ELA catalog for e1000e and cxgb3 driver

* Fri Jan 11 2013 - Vasant Hegde <hegdevasant@in.ibm.com> - 2.6.0-1
- ppc64_diag_notify alignment fix

* Wed Dec 19 2012 - Vasant Hegde <hegdevasant@in.ibm.com> - 2.6.0
- Added Light Path Diagnostics code.

* Fri Nov 23 2012 - Vasant Hegde <hegdevasant@in.ibm.com> - 2.5.1
- 2.5.1 release

* Fri Sep 07 2012 - Vasant Hegde <hegdevasant@in.ibm.com> - 2.5.0
- Introduced new options to diag_encl command (Jim).
- Added bluehawk enclosure diagnostics support (Jim).
- Introduced new command "encl_led" to modify identify/fault indicators
  for SCSI enclosures (Jim).
- Fixed bug #78826.
- Added libvpd-devel as compilation dependency.

* Wed May 23 2012 - Vasant Hegde <hegdevasant@in.ibm.com> - 2.4.4
- Fixed bug #80220 and #81288.

* Tue Feb 14 2012 - Jim Keniston <jkenisto@us.ibm.com> - 2.4.3
- Added message catalogs for the ipr, ixgb, lpfc, and qla2xxx drivers
  (Anithra).  Fixed bugs #75118, #74636 and #74308.  Removed obsolete
  ppc64_diag_servagent script.

* Mon Jul 11 2011 - Anithra P Janakiraman <janithra@in.ibm.com> -2.4.2-1
- Minor modifications to GPFS catalog files and syslog_to_svclog.cpp 

* Wed Jun 29 2011 - Anithra P Janakiraman <janithra@in.ibm.com> -2.4.2-0
- Added gpfs files to the catalog, updated ppc64-diag-setup notification
  commands

* Wed Jun 15 2011 - Jim Keniston <jkenisto@us.ibm.com> - 2.4.1-0
- Changed Makefiles and rules.mk to build for the default architecture
  rather than -m32.

* Tue Feb 22 2011 - Anithra P Janakiraman <janithra@in.ibm.com> - 2.4.0-0
- Added ELA code to the package, made changes to the rules.mk and minor changes
  to the spec file.

* Fri Nov 19 2010 - Brad Peters <bpeters@us.ibm.com> - 2.3.5-0
- Bug fix adding in support for -e and -l, so that root users can
  be notified of serviceable events. Addresses bug #26192

* Wed Feb 24 2010 - Mike Mason <masonmik@us.ibm.com> - 2.3.4-2
- Added SIGCHLD handler to clean up servicelog notification scripts.

* Tue Sep 22 2009 - Brad Peters <bpeters@us.ibm.com> - 2.3.2-2
- Removed all absolute path references, specifically to /sbin/lsvpd and lsvpd

* Mon Sep 21 2009 - Brad Peters <bpeters@us.ibm.com> - 2.3.2-1
- Removed .spec references to aaa_base and insserv, which are SLES specific
