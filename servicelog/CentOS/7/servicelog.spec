%global commit          %{?git_commit_id}
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitcommittag    .git%{shortcommit}

Name:           servicelog
Version:        1.1.14
Release:        7%{?extraver}%{gitcommittag}%{?dist}
Summary:        Servicelog Tools

Group:          System Environment/Base
License:        GPLv2
Vendor:		IBM Corp.
URL:            http://linux-diag.sourceforge.net/servicelog
Source0:        %{name}.tar.gz

BuildRequires:  libservicelog-devel libtool automake
# Without librtas, the build fails because of missing modules
BuildRequires:  librtas-devel
ExclusiveArch:	ppc ppc64 ppc64le

%description
Command-line interfaces for viewing and manipulating the contents of
the servicelog database. Servicelog contains entries that are useful
for performing system service operations, and for providing a history
of service operations that have been performed on the system.

%files
%defattr(744,root,root,-)
%doc COPYING README
%{_bindir}/servicelog
%{_bindir}/v1_servicelog
%{_bindir}/v29_servicelog
%{_bindir}/servicelog_notify
%{_bindir}/log_repair_action
%{_sbindir}/slog_common_event
%{_bindir}/servicelog_manage
%{_mandir}/man8/*.8*

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

%changelog
* Wed Mar 16 2016  Vasant Hegde <hegdevasant at linux.vnet.ibm.com> 1.1.14
- PowerKVM is a distro, not a platform
- Replace popen with native time function
- Code cleanup

* Thu Aug 14 2014  Vasant Hegde <hegdevasant at linux.vnet.ibm.com> 1.1.13
- Grant permission to link with librtas library
- Fixed couple of issues in build tool

* Fri Mar 07 2014 Vasant Hegde <hegdevasant at linux.vnet.ibm.com> 1.1.12
- Added platform validation

* Tue Jan 29 2013 Vasant Hegde <hegdevasant at linux.vnet.ibm.com> 1.1.11-3
- log_repair_action : usage message format fix

* Thu Jan 10 2013 Vasant Hegde <hegdevasant at linux.vnet.ibm.com> 1.1.11-2
- servicelog_notify : validate command line arguments
- Minor fix to man pages
- Spec file cleanup

* Wed Sep 12 2012 Vasant Hegde <hegdevasant at linux.vnet.ibm.com> 1.1.11
- servicelog_manage : resurrecting the --clean option

* Fri Sep 7 2012 Vasant Hegde <hegdevasant at linux.vnet.ibm.com> 1.1.11
- Minor changes

* Mon Feb 13 2012 Jim Keniston <jkenisto at us.ibm.com> 1.1.10
- Resurrected servicelog_manage(8) man page (LTC bugzilla #70852).
- Major fixups to the other man pages (#70853) and to servicelog_notify.

* Mon Mar 28 2011 Jim Keniston <jkenisto at us.ibm.com> 1.1.9
- Fixed servicelog_manage bugs (LTC bugzilla #70459).

* Wed Oct 20 2010 Brad Peters 1.1.8
- Minor changes

* Sat Nov 07 2009 Jim Keniston <jkenisto at us.ibm.com>, Brad Peters 1.1.x
- Added backward compatibility with [lib]servicelog v0.2.9.

* Mon Aug 18 2008 Mike Strosaker <strosake at austin.ibm.com> 1.0.1
- Various small fixes to the servicelog_notify command

* Tue Mar 04 2008 Mike Strosaker <strosake at austin.ibm.com> 1.0.0
- Initial creation of the package
