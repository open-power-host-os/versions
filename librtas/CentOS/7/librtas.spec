%global commit          %{?git_commit_id}
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitcommittag    .git%{shortcommit}

Summary: Libraries to provide access to RTAS calls and RTAS events.
Name: librtas
Version: 1.4.1
Release: 4%{?extraver}%{gitcommittag}%{?dist}
License: GNU Lesser General Public License (LGPL)
Source:  %{name}.tar.gz
Group: System Environment/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)


%description
The librtas shared library provides userspace with an interface
through which certain RTAS calls can be made.  The library uses
either of the RTAS User Module or the RTAS system call to direct
the kernel in making these calls.

The librtasevent shared library provides users with a set of
definitions and common routines useful in parsing and dumping
the contents of RTAS events.

%package devel
Summary:  C header files for development with librtas
Group:    Development/Libraries
Requires: %{name} = %{version}-%{release}

%description devel
The librtas-devel packages contains the header files necessary for
developing programs using librtas.

%prep
%setup -q -n %{name}

%build
%{__make} %{?_smp_mflags}

%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__make} install DESTDIR=$RPM_BUILD_ROOT


%files
%defattr(-, root, root)
%{_docdir}/packages/%{name}/COPYING.LESSER
%{_docdir}/packages/%{name}/README
%{_libdir}/librtas.so.%{version}
%{_libdir}/librtasevent.so.%{version}

%files devel
%defattr(-, root, root, -)
%{_includedir}/librtas.h
%{_libdir}/librtas.so
%{_libdir}/librtas.so.1
%{_libdir}/librtasevent.so
%{_libdir}/librtasevent.so.1
%{_includedir}/librtasevent.h
%{_includedir}/librtasevent_v4.h
%{_includedir}/librtasevent_v6.h


%post
# Post-install script -------------------------------------------------
ln -sf %{_libdir}/librtas.so.%{version} %{_libdir}/librtas.so
ln -sf %{_libdir}/librtas.so.%{version} %{_libdir}/librtas.so.1
ln -sf %{_libdir}/librtasevent.so.%{version} %{_libdir}/librtasevent.so
ldconfig

%postun
# Post-uninstall script -----------------------------------------------
if [ "$1" = "0" ] ; then        # last uninstall
    rm -f %{_libdir}/librtas.so
    rm -f %{_libdir}/librtasevent.so
fi
ldconfig

%changelog
* Mon Aug 14 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 1.4.1-4.git
- Bump release

* Mon Aug 07 2017 Fabiano Rosas <farosas@linux.vnet.ibm.com> - 1.4.1-3.git
- Add extraver macro to Release field

* Thu Nov 3 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 1.4.1-2
- added changelog section
- spec cleanup
