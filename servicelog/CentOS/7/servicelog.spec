%global commit          %{?git_commit_id}
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitcommittag    .git%{shortcommit}

Name:           servicelog
Version:        1.1.14
Release:        5%{?extraver}%{gitcommittag}%{?dist}
Summary:        Servicelog Tools

Group:          System Environment/Base
License:        GPLv2
URL:            http://linux-diag.sourceforge.net/servicelog
Source0:        %{name}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#Requires(pre):       shadow-utils

BuildRequires:  libservicelog-devel >= 1.1.9-2
BuildRequires:  autoconf libtool

# because of librtas-devel in libservicelog
ExclusiveArch:  ppc64 ppc64le

%description
Command-line interfaces for viewing and manipulating the contents of
the servicelog database. Contains entries that are useful
for performing system service operations, and for providing a history
of service operations that have been performed on the system.

%prep
%setup -q -n %{name}
./bootstrap.sh

%build
%configure
%{__make} %{?_smp_mflags}


%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__make} install DESTDIR=$RPM_BUILD_ROOT

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root, -)
%doc COPYING
%{_bindir}/servicelog
%{_bindir}/v1_servicelog
%{_bindir}/v29_servicelog
%{_bindir}/servicelog_notify
%{_bindir}/log_repair_action
%{_sbindir}/slog_common_event
%{_bindir}/servicelog_manage
%{_mandir}/man[18]/*.[18]*

%changelog
* Mon Aug 07 2017 Fabiano Rosas <farosas@linux.vnet.ibm.com> - 1.1.14-5.git
- Add extraver macro to Release field

* Fri Jan 13 2017 Fabiano Rosas <farosas@linux.vnet.ibm.com> - 1.1.14-4
- Bump release so that this package takes precedence over CentOS version
  (1.1.14-3)

* Thu Oct 13 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 1.1.16
- Rebase to 1.1.14i
- Remove man page generation of slog_common_event (with help2man) cause it's not
  supported on powernv, where we currently build hostOS

* Fri Sep 05 2014 Jakub Čajka <jcajka@redhat.com> - 1.1.13-2
- Related: #1088495 - trimed buildRequires

* Thu Sep 04 2014 Jakub Čajka <jcajka@redhat.com> - 1.1.13-1
- Related: #1088495 - [7.1 FEAT] servicelog package update - ppc64
- Rebase to 1.1.13

* Thu Aug 21 2014 Jakub Čajka <jcajka@redhat.com> - 1.1.12-1
- Resolves: #1124011 - servicelog needs ppc64le added to ExclusiveArch
- Resolves: #1088495 - [7.1 FEAT] servicelog package update - ppc64

* Mon Apr 28 2014 Jakub Čajka <jcajka@redhat.com> - 1.1.11-3
- Resolves: #1088413 - RHEL7.0 - servicelog: License: Grant permission to link with librtas library

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1.1.11-2
- Mass rebuild 2013-12-27

* Tue May 21 2013 Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 1.1.11
- Update to latest upstream 1.1.11

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.10-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue May 08 2012 Karsten Hopp <karsten@redhat.com> 1.1.10-1
- update to servicelog-1.1.10

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Aug 09 2011 Jiri Skala <jskala@redhat.com> - 1.1.9-1
- update to latest upstream 1.1.9

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.7-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Jun 16 2010 Roman Rakus <rrakus@redhat.com> - 1.1.7-2
- Generate missing man page from help (help2man)

* Tue May 18 2010 Roman Rakus <rrakus@redhat.com> - 1.1.7-1
- Initial packaging
