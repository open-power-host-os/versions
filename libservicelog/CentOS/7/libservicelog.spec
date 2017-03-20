%global commit          %{?git_commit_id}
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitcommittag    .git%{shortcommit}

Name:           libservicelog
Version:        1.1.16
Release:        2%{gitcommittag}%{?dist}
Summary:        Servicelog Database and Library

Group:          System Environment/Libraries
License:        LGPLv2
URL:            http://linux-diag.sourceforge.net/servicelog
Source0:        %{name}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires(pre):       shadow-utils

BuildRequires:  sqlite-devel autoconf libtool bison librtas-devel flex

Obsoletes: libservicelog(ppc)
# because of librtas-devel
ExclusiveArch: ppc64 ppc64le


# Link with needed libraries
Patch0: libservicelog-1.1.15-libs.patch

%description
The libservicelog package contains a library to create and maintain a
database for storing events related to system service.  This database
allows for the logging of serviceable and informational events, and for
the logging of service procedures that have been performed upon the system.


%package        devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       pkgconfig sqlite-devel

%description    devel
Contains header files for building with libservicelog.


%prep
%setup -q -n %{name}
%patch0 -p1 -b .libs

%build
autoreconf -fiv
%configure --disable-static
%{__make} %{?_smp_mflags}


%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__make} install DESTDIR=$RPM_BUILD_ROOT
%{__rm} -f %{buildroot}%{_libdir}/*.la


%clean
%{__rm} -rf $RPM_BUILD_ROOT

%pre
getent group service >/dev/null || /usr/sbin/groupadd service

%post -p /sbin/ldconfig

%postun
/sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc COPYING AUTHORS
%{_libdir}/libservicelog-*.so.*
%dir %attr(755, root, service) /var/lib/servicelog
%verify(not md5 size mtime) %attr(644,root,service) /var/lib/servicelog/servicelog.db
%config(noreplace) /var/lib/servicelog/servicelog.db

%files devel
%defattr(-,root,root,-)
%{_includedir}/servicelog-1
%{_libdir}/*.so
%{_libdir}/pkgconfig/servicelog-1.pc


%changelog
* Sat Nov 26 2016 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 1.1.16-2
- 48875ee8614eeefaa3d5d8ff92fb424915738169 NULL check before strdup call
- 40b4f7a52e61fb9da30b4cb9b5de9a85673da262 NULL check before strlen call
- b5ebd51d01245a7bff961f30ca9db794629b0f8a libservicelog: Creating the service group as a system one

* Thu Oct 13 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 1.1.16
- Rebase to 1.1.16

* Mon Nov 10 2014 Jakub Čajka <jcajka@redhat.com> - 1.1.15-2
- Related: #1161551 - librtas package update - rebuild

* Thu Sep 04 2014 Jakub Čajka <jcajka@redhat.com> - 1.1.15-1
- Related: #1088494 - [7.1 FEAT] libservicelog package update - ppc64
Rebase to 1.1.15

* Wed Aug 13 2014 Jakub Čajka <jcajka@redhat.com> - 1.1.14-1
- Resolves: #1088494 - [7.1 FEAT] libservicelog package update - ppc64
- Related: #1098216 - [7.1 FEAT] libservicelog - drop 32bit package - ppc64

* Wed Jan 08 2014 Phil Knirsch <pknirsch@redhat.com> - 1.1.13-3
- Fixed build issue
Resolves: rhbz#1048877

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1.1.13-2
- Mass rebuild 2013-12-27

* Sat May 18 2013 Vasant Hegde <hegdevasant@fedoraproject.org> - 1.1.13
- Update to latest upstream 1.1.13

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.11-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.11-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.11-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Aug 08 2011 Jiri Skala <jskala@redhat.com> - 1.1.11-1
- update to latest upstream 1.1.11

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.9-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Jun 04 2010 Roman Rakus <rrakus@redhat.com> - 1.1.9-4
- Properly handle servicelog.db

* Tue May 18 2010 Roman Rakus <rrakus@redhat.com> - 1.1.9-2
- Link with needed libraries (sqlite, rtas, rtasevent)

* Tue May 11 2010 Roman Rakus <rrakus@redhat.com> - 1.1.9-1
- Update to 1.1.9

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Mar 31 2009 Roman Rakus <rrakus@redhat.com> - 1.0.1-2
- Added missing requires sqlite-devel in devel subpackage

* Fri Feb 20 2009 Roman Rakus <rrakus@redhat.com> - 1.0.1-1
- Initial packaging
