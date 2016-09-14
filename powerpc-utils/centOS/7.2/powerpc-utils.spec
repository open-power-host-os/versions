Name:           powerpc-utils
Version:        1.3.2
Release:        2%{?dist}
Summary:        Utilities for PowerPC platforms
Group:          System Environment/Base
License:        CPL
URL:            http://sourceforge.net/projects/%{name}/

Source0:        %{name}.tar.gz
Source1:        nvsetenv

# This hack is needed only for platforms with autoconf < 2.63
Patch0:         powerpc-utils-autoconf.patch
Patch1:         powerpc-utils-1.2.15-man.patch

ExclusiveArch:  ppc64 ppc64le

# This is done before release of F12
Obsoletes:      powerpc-utils-papr < 1.1.6-3
Provides:       powerpc-utils-papr = 1.1.6-3

# should be fixed - libservicelog is not right name
Requires:       libservicelog bc which
Requires:       powerpc-utils-python
Requires:       perl(Data::Dumper)
BuildRequires:  zlib-devel doxygen automake librtas-devel libservicelog-devel >= 1.0.1-2


%description
Utilities for PowerPC platforms.


%prep
%setup -q -n %{name}
./autogen.sh
# This hack is needed only for platforms with autoconf < 2.63
%if 0%{?fedora} < 9 && 0%{?rhel} < 6
%patch0 -p1 -b .aconf
%endif
%patch1 -p1 -b .man

%build
export CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing"
%configure
make %{?_smp_mflags}


%install
make install DESTDIR=$RPM_BUILD_ROOT FILES= RCSCRIPTS=
install -m 755 %{SOURCE1} $RPM_BUILD_ROOT%{_sbindir}/nvsetenv

%define pkgdocdir %{_datadir}/doc/%{name}-%{version}
# move doc files
mkdir -p $RPM_BUILD_ROOT%{pkgdocdir}
install $RPM_BUILD_ROOT/usr/share/doc/packages/powerpc-utils/* -t $RPM_BUILD_ROOT%{pkgdocdir}
rm -rf $RPM_BUILD_ROOT/usr/share/doc/packages/powerpc-utils

# remove init script and perl script. They are deprecated
rm -rf $RPM_BUILD_ROOT/etc/init.d/ibmvscsis.sh $RPM_BUILD_ROOT/usr/sbin/vscsisadmin

# nvsetenv is just a wrapper to nvram
ln -s nvram.8.gz $RPM_BUILD_ROOT/%{_mandir}/man8/nvsetenv.8.gz


%files
%{_sbindir}/nvsetenv
%{_sbindir}/nvram
#deprecated, use sosreport instead
%exclude %{_sbindir}/snap
%{_sbindir}/bootlist
%{_sbindir}/ofpathname
%{_sbindir}/ppc64_cpu
%{_sbindir}/lsdevinfo
%{_sbindir}/lsprop
%{_mandir}/man8/nvram.8*
%{_mandir}/man8/nvsetenv.8*
%exclude %{_mandir}/man8/snap.8*
%{_mandir}/man8/bootlist.8*
%{_mandir}/man8/ofpathname.8*

%{_sbindir}/update_flash
%{_sbindir}/activate_firmware
%{_sbindir}/set_poweron_time
%{_sbindir}/rtas_ibm_get_vpd
%{_sbindir}/serv_config
%{_sbindir}/uesensor
%{_sbindir}/hvcsadmin
%{_sbindir}/rtas_dump
%{_sbindir}/rtas_event_decode
%{_sbindir}/sys_ident
%{_sbindir}/drmgr
%{_sbindir}/lsslot
%{_sbindir}/ls-vdev
%{_sbindir}/ls-veth
%{_sbindir}/ls-vscsi
%{_sbindir}/lparstat
%{_sbindir}/pseries_platform
%{_sbindir}/update_flash_nv
%{_sbindir}/errinjct
%{_sbindir}/rtas_dbg

%{_bindir}/amsstat
%{_mandir}/man8/update_flash.8*
%{_mandir}/man8/activate_firmware.8*
%{_mandir}/man8/set_poweron_time.8*
%{_mandir}/man8/rtas_ibm_get_vpd.8*
%{_mandir}/man8/serv_config.8*
%{_mandir}/man8/uesensor.8*
%{_mandir}/man8/hvcsadmin.8*
%{_mandir}/man8/rtas_dump.8*
%{_mandir}/man8/sys_ident.8*
%{_mandir}/man8/lparstat.8*
%{_mandir}/man5/lparcfg.5*
%{_mandir}/man1/amsstat.1*
%{_mandir}/man8/lsdevinfo.8*
%{_mandir}/man8/rtas_event_decode.8*
%{_mandir}/man8/ls-vdev.8*
%{_mandir}/man8/lsslot.8*
%{_mandir}/man8/lsprop.8*
%{_mandir}/man8/drmgr.8*
%{_mandir}/man8/ls-veth.8*
%{_mandir}/man8/ppc64_cpu.8*
%{_mandir}/man8/ls-vscsi.8*
%{_mandir}/man8/errinjct.8*
%{_mandir}/man8/rtas_dbg.8*
%doc README COPYING Changelog


%changelog
* Tue Sep 08 2015 Jakub Čajka <jcajka@redhat.com> - 1.2.26-2
- Resolves: #1260285 - chhwres command hungs when creating VNIC adapter on RHEL7.1 LE partition (powerpc-utils)

* Thu Jun 25 2015 Jakub Čajka <jcajka@redhat.com> - 1.2.26-1
- Resolves: #1182040 - [7.2 FEAT] powerpc-utils package update - ppc64/ppc64le

* Fri Jun 19 2015 Jakub Čajka <jcajka@redhat.com> - 1.2.25-1
- Resolves: #1182040 - [7.2 FEAT] powerpc-utils package update - ppc64/ppc64le
- Resolves: #1199348 - After migration of RHEL7.1 Little Endian lpar, RMC connection on HMC will be lost (LPM)
- Resolves: #1207823 - drmgr -R flag is not working (powerpc-utils)


* Thu Jan 08 2015 Jakub Čajka <jcajka@redhat.com> - 1.2.24-7
- Related: #1179263 - reverted changes related to this bug

* Tue Jan 06 2015 Jakub Čajka <jcajka@redhat.com> - 1.2.24-6
- Related: #1179263 - fixed file permissions

* Tue Jan 06 2015 Jakub Čajka <jcajka@redhat.com> - 1.2.24-5
- Resolves: #1179263 - RHEL 7.1-LE LPAR: ppc64_cpu --threads-per-core gives wrong data when --smt value set

* Fri Jan 02 2015 Jakub Čajka <jcajka@redhat.com> - 1.2.24-4
- Resolves: #1175812 - powerpc-utils: rtas_dump showing some unwanted character

* Tue Dec 09 2014 Jakub Čajka <jcajka@redhat.com> - 1.2.24-3
- Resolves: #1172087 - snap fails
- snap removed, sosreport should be used instead

* Fri Dec 05 2014 Jakub Čajka <jcajka@redhat.com> - 1.2.24-2
- Resolves: #1170856 - Could not gather LMB information when doing Mem DLPAR on RHEL7.1 Alpha LE (powerpc-utils)

* Thu Nov 27 2014 Jakub Čajka <jcajka@redhat.com> - 1.2.24-1
- Resolves: #1167865 - CPU/Mem DLPAR failed on both RHEL7.1 Alpha BE and LE
- Rebase to 1.2.24

* Fri Nov 14 2014 Jakub Čajka <jcajka@redhat.com> - 1.2.23-2
- Resolves: #1164147 - CVE-2014-4040 powerpc-utils: snap creates archives with fstab and yaboot.conf which may expose certain passwords [rhel-7.1]

* Mon Nov 10 2014 Jakub Čajka <jcajka@redhat.com> - 1.2.23-1
- Resolves: #1161552 - powerpc-utils package update for RHEL7.1 Beta

* Tue Oct 14 2014 Jakub Čajka <jcajka@redhat.com> - 1.2.22-2
- Resolves: #1152313 - STC820:Brazos:JMET:lisafp1:lisap05:RHEL7 Hung/Crashed while running htx ...

* Thu Sep 04 2014 Jakub Čajka <jcajka@redhat.com> - 1.2.22-1
- Related: #1088539 - [7.1 FEAT] powerpc-utils package update - ppc64
- Rebase to 1.2.22

* Mon Aug 25 2014 Jakub Čajka <jcajka@redhat.com> - 1.2.21-1
- Resolves: #1088539 - [7.1 FEAT] powerpc-utils package update - ppc64
- Resolves: #1083221 - Validation Failure with Linux partitions - Inactive RMC ...
- Resolves: #1079246 - powerpc-utils: lsdevinfo does not handle path of device on full system lpar.
- Resolves: #1083791 - powerpc-utils: add support for hotplug of qemu pci virtio devices
- Resolves: #1124006 - powerpc-utils needs ppc64le added to ExclusiveArch

* Wed Mar 12 2014 Karsten Hopp <karsten@redhat.com> 1.2.18-9
- fix parsing of the value supplied for the -s option
- Resolves: #1074629
- fix wrong check of valid_platform() return value
- Resolves: #1074635

* Mon Mar 10 2014 Karsten Hopp <karsten@redhat.com> 1.2.18-8
- update display message when Power System FW entitlement expires
- Resolves: rhbz 1071555

* Mon Feb 17 2014 Jaromir Capik <jcapik@redhat.com> - 1.2.18-7
- drmgr: Fixing addition of device nodes (#1064220)
- sys_ident: Adding support for P8 Systems (#1064484)
- Resolves: rhbz#1064220, rhbz#1064484

* Mon Feb 10 2014 Jaromir Capik <jcapik@redhat.com> - 1.2.18-6
- drmgr: Fixing allocation failures & race when removing adapter (#1061179)
- drmgr: Fixing return code when running with --capabilities (#1061092)
- Fixing bogus date in the changelog
- Cleaning the spec
- Resolves: rhbz#1061179, rhbz#1061092

* Thu Jan 16 2014 Filip Kocina <fkocina@redhat.com> - 1.2.18-5
- Resolves: #1054031 - snap command get hung. No response

* Tue Jan 14 2014 Filip Kocina <fkocina@redhat.com> - 1.2.18-4
- Resolves: #1043455 && #1039473 - nvram tool fails to decompress the data && ofpathname in RHEL7 doesn't handle virtio-blk disks

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1.2.18-3
- Mass rebuild 2013-12-27

* Thu Nov 28 2013 Filip Kocina <fkocina@redhat.com> - 1.2.18-2
- Resolves: #1030236 - update FW entitlement message terminology

* Wed Sep 25 2013 Filip Kocina <fkocina@redhat.com> - 1.2.18-1
- Resolves: #1011038 - updated to latest upstream 1.2.18

* Thu Sep 12 2013 Filip Kocina <fkocina@redhat.com> - 1.2.17-1
- Resolves: #947179 - updated to latest upstream 1.2.17 && applying patch nvram

* Wed Jun 26 2013 Tony Breeds <tony@bakeyournoodle.com> - 1.2.16-2
- drmgr: Check for rpadlpar_io module
- resolves: #972606

* Tue May 21 2013 Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 1.2.16
- Update to latest upstream 1.2.16

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.15-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jan 16 2013 Karsten Hopp <karsten@redhat.com> 1.2.15-1
- update to 1.2.15
- usysident/usysattn got moved to ppc64-diag package
- multipath ofpathname patch removed as it is upstream now

* Tue Dec 18 2012 Filip Kocina <fkocina@redhat.com> 1.2.14-1
- Resolves: #859222 - updated to latest upstream 1.2.14

* Thu Dec 13 2012 Karsten Hopp <karsten@redhat.com> 1.2.12-4
- Add multipath support to ofpathname for bug #884826

* Tue Sep 04 2012 Karsten Hopp <karsten@redhat.com> 1.2.12-3
- require powerpc-utils-python (#852326 comment 7)

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.12-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Mar 22 2012 Jiri Skala <jskala@redhat.com> - 1.2.12-1
- updated to latest upstream 1.2.12

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.11-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Nov 03 2011 Jiri Skala <jskala@redhat.com> - 1.2.11-2
- updated dependecy

* Mon Oct 31 2011 Jiri Skala <jskala@redhat.com> - 1.2.11-1
- updated to latest upstream 1.2.11
-fixes #749892 - powerpc-utils spec file missing dependency

* Fri Aug 05 2011 Jiri Skala <jskala@redhat.com> - 1.2.10-1
- updated to latest upstream 1.2.10

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 24 2011 Jiri Skala <jskala@redhat.com> - 1.2.6-1
- updated to latest upstream 1.2.6
- removed amsvis man page (amsvis moved to powerpc-utils-python)
- added lparcfg man page - doc to /proc/ppc64/lparcfg

* Thu Jun 24 2010 Roman Rakus <rrakus@redhat.com> - 1.2.2-14
- Compile with -fno-strict-aliasing CFLAG
- linked nvsetenv man page to nvram man page
- Updated man page of ofpathname
- Updated amsstat script

* Tue Jun 15 2010 Roman Rakus <rrakus@redhat.com> - 1.2.2-11
- Correct the parameter handling of ppc64_cpu when setting the run-mode

* Wed Jun 09 2010 Roman Rakus <rrakus@redhat.com> - 1.2.2-10
- Added some upstream patches
- also bump release

* Wed Jun 02 2010 Roman Rakus <rrakus@redhat.com> - 1.2.2-4
- correct the parameter checking when attempting to set the run mode
- also bump release

* Fri Mar 05 2010 Roman Rakus <rrakus@redhat.com> - 1.2.2-2
- Removed deprecated init script and perl script

* Thu Oct 29 2009 Stepan Kasal <skasal@redhat.com> - 1.2.2-1
- new upstream version
- amsvis removed, this package has no longer anything with python
- change the manual pages in the file list so that it does not depend on
  particular compression used
- add patch for configure.ac on platforms with autoconf < 2.63
- use standard %%configure/make in %%build

* Mon Aug 17 2009 Roman Rakus <rrakus@redhat.com> - 1.2.0-1
- Bump tu version 1.2.0 - powerpc-utils and powerpc-utils-papr get merged

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Apr 06 2009 Roman Rakus <rrakus@redhat.com> - 1.1.3-1
- new upstream version 1.1.3

* Tue Mar 03 2009 Roman Rakus <rrakus@redhat.com> - 1.1.2-1
- new upstream version 1.1.2

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Feb 19 2009 Roman Rakus <rrakus@redhat.com> - 1.1.1-1
- new upstream version 1.1.1

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.0.6-3
- Autorebuild for GCC 4.3

* Mon Dec  3 2007 David Woodhouse <dwmw2@redhat.com> 1.0.6-2
- Add --version to nvsetenv, for ybin compatibility

* Fri Nov 23 2007 David Woodhouse <dwmw2@redhat.com> 1.0.6-1
- New package, split from ppc64-utils

