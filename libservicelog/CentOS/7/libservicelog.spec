%global commit          %{?git_commit_id}
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitcommittag    .git%{shortcommit}

Name:           libservicelog
Version:        1.1.18
Release:        2%{?extraver}%{?gitcommittag}%{?dist}
Summary:        Servicelog Database and Library
Group:          System Environment/Libraries
License:        LGPLv2
Vendor:		IBM Corp.
URL:            http://linux-diag.sourceforge.net/libservicelog
Source0:        %{name}.tar.gz
ExclusiveArch:	ppc ppc64 ppc64le
BuildRequires:  sqlite-devel bison flex librtas-devel libtool automake
Requires(pre):	/usr/sbin/groupadd

%description
The libservicelog package contains a library to create and maintain a
database for storing events related to system service. This database
allows for the logging of serviceable and informational events, and for
the logging of service procedures that have been performed upon the system.


%package        devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:	pkgconfig sqlite-devel
Requires:       %{name} = %{version}-%{release}

%description    devel
Contains header files for building with libservicelog.


%prep
%setup -q -n %{name}

%build
./bootstrap.sh
%configure --disable-static
%{__make} %{?_smp_mflags}
touch servicelog.db
install -D --mode=754 servicelog.db \
	$RPM_BUILD_ROOT/var/lib/servicelog/servicelog.db

%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__make} install DESTDIR=$RPM_BUILD_ROOT

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%pre
getent group service >/dev/null || /usr/sbin/groupadd -r service

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc COPYING AUTHORS README
%exclude %{_libdir}/*.la
%{_libdir}/libservicelog-*.so.*
%attr( 754, root, service ) %dir /var/lib/servicelog
%config(noreplace) %verify(not md5 size mtime) %attr(644,root,service) /var/lib/servicelog/servicelog.db

%files devel
%defattr(-,root,root,-)
%{_libdir}/*.so
%{_includedir}/servicelog-1
%{_libdir}/*.la
%{_libdir}/pkgconfig/servicelog-1.pc

%changelog
* Thu Aug 24 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 1.1.18-2.git
- Updating to 1e39e77 libservicelog v1.1.18 release

* Tue Aug 22 2017 Ankit Kumar <ankit@linux.vnet.ibm.com> 1.1.18
- Sqlite bind call validation
- Added libservicelog test cases
- Print machine serial number
- Fixed few regression issues

* Wed Mar 22 2017 Vasant Hegde <hegdevasant at linux.vnet.ibm.com> 1.1.17
- NULL check before calling strdup
- Fixed various bugs

* Tue Mar 15 2016 Vasant Hegde <hegdevasant at linux.vnet.ibm.com> 1.1.16
- Fixed security issues like buffer overflow, memory allocation validation
- Fixed sqlite bind issue
- Fixed several build warnings

* Thu Aug 14 2014 Vasant Hegde <hegdevasant at linux.vnet.ibm.com> 1.1.15
- Cleanup build tools (configure.ac and Makefile.am)

* Tue Aug 20 2013 Vasant Hegde <hegdevasant at linux.vnet.ibm.com> 1.1.14
- Include servicelog.db and bootstrap.sh file into compression file list

* Thu Jan 10 2013 Vasant Hegde <hegdevasant at linux.vnet.ibm.com> 1.1.13
- Legalize SQL insert command input string
- repair_action : fix output format issue
- Minor typo fix

* Wed Sep 12 2012 Vasant Hegde <hegdevasant at linux.vnet.ibm.com> 1.1.12
- Minor changes

* Sat Nov 07 2009 Jim Keniston <jkenisto at us.ibm.com>, Brad Peters 1.1.x
- Minor changes continued in the ensuing months

* Sat Aug 16 2008 Mike Strosaker <strosake at austin.ibm.com> 1.0.1
- Create /var/lib/servicelog/servicelog.db at install time
- Additional comments and code cleanup
- Fix issue with notification tools not being started
- Beautify printing of notification tools

* Tue Mar 04 2008 Mike Strosaker <strosake at austin.ibm.com> 1.0.0
- Initial creation of the package
