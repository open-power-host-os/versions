%global commit          %{?git_commit_id}
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitcommittag    .git%{shortcommit}

Name:		lsvpd
Version:	1.7.8
Release:	1%{?extraver}%{gitcommittag}%{?dist}
Summary:	VPD/hardware inventory utilities for Linux
Group:		Applications/System
License:	GPLv2+
URL:		http://linux-diag.sf.net/Lsvpd.html

Source0:	%{name}.tar.gz

Requires:	iprutils >= 2.3.12
Requires(pre):	iprutils >= 2.3.12
Requires(postun): iprutils >= 2.3.12

BuildRequires:	libvpd-devel >= 2.2.5
BuildRequires:	sg3_utils-devel zlib-devel automake libtool
BuildRequires:	librtas-devel
Requires(post): /usr/sbin/vpdupdate

ExclusiveArch: ppc64 ppc64le

%description
The lsvpd package contains all of the lsvpd, lscfg and lsmcode
commands. These commands, along with a scanning program
called vpdupdate, constitute a hardware inventory
system. The lsvpd command provides Vital Product Data (VPD) about
hardware components to higher-level serviceability tools. The lscfg
command provides a more human-readable format of the VPD, as well as
some system-specific information.  lsmcode lists microcode and
firmware levels.  lsvio lists virtual devices, usually only found
on POWER PC based systems.

%prep
%setup -q -n %{name}

%build
./bootstrap.sh
%configure
%{__make} %{?_smp_mflags}

%install
%{__make} install DESTDIR=$RPM_BUILD_ROOT

%post
# do not fail in KVM guest
/usr/sbin/vpdupdate || :

%files
%doc COPYING NEWS README
%{_sbindir}/lsvpd
%{_sbindir}/lscfg
%{_sbindir}/lsmcode
%{_sbindir}/lsvio
%{_sbindir}/vpdupdate
%{_mandir}/man8/vpdupdate.8.gz
%{_mandir}/man8/lsvpd.8.gz
%{_mandir}/man8/lscfg.8.gz
%{_mandir}/man8/lsvio.8.gz
%{_mandir}/man8/lsmcode.8.gz
%config %{_sysconfdir}/lsvpd/scsi_templates.conf
%config %{_sysconfdir}/lsvpd/cpu_mod_conv.conf
%dir %{_sysconfdir}/lsvpd

%changelog
* Fri Aug 25 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 1.7.8-1.git
- Version update
- Updating to b5542ab Roll out v1.7.8

* Mon Aug 14 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 1.7.7-8.git
- Bump release

* Mon Aug 07 2017 Fabiano Rosas <farosas@linux.vnet.ibm.com> - 1.7.7-7.git
- Add extraver macro to Release field

* Sat Nov 26 2016 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 1.7.7-6
- 3a5f5e1fdf82ebc6efdda4cfc51fd24776bad8be Fix NVMe device description field
- 22bf31003c097d993e73d22e745c36d16b5f85a2 Add check if lstat gets failed

* Wed Oct 19 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> 1.7.7-5
- Spec cleanup: Remove indirections in Version and Name tags.

* Mon Oct 12 2015 Jaromir Capik <jcapik@redhat.com> - 1.7.5-4
- Fixing syntax error when running vpdupdate (#1184517)
- Cleaning the spec file
- Fixing bogus dates in the changelog
- Resolves: #1184517

* Mon Dec 15 2014 Jakub Čajka <jcajka@redhat.com> - 1.7.5-3
- Resolves: #1174174 - lsvpd to report "Not supported on PowerKVM guest"

* Mon Nov 10 2014 Jakub Čajka <jcajka@redhat.com> - 1.7.5-2
- Related: #1161551 - librtas package update - rebuild

* Thu Sep 04 2014 Jakub Čajka <jcajka@redhat.com> - 1.7.5-1
- Related: #1088597 - [7.1 FEAT] lsvpd package update - ppc64
- Rebase to 1.7.5

* Thu Aug 21 2014 Jakub Čajka <jcajka@redhat.com> - 1.7.4-1
- Resolves: #1088597 - [7.1 FEAT] lsvpd package update - ppc64
- Resolves: #1124004 - lsvpd needs ppc64le added to ExclusiveArch

* Mon Apr 28 2014 Jakub Čajka <jcajka@redhat.com> - 1.7.1-4
- Resolves: #1088414 - RHEL7.0 - lsvpd: License: Grant permission to link with librtas library

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1.7.1-3
- Mass rebuild 2013-12-27

* Thu Nov 28 2013 Filip Kocina <fkocina@redhat.com> 1.7.1-2
- Resolves: #1030237 - fix FW expiry display terminology

* Tue May 21 2013 Vasant Hegde <hegdevasant@linux.vnet.ibm.com>
- Update to latest upstream 1.7.1
- Exclude invscout command from lsvpd package

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.12-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.12-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri May 04 2012 Karsten Hopp <karsten@redhat.com> 1.6.12-1
- update to 1.6.12

* Tue Feb 28 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.11-5
- Rebuilt for c++ ABI breakage

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.11-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Nov 23 2011 Jiri Skala <jskala@redhat.com> - 1.6.11-3
- added ExclusiveArch for ppc[64]

* Wed Nov 09 2011 Jiri Skala <jskala@redhat.com> - 1.6.11-2
- fixes #752244 - similar output for different options in lsmcode

* Wed Aug 10 2011 Jiri Skala <jskala@redhat.com> - 1.6.11-1
- rebase to latest upstream 1.6.11

* Tue Feb 15 2011 Jiri Skala <jskala@redhat.com> - 1.6.10-1
- rebase to latest upstream 1.6.10

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Apr 13 2010 Dan Horák <dan@danny.cz> - 1.6.8-2
- rebuilt for sg3_utils 1.29

* Tue Apr 06 2010 Roman Rakus <rrakus@redhat.com> - 1.6.8-1
- Version 1.6.8 (need ugly bootstrap)

* Wed Dec 02 2009 Eric Munson <ebmunson@us.ibm.com> - 1.6.7-1
- Update to latest lsvpd release
- Add librtas support to build on POWERPC
- Add patch to lookup *.ids file location at runtime

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Apr 28 2009 - Dan Horak <dan[at]danny.cz> - 1.6.5-2
- rebuild for sg3_utils 1.27

* Mon Mar 16 2009 Eric Munson <ebmunson@us.ibm.com> - 1.6.5-1
- Update source to use new glibc C header includes

* Mon Mar 16 2009 Eric Munson <ebmunson@us.ibm.com> - 1.6.4-6
- Bump for rebuild against latest build of libvpd

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.4-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Aug 14 2008 - Eric Munson <ebmunson@us.ibm.com> - 1.6.4-4
- Bump for rebuild with new libvpd.

* Mon Jun 30 2008 - Dan Horak <dan[at]danny.cz> - 1.6.4-3
- add patch for sg3_utils 1.26 and rebuild

* Fri Jun 06 2008 - Caolán McNamara <caolanm@redhat.com> - 1.6.4-2
- rebuild for dependancies

* Fri Apr 25 2008 - Brad Peters <bpeters@us.ibm.com> - 1.6.4-1
- Adding ability to limit SCSI direct inquiry size, fixing Windows SCSI
  device inquiry problem

* Fri Mar 21 2008 - Eric Munson <ebmunson@us.ibm.com> - 1.6.3-1
- Adding proper conf file handling
- Removing executable bit on config and documentation files
- Removing second listing for config files

* Fri Mar 14 2008 - Eric Munson <ebmunson@us.ibm.com> - 1.6.2-3
- Becuase librtas is not yet in Fedora, the extra ppc dependency should
  be ignored

* Thu Mar 13 2008 - Eric Munson <ebmunson@us.ibm.com> - 1.6.2-2
- Adding arch check for ppc[64] dependency.

* Tue Mar 4 2008 - Eric Munson <ebmunson@us.ibm.com> - 1.6.2-1
- Updating for lsvpd-1.6.2

* Mon Mar 3 2008 - Eric Munson <ebmunson@us.ibm.com> - 1.6.1-1
- Updating for lsvpd-1.6.1

* Sat Feb 2 2008 - Eric Munson <ebmunson@us.ibm.com> - 1.6.0-1
- Updating lsvpd to use the new libvpd-2.0.0
- Removing %%{_mandir}/man8/* from %%files and replacing it with each
  individual file installed in the man8 directory

* Fri Dec 7 2007 - Brad Peters <bpeters@us.ibm.com> - 1.5.0
- Major changes in device detection code, basing detection on /sys/devices
  rather than /sys/bus as before
- Enhanced aggressiveness of AIX naming, ensuring that every detected device
  has at least one AIX name, and thus appears in lscfg output
- Changed method for discovering /sys/class entries
- Added some new VPD fields, one example of which is the device driver
  associated with the device
- Some minor changes to output formating
- Some changes to vpd collection
- Removing unnecessary Requires field

* Fri Nov 16 2007 - Eric Munson <ebmunson@us.ibm.com> - 1.4.0-1
- Removing udev rules from install as they are causing problems.  Hotplug
  will be disabled until we find a smarter way of handling it.
- Updating License
- Adjusting the way vpdupdater is inserted into run control
- Removing #! from the beginning of the file.
- Fixes requested by Fedora Community

* Tue Oct 30 2007 - Eric Munson <ebmunson@us.ibm.com> - 1.3.5-1
- Remove calls to ldconfig
