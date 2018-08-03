%define milestone alpha
%if "%{milestone}"
%define milestone_tag .%{milestone}
%endif

Name: open-power-host-os
Version: 3.5
Release: 22%{?milestone_tag}%{dist}
Summary: OpenPOWER Host OS metapackages
Group: System Environment/Base
License: GPLv3
BuildArch: noarch

%description
%{summary}


%package release

Summary: OpenPOWER Host OS release

Source0: open-power-host-os-smt.service
Source1: 90-open-power-host-os-default.preset

Requires: centos-release >= 7
Requires: epel-release >= 7

# openvswitch selinux issue
# https://github.com/open-power-host-os/builds/issues/226
Source1001: hostos-openvswitch.te
Requires(pre): policycoreutils
Requires(pre): coreutils
Requires(pre): selinux-policy
Requires(pre): selinux-policy-targeted
BuildRequires: checkpolicy
BuildRequires: policycoreutils-python


%description release
%{summary}


# The OpenPOWER Host OS packages need to require the transitive dependencies
# to force the correct versions of packages to be present on reinstallation,
# since the post section of the subpackages that are already installed will
# not be executed in this case.

%package all

Summary: OpenPOWER Host OS full package set

Requires: %{name}-base = %{version}-%{release}
Requires(post): kernel = 4.16.0-2%{?extraver}.git5ed4ce3%{dist}
Requires: %{name}-virt = %{version}-%{release}
Requires(post): SLOF = 20171214-2%{?extraver}.gitc2a331f%{dist}
Requires(post): libvirt = 4.2.0-2%{?extraver}.gitbf217de%{dist}
Requires(post): qemu = 15:2.11.91-1%{?extraver}.git46a0689%{dist}
Requires: %{name}-ras = %{version}-%{release}
Requires(post): crash
Requires(post): hwdata = 0.288-3%{?extraver}.git625a119%{dist}
Requires(post): lshw
Requires(post): opal-firmware
Requires(post): opal-prd
Requires(post): opal-utils
Requires(post): ppc64-diag = 2.7.4-3%{?extraver}.git608507e%{dist}
Requires(post): sos


%description all
%{summary}


%package base

Summary: OpenPOWER Host OS basic packages

Requires: %{name}-release = %{version}-%{release}

Requires(post): kernel = 4.16.0-2%{?extraver}.git5ed4ce3%{dist}

Obsoletes: open-power-host-os-virt-management < 3.0-7

%description base
%{summary}


%package virt

Summary: OpenPOWER Host OS hypervisor packages

Requires: %{name}-base = %{version}-%{release}
Requires(post): kernel = 4.16.0-2%{?extraver}.git5ed4ce3%{dist}

Requires(post): SLOF = 20171214-2%{?extraver}.gitc2a331f%{dist}
Requires(post): libvirt = 4.2.0-2%{?extraver}.gitbf217de%{dist}
Requires(post): qemu = 15:2.11.91-1%{?extraver}.git46a0689%{dist}

%description virt
%{summary}


%package ras

Summary: OpenPOWER Host OS RAS (Reliability Availability Serviceability) packages

Requires: %{name}-base = %{version}-%{release}
Requires(post): kernel = 4.16.0-2%{?extraver}.git5ed4ce3%{dist}

Requires(post): crash
Requires(post): hwdata = 0.288-3%{?extraver}.git625a119%{dist}
Requires(post): lshw
Requires(post): opal-firmware
Requires(post): opal-prd
Requires(post): opal-utils
Requires(post): ppc64-diag = 2.7.4-3%{?extraver}.git608507e%{dist}
Requires(post): sos

%description ras
%{summary}


%prep
install -pm 644 %{SOURCE0} .
install -pm 644 %{SOURCE1} .

%build

# build openvswitch selinux policy
checkmodule -M -m -o hostos-openvswitch.mod %{SOURCE1001}
semodule_package -o hostos-openvswitch.pp -m hostos-openvswitch.mod

%install
rm -rf $RPM_BUILD_ROOT

# install openvswitch selinux policy
%{__mkdir_p} %{buildroot}%{_sysconfdir}/selinux/open-power-host-os
%{__cp} -f %{SOURCE1001} %{buildroot}%{_sysconfdir}/selinux/open-power-host-os/
%{__cp} -f hostos-openvswitch.{mod,pp} %{buildroot}%{_sysconfdir}/selinux/open-power-host-os/

BUILD_TIMESTAMP=$(date +"%Y-%m-%d")
VERSION_STRING=%{version}-%{milestone}
HOST_OS_RELEASE_TEXT="OpenPOWER Host OS $VERSION_STRING ($BUILD_TIMESTAMP)"
echo $HOST_OS_RELEASE_TEXT > open-power-host-os-release

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}
install -pm 444 open-power-host-os-release \
        $RPM_BUILD_ROOT%{_sysconfdir}/open-power-host-os-release

%{__mkdir_p} %{buildroot}%{_prefix}/lib/systemd/system/
%{__cp} %{SOURCE0} %{buildroot}%{_prefix}/lib/systemd/system/

%{__mkdir_p} %{buildroot}%{_prefix}/lib/systemd/system-preset/
%{__cp} %{SOURCE1} %{buildroot}%{_prefix}/lib/systemd/system-preset/


%post release

# load openvswitch selinux policy
semodule -i %{_sysconfdir}/selinux/open-power-host-os/hostos-openvswitch.pp >/tmp/hostos-openvswitch.log 2>&1 || :

%clean
rm -rf $RPM_BUILD_ROOT


%files release
%defattr(-, root, root, -)
%attr(0444, root, root) %{_sysconfdir}/open-power-host-os-release
%attr(0644, root, root) %{_sysconfdir}/selinux/open-power-host-os/hostos-openvswitch.te
%attr(0644, root, root) %{_sysconfdir}/selinux/open-power-host-os/hostos-openvswitch.mod
%attr(0644, root, root) %{_sysconfdir}/selinux/open-power-host-os/hostos-openvswitch.pp

%attr(0644, root, root) %{_prefix}/lib/systemd/system/open-power-host-os-smt.service
%attr(0644, root, root) %{_prefix}/lib/systemd/system-preset/90-open-power-host-os-default.preset

%files all
%files base
%files virt
%files ras


%changelog
* Thu May 31 2018 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 3.5-22.alpha
- Update package dependencies

* Fri May 25 2018 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 3.5-21.alpha
- Update package dependencies

* Thu May 17 2018 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 3.5-20.alpha
- Update package dependencies

* Wed May 16 2018 Fabiano Rosas <farosas@linux.ibm.com> - 3.5-19.alpha
- Update package dependencies

* Wed May 16 2018 Fabiano Rosas <farosas@linux.ibm.com> - 3.5-18.alpha
- Use systemtap from the base distro

* Tue May 15 2018 Fabiano Rosas <farosas@linux.ibm.com> - 3.5-17.alpha
- Update package dependencies

* Wed Apr 04 2018 Fabiano Rosas <farosas@linux.ibm.com> - 3.5-16.alpha
- Update package dependencies

* Wed Apr 04 2018 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 3.5-15.alpha
- Update package dependencies

* Wed Mar 14 2018 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 3.5-14.alpha
- Update package dependencies

* Tue Mar 13 2018 Fabiano Rosas <farosas@linux.vnet.ibm.com> - 3.5-13.alpha
- Stop using custom gcc package

* Mon Mar 05 2018 Fabiano Rosas <farosas@linux.vnet.ibm.com> - 3.5-12.alpha
- Update package dependencies

* Thu Mar 01 2018 Fabiano Rosas <farosas@linux.vnet.ibm.com> - 3.5-11.alpha
- Include opal-* packages

* Wed Feb 14 2018 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 3.5-10.alpha
- Update package dependencies

* Fri Feb 02 2018 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 3.5-9.alpha
- Update package dependencies

* Sun Jan 21 2018 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 3.5-8.alpha
- Update package dependencies

* Thu Jan 18 2018 Murilo Opsfelder Araújo <muriloo@linux.vnet.ibm.com> - 3.5-7.alpha
- Remove libnl3 from dependencies

* Tue Dec 19 2017 Murilo Opsfelder Araújo <muriloo@linux.vnet.ibm.com> - 3.5-6.alpha
- Update package dependencies

* Tue Dec 19 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 3.5-5.alpha
- Update package dependencies

* Fri Dec 08 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 3.5-4.alpha
- Update package dependencies

* Wed Nov 22 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 3.5-3.alpha
- Update package dependencies

* Tue Oct 31 2017 Murilo Opsfelder Araujo <muriloo@linux.vnet.ibm.com> - 3.5-2.alpha
- Update deps to systemtap 3.2

* Sat Oct 07 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 3.5-1.alpha
- Update package dependencies

* Fri Sep 29 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 3.0-20.alpha
- Update package dependencies

* Thu Sep 28 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 3.0-19.alpha
- Update package dependencies

* Mon Sep 25 2017 Fabiano Rosas <farosas@linux.vnet.ibm.com> - 3.0-18.alpha
- Update package dependencies

* Sat Sep 23 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 3.0-17.alpha
- Update package dependencies

* Thu Sep 21 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 3.0-16.alpha
- Update package dependencies

* Thu Sep 21 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 3.0-15.alpha
- Update package dependencies

* Thu Sep 21 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 3.0-14.alpha
- Update package dependencies

* Mon Sep 18 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 3.0-13.alpha
- Remove librtas dependency
- Bump servicelog release

* Fri Aug 25 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 3.0-12.alpha
- Fix open-power-host-os-virt-management obsoleted version

* Fri Aug 25 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 3.0-11.alpha
- Update package dependencies

* Wed Aug 23 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 3.0-10.alpha
- Update package dependencies

* Tue Aug 22 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 3.0-9.alpha
- Obsolete open-power-host-os-virt-management

* Tue Aug 22 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 3.0-8.alpha
- Remove extraver macro

* Tue Aug 22 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 3.0-7.alpha
- Update package dependencies

* Tue Aug 15 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 3.0-6.alpha
- Remove virt-management subpackage

* Mon Aug 14 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 3.0-5.alpha
- Update package dependencies

* Thu Aug 10 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 3.0-4.alpha
- Update package dependencies

* Tue Aug 08 2017 Fabiano Rosas <farosas@linux.vnet.ibm.com> - 3.0-3.alpha
- Update package dependencies

* Mon Aug 07 2017 Fabiano Rosas <farosas@linux.vnet.ibm.com> - 3.0-2.alpha
- Add extraver macro to Release field

* Wed Aug 02 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 3.0-1.alpha
- Update package dependencies

* Wed Jul 12 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.5-17
- Update package dependencies

* Thu Jul 06 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 2.5-16.alpha
- Update package dependencies

* Thu Jun 29 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.5-15.alpha
- Update package dependencies

* Wed Jun 14 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.5-14.alpha
- Update package dependencies

* Wed Jun 07 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.5-13.alpha
- Update package dependencies

* Tue Jun 06 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 2.5-12.alpha
- Update package dependencies

* Thu Jun 01 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.5-11.alpha
- Update package dependencies

* Wed May 24 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.5-10.alpha
- Update package dependencies

* Wed May 17 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.5-9.alpha
- Update package dependencies

* Wed May 10 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.5-8.alpha
- Update package dependencies

* Wed May 03 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.5-7.alpha
- Update package dependencies

* Wed Apr 26 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.5-6.alpha
- Update package dependencies

* Thu Apr 20 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.5-5.alpha
- Update package dependencies

* Wed Apr 12 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.5-4.alpha
- Update package dependencies

* Wed Apr 05 2017 Fabiano Rosas <farosas@linux.vnet.ibm.com> - 2.5-3.alpha
- Fix installation of open-power-host-os-smt files

* Wed Apr 05 2017 Murilo Opsfelder Araújo <muriloo@linux.vnet.ibm.com> - 2.5-2.alpha
- Update package dependencies for SELinux (https://github.com/open-power-host-os/builds/issues/226)

* Wed Apr 05 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.5-1.alpha
- Update package dependencies

* Fri Mar 31 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.0-9
- Update package dependencies

* Fri Mar 31 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.0-8.beta
- Update package dependencies

* Wed Mar 29 2017 Murilo Opsfelder Araújo <muriloo@linux.vnet.ibm.com> 2.0-7.beta
- Add selinux policy to allow openvswitch generic netlink socket
- Fix https://github.com/open-power-host-os/builds/issues/226

* Wed Mar 29 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.0-6.beta
- Update package dependencies

* Wed Mar 29 2017 Lucas Tadeu Teixeira <ltadeu@br.ibm.com> 2.0-5.alpha
- Add systemd service to disable SMT

* Fri Mar 24 2017 Olav Philipp Henschel  <olavph@linux.vnet.ibm.com> - 2.0-4.alpha
- Explicitly mention transitive dependencies. This forces the packages versions
  to match when reinstalling a package group.

* Thu Mar 23 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.0-3.alpha
- Update package dependencies

* Wed Mar 15 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.0-2.alpha
- Update package dependencies

* Wed Mar 08 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.0-1.alpha
- Update package dependencies

* Mon Mar 06 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> 2.0-1.alpha
- Create release file and package groups
