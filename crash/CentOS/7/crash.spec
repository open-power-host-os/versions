%global commit          64531dc850f2840cedafa143fe051d2cfeae5247
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

#
# crash core analysis suite
#
Summary: Kernel analysis utility for live systems, netdump, diskdump, kdump, LKCD or mcore dumpfiles
Name: crash
Version: 7.1.6
Release: 1.git%{shortcommit}%{?dist}
License: GPLv3
Group: Development/Debuggers
Source: %{name}.tar.gz
URL: http://people.redhat.com/anderson
ExclusiveOS: Linux
ExclusiveArch: %{ix86} ia64 x86_64 ppc ppc64 s390 s390x %{arm} aarch64 ppc64le
Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot-%(%{__id_u} -n)
BuildRequires: ncurses-devel zlib-devel lzo-devel snappy-devel bison readline-devel
BuildRequires: wget
Requires: binutils
Provides: bundled(libiberty)
Provides: bundled(gdb) = 7.6
Patch0: lzo_snappy.patch
Patch1: use_system_readline_v3.patch
Patch2: glibc_ps_get_thread_area_workaround.patch

%description
The core analysis suite is a self-contained tool that can be used to
investigate either live systems, kernel core dumps created from the
netdump, diskdump and kdump packages from Red Hat Linux, the mcore kernel patch
offered by Mission Critical Linux, or the LKCD kernel patch.

%package devel
Requires: %{name} = %{version}, zlib-devel
Summary: kernel crash analysis utility for live systems, netdump, diskdump, kdump, LKCD or mcore dumpfiles
Group: Development/Debuggers

%description devel
The core analysis suite is a self-contained tool that can be used to
investigate either live systems, kernel core dumps created from the
netdump, diskdump and kdump packages from Red Hat Linux, the mcore kernel patch
offered by Mission Critical Linux, or the LKCD kernel patch.

%prep
%setup -n %{name} -q
%patch0 -p1 -b lzo_snappy.patch
%patch1 -p1 -b use_system_readline_v3.patch
%patch2 -p1 -b glibc_ps_get_thread_area_workaround.patch

%build
make RPMPKG="%{version}-%{release}" CFLAGS="%{optflags}"

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_bindir}
make DESTDIR=%{buildroot} install
mkdir -p %{buildroot}%{_mandir}/man8
cp -p crash.8 %{buildroot}%{_mandir}/man8/crash.8
mkdir -p %{buildroot}%{_includedir}/crash
chmod 0644 defs.h
cp -p defs.h %{buildroot}%{_includedir}/crash

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{_bindir}/crash
%{_mandir}/man8/crash.8*
%doc README COPYING3

%files devel
%defattr(-,root,root,-)
%{_includedir}/*

%changelog
* Fri Oct 14 2016 Dave Anderson <anderson@redhat.com> - 7.1.6-1
- Update to latest upstream release
- Fix for RHBZ#1044119 - crash bundles gdb

* Thu May  5 2016 Dave Anderson <anderson@redhat.com> - 7.1.5-2
- BZ #1333295 - FTBFS due compiler warnings in elf64-s390.c

* Thu Apr 28 2016 Dave Anderson <anderson@redhat.com> - 7.1.5-1
- Update to latest upstream release

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 7.1.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Dec 17 2015 Dave Anderson <anderson@redhat.com> - 7.1.4-1
- Update to latest upstream release

* Thu Sep  3 2015 Dave Anderson <anderson@redhat.com> - 7.1.3-1
- Update to latest upstream release

* Mon Jul 13 2015 Dave Anderson <anderson@redhat.com> - 7.1.2-1
- Update to latest upstream release

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 7.1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu May 28 2015 Dave Anderson <anderson@redhat.com> - 7.1.1-1
- Update to latest upstream release

* Mon Mar  2 2015 Dave Anderson <anderson@redhat.com> - 7.1.0-3
- Support increment of Linux version from 3 to 4

* Sat Feb 21 2015 Till Maas <opensource@till.name> - 7.1.0-2
- Rebuilt for Fedora 23 Change
  https://fedoraproject.org/wiki/Changes/Harden_all_packages_with_position-independent_code

* Tue Feb 10 2015 Dave Anderson <anderson@redhat.com> - 7.1.0-1
- Update to latest upstream release

* Fri Nov 15 2014 Dave Anderson <anderson@redhat.com> - 7.0.9-1
- Update to latest upstream release

* Mon Sep 15 2014 Dave Anderson <anderson@redhat.com> - 7.0.8-1
- Update to latest upstream release
- Add ppc64le as supported architecture for crash package (BZ #1136050)

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 7.0.7-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Wed Jul 02 2014 Dave Anderson <anderson@redhat.com> - 7.0.7-2
- Fix FTBS for aarch64 (BZ #1114588)

* Wed Jun 11 2014 Dave Anderson <anderson@redhat.com> - 7.0.7-1
- Update to latest upstream release
- Fix Fedora_21_Mass_Rebuild FTBFS (BZ #1106090)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 7.0.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Feb 28 2014 Dave Anderson <anderson@redhat.com> - 7.0.5-1
- Update to latest upstream release
- Use system readline library
- Fix "crash --log vmcore" command for 3.11 and later kernels.

* Tue Dec 17 2013 Toshio Kuratomi <toshio@fedoraproject.org> - 7.0.4-2
- crash bundles gdb which bundles libiberty.  Add virtual Provides for
  libiberty tracking.  Open a bug for unbundling gdb RHBZ#1044119

* Mon Dec 16 2013 Dave Anderson <anderson@redhat.com> - 7.0.4-1
- Update to latest upstream release

* Tue Oct 29 2013 Dave Anderson <anderson@redhat.com> - 7.0.3-1
- Update to latest upstream release

* Wed Sep 04 2013 Dave Anderson <anderson@redhat.com> - 7.0.2-1
- Update to latest upstream release
- Build with lzo and snappy compression capability

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 7.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Jun 17 2013 Dave Anderson <anderson@redhat.com> - 7.0.1-1
- Update to latest upstream release
- Add aarch64 as an exclusive arch

* Tue Apr  9 2013 Dave Anderson <anderson@redhat.com> - 6.1.6-1
- Update to latest upstream release

* Tue Feb 19 2013 Dave Anderson <anderson@redhat.com> - 6.1.4-1
- Update to latest upstream release

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6.1.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jan  9 2013 Dave Anderson <anderson@redhat.com> - 6.1.2-1
- Update to latest upstream release

* Tue Nov 27 2012 Dave Anderson <anderson@redhat.com> - 6.1.1-1
- Update to latest upstream release

* Mon Sep  1 2012 Dave Anderson <anderson@redhat.com> - 6.1.0-1
- Add ppc to ExclusiveArch list
- Update to latest upstream release

* Tue Aug 21 2012 Dave Anderson <anderson@redhat.com> - 6.0.9-1
- Update to latest upstream release

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6.0.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jul  1 2012 Dave Anderson <anderson@redhat.com> - 6.0.8-1
- Update to latest upstream release.
- Replace usage of "struct siginfo" with "siginfo_t".

* Mon Apr 30 2012 Dave Anderson <anderson@redhat.com> - 6.0.6-1
- Update to latest upstream release

* Mon Mar 26 2012 Dave Anderson <anderson@redhat.com> - 6.0.5-1
- Update to latest upstream release

* Wed Jan  4 2012 Dave Anderson <anderson@redhat.com> - 6.0.2-1
- Update to latest upstream release

* Wed Oct 26 2011 Dave Anderson <anderson@redhat.com> - 6.0.0-1
- Update to latest upstream release

* Tue Sep 20 2011 Dave Anderson <anderson@redhat.com> - 5.1.8-1
- Update to latest upstream release
- Additional fixes for gcc-4.6 -Werror compile failures for ARM architecture.

* Thu Sep  1 2011 Dave Anderson <anderson@redhat.com> - 5.1.7-2
- Fixes for gcc-4.6 -Werror compile failures for ARM architecture.

* Wed Aug 17 2011 Dave Anderson <anderson@redhat.com> - 5.1.7-1
- Update to latest upstream release
- Fixes for gcc-4.6 -Werror compile failures for ppc64/ppc.

* Tue May 31 2011 Peter Robinson <pbrobinson@gmail.com> - 5.1.5-1
- Update to latest upstream release
- Add ARM to the Exclusive arch

* Wed Feb 25 2011 Dave Anderson <anderson@redhat.com> - 5.1.2-2
- Fixes for gcc-4.6 -Werror compile failures in gdb module.  

* Wed Feb 23 2011 Dave Anderson <anderson@redhat.com> - 5.1.2-1
- Upstream version.

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.0.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Jul 20 2010 Dave Anderson <anderson@redhat.com> - 5.0.6-2
- Bump version.

* Tue Jul 20 2010 Dave Anderson <anderson@redhat.com> - 5.0.6-1
- Update to upstream version.

* Fri Sep 11 2009 Dave Anderson <anderson@redhat.com> - 4.0.9-2
  Bump version.

* Fri Sep 11 2009 Dave Anderson <anderson@redhat.com> - 4.0.9-1
- Update to upstream release, which allows the removal of the 
  Revision tag workaround, the crash-4.0-8.11-dwarf3.patch and 
  the crash-4.0-8.11-optflags.patch

* Sun Aug 05 2009 Lubomir Rintel <lkundrak@v3.sk> - 4.0.8.11-2
- Fix reading of dwarf 3 DW_AT_data_member_location
- Use proper compiler flags

* Wed Aug 05 2009 Lubomir Rintel <lkundrak@v3.sk> - 4.0.8.11-1
- Update to later upstream release
- Fix abuse of Revision tag

- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild
* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0-9.7.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0-8.7.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Feb 19 2009 Dave Anderson <anderson@redhat.com> - 4.0-7.7.2
- Replace exclusive arch i386 with ix86.

* Thu Feb 19 2009 Dave Anderson <anderson@redhat.com> - 4.0-7.7.1
- Updates to this file per crash merge review
- Update to upstream version 4.0-7.7.  Full changelog viewable in:
    http://people.redhat.com/anderson/crash.changelog.html

* Tue Jul 15 2008 Tom "spot" Callaway <tcallawa@redhat.com> 4.0-7
- fix license tag

* Tue Apr 29 2008 Dave Anderson <anderson@redhat.com> - 4.0-6.3
- Added crash-devel subpackage
- Updated crash.patch to match upstream version 4.0-6.3

* Wed Feb 20 2008 Dave Anderson <anderson@redhat.com> - 4.0-6.0.5
- Second attempt at addressing the GCC 4.3 build, which failed due
  to additional ptrace.h includes in the lkcd vmdump header files.

* Wed Feb 20 2008 Dave Anderson <anderson@redhat.com> - 4.0-6.0.4
- First attempt at addressing the GCC 4.3 build, which failed on x86_64
  because ptrace-abi.h (included by ptrace.h) uses the "u32" typedef,
  which relies on <asm/types.h>, and include/asm-x86_64/types.h
  does not not typedef u32 as done in include/asm-x86/types.h.

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 4.0-6.0.3
- Autorebuild for GCC 4.3

* Wed Jan 23 2008 Dave Anderson <anderson@redhat.com> - 4.0-5.0.3
- Updated crash.patch to match upstream version 4.0-5.0.

* Wed Aug 29 2007 Dave Anderson <anderson@redhat.com> - 4.0-4.6.2
- Updated crash.patch to match upstream version 4.0-4.6.

* Wed Sep 13 2006 Dave Anderson <anderson@redhat.com> - 4.0-3.3
- Updated crash.patch to match upstream version 4.0-3.3.
- Support for x86_64 relocatable kernels.  BZ #204557

* Mon Aug  7 2006 Dave Anderson <anderson@redhat.com> - 4.0-3.1
- Updated crash.patch to match upstream version 4.0-3.1.
- Added kdump reference to description.
- Added s390 and s390x to ExclusiveArch list.  BZ #199125
- Removed LKCD v1 pt_regs references for s390/s390x build.
- Removed LKCD v2_v3 pt_regs references for for s390/s390x build.

* Fri Jul 14 2006 Jesse Keating <jkeating@redhat.com> - 4.0-3
- rebuild

* Mon May 15 2006 Dave Anderson <anderson@redhat.com> - 4.0-2.26.4
- Updated crash.patch such that <asm/page.h> is not #include'd
  by s390_dump.c; IBM did not make the file s390[s] only; BZ #192719

* Mon May 15 2006 Dave Anderson <anderson@redhat.com> - 4.0-2.26.3
- Updated crash.patch such that <asm/page.h> is not #include'd
  by vas_crash.h; only ia64 build complained; BZ #191719

* Mon May 15 2006 Dave Anderson <anderson@redhat.com> - 4.0-2.26.2
- Updated crash.patch such that <asm/segment.h> is not #include'd
  by lkcd_x86_trace.c; also for BZ #191719

* Mon May 15 2006 Dave Anderson <anderson@redhat.com> - 4.0-2.26.1
- Updated crash.patch to bring it up to 4.0-2.26, which should 
  address BZ #191719 - "crash fails to build in mock"

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 4.0-2.18.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Wed Jan 04 2006 Dave Anderson <anderson@redhat.com> 4.0-2.18
- Updated source package to crash-4.0.tar.gz, and crash.patch
  to bring it up to 4.0-2.18.

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Thu Mar 03 2005 Dave Anderson <anderson@redhat.com> 3.10-13
- Compiler error- and warning-related fixes for gcc 4 build.
- Update to enhance x86 and x86_64 gdb disassembly output so as to
  symbolically display call targets from kernel module text without
  requiring module debuginfo data.
- Fix hole where an ia64 vmcore could be mistakenly accepted as a
  usable dumpfile on an x86_64 machine, leading eventually to a
  non-related error message.
* Wed Mar 02 2005 Dave Anderson <anderson@redhat.com> 3.10-12
- rebuild (gcc 4)
* Thu Feb 10 2005 Dave Anderson <anderson@redhat.com> 3.10-9
- Updated source package to crash-3.10.tar.gz, containing
  IBM's final ppc64 processor support for RHEL4
- Fixes potential "bt -a" hang on dumpfile where netdump IPI interrupted
  an x86 process while executing the instructions just after it had entered
  the kernel for a syscall, but before calling the handler.  BZ #139437
- Update to handle backtraces in dumpfiles generated on IA64 with the
  INIT switch (functionality intro'd in RHEL3-U5 kernel).  BZ #139429
- Fix for handling ia64 and x86_64 machines booted with maxcpus=1 on
  an SMP kernel.  BZ #139435
- Update to handle backtraces in dumpfiles generated on x86_64 from the
  NMI exception stack (functionality intro'd in RHEL3-U5 kernel).
- "kmem -[sS]" beefed up to more accurately verify slab cache chains
  and report errors found.
- Fix for ia64 INIT switch-generated backtrace handling when
  init_handler_platform() is inlined into ia64_init_handler();
  properly handles both RHEL3 and RHEL4 kernel patches.
  BZ #138350
- Update to enhance ia64 gdb disassembly output so as to
  symbolically display call targets from kernel module
  text without requiring module debuginfo data.

* Wed Jul 14 2004 Dave Anderson <anderson@redhat.com> 3.8-5
- bump release for fc3

* Tue Jul 13 2004 Dave Anderson <anderson@redhat.com> 3.8-4
- Fix for gcc 3.4.x/gdb issue where vmlinux was mistakenly presumed non-debug 

* Fri Jun 25 2004 Dave Anderson <anderson@redhat.com> 3.8-3
- remove (harmless) error message during ia64 diskdump invocation when
  an SMP system gets booted with maxcpus=1
- several 2.6 kernel specific updates

* Thu Jun 17 2004 Dave Anderson <anderson@redhat.com> 3.8-2
- updated source package to crash-3.8.tar.gz 
- diskdump support
- x86_64 processor support 

* Mon Sep 22 2003 Dave Anderson <anderson@redhat.com> 3.7-5
- make bt recovery code start fix-up only upon reaching first faulting frame

* Fri Sep 19 2003 Dave Anderson <anderson@redhat.com> 3.7-4
- fix "bt -e" and bt recovery code to recognize new __KERNEL_CS and DS

* Wed Sep 10 2003 Dave Anderson <anderson@redhat.com> 3.7-3
- patch to recognize per-cpu GDT changes that redefine __KERNEL_CS and DS

* Wed Sep 10 2003 Dave Anderson <anderson@redhat.com> 3.7-2
- patches for netdump active_set determination and slab info gathering 

* Wed Aug 20 2003 Dave Anderson <anderson@redhat.com> 3.7-1
- updated source package to crash-3.7.tar.gz

* Wed Jul 23 2003 Dave Anderson <anderson@redhat.com> 3.6-1
- removed Packager, Distribution, and Vendor tags
- updated source package to crash-3.6.tar.gz 

* Fri Jul 18 2003 Jay Fenlason <fenlason@redhat.com> 3.5-2
- remove ppc from arch list, since it doesn't work with ppc64 kernels
- remove alpha from the arch list since we don't build it any more

* Fri Jul 18 2003 Matt Wilson <msw@redhat.com> 3.5-1
- use %%defattr(-,root,root)

* Tue Jul 15 2003 Jay Fenlason <fenlason@redhat.com>
- Updated spec file as first step in turning this into a real RPM for taroon.
- Wrote man page.
