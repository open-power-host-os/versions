%define milestone alpha
%if "%{milestone}"
%define milestone_tag .%{milestone}
%endif

Name: open-power-host-os
Version: 3.0
Release: 1%{?milestone_tag}%{dist}
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
Requires(post): kernel = 4.13.0-1.rc3.gitec0d270%{dist}
Requires: %{name}-container = %{version}-%{release}
Requires(post): container-selinux = 2:2.17-1%{dist}
Requires(post): docker = 2:1.12.6-6.gitae7d637%{dist}
Requires(post): docker-swarm = 1.1.0-1.gita0fd82b
Requires(post): flannel = 0.5.5-1.gitcb8284f%{dist}
Requires(post): kubernetes = 1.2.0-0.21.git4a3f9c5%{dist}
Requires(post): skopeo = 0.1.20-1.gite802625%{dist}
Requires: %{name}-virt = %{version}-%{release}
Requires(post): SLOF = 20170303-3.gitc39657a%{dist}
Requires(post): libvirt = 3.2.0-3.gitf81f00f%{dist}
Requires(post): qemu = 15:2.9.0-5.git4cfb657%{dist}
Requires: %{name}-virt-management = %{version}-%{release}
Requires(post): novnc = 0.5.1-5.gitfc00821%{dist}
Requires(post): ginger = 2.3.0-17.gite9b8a1b%{dist}
Requires(post): ginger-base = 2.2.1-13.git109815c%{dist}
Requires(post): kimchi = 2.3.0-17.git3830c25%{dist}
Requires(post): wok = 2.3.0-15.git7f5e0ae%{dist}
Requires: %{name}-ras = %{version}-%{release}
Requires(post): crash = 7.1.6-1.git64531dc%{dist}
Requires(post): hwdata = 0.288-1.git625a119%{dist}
Requires(post): libnl3 = 3.2.28-4%{dist}
Requires(post): librtas = 1.4.1-2.git3fe4911%{dist}
Requires(post): libservicelog = 1.1.16-2.git48875ee%{dist}
Requires(post): libvpd = 2.2.5-4.git8cb3fe0%{dist}
Requires(post): lshw = B.02.18-1.gitf9bdcc3
Requires(post): lsvpd = 1.7.7-6.git3a5f5e1%{dist}
Requires(post): ppc64-diag = 2.7.2-1.gitd56f7f1%{dist}
Requires(post): servicelog = 1.1.14-4.git7d33cd3%{dist}
Requires(post): sos = 3.3-18.git52dd1db%{dist}
Requires(post): systemtap = 3.1-3.git39b62b4%{dist}

Requires(post): gcc = 4.8.5-13.svn240558%{dist}
Requires(post): golang-github-russross-blackfriday = 1:1.2-6.git5f33e7b%{dist}
Requires(post): golang-github-shurcooL-sanitized_anchor_name = 1:0-1.git1dba4b3%{dist}
Requires(post): golang = 1.7.1-3%{dist}

%description all
%{summary}


%package base

Summary: OpenPOWER Host OS basic packages

Requires: %{name}-release = %{version}-%{release}

Requires(post): kernel = 4.13.0-1.rc3.gitec0d270%{dist}

%description base
%{summary}


%package container

Summary: OpenPOWER Host OS container packages

Requires: %{name}-base = %{version}-%{release}
Requires(post): kernel = 4.13.0-1.rc3.gitec0d270%{dist}

Requires(post): container-selinux = 2:2.17-1%{dist}
Requires(post): docker = 2:1.12.6-6.gitae7d637%{dist}
Requires(post): docker-swarm = 1.1.0-1.gita0fd82b
Requires(post): flannel = 0.5.5-1.gitcb8284f%{dist}
Requires(post): kubernetes = 1.2.0-0.21.git4a3f9c5%{dist}
Requires(post): skopeo = 0.1.20-1.gite802625%{dist}

%description container
%{summary}


%package virt

Summary: OpenPOWER Host OS hypervisor packages

Requires: %{name}-base = %{version}-%{release}
Requires(post): kernel = 4.13.0-1.rc3.gitec0d270%{dist}

Requires(post): SLOF = 20170303-3.gitc39657a%{dist}
Requires(post): libvirt = 3.2.0-3.gitf81f00f%{dist}
Requires(post): qemu = 15:2.9.0-5.git4cfb657%{dist}

%description virt
%{summary}


%package virt-management

Summary: OpenPOWER Host OS hypervisor management packages

Requires: %{name}-base = %{version}-%{release}
Requires(post): kernel = 4.13.0-1.rc3.gitec0d270%{dist}
Requires: %{name}-virt = %{version}-%{release}
Requires(post): SLOF = 20170303-3.gitc39657a%{dist}
Requires(post): libvirt = 3.2.0-3.gitf81f00f%{dist}
Requires(post): qemu = 15:2.9.0-5.git4cfb657%{dist}

Requires(post): novnc = 0.5.1-5.gitfc00821%{dist}
Requires(post): ginger = 2.3.0-17.gite9b8a1b%{dist}
Requires(post): ginger-base = 2.2.1-13.git109815c%{dist}
Requires(post): kimchi = 2.3.0-17.git3830c25%{dist}
Requires(post): wok = 2.3.0-15.git7f5e0ae%{dist}

%description virt-management
%{summary}


%package ras

Summary: OpenPOWER Host OS RAS (Reliability Availability Serviceability) packages

Requires: %{name}-base = %{version}-%{release}
Requires(post): kernel = 4.13.0-1.rc3.gitec0d270%{dist}

Requires(post): crash = 7.1.6-1.git64531dc%{dist}
Requires(post): hwdata = 0.288-1.git625a119%{dist}
Requires(post): libnl3 = 3.2.28-4%{dist}
Requires(post): librtas = 1.4.1-2.git3fe4911%{dist}
Requires(post): libservicelog = 1.1.16-2.git48875ee%{dist}
Requires(post): libvpd = 2.2.5-4.git8cb3fe0%{dist}
Requires(post): lshw = B.02.18-1.gitf9bdcc3
Requires(post): lsvpd = 1.7.7-6.git3a5f5e1%{dist}
Requires(post): ppc64-diag = 2.7.2-1.gitd56f7f1%{dist}
Requires(post): servicelog = 1.1.14-4.git7d33cd3%{dist}
Requires(post): sos = 3.3-18.git52dd1db%{dist}
Requires(post): systemtap = 3.1-3.git39b62b4%{dist}

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
HOST_OS_RELEASE_TEXT="OpenPOWER Host OS $VERSION_STRING ($BUILD_TIMESTAMP)\n"
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
%files container
%files virt
%files virt-management
%files ras


%changelog
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
