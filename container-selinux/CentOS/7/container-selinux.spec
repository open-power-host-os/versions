%global debug_package   %{nil}

# container-selinux
%global git0 https://github.com/projectatomic/container-selinux
%if 0%{?fedora}
%global commit0 ed3082b4d72740d197f4680749347ca507fc1203
%else
# use upstream's RHEL-1.12 branch for CentOS 7
%global commit0 %{?git_commit_id}
%endif
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

# container-selinux stuff (prefix with ds_ for version/release etc.)
# Some bits borrowed from the openstack-selinux package
%global selinuxtype targeted
%global moduletype services
%global modulenames container

# Usage: _format var format
# Expand 'modulenames' into various formats as needed
# Format must contain '$x' somewhere to do anything useful
%global _format() export %1=""; for x in %{modulenames}; do %1+=%2; %1+=" "; done;

# Relabel files
%global relabel_files() %{_sbindir}/restorecon -R %{_bindir}/docker* %{_localstatedir}/run/containerd.sock %{_localstatedir}/run/docker.sock %{_localstatedir}/run/docker.pid %{_sysconfdir}/docker %{_localstatedir}/log/docker %{_localstatedir}/log/lxc %{_localstatedir}/lock/lxc %{_unitdir}/docker.service %{_unitdir}/docker-containerd.service %{_unitdir}/docker-latest.service %{_unitdir}/docker-latest-containerd.service %{_sysconfdir}/docker %{_libexecdir}/docker* &> /dev/null || :

# Version of SELinux we were using
%if 0%{?fedora} >= 22
%global selinux_policyver 3.13.1-220
%else
%global selinux_policyver 3.13.1-39
%endif

Name: container-selinux
%if 0%{?fedora} || 0%{?centos}
Epoch: 2
%endif
Version: 2.17
Release: 3%{?extraver}%{?dist}
License: GPLv2
URL: %{git0}
Summary: SELinux policies for container runtimes
Source0: %{name}.tar.gz
BuildArch: noarch
BuildRequires: git
BuildRequires: pkgconfig(systemd)
BuildRequires: selinux-policy >= %{selinux_policyver}
BuildRequires: selinux-policy-devel >= %{selinux_policyver}
# RE: rhbz#1195804 - ensure min NVR for selinux-policy
Requires: selinux-policy >= %{selinux_policyver}
Requires(post): selinux-policy-base >= %{selinux_policyver}
Requires(post): selinux-policy-targeted >= %{selinux_policyver}
Requires(post): policycoreutils
%if 0%{?fedora}
Requires(post): policycoreutils-python-utils
%else
Requires(post): policycoreutils-python
%endif
Requires(post): libselinux-utils
Obsoletes: %{name} <= 2:1.12.5-13
Obsoletes: docker-selinux <= 2:1.12.4-28
Provides: docker-selinux = %{epoch}:%{version}-%{release}

%description
SELinux policy modules for use with container runtimes.

%prep  -q -n %{name}
%autosetup -Sgit -n %{name}

%build
make

%install
# install policy modules
%_format MODULES $x.pp.bz2
install -d %{buildroot}%{_datadir}/selinux/packages
install -d -p %{buildroot}%{_datadir}/selinux/devel/include/services
install -p -m 644 container.if %{buildroot}%{_datadir}/selinux/devel/include/services
install -m 0644 $MODULES %{buildroot}%{_datadir}/selinux/packages

# remove spec file
rm -rf container-selinux.spec

%check

%post
# Install all modules in a single transaction
if [ $1 -eq 1 ]; then
    %{_sbindir}/setsebool -P -N virt_use_nfs=1 virt_sandbox_use_all_caps=1
fi
%_format MODULES %{_datadir}/selinux/packages/$x.pp.bz2
%{_sbindir}/semodule -n -s %{selinuxtype} -r container 2> /dev/null
%{_sbindir}/semodule -n -s %{selinuxtype} -d docker 2> /dev/null
%{_sbindir}/semodule -n -s %{selinuxtype} -d gear 2> /dev/null
%{_sbindir}/semodule -n -X 200 -s %{selinuxtype} -i $MODULES > /dev/null
if %{_sbindir}/selinuxenabled ; then
    %{_sbindir}/load_policy
    %relabel_files
    if [ $1 -eq 1 ]; then
	restorecon -R %{_sharedstatedir}/docker &> /dev/null || :
    fi
fi

%postun
if [ $1 -eq 0 ]; then
%{_sbindir}/semodule -n -r %{modulenames} docker &> /dev/null || :
if %{_sbindir}/selinuxenabled ; then
%{_sbindir}/load_policy
%relabel_files
fi
fi

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%files
%doc README.md
%{_datadir}/selinux/*

%changelog
* Mon Aug 14 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 2:2.17-3
- Bump release

* Mon Aug 07 2017 Fabiano Rosas <farosas@linux.vnet.ibm.com> - 2:2.17-2
- Add extraver macro to Release field

* Mon Jun 5 2017 Dan Walsh <dwalsh@fedoraproject.org> - 2.17-1
- Revert change to run the container_runtime as ranged

* Thu Jun 1 2017 Dan Walsh <dwalsh@fedoraproject.org> - 2.16-1
- Add default labeling for cri-o in /etc/crio directories

* Wed May 31 2017 Dan Walsh <dwalsh@fedoraproject.org> - 2.15-1
- Allow container types to read/write container_runtime fifo files
- Allow a container runtime to mount on top of its own /proc

* Fri May 19 2017 Dan Walsh <dwalsh@fedoraproject.org> - 2.14-1
- Add labels for crio rename
- Break container_t rules out to use a separate container_domain
- Allow containers to be able to set namespaced SYCTLS
- Allow sandbox containers manage fuse files.
- Fixes to make container_runtimes work on MLS machines
- Bump version to allow handling of container_file_t filesystems
- Allow containers to mount, remount and umount container_file_t file systems
- Fixes to handle cap_userns
- Give container_t access to XFRM sockets
- Allow spc_t to dbus chat with init system
- Allow spc_t to dbus chat with init system
- Add rules to allow container runtimes to run with unconfined disabled
- Add rules to support cgroup file systems mounted into container.
- Fix typebounds entrypoint problems
- Fix typebounds problems
- Add typebounds statement for container_t from container_runtime_t
- We should only label runc not runc*

* Tue Feb 28 2017 Dan Walsh <dwalsh@fedoraproject.org> - 2.10-1
- Add rules to allow container runtimes to run with unconfined disabled
- Add rules to support cgroup file systems mounted into container.

* Mon Feb 13 2017 Dan Walsh <dwalsh@fedoraproject.org> - 2.9-1
- Add rules to allow container_runtimes to run with unconfined disabled

* Thu Feb 9 2017 Dan Walsh <dwalsh@fedoraproject.org> - 2:8.1-1
- Allow container_file_t to be stored on cgroup_t file systems

* Tue Feb 7 2017 Dan Walsh <dwalsh@fedoraproject.org> - 2:7.1-1
- Fix type in container interface file

* Mon Feb 6 2017 Dan Walsh <dwalsh@fedoraproject.org> - 2:6.1-1
- Fix typebounds entrypoint problems

* Fri Jan 27 2017 Dan Walsh <dwalsh@fedoraproject.org> - 2:5.1-1
- Fix typebounds problems

* Thu Jan 19 2017 Dan Walsh <dwalsh@fedoraproject.org> - 2:4.1-1
- Add typebounds statement for container_t from container_runtime_t
- We should only label runc not runc*

* Tue Jan 17 2017 Dan Walsh <dwalsh@fedoraproject.org> - 2:3.1-1
- Fix labeling on /usr/bin/runc.*
- Add sandbox_net_domain access to container.te
- Remove containers ability to look at /etc content

* Wed Jan 11 2017 Lokesh Mandvekar <lsm5@fedoraproject.org> - 2:2.2-4
- use upstream's RHEL-1.12 branch, commit 56c32da for CentOS 7

* Tue Jan 10 2017 Jonathan Lebon <jlebon@redhat.com> - 2:2.2-3
- properly disable docker module in %post

* Sat Jan 07 2017 Lokesh Mandvekar <lsm5@fedoraproject.org> - 2:2.2-2
- depend on selinux-policy-targeted
- relabel docker-latest* files as well

* Fri Jan 06 2017 Lokesh Mandvekar <lsm5@fedoraproject.org> - 2:2.2-1
- bump to v2.2
- additional labeling for ocid

* Fri Jan 06 2017 Lokesh Mandvekar <lsm5@fedoraproject.org> - 2:2.0-2
- install policy at level 200
- From: Dan Walsh <dwalsh@redhat.com>

* Fri Jan 06 2017 Lokesh Mandvekar <lsm5@fedoraproject.org> - 2:2.0-1
- Resolves: #1406517 - bump to v2.0 (first upload to Fedora as a
standalone package)
- include projectatomic/RHEL-1.12 branch commit for building on centos/rhel

* Mon Dec 19 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 2:1.12.4-29
- new package (separated from docker)
