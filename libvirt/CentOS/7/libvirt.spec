%global commit          %{?git_commit_id}
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitcommittag    .git%{shortcommit}

# The tests are disabled by default.
# Set --with tests or bcond_without to run tests.
%bcond_with tests

# -*- rpm-spec -*-

# This spec file assumes you are building on a Fedora or RHEL version
# that's still supported by the vendor: that means Fedora 23 or newer,
# or RHEL 6 or newer. It may need some tweaks for other distros.
# If neither fedora nor rhel was defined, try to guess them from dist
%if (0%{?fedora} && 0%{?fedora} >= 23) || (0%{?rhel} && 0%{?rhel} >= 6)
    %define supported_platform 1
%else
    %define supported_platform 0
%endif

# Default to skipping autoreconf.  Distros can change just this one line
# (or provide a command-line override) if they backport any patches that
# touch configure.ac or Makefile.am.
%{!?enable_autotools:%global enable_autotools 1}


# The hypervisor drivers that run in libvirtd
%define with_xen           0%{!?_without_xen:1}
%define with_qemu          0%{!?_without_qemu:1}
%define with_lxc           0%{!?_without_lxc:1}
%define with_uml           0%{!?_without_uml:1}
%define with_libxl         0%{!?_without_libxl:1}
%define with_vbox          0%{!?_without_vbox:1}

%define with_qemu_tcg      %{with_qemu}

%define qemu_kvm_arches %{ix86} x86_64 ppc64le

%if 0%{?fedora}
    %define qemu_kvm_arches %{ix86} x86_64 %{power64} s390x %{arm} aarch64 ppc64le
%endif

%if 0%{?rhel}
    %define with_qemu_tcg 0
    %define qemu_kvm_arches x86_64
    %if 0%{?rhel} >= 7
        %define qemu_kvm_arches x86_64 %{power64} aarch64 ppc64le
    %endif
%endif

%ifarch %{qemu_kvm_arches}
    %define with_qemu_kvm      %{with_qemu}
%else
    %define with_qemu_kvm      0
%endif

%if ! %{with_qemu_tcg} && ! %{with_qemu_kvm}
    %define with_qemu 0
%endif

# Then the hypervisor drivers that run outside libvirtd, in libvirt.so
%define with_openvz        0%{!?_without_openvz:1}
%define with_vmware        0%{!?_without_vmware:1}
%define with_phyp          0%{!?_without_phyp:1}
%define with_esx           0%{!?_without_esx:1}
%define with_hyperv        0%{!?_without_hyperv:1}

# Then the secondary host drivers, which run inside libvirtd
%if 0%{?fedora} || 0%{?rhel} >= 7
    %define with_storage_rbd      0%{!?_without_storage_rbd:1}
%else
    %define with_storage_rbd      0
%endif
%if 0%{?fedora}
    %define with_storage_sheepdog 0%{!?_without_storage_sheepdog:1}
%else
    %define with_storage_sheepdog 0
%endif
%define with_storage_gluster 0%{!?_without_storage_gluster:1}
%define with_numactl          0%{!?_without_numactl:1}

# F25+ has zfs-fuse
%if 0%{?fedora} >= 25
    %define with_storage_zfs      0%{!?_without_storage_zfs:1}
%else
    %define with_storage_zfs      0
%endif

# A few optional bits off by default, we enable later
%define with_fuse          0%{!?_without_fuse:0}
%define with_cgconfig      0%{!?_without_cgconfig:0}
%define with_sanlock       0%{!?_without_sanlock:0}
%define with_systemd       0%{!?_without_systemd:0}
%define with_numad         0%{!?_without_numad:0}
%define with_firewalld     0%{!?_without_firewalld:0}
%define with_libssh2       0%{!?_without_libssh2:0}
%define with_wireshark     0%{!?_without_wireshark:0}
%define with_libssh        0%{!?_without_libssh:0}
%define with_pm_utils      1

# Finally set the OS / architecture specific special cases

# Xen is available only on i386 x86_64 ia64
%ifnarch %{ix86} x86_64 ia64
    %define with_xen 0
    %define with_libxl 0
%endif

# vbox is available only on i386 x86_64
%ifnarch %{ix86} x86_64
    %define with_vbox 0
%endif

# Numactl is not available on s390[x] and ARM
%ifarch s390 s390x %{arm}
    %define with_numactl 0
%endif

# libgfapi is built only on x86_64 on rhel
%ifnarch x86_64
    %if 0%{?rhel}
        %define with_storage_gluster 0
    %endif
%endif

# librados and librbd are built only on x86_64 on rhel
%ifnarch x86_64
    %if 0%{?rhel} >= 7
        %define with_storage_rbd 0
    %endif
%endif

# zfs-fuse is not available on some architectures
%ifarch s390 s390x aarch64
    %define with_storage_zfs 0
%endif


# RHEL doesn't ship OpenVZ, VBox, UML, PowerHypervisor,
# VMware, libxenserver (xenapi), libxenlight (Xen 4.1 and newer),
# or HyperV.
%if 0%{?rhel}
    %define with_openvz 0
    %define with_vbox 0
    %define with_uml 0
    %define with_phyp 0
    %define with_vmware 0
    %define with_xenapi 0
    %define with_libxl 0
    %define with_hyperv 0
    %define with_vz 0
%endif

# Fedora 17 / RHEL-7 are first where we use systemd. Although earlier
# Fedora has systemd, libvirt still used sysvinit there.
%if 0%{?fedora} || 0%{?rhel} >= 7
    %define with_systemd 1
    %define with_pm_utils 0
%endif

# Fedora 18 / RHEL-7 are first where firewalld support is enabled
%if 0%{?fedora} || 0%{?rhel} >= 7
    %define with_firewalld 1
%endif

# RHEL-6 stopped including Xen on all archs.
%if 0%{?rhel}
    %define with_xen 0
%endif

# fuse is used to provide virtualized /proc for LXC
%if 0%{?fedora} || 0%{?rhel} >= 7
    %define with_fuse      0%{!?_without_fuse:1}
%endif

# Enable sanlock library for lock management with QEMU
# Sanlock is available only on arches where kvm is available for RHEL
%if 0%{?fedora}
    %define with_sanlock 0%{!?_without_sanlock:1}
%endif
%if 0%{?rhel}
    %ifarch %{qemu_kvm_arches}
        %define with_sanlock 0%{!?_without_sanlock:1}
    %endif
%endif

# Enable libssh2 transport for new enough distros
%if 0%{?fedora}
    %define with_libssh2 0%{!?_without_libssh2:1}
%endif

# Enable wireshark plugins for all distros shipping libvirt 1.2.2 or newer
%if 0%{?fedora}
    %define with_wireshark 0%{!?_without_wireshark:1}
%endif

# Enable libssh transport for new enough distros
%if 0%{?fedora}
    %define with_libssh 0%{!?_without_libssh:1}
%endif


%if %{with_qemu} || %{with_lxc} || %{with_uml}
# numad is used to manage the CPU and memory placement dynamically,
# it's not available on s390[x] and ARM.
    %ifnarch s390 s390x %{arm}
        %define with_numad    0%{!?_without_numad:1}
    %endif
%endif

# Pull in cgroups config system
%if %{with_qemu} || %{with_lxc}
    %define with_cgconfig 0%{!?_without_cgconfig:1}
%endif

# Force QEMU to run as non-root
%define qemu_user  qemu
%define qemu_group  qemu


%if 0%{?fedora} || 0%{?rhel} >= 7
    %define with_systemd_macros 1
%else
    %define with_systemd_macros 0
%endif


# RHEL releases provide stable tool chains and so it is safe to turn
# compiler warning into errors without being worried about frequent
# changes in reported warnings
%if 0%{?rhel}
    %define enable_werror --enable-werror
%else
    %define enable_werror --disable-werror
%endif

%if 0%{?fedora} >= 25
    %define tls_priority "@LIBVIRT,SYSTEM"
%else
    %if 0%{?fedora}
        %define tls_priority "@SYSTEM"
    %else
        %define tls_priority "NORMAL"
    %endif
%endif


Summary: Library providing a simple virtualization API
Name: libvirt
Version: 4.0.0
Release: 2%{?extraver}%{gitcommittag}%{?dist}
License: LGPLv2+
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
URL: https://libvirt.org/

%if %(echo %{version} | grep -q "\.0$"; echo $?) == 1
    %define mainturl stable_updates/
%endif
Source: %{name}.tar.gz

Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-daemon-config-network = %{version}-%{release}
Requires: libvirt-daemon-config-nwfilter = %{version}-%{release}
%if %{with_libxl}
Requires: libvirt-daemon-driver-libxl = %{version}-%{release}
%endif
%if %{with_lxc}
Requires: libvirt-daemon-driver-lxc = %{version}-%{release}
%endif
%if %{with_qemu}
Requires: libvirt-daemon-driver-qemu = %{version}-%{release}
%endif
%if %{with_uml}
Requires: libvirt-daemon-driver-uml = %{version}-%{release}
%endif
%if %{with_xen}
Requires: libvirt-daemon-driver-xen = %{version}-%{release}
%endif
%if %{with_vbox}
Requires: libvirt-daemon-driver-vbox = %{version}-%{release}
%endif
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}

Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-client = %{version}-%{release}
Requires: libvirt-libs = %{version}-%{release}

# All build-time requirements. Run-time requirements are
# listed against each sub-RPM
%if 0%{?enable_autotools}
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: gettext-devel
BuildRequires: libtool
BuildRequires: /usr/bin/pod2man
%endif
BuildRequires: git
BuildRequires: perl
BuildRequires: python
%if %{with_systemd}
BuildRequires: systemd-units
%endif
%if %{with_xen} || %{with_libxl}
BuildRequires: xen-devel
%endif
BuildRequires: libxml2-devel
BuildRequires: xhtml1-dtds
BuildRequires: libxslt
BuildRequires: readline-devel
BuildRequires: ncurses-devel
BuildRequires: gettext
BuildRequires: libtasn1-devel
%if (0%{?rhel} && 0%{?rhel} < 7)
BuildRequires: libgcrypt-devel
%endif
BuildRequires: gnutls-devel
BuildRequires: libattr-devel
# For pool-build probing for existing pools
BuildRequires: libblkid-devel >= 2.17
# for augparse, optionally used in testing
BuildRequires: augeas
%if 0%{?fedora} || 0%{?rhel} >= 7
BuildRequires: systemd-devel >= 185
%else
BuildRequires: libudev-devel >= 145
%endif
BuildRequires: libpciaccess-devel >= 0.10.9
BuildRequires: yajl-devel
%if %{with_sanlock}
BuildRequires: sanlock-devel >= 2.4
%endif
BuildRequires: libpcap-devel
%if 0%{?rhel} && 0%{?rhel} < 7
BuildRequires: libnl-devel
%else
BuildRequires: libnl3-devel
%endif
BuildRequires: avahi-devel
BuildRequires: libselinux-devel
BuildRequires: dnsmasq >= 2.41
BuildRequires: iptables
%if 0%{?rhel} && 0%{?rhel} < 7
BuildRequires: iptables-ipv6
%endif
BuildRequires: radvd
BuildRequires: ebtables
BuildRequires: module-init-tools
BuildRequires: cyrus-sasl-devel
%if 0%{?fedora} || 0%{?rhel} >= 7
# F22 polkit-devel doesn't pull in polkit anymore, which we need for pkcheck
BuildRequires: polkit >= 0.112
BuildRequires: polkit-devel >= 0.112
%else
BuildRequires: polkit-devel >= 0.93
%endif
# For mount/umount in FS driver
BuildRequires: util-linux
%if %{with_qemu}
# For managing ACLs
BuildRequires: libacl-devel
# From QEMU RPMs
BuildRequires: /usr/bin/qemu-img
%else
    %if %{with_xen}
# From Xen RPMs
BuildRequires: /usr/sbin/qcow-create
    %endif
%endif
# For LVM drivers
BuildRequires: lvm2
# For ISCSI driver
BuildRequires: iscsi-initiator-utils
# For disk driver
BuildRequires: parted-devel
# For Multipath support
BuildRequires: device-mapper-devel
%if %{with_storage_rbd}
    %if 0%{?fedora} || 0%{?rhel} >= 7
BuildRequires: librados2-devel
BuildRequires: librbd1-devel
    %else
BuildRequires: ceph-devel
    %endif
%endif
%if %{with_storage_gluster}
BuildRequires: glusterfs-api-devel >= 3.4.1
BuildRequires: glusterfs-devel >= 3.4.1
%endif
%if %{with_storage_sheepdog}
BuildRequires: sheepdog
%endif
%if %{with_storage_zfs}
# Support any conforming implementation of zfs. On stock Fedora
# this is zfs-fuse, but could be zfsonlinux upstream RPMs
BuildRequires: /sbin/zfs
BuildRequires: /sbin/zpool
%endif
%if %{with_numactl}
# For QEMU/LXC numa info
BuildRequires: numactl-devel
%endif
BuildRequires: libcap-ng-devel >= 0.5.0
%if %{with_fuse}
BuildRequires: fuse-devel >= 2.8.6
%endif
%if %{with_phyp} || %{with_libssh2}
BuildRequires: libssh2-devel >= 1.3.0
%endif

%if 0%{?fedora} || 0%{?rhel} >= 7
BuildRequires: netcf-devel >= 0.2.2
%else
BuildRequires: netcf-devel >= 0.1.8
%endif
%if %{with_esx}
BuildRequires: libcurl-devel
%endif
%if %{with_hyperv}
BuildRequires: libwsman-devel >= 2.2.3
%endif
BuildRequires: audit-libs-devel
# we need /usr/sbin/dtrace
BuildRequires: systemtap-sdt-devel

# For mount/umount in FS driver
BuildRequires: util-linux
# For showmount in FS driver (netfs discovery)
BuildRequires: nfs-utils

# Communication with the firewall and polkit daemons use DBus
BuildRequires: dbus-devel

# Fedora build root suckage
BuildRequires: gawk

# For storage wiping with different algorithms
BuildRequires: scrub

%if %{with_numad}
BuildRequires: numad
%endif

%if %{with_wireshark}
    %if 0%{fedora} >= 24
BuildRequires: wireshark-devel >= 2.1.0
    %else
BuildRequires: wireshark-devel >= 1.12.1
    %endif
%endif

%if %{with_libssh}
BuildRequires: libssh-devel >= 0.7.0
%endif

Provides: bundled(gnulib)

%description
Libvirt is a C toolkit to interact with the virtualization capabilities
of recent versions of Linux (and other OSes). The main package includes
the libvirtd server exporting the virtualization support.

%package docs
Summary: API reference and website documentation
Group: Development/Libraries

%description docs
Includes the API reference for the libvirt C library, and a complete
copy of the libvirt.org website documentation.

%package daemon
Summary: Server side daemon and supporting files for libvirt library
Group: Development/Libraries

# All runtime requirements for the libvirt package (runtime requrements
# for subpackages are listed later in those subpackages)

# The client side, i.e. shared libs are in a subpackage
Requires: %{name}-libs = %{version}-%{release}

# for modprobe of pci devices
Requires: module-init-tools
# for /sbin/ip & /sbin/tc
Requires: iproute
Requires: avahi-libs
%if 0%{?fedora} || 0%{?rhel} >= 7
Requires: polkit >= 0.112
%else
Requires: polkit >= 0.93
%endif
%if %{with_cgconfig}
Requires: libcgroup
%endif
%ifarch %{ix86} x86_64 ia64
# For virConnectGetSysinfo
Requires: dmidecode
%endif
# For service management
%if %{with_systemd}
Requires(post): systemd-units
Requires(post): systemd-sysv
Requires(preun): systemd-units
Requires(postun): systemd-units
%endif
%if %{with_numad}
Requires: numad
%endif
# libvirtd depends on 'messagebus' service
Requires: dbus
# For uid creation during pre
Requires(pre): shadow-utils

%description daemon
Server side daemon required to manage the virtualization capabilities
of recent versions of Linux. Requires a hypervisor specific sub-RPM
for specific drivers.

%package daemon-config-network
Summary: Default configuration files for the libvirtd daemon
Group: Development/Libraries

Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}

%description daemon-config-network
Default configuration files for setting up NAT based networking

%package daemon-config-nwfilter
Summary: Network filter configuration files for the libvirtd daemon
Group: Development/Libraries

Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}

%description daemon-config-nwfilter
Network filter configuration files for cleaning guest traffic

%package daemon-driver-network
Summary: Network driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}
Requires: dnsmasq >= 2.41
Requires: radvd
Requires: iptables
%if 0%{?rhel} && 0%{?rhel} < 7
Requires: iptables-ipv6
%endif

%description daemon-driver-network
The network driver plugin for the libvirtd daemon, providing
an implementation of the virtual network APIs using the Linux
bridge capabilities.


%package daemon-driver-nwfilter
Summary: Nwfilter driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}
Requires: iptables
%if 0%{?rhel} && 0%{?rhel} < 7
Requires: iptables-ipv6
%endif
Requires: ebtables

%description daemon-driver-nwfilter
The nwfilter driver plugin for the libvirtd daemon, providing
an implementation of the firewall APIs using the ebtables,
iptables and ip6tables capabilities


%package daemon-driver-nodedev
Summary: Nodedev driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}
# needed for device enumeration
%if 0%{?fedora} || 0%{?rhel} >= 7
Requires: systemd >= 185
%else
Requires: udev >= 145
%endif

%description daemon-driver-nodedev
The nodedev driver plugin for the libvirtd daemon, providing
an implementation of the node device APIs using the udev
capabilities.


%package daemon-driver-interface
Summary: Interface driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}
%if (0%{?fedora} || 0%{?rhel} >= 7)
Requires: netcf-libs >= 0.2.2
%endif

%description daemon-driver-interface
The interface driver plugin for the libvirtd daemon, providing
an implementation of the network interface APIs using the
netcf library


%package daemon-driver-secret
Summary: Secret driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}

%description daemon-driver-secret
The secret driver plugin for the libvirtd daemon, providing
an implementation of the secret key APIs.

%package daemon-driver-storage-core
Summary: Storage driver plugin including base backends for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}
Requires: nfs-utils
# For mkfs
Requires: util-linux
%if %{with_qemu}
# From QEMU RPMs
Requires: /usr/bin/qemu-img
%else
    %if %{with_xen}
# From Xen RPMs
Requires: /usr/sbin/qcow-create
    %endif
%endif

%description daemon-driver-storage-core
The storage driver plugin for the libvirtd daemon, providing
an implementation of the storage APIs using files, local disks, LVM, SCSI,
iSCSI, and multipath storage.

%package daemon-driver-storage-logical
Summary: Storage driver plugin for lvm volumes
Group: Development/Libraries
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: lvm2

%description daemon-driver-storage-logical
The storage driver backend adding implementation of the storage APIs for block
volumes using lvm.


%package daemon-driver-storage-disk
Summary: Storage driver plugin for disk
Group: Development/Libraries
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: parted
Requires: device-mapper

%description daemon-driver-storage-disk
The storage driver backend adding implementation of the storage APIs for block
volumes using the host disks.


%package daemon-driver-storage-scsi
Summary: Storage driver plugin for local scsi devices
Group: Development/Libraries
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}

%description daemon-driver-storage-scsi
The storage driver backend adding implementation of the storage APIs for scsi
host devices.


%package daemon-driver-storage-iscsi
Summary: Storage driver plugin for iscsi
Group: Development/Libraries
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: iscsi-initiator-utils

%description daemon-driver-storage-iscsi
The storage driver backend adding implementation of the storage APIs for iscsi
volumes using the host iscsi stack.


%package daemon-driver-storage-mpath
Summary: Storage driver plugin for multipath volumes
Group: Development/Libraries
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: device-mapper

%description daemon-driver-storage-mpath
The storage driver backend adding implementation of the storage APIs for
multipath storage using device mapper.


%if %{with_storage_gluster}
%package daemon-driver-storage-gluster
Summary: Storage driver plugin for gluster
Group: Development/Libraries
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
    %if 0%{?fedora}
Requires: glusterfs-client >= 2.0.1
    %endif
    %if (0%{?fedora} || 0%{?with_storage_gluster})
Requires: /usr/sbin/gluster
    %endif

%description daemon-driver-storage-gluster
The storage driver backend adding implementation of the storage APIs for gluster
volumes using libgfapi.
%endif


%if %{with_storage_rbd}
%package daemon-driver-storage-rbd
Summary: Storage driver plugin for rbd
Group: Development/Libraries
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}

%description daemon-driver-storage-rbd
The storage driver backend adding implementation of the storage APIs for rbd
volumes using the ceph protocol.
%endif


%if %{with_storage_sheepdog}
%package daemon-driver-storage-sheepdog
Summary: Storage driver plugin for sheepdog
Group: Development/Libraries
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: sheepdog

%description daemon-driver-storage-sheepdog
The storage driver backend adding implementation of the storage APIs for
sheepdog volumes using.
%endif


%if %{with_storage_zfs}
%package daemon-driver-storage-zfs
Summary: Storage driver plugin for ZFS
Group: Development/Libraries
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
# Support any conforming implementation of zfs
Requires: /sbin/zfs
Requires: /sbin/zpool

%description daemon-driver-storage-zfs
The storage driver backend adding implementation of the storage APIs for
ZFS volumes.
%endif


%package daemon-driver-storage
Summary: Storage driver plugin including all backends for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: libvirt-daemon-driver-storage-disk = %{version}-%{release}
Requires: libvirt-daemon-driver-storage-logical = %{version}-%{release}
Requires: libvirt-daemon-driver-storage-scsi = %{version}-%{release}
Requires: libvirt-daemon-driver-storage-iscsi = %{version}-%{release}
Requires: libvirt-daemon-driver-storage-mpath = %{version}-%{release}
%if %{with_storage_gluster}
Requires: libvirt-daemon-driver-storage-gluster = %{version}-%{release}
%endif
%if %{with_storage_rbd}
Requires: libvirt-daemon-driver-storage-rbd = %{version}-%{release}
%endif
%if %{with_storage_sheepdog}
Requires: libvirt-daemon-driver-storage-sheepdog = %{version}-%{release}
%endif
%if %{with_storage_zfs}
Requires: libvirt-daemon-driver-storage-zfs = %{version}-%{release}
%endif

%description daemon-driver-storage
The storage driver plugin for the libvirtd daemon, providing
an implementation of the storage APIs using LVM, iSCSI,
parted and more.


%if %{with_qemu}
%package daemon-driver-qemu
Summary: QEMU driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}
# There really is a hard cross-driver dependency here
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-storage-core = %{version}-%{release}
Requires: /usr/bin/qemu-img
# For image compression
Requires: gzip
Requires: bzip2
Requires: lzop
Requires: xz
    %if 0%{?fedora} >= 24
Requires: systemd-container
    %endif

%description daemon-driver-qemu
The qemu driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
QEMU
%endif


%if %{with_lxc}
%package daemon-driver-lxc
Summary: LXC driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}
# There really is a hard cross-driver dependency here
Requires: libvirt-daemon-driver-network = %{version}-%{release}
    %if 0%{?fedora} >= 24
Requires: systemd-container
    %endif

%description daemon-driver-lxc
The LXC driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
the Linux kernel
%endif


%if %{with_uml}
%package daemon-driver-uml
Summary: Uml driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}

%description daemon-driver-uml
The UML driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
User Mode Linux
%endif


%if %{with_xen}
%package daemon-driver-xen
Summary: Xen driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}

%description daemon-driver-xen
The Xen driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
Xen
%endif


%if %{with_vbox}
%package daemon-driver-vbox
Summary: VirtualBox driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}

%description daemon-driver-vbox
The vbox driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
VirtualBox
%endif


%if %{with_libxl}
%package daemon-driver-libxl
Summary: Libxl driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}

%description daemon-driver-libxl
The Libxl driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
Libxl
%endif



%if %{with_qemu_tcg}
%package daemon-qemu
Summary: Server side daemon & driver required to run QEMU guests
Group: Development/Libraries

Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-daemon-driver-qemu = %{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}
Requires: qemu

%description daemon-qemu
Server side daemon and driver required to manage the virtualization
capabilities of the QEMU TCG emulators
%endif


%if %{with_qemu_kvm}
%package daemon-kvm
Summary: Server side daemon & driver required to run KVM guests
Group: Development/Libraries

Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-daemon-driver-qemu = %{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}
Requires: qemu-kvm

%description daemon-kvm
Server side daemon and driver required to manage the virtualization
capabilities of the KVM hypervisor
%endif


%if %{with_lxc}
%package daemon-lxc
Summary: Server side daemon & driver required to run LXC guests
Group: Development/Libraries

Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-daemon-driver-lxc = %{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}

%description daemon-lxc
Server side daemon and driver required to manage the virtualization
capabilities of LXC
%endif


%if %{with_uml}
%package daemon-uml
Summary: Server side daemon & driver required to run UML guests
Group: Development/Libraries

Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-daemon-driver-uml = %{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}
# There are no UML kernel RPMs in Fedora/RHEL to depend on.

%description daemon-uml
Server side daemon and driver required to manage the virtualization
capabilities of UML
%endif


%if %{with_xen} || %{with_libxl}
%package daemon-xen
Summary: Server side daemon & driver required to run XEN guests
Group: Development/Libraries

Requires: libvirt-daemon = %{version}-%{release}
    %if %{with_xen}
Requires: libvirt-daemon-driver-xen = %{version}-%{release}
    %endif
    %if %{with_libxl}
Requires: libvirt-daemon-driver-libxl = %{version}-%{release}
    %endif
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}
Requires: xen

%description daemon-xen
Server side daemon and driver required to manage the virtualization
capabilities of XEN
%endif

%if %{with_vbox}
%package daemon-vbox
Summary: Server side daemon & driver required to run VirtualBox guests
Group: Development/Libraries

Requires: libvirt-daemon = %{version}-%{release}
Requires: libvirt-daemon-driver-vbox = %{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}

%description daemon-vbox
Server side daemon and driver required to manage the virtualization
capabilities of VirtualBox
%endif

%package client
Summary: Client side utilities of the libvirt library
Group: Development/Libraries
Requires: %{name}-libs = %{version}-%{release}
Requires: readline
Requires: ncurses
# Needed by /usr/libexec/libvirt-guests.sh script.
Requires: gettext
# Needed by virt-pki-validate script.
Requires: gnutls-utils
%if %{with_pm_utils}
# Needed for probing the power management features of the host.
Requires: pm-utils
%endif

%description client
The client binaries needed to access the virtualization
capabilities of recent versions of Linux (and other OSes).

%package libs
Summary: Client side libraries
Group: Development/Libraries
# So remote clients can access libvirt over SSH tunnel
# (client invokes 'nc' against the UNIX socket on the server)
Requires: nc
Requires: cyrus-sasl
# Needed by default sasl.conf - no onerous extra deps, since
# 100's of other things on a system already pull in krb5-libs
Requires: cyrus-sasl-gssapi

%description libs
Shared libraries for accessing the libvirt daemon.

%package admin
Summary: Set of tools to control libvirt daemon
Group: Development/Libraries
Requires: %{name}-libs = %{version}-%{release}
Requires: readline

%description admin
The client side utilities to control the libvirt daemon.

%if %{with_wireshark}
%package wireshark
Summary: Wireshark dissector plugin for libvirt RPC transactions
Group: Development/Libraries
Requires: wireshark >= 1.12.6-4
Requires: %{name}-libs = %{version}-%{release}

%description wireshark
Wireshark dissector plugin for better analysis of libvirt RPC traffic.
%endif

%if %{with_lxc}
%package login-shell
Summary: Login shell for connecting users to an LXC container
Group: Development/Libraries
Requires: %{name}-libs = %{version}-%{release}

%description login-shell
Provides the set-uid virt-login-shell binary that is used to
connect a user to an LXC container when they login, by switching
namespaces.
%endif

%package devel
Summary: Libraries, includes, etc. to compile with the libvirt library
Group: Development/Libraries
Requires: %{name}-libs = %{version}-%{release}
Requires: pkgconfig

%description devel
Include header files & development libraries for the libvirt C library.

%if %{with_sanlock}
%package lock-sanlock
Summary: Sanlock lock manager plugin for QEMU driver
Group: Development/Libraries
Requires: sanlock >= 2.4
#for virt-sanlock-cleanup require augeas
Requires: augeas
Requires: %{name}-daemon = %{version}-%{release}
Requires: %{name}-libs = %{version}-%{release}

%description lock-sanlock
Includes the Sanlock lock manager plugin for the QEMU
driver
%endif

%package nss
Summary: Libvirt plugin for Name Service Switch
Group: Development/Libraries
Requires: libvirt-daemon-driver-network = %{version}-%{release}

%description nss
Libvirt plugin for NSS for translating domain names into IP addresses.


%prep
%if ! %{supported_platform}
echo "This RPM requires either Fedora >= 20 or RHEL >= 6"
exit 1
%endif

%setup -q -n %{name}

# Patches have to be stored in a temporary file because RPM has
# a limit on the length of the result of any macro expansion;
# if the string is longer, it's silently cropped
%{lua:
    tmp = os.tmpname();
    f = io.open(tmp, "w+");
    count = 0;
    for i, p in ipairs(patches) do
        f:write(p.."\n");
        count = count + 1;
    end;
    f:close();
    print("PATCHCOUNT="..count.."\n")
    print("PATCHLIST="..tmp.."\n")
}

git init -q
git config user.name rpm-build
git config user.email rpm-build
git config gc.auto 0
git add .
git commit -q -a --author 'rpm-build <rpm-build>' \
           -m '%{name}-%{version} base'

COUNT=$(grep '\.patch$' $PATCHLIST | wc -l)
if [ $COUNT -ne $PATCHCOUNT ]; then
    echo "Found $COUNT patches in $PATCHLIST, expected $PATCHCOUNT"
    exit 1
fi
if [ $COUNT -gt 0 ]; then
    xargs git am <$PATCHLIST || exit 1
fi
echo "Applied $COUNT patches"
rm -f $PATCHLIST
rm -rf .git

%build
%if %{with_xen}
    %define arg_xen --with-xen
%else
    %define arg_xen --without-xen
%endif

%if %{with_qemu}
    %define arg_qemu --with-qemu
%else
    %define arg_qemu --without-qemu
%endif

%if %{with_openvz}
    %define arg_openvz --with-openvz
%else
    %define arg_openvz --without-openvz
%endif

%if %{with_lxc}
    %define arg_lxc --with-lxc
%else
    %define arg_lxc --without-lxc
%endif

%if %{with_vbox}
    %define arg_vbox --with-vbox
%else
    %define arg_vbox --without-vbox
%endif

%if %{with_libxl}
    %define arg_libxl --with-libxl
%else
    %define arg_libxl --without-libxl
%endif

%if %{with_phyp}
    %define arg_phyp --with-phyp
%else
    %define arg_phyp --without-phyp
%endif

%if %{with_esx}
    %define arg_esx --with-esx
%else
    %define arg_esx --without-esx
%endif

%if %{with_hyperv}
    %define arg_hyperv --with-hyperv
%else
    %define arg_hyperv --without-hyperv
%endif

%if %{with_vmware}
    %define arg_vmware --with-vmware
%else
    %define arg_vmware --without-vmware
%endif

%if %{with_uml}
    %define arg_uml --with-uml
%else
    %define arg_uml --without-uml
%endif

%if %{with_storage_rbd}
    %define arg_storage_rbd --with-storage-rbd
%else
    %define arg_storage_rbd --without-storage-rbd
%endif

%if %{with_storage_sheepdog}
    %define arg_storage_sheepdog --with-storage-sheepdog
%else
    %define arg_storage_sheepdog --without-storage-sheepdog
%endif

%if %{with_storage_gluster}
    %define arg_storage_gluster --with-storage-gluster
%else
    %define arg_storage_gluster --without-storage-gluster
%endif

%if %{with_storage_zfs}
    %define arg_storage_zfs --with-storage-zfs
%else
    %define arg_storage_zfs --without-storage-zfs
%endif

%if %{with_numactl}
    %define arg_numactl --with-numactl
%else
    %define arg_numactl --without-numactl
%endif

%if %{with_numad}
    %define arg_numad --with-numad
%else
    %define arg_numad --without-numad
%endif

%if %{with_fuse}
    %define arg_fuse --with-fuse
%else
    %define arg_fuse --without-fuse
%endif

%if %{with_sanlock}
    %define arg_sanlock --with-sanlock
%else
    %define arg_sanlock --without-sanlock
%endif

%if %{with_firewalld}
    %define arg_firewalld --with-firewalld
%else
    %define arg_firewalld --without-firewalld
%endif

%if %{with_wireshark}
    %define arg_wireshark --with-wireshark-dissector
%else
    %define arg_wireshark --without-wireshark-dissector
%endif

%if %{with_pm_utils}
    %define arg_pm_utils --with-pm-utils
%else
    %define arg_pm_utils --without-pm-utils
%endif

%define when  %(date +"%%F-%%T")
%define where %(hostname)
%define who   %{?packager}%{!?packager:Unknown}
%define arg_packager --with-packager="%{who}, %{when}, %{where}"
%define arg_packager_version --with-packager-version="%{release}"

%if %{with_systemd}
    %define arg_init_script --with-init-script=systemd
%else
    %define arg_init_script --with-init-script=redhat
%endif

%if 0%{?fedora} || 0%{?rhel} >= 7
    %define arg_selinux_mount --with-selinux-mount="/sys/fs/selinux"
%else
    %define arg_selinux_mount --with-selinux-mount="/selinux"
%endif

%if 0%{?fedora}
    # Nightly firmware repo x86/OVMF
    LOADERS="/usr/share/edk2.git/ovmf-x64/OVMF_CODE-pure-efi.fd:/usr/share/edk2.git/ovmf-x64/OVMF_VARS-pure-efi.fd"
    # Nightly firmware repo aarch64/AAVMF
    LOADERS="$LOADERS:/usr/share/edk2.git/aarch64/QEMU_EFI-pflash.raw:/usr/share/edk2.git/aarch64/vars-template-pflash.raw"
    # Fedora official x86/OVMF
    LOADERS="$LOADERS:/usr/share/edk2/ovmf/OVMF_CODE.fd:/usr/share/edk2/ovmf/OVMF_VARS.fd"
    # Fedora official aarch64/AAVMF
    LOADERS="$LOADERS:/usr/share/edk2/aarch64/QEMU_EFI-pflash.raw:/usr/share/edk2/aarch64/vars-template-pflash.raw"
    %define arg_loader_nvram --with-loader-nvram="$LOADERS"
%endif

# place macros above and build commands below this comment

./bootstrap --no-git --gnulib-srcdir=.gnulib
./autogen.sh --system \
           %{?arg_xen} \
           %{?arg_qemu} \
           %{?arg_openvz} \
           %{?arg_lxc} \
           %{?arg_vbox} \
           %{?arg_libxl} \
           --with-sasl \
           --with-avahi \
           --with-polkit \
           --with-libvirtd \
           %{?arg_uml} \
           %{?arg_phyp} \
           %{?arg_esx} \
           %{?arg_hyperv} \
           %{?arg_vmware} \
           --without-xenapi \
           --without-vz \
           --without-bhyve \
           --with-interface \
           --with-network \
           --with-storage-fs \
           --with-storage-lvm \
           --with-storage-iscsi \
           --with-storage-scsi \
           --with-storage-disk \
           --with-storage-mpath \
           %{?arg_storage_rbd} \
           %{?arg_storage_sheepdog} \
           %{?arg_storage_gluster} \
           %{?arg_storage_zfs} \
           --without-storage-vstorage \
           %{?arg_numactl} \
           %{?arg_numad} \
           --with-capng \
           %{?arg_fuse} \
           --with-netcf \
           --with-selinux \
           %{?arg_selinux_mount} \
           --without-apparmor \
           --without-hal \
           --with-udev \
           --with-yajl \
           %{?arg_sanlock} \
           --with-libpcap \
           --with-macvtap \
           --with-audit \
           --with-dtrace \
           --with-driver-modules \
           %{?arg_firewalld} \
           %{?arg_wireshark} \
           %{?arg_pm_utils} \
           --with-nss-plugin \
           %{arg_packager} \
           %{arg_packager_version} \
           --with-qemu-user=%{qemu_user} \
           --with-qemu-group=%{qemu_group} \
           --with-tls-priority=%{tls_priority} \
           %{?arg_loader_nvram} \
           %{?enable_werror} \
           --enable-expensive-tests \
           %{arg_init_script}
make %{?_smp_mflags}
gzip -9 ChangeLog

%install
rm -fr %{buildroot}

# Avoid using makeinstall macro as it changes prefixes rather than setting
# DESTDIR. Newer make_install macro would be better but it's not available
# on RHEL 5, thus we need to expand it here.
make %{?_smp_mflags} install DESTDIR=%{?buildroot} SYSTEMD_UNIT_DIR=%{_unitdir}

make %{?_smp_mflags} -C examples distclean

rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/*.a
rm -f $RPM_BUILD_ROOT%{_libdir}/libvirt/lock-driver/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/libvirt/lock-driver/*.a
rm -f $RPM_BUILD_ROOT%{_libdir}/libvirt/connection-driver/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/libvirt/connection-driver/*.a
rm -f $RPM_BUILD_ROOT%{_libdir}/libvirt/storage-backend/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/libvirt/storage-backend/*.a
%if %{with_wireshark}
    %if 0%{fedora} >= 24
rm -f $RPM_BUILD_ROOT%{_libdir}/wireshark/plugins/libvirt.la
    %else
rm -f $RPM_BUILD_ROOT%{_libdir}/wireshark/plugins/*/libvirt.la
mv $RPM_BUILD_ROOT%{_libdir}/wireshark/plugins/*/libvirt.so \
      $RPM_BUILD_ROOT%{_libdir}/wireshark/plugins/libvirt.so
    %endif
%endif

install -d -m 0755 $RPM_BUILD_ROOT%{_datadir}/lib/libvirt/dnsmasq/
# We don't want to install /etc/libvirt/qemu/networks in the main %files list
# because if the admin wants to delete the default network completely, we don't
# want to end up re-incarnating it on every RPM upgrade.
install -d -m 0755 $RPM_BUILD_ROOT%{_datadir}/libvirt/networks/
cp $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/qemu/networks/default.xml \
   $RPM_BUILD_ROOT%{_datadir}/libvirt/networks/default.xml
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/qemu/networks/default.xml
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/qemu/networks/autostart/default.xml

# nwfilter files are installed in /usr/share/libvirt and copied to /etc in %post
# to avoid verification errors on changed files in /etc
install -d -m 0755 $RPM_BUILD_ROOT%{_datadir}/libvirt/nwfilter/
cp -a $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/nwfilter/*.xml \
    $RPM_BUILD_ROOT%{_datadir}/libvirt/nwfilter/

# Strip auto-generated UUID - we need it generated per-install
sed -i -e "/<uuid>/d" $RPM_BUILD_ROOT%{_datadir}/libvirt/networks/default.xml
%if ! %{with_qemu}
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/libvirtd_qemu.aug
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/tests/test_libvirtd_qemu.aug
%endif
%find_lang %{name}

%if ! %{with_sanlock}
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/libvirt_sanlock.aug
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/tests/test_libvirt_sanlock.aug
%endif

%if ! %{with_lxc}
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/libvirtd_lxc.aug
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/tests/test_libvirtd_lxc.aug
%endif

%if ! %{with_qemu}
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/qemu.conf
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/libvirtd.qemu
%endif
%if ! %{with_lxc}
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/lxc.conf
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/libvirtd.lxc
%endif
%if ! %{with_libxl}
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/libxl.conf
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/libvirtd.libxl
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/libvirtd_libxl.aug
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/tests/test_libvirtd_libxl.aug
%endif
%if ! %{with_uml}
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/libvirtd.uml
%endif

# Copied into libvirt-docs subpackage eventually
mv $RPM_BUILD_ROOT%{_datadir}/doc/libvirt-%{version} libvirt-docs

%ifarch %{power64} s390x x86_64 ia64 alpha sparc64
mv $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/libvirt_probes.stp \
   $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/libvirt_probes-64.stp
mv $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/libvirt_qemu_probes.stp \
   $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/libvirt_qemu_probes-64.stp
%endif

%clean
rm -fr %{buildroot}

%if %{with tests}
%check
cd tests
# These tests don't current work in a mock build root
for i in nodeinfotest seclabeltest
do
  rm -f $i
  printf 'int main(void) { return 0; }' > $i.c
  printf '#!/bin/sh\nexit 0\n' > $i
  chmod +x $i
done
if ! make %{?_smp_mflags} check VIR_TEST_DEBUG=1
then
  cat test-suite.log || true
  exit 1
fi
%endif

%pre daemon
# 'libvirt' group is just to allow password-less polkit access to
# libvirtd. The uid number is irrelevant, so we use dynamic allocation
# described at the above link.
getent group libvirt >/dev/null || groupadd -r libvirt

exit 0

%post daemon

%if %{with_systemd}
    %if %{with_systemd_macros}
        %systemd_post virtlockd.socket virtlogd.socket libvirtd.service
    %else
if [ $1 -eq 1 ] ; then
    # Initial installation
    /bin/systemctl enable \
        virtlockd.socket \
        virtlogd.socket \
        libvirtd.service >/dev/null 2>&1 || :
fi
    %endif
%else
    %if %{with_cgconfig}
# Starting with Fedora 16/RHEL-7, systemd automounts all cgroups,
# and cgconfig is no longer a necessary service.
        %if 0%{?rhel} && 0%{?rhel} < 7
if [ "$1" -eq "1" ]; then
/sbin/chkconfig cgconfig on
fi
        %endif
    %endif

/sbin/chkconfig --add libvirtd
/sbin/chkconfig --add virtlogd
/sbin/chkconfig --add virtlockd
%endif

%preun daemon
%if %{with_systemd}
    %if %{with_systemd_macros}
        %systemd_preun libvirtd.service virtlogd.socket virtlogd.service virtlockd.socket virtlockd.service
    %else
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable \
        libvirtd.service \
        virtlogd.socket \
        virtlogd.service \
        virtlockd.socket \
        virtlockd.service > /dev/null 2>&1 || :
    /bin/systemctl stop \
        libvirtd.service \
        virtlogd.socket \
        virtlogd.service \
        virtlockd.socket \
        virtlockd.service > /dev/null 2>&1 || :
fi
    %endif
%else
if [ $1 = 0 ]; then
    /sbin/service libvirtd stop 1>/dev/null 2>&1
    /sbin/chkconfig --del libvirtd
    /sbin/service virtlogd stop 1>/dev/null 2>&1
    /sbin/chkconfig --del virtlogd
    /sbin/service virtlockd stop 1>/dev/null 2>&1
    /sbin/chkconfig --del virtlockd
fi
%endif

%postun daemon
%if %{with_systemd}
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    /bin/systemctl reload-or-try-restart virtlockd.service >/dev/null 2>&1 || :
    /bin/systemctl reload-or-try-restart virtlogd.service >/dev/null 2>&1 || :
    /bin/systemctl try-restart libvirtd.service >/dev/null 2>&1 || :
fi
%else
if [ $1 -ge 1 ]; then
    /sbin/service virtlockd reload > /dev/null 2>&1 || :
    /sbin/service virtlogd reload > /dev/null 2>&1 || :
    /sbin/service libvirtd condrestart > /dev/null 2>&1
fi
%endif

%if %{with_systemd}
%else
%triggerpostun daemon -- libvirt-daemon < 1.2.1
if [ "$1" -ge "1" ]; then
    /sbin/service virtlockd reload > /dev/null 2>&1 || :
    /sbin/service virtlogd reload > /dev/null 2>&1 || :
    /sbin/service libvirtd condrestart > /dev/null 2>&1
fi
%endif

# In upgrade scenario we must explicitly enable virtlockd/virtlogd
# sockets, if libvirtd is already enabled and start them if
# libvirtd is running, otherwise you'll get failures to start
# guests
%triggerpostun daemon -- libvirt-daemon < 1.3.0
if [ $1 -ge 1 ] ; then
%if %{with_systemd}
        /bin/systemctl is-enabled libvirtd.service 1>/dev/null 2>&1 &&
            /bin/systemctl enable virtlogd.socket || :
        /bin/systemctl is-active libvirtd.service 1>/dev/null 2>&1 &&
            /bin/systemctl start virtlogd.socket || :
%else
        /sbin/chkconfig libvirtd 1>/dev/null 2>&1 &&
            /sbin/chkconfig virtlogd on || :
        /sbin/service libvirtd status 1>/dev/null 2>&1 &&
            /sbin/service virtlogd start || :
%endif
fi

%post daemon-config-network
if test $1 -eq 1 && test ! -f %{_sysconfdir}/libvirt/qemu/networks/default.xml ; then
    # see if the network used by default network creates a conflict,
    # and try to resolve it
    # NB: 192.168.122.0/24 is used in the default.xml template file;
    # do not modify any of those values here without also modifying
    # them in the template.
    orig_sub=122
    sub=${orig_sub}
    nl='
'
    routes="${nl}$(ip route show | cut -d' ' -f1)${nl}"
    case ${routes} in
      *"${nl}192.168.${orig_sub}.0/24${nl}"*)
        # there was a match, so we need to look for an unused subnet
        for new_sub in $(seq 124 254); do
          case ${routes} in
          *"${nl}192.168.${new_sub}.0/24${nl}"*)
            ;;
          *)
            sub=$new_sub
            break;
            ;;
          esac
        done
        ;;
      *)
        ;;
    esac

    UUID=`/usr/bin/uuidgen`
    sed -e "s/${orig_sub}/${sub}/g" \
        -e "s,</name>,</name>\n  <uuid>$UUID</uuid>," \
         < %{_datadir}/libvirt/networks/default.xml \
         > %{_sysconfdir}/libvirt/qemu/networks/default.xml
    ln -s ../default.xml %{_sysconfdir}/libvirt/qemu/networks/autostart/default.xml

    # Make sure libvirt picks up the new network defininiton
%if %{with_systemd}
    /bin/systemctl try-restart libvirtd.service >/dev/null 2>&1 ||:
%else
    /sbin/service libvirtd condrestart > /dev/null 2>&1 || :
%endif

fi


%post daemon-config-nwfilter
cp %{_datadir}/libvirt/nwfilter/*.xml %{_sysconfdir}/libvirt/nwfilter/
# Make sure libvirt picks up the new nwfilter defininitons
%if %{with_systemd}
    /bin/systemctl try-restart libvirtd.service >/dev/null 2>&1 ||:
%else
    /sbin/service libvirtd condrestart > /dev/null 2>&1 || :
%endif


%if %{with_systemd}
%triggerun -- libvirt < 0.9.4
%{_bindir}/systemd-sysv-convert --save libvirtd >/dev/null 2>&1 ||:

# If the package is allowed to autostart:
/bin/systemctl --no-reload enable libvirtd.service >/dev/null 2>&1 ||:

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del libvirtd >/dev/null 2>&1 || :
/bin/systemctl try-restart libvirtd.service >/dev/null 2>&1 || :
%endif

%if %{with_qemu}
%pre daemon-driver-qemu
# We want soft static allocation of well-known ids, as disk images
# are commonly shared across NFS mounts by id rather than name; see
# https://fedoraproject.org/wiki/Packaging:UsersAndGroups
getent group kvm >/dev/null || groupadd -f -g 36 -r kvm
getent group qemu >/dev/null || groupadd -f -g 107 -r qemu
if ! getent passwd qemu >/dev/null; then
  if ! getent passwd 107 >/dev/null; then
    useradd -r -u 107 -g qemu -G kvm -d / -s /sbin/nologin -c "qemu user" qemu
  else
    useradd -r -g qemu -G kvm -d / -s /sbin/nologin -c "qemu user" qemu
  fi
fi
exit 0
%endif

%preun client

%if %{with_systemd}
    %if %{with_systemd_macros}
        %systemd_preun libvirt-guests.service
    %endif
%else
if [ $1 = 0 ]; then
    /sbin/chkconfig --del libvirt-guests
    rm -f /var/lib/libvirt/libvirt-guests
fi
%endif

%post client

/sbin/ldconfig
%if %{with_systemd}
    %if %{with_systemd_macros}
        %systemd_post libvirt-guests.service
    %endif
%else
/sbin/chkconfig --add libvirt-guests
%endif

%postun client

/sbin/ldconfig
%if %{with_systemd}
    %if %{with_systemd_macros}
        %systemd_postun libvirt-guests.service
    %endif
%triggerun client -- libvirt < 0.9.4
%{_bindir}/systemd-sysv-convert --save libvirt-guests >/dev/null 2>&1 ||:

# If the package is allowed to autostart:
/bin/systemctl --no-reload enable libvirt-guests.service >/dev/null 2>&1 ||:

# Run this because the SysV package being removed won't do them
/sbin/chkconfig --del libvirt-guests >/dev/null 2>&1 || :
%endif

%if %{with_sanlock}
%post lock-sanlock
if getent group sanlock > /dev/null ; then
    chmod 0770 %{_localstatedir}/lib/libvirt/sanlock
    chown root:sanlock %{_localstatedir}/lib/libvirt/sanlock
fi
%endif

%if %{with_lxc}
%pre login-shell
getent group virtlogin >/dev/null || groupadd -r virtlogin
exit 0
%endif

%files

%files docs
%doc AUTHORS ChangeLog.gz README
%doc libvirt-docs/*

# API docs
%dir %{_datadir}/gtk-doc/html/libvirt/
%doc %{_datadir}/gtk-doc/html/libvirt/*.devhelp
%doc %{_datadir}/gtk-doc/html/libvirt/*.html
%doc %{_datadir}/gtk-doc/html/libvirt/*.png
%doc %{_datadir}/gtk-doc/html/libvirt/*.css
%doc examples/hellolibvirt
%doc examples/object-events
%doc examples/dominfo
%doc examples/domsuspend
%doc examples/dommigrate
%doc examples/openauth
%doc examples/xml
%doc examples/rename
%doc examples/systemtap
%doc examples/admin


%files daemon

%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/

%if %{with_systemd}
%{_unitdir}/libvirtd.service
%{_unitdir}/virt-guest-shutdown.target
%{_unitdir}/virtlogd.service
%{_unitdir}/virtlogd.socket
%{_unitdir}/virtlockd.service
%{_unitdir}/virtlockd.socket
%else
%{_sysconfdir}/rc.d/init.d/libvirtd
%{_sysconfdir}/rc.d/init.d/virtlogd
%{_sysconfdir}/rc.d/init.d/virtlockd
%endif
%doc daemon/libvirtd.upstart
%config(noreplace) %{_sysconfdir}/sysconfig/libvirtd
%config(noreplace) %{_sysconfdir}/sysconfig/virtlogd
%config(noreplace) %{_sysconfdir}/sysconfig/virtlockd
%config(noreplace) %{_sysconfdir}/libvirt/libvirtd.conf
%config(noreplace) %{_sysconfdir}/libvirt/virtlogd.conf
%config(noreplace) %{_sysconfdir}/libvirt/virtlockd.conf
%config(noreplace) %{_prefix}/lib/sysctl.d/60-libvirtd.conf

%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd
%dir %{_datadir}/libvirt/

%ghost %dir %{_localstatedir}/run/libvirt/

%dir %attr(0711, root, root) %{_localstatedir}/lib/libvirt/images/
%dir %attr(0711, root, root) %{_localstatedir}/lib/libvirt/filesystems/
%dir %attr(0711, root, root) %{_localstatedir}/lib/libvirt/boot/
%dir %attr(0711, root, root) %{_localstatedir}/cache/libvirt/


%dir %attr(0755, root, root) %{_libdir}/libvirt/lock-driver
%attr(0755, root, root) %{_libdir}/libvirt/lock-driver/lockd.so

%{_datadir}/augeas/lenses/libvirtd.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd.aug
%{_datadir}/augeas/lenses/virtlogd.aug
%{_datadir}/augeas/lenses/tests/test_virtlogd.aug
%{_datadir}/augeas/lenses/virtlockd.aug
%{_datadir}/augeas/lenses/tests/test_virtlockd.aug
%{_datadir}/augeas/lenses/libvirt_lockd.aug
%if %{with_qemu}
%{_datadir}/augeas/lenses/tests/test_libvirt_lockd.aug
%endif

%{_datadir}/polkit-1/actions/org.libvirt.unix.policy
%{_datadir}/polkit-1/actions/org.libvirt.api.policy
%{_datadir}/polkit-1/rules.d/50-libvirt.rules

%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/

%attr(0755, root, root) %{_libexecdir}/libvirt_iohelper

%attr(0755, root, root) %{_sbindir}/libvirtd
%attr(0755, root, root) %{_sbindir}/virtlogd
%attr(0755, root, root) %{_sbindir}/virtlockd

%{_mandir}/man8/libvirtd.8*
%{_mandir}/man8/virtlogd.8*
%{_mandir}/man8/virtlockd.8*
%{_mandir}/man7/virkey*.7*

%doc examples/polkit/*.rules

%files daemon-config-network
%dir %{_datadir}/libvirt/networks/
%{_datadir}/libvirt/networks/default.xml

%files daemon-config-nwfilter
%dir %{_datadir}/libvirt/nwfilter/
%{_datadir}/libvirt/nwfilter/*.xml
%ghost %{_sysconfdir}/libvirt/nwfilter/*.xml

%files daemon-driver-interface
%{_libdir}/%{name}/connection-driver/libvirt_driver_interface.so

%files daemon-driver-network
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/networks/
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/networks/autostart
%ghost %dir %{_localstatedir}/run/libvirt/network/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/network/
%dir %attr(0755, root, root) %{_localstatedir}/lib/libvirt/dnsmasq/
%attr(0755, root, root) %{_libexecdir}/libvirt_leaseshelper
%{_libdir}/%{name}/connection-driver/libvirt_driver_network.so

%files daemon-driver-nodedev
%{_libdir}/%{name}/connection-driver/libvirt_driver_nodedev.so

%files daemon-driver-nwfilter
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/nwfilter/
%ghost %dir %{_localstatedir}/run/libvirt/network/
%{_libdir}/%{name}/connection-driver/libvirt_driver_nwfilter.so

%files daemon-driver-secret
%{_libdir}/%{name}/connection-driver/libvirt_driver_secret.so

%files daemon-driver-storage

%files daemon-driver-storage-core
%attr(0755, root, root) %{_libexecdir}/libvirt_parthelper
%{_libdir}/%{name}/connection-driver/libvirt_driver_storage.so
%{_libdir}/%{name}/storage-backend/libvirt_storage_backend_fs.so

%files daemon-driver-storage-disk
%{_libdir}/%{name}/storage-backend/libvirt_storage_backend_disk.so

%files daemon-driver-storage-logical
%{_libdir}/%{name}/storage-backend/libvirt_storage_backend_logical.so

%files daemon-driver-storage-scsi
%{_libdir}/%{name}/storage-backend/libvirt_storage_backend_scsi.so

%files daemon-driver-storage-iscsi
%{_libdir}/%{name}/storage-backend/libvirt_storage_backend_iscsi.so

%files daemon-driver-storage-mpath
%{_libdir}/%{name}/storage-backend/libvirt_storage_backend_mpath.so

%if %{with_storage_gluster}
%files daemon-driver-storage-gluster
%{_libdir}/%{name}/storage-backend/libvirt_storage_backend_gluster.so
%endif

%if %{with_storage_rbd}
%files daemon-driver-storage-rbd
%{_libdir}/%{name}/storage-backend/libvirt_storage_backend_rbd.so
%endif

%if %{with_storage_sheepdog}
%files daemon-driver-storage-sheepdog
%{_libdir}/%{name}/storage-backend/libvirt_storage_backend_sheepdog.so
%endif

%if %{with_storage_zfs}
%files daemon-driver-storage-zfs
%{_libdir}/%{name}/storage-backend/libvirt_storage_backend_zfs.so
%endif

%if %{with_qemu}
%files daemon-driver-qemu
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/qemu/
%config(noreplace) %{_sysconfdir}/libvirt/qemu.conf
%config(noreplace) %{_sysconfdir}/libvirt/qemu-lockd.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd.qemu
%ghost %dir %attr(0700, root, root) %{_localstatedir}/run/libvirt/qemu/
%dir %attr(0751, %{qemu_user}, %{qemu_group}) %{_localstatedir}/lib/libvirt/qemu/
%dir %attr(0750, %{qemu_user}, %{qemu_group}) %{_localstatedir}/cache/libvirt/qemu/
%{_datadir}/augeas/lenses/libvirtd_qemu.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd_qemu.aug
%{_libdir}/%{name}/connection-driver/libvirt_driver_qemu.so
%endif

%if %{with_lxc}
%files daemon-driver-lxc
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/lxc/
%config(noreplace) %{_sysconfdir}/libvirt/lxc.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd.lxc
%ghost %dir %{_localstatedir}/run/libvirt/lxc/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/lxc/
%{_datadir}/augeas/lenses/libvirtd_lxc.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd_lxc.aug
%attr(0755, root, root) %{_libexecdir}/libvirt_lxc
%{_libdir}/%{name}/connection-driver/libvirt_driver_lxc.so
%endif

%if %{with_uml}
%files daemon-driver-uml
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/uml/
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd.uml
%ghost %dir %{_localstatedir}/run/libvirt/uml/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/uml/
%{_libdir}/%{name}/connection-driver/libvirt_driver_uml.so
%endif

%if %{with_xen}
%files daemon-driver-xen
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/xen/
%{_libdir}/%{name}/connection-driver/libvirt_driver_xen.so
%endif

%if %{with_libxl}
%files daemon-driver-libxl
%config(noreplace) %{_sysconfdir}/libvirt/libxl.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd.libxl
%config(noreplace) %{_sysconfdir}/libvirt/libxl-lockd.conf
%{_datadir}/augeas/lenses/libvirtd_libxl.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd_libxl.aug
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/libxl/
%ghost %dir %{_localstatedir}/run/libvirt/libxl/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/libxl/
%{_libdir}/%{name}/connection-driver/libvirt_driver_libxl.so
%endif

%if %{with_vbox}
%files daemon-driver-vbox
%{_libdir}/%{name}/connection-driver/libvirt_driver_vbox.so
%endif

%if %{with_qemu_tcg}
%files daemon-qemu
%endif

%if %{with_qemu_kvm}
%files daemon-kvm
%endif

%if %{with_lxc}
%files daemon-lxc
%endif

%if %{with_uml}
%files daemon-uml
%endif

%if %{with_xen} || %{with_libxl}
%files daemon-xen
%endif

%if %{with_vbox}
%files daemon-vbox
%endif

%if %{with_sanlock}
%files lock-sanlock
    %if %{with_qemu}
%config(noreplace) %{_sysconfdir}/libvirt/qemu-sanlock.conf
    %endif
    %if %{with_libxl}
%config(noreplace) %{_sysconfdir}/libvirt/libxl-sanlock.conf
    %endif
%attr(0755, root, root) %{_libdir}/libvirt/lock-driver/sanlock.so
%{_datadir}/augeas/lenses/libvirt_sanlock.aug
%{_datadir}/augeas/lenses/tests/test_libvirt_sanlock.aug
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/sanlock
%{_sbindir}/virt-sanlock-cleanup
%{_mandir}/man8/virt-sanlock-cleanup.8*
%attr(0755, root, root) %{_libexecdir}/libvirt_sanlock_helper
%endif

%files client
%{_mandir}/man1/virsh.1*
%{_mandir}/man1/virt-xml-validate.1*
%{_mandir}/man1/virt-pki-validate.1*
%{_mandir}/man1/virt-host-validate.1*
%{_bindir}/virsh
%{_bindir}/virt-xml-validate
%{_bindir}/virt-pki-validate
%{_bindir}/virt-host-validate

%{_datadir}/systemtap/tapset/libvirt_probes*.stp
%{_datadir}/systemtap/tapset/libvirt_qemu_probes*.stp
%{_datadir}/systemtap/tapset/libvirt_functions.stp


%if %{with_systemd}
%{_unitdir}/libvirt-guests.service
%else
%{_sysconfdir}/rc.d/init.d/libvirt-guests
%endif
%config(noreplace) %{_sysconfdir}/sysconfig/libvirt-guests
%attr(0755, root, root) %{_libexecdir}/libvirt-guests.sh

%files libs -f %{name}.lang
%doc COPYING COPYING.LESSER
%config(noreplace) %{_sysconfdir}/libvirt/libvirt.conf
%config(noreplace) %{_sysconfdir}/libvirt/libvirt-admin.conf
%{_libdir}/libvirt.so.*
%{_libdir}/libvirt-qemu.so.*
%{_libdir}/libvirt-lxc.so.*
%{_libdir}/libvirt-admin.so.*
%dir %{_datadir}/libvirt/
%dir %{_datadir}/libvirt/schemas/
%dir %attr(0755, root, root) %{_localstatedir}/lib/libvirt/

%{_datadir}/libvirt/schemas/basictypes.rng
%{_datadir}/libvirt/schemas/capability.rng
%{_datadir}/libvirt/schemas/cputypes.rng
%{_datadir}/libvirt/schemas/domain.rng
%{_datadir}/libvirt/schemas/domaincaps.rng
%{_datadir}/libvirt/schemas/domaincommon.rng
%{_datadir}/libvirt/schemas/domainsnapshot.rng
%{_datadir}/libvirt/schemas/interface.rng
%{_datadir}/libvirt/schemas/network.rng
%{_datadir}/libvirt/schemas/networkcommon.rng
%{_datadir}/libvirt/schemas/nodedev.rng
%{_datadir}/libvirt/schemas/nwfilter.rng
%{_datadir}/libvirt/schemas/secret.rng
%{_datadir}/libvirt/schemas/storagecommon.rng
%{_datadir}/libvirt/schemas/storagepool.rng
%{_datadir}/libvirt/schemas/storagevol.rng

%{_datadir}/libvirt/cpu_map.xml

%{_datadir}/libvirt/test-screenshot.png

%config(noreplace) %{_sysconfdir}/sasl2/libvirt.conf

%files admin
%{_mandir}/man1/virt-admin.1*
%{_bindir}/virt-admin


%if %{with_wireshark}
%files wireshark
%{_libdir}/wireshark/plugins/libvirt.so
%endif

%files nss
%{_libdir}/libnss_libvirt.so.2
%{_libdir}/libnss_libvirt_guest.so.2

%if %{with_lxc}
%files login-shell
%attr(4750, root, virtlogin) %{_bindir}/virt-login-shell
%config(noreplace) %{_sysconfdir}/libvirt/virt-login-shell.conf
%{_mandir}/man1/virt-login-shell.1*
%endif

%files devel
%{_libdir}/libvirt.so
%{_libdir}/libvirt-admin.so
%{_libdir}/libvirt-qemu.so
%{_libdir}/libvirt-lxc.so
%dir %{_includedir}/libvirt
%{_includedir}/libvirt/virterror.h
%{_includedir}/libvirt/libvirt.h
%{_includedir}/libvirt/libvirt-admin.h
%{_includedir}/libvirt/libvirt-common.h
%{_includedir}/libvirt/libvirt-domain.h
%{_includedir}/libvirt/libvirt-domain-snapshot.h
%{_includedir}/libvirt/libvirt-event.h
%{_includedir}/libvirt/libvirt-host.h
%{_includedir}/libvirt/libvirt-interface.h
%{_includedir}/libvirt/libvirt-network.h
%{_includedir}/libvirt/libvirt-nodedev.h
%{_includedir}/libvirt/libvirt-nwfilter.h
%{_includedir}/libvirt/libvirt-secret.h
%{_includedir}/libvirt/libvirt-storage.h
%{_includedir}/libvirt/libvirt-stream.h
%{_includedir}/libvirt/libvirt-qemu.h
%{_includedir}/libvirt/libvirt-lxc.h
%{_libdir}/pkgconfig/libvirt.pc
%{_libdir}/pkgconfig/libvirt-admin.pc
%{_libdir}/pkgconfig/libvirt-qemu.pc
%{_libdir}/pkgconfig/libvirt-lxc.pc

%dir %{_datadir}/libvirt/api/
%{_datadir}/libvirt/api/libvirt-api.xml
%{_datadir}/libvirt/api/libvirt-admin-api.xml
%{_datadir}/libvirt/api/libvirt-qemu-api.xml
%{_datadir}/libvirt/api/libvirt-lxc-api.xml
# Needed building python bindings
%doc docs/libvirt-api.xml


%changelog
* Sat Jan 20 2018 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.0.0-2.git
- Updating to 5e6f8a1 Merge tag v4.0.0-rc2 into hostos-devel

* Tue Jan 16 2018 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.0.0-1.git
- Version update
- Updating to 7418247 Merge tag v4.0.0-rc1 into hostos-devel

* Fri Dec 22 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 3.9.0-3.git
- Updating to cb3885f Partly revert 99ed075

* Wed Dec 06 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 3.9.0-2.git
- Updating to 99ed075 treat host models as case-insensitive strings

* Thu Nov 23 2017 Murilo Opsfelder Araújo <muriloo@linux.vnet.ibm.com> - 3.9.0-1.git
- Update to 3.9.0

* Thu Sep 07 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 3.6.0-3.git
- Updating to dd9401b virsh: Implement managedsave-edit command

* Mon Aug 14 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 3.6.0-2.git
- Bump release

* Thu Aug 10 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 3.6.0-1.git40c1264
- Version update
- Updating to 40c1264 Merge branch hostos-devel of https://github.com/open-power-host-os/libvirt into v3.6.0

* Mon Aug 07 2017 Fabiano Rosas <farosas@linux.vnet.ibm.com> - 3.2.0-4.git
- Add extraver macro to Release field

* Wed Jun 14 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 3.2.0-3.git
- Updating to f81f00f util: hostcpu: Correctly report total number of vcpus in
  virHostCPUGetMap

* Wed May 24 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 3.2.0-2.git
- Updating to 1381536 Adding POWER9 cpu model to cpu_map.xml

* Wed Apr 19 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 3.2.0-1.git1587323
- Updating to version 3.2.0

* Thu Mar 23 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.2.0-7.git
- Updating to f25cbfd virtlogd.socket: Tie lifecycle to libvirtd.service

* Wed Oct 19 2016 Murilo Opsfelder Araújo <muriloo@linux.vnet.ibm.com> - 2.2.0-6
- Remove unused macros and simplify package numbering
- Bump release

* Wed Oct 05 2016 user - 2.2.0-5.3200.0
- ddccbf6 qemu: Fix coldplug of vcpus
98fe4f8 qemu: process: Enforce vcpu order range to <1,maxvcpus>
a783b65 qemu: process: Dont use shifted indexes for vcpu order verification
2ba15ac qemu: process: Fix off-by-one in vcpu order duplicate error message
d72de66 qemu: driver: Dont return automatic NUMA emulator pinning data for persistentDef
73bd880 qemu: driver: Dont return automatic NUMA vCPU pinning data for persistentDef
979edc3 qemu: domain: Add macro to simplify access to vm private data
147b668 conf: Introduce virDomainObjGetOneDefState
8b43f06 qemu: domain: Dont infer vcpu state
5c149d8 qemu: monitor: Add vcpu state information to monitor data
fe0fa43 qemu: monitor: qemuMonitorGetCPUInfoHotplug: Add iterator anycpu
557d6f7 qemu: monitor: Use a more obvious iterator name
a2299ad numa: Rename virNumaGetHostNodeset and make it return only nodes with memory
f856b8c util: numa: Remove impossible error handling
ea783c1 qemu: Add missing p to qemuCgrouEmulatorAllNodesRestore
092ecc6 qemu: driver: Remove unnecessary condition
d7e1062 qemu: process: Fix start with unpluggable vcpus with NUMA pinning
691d038 qemu: cgroup: Extract temporary relaxing of cgroup setting for vcpu hotplug
62135c2 virsh: use virConnectGetDomainCapabilities with maxvcpus

* Thu Sep 22 2016 user - 2.2.0-4.3200.0
- 62135c2 virsh: use virConnectGetDomainCapabilities with maxvcpus
238a70f Enable PCI Multifunction hotplug/unplug

* Tue Aug 30 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 1.3.4-2.pkvm3_1_1.3100.0
- Build August, 24th, 2016

* Wed Jun 15 2016 <baseuser@ibm.com>
  Log from git:
- 232c054965d4a5d97fae4b859e3c854f13412747 Enable seccomp sandbox by default in qemu.conf
- 6e397a036d72a99285724e90402e225055db5fa5 Free the entire slot when not using the multifunction
- 98f3db5878227f7eaedeee4d4377ddf739dffa82 Revert "util: set MAC address for VF via netlink message to PF+VF# when possible"
- a0123e85f86736ac6799e49e7e79a8ba0ee22901 Revert "util: don't use netlink to save/set mac for macvtap+passthrough+802.1Qbh"
- ceb4a0c152f4201f95223c703260d4d87f24bca2 Enable PCI Multifunction hotplug/unplug
- 23f6f531c0b96444a8ca8dca978b811d10c3938f Move the detach of PCI device to the beginnging of live hotplug
- 8f6f0942ec9d6bca32d101599a7b74ade0ce7920 Separate the hostdevice preparation and checks to a new funtion
- e6f2f3ca73aed4941182f579dc26d60d51e91627 Introduce virDomainPCIMultifunctionDeviceAddressAssign
- 2a5de69ed3a08b95813c45af8f0d1b5b8552c625 Introduce PCI Multifunction device parser
- 1cdb059fa12b4fef92fec7f891c4c706c9bc42ce Validate address in virDomainPCIAddressReleaseAddr
- 4b08e05651533c00682416a9873504965d746d25 Release address in function granularity than slot
- c70b04bc19069e9105f1ae293e06d18c16cf10f4 Revert "prevent hot unplugging multi function PCI device"
- 560630a198f7e880c3d9e81fa1197e26e08a2793 qemu: hotplug: Fix possible memory leak of props
- 2abf58779da7a74c3c0e305f01711987994c285c qemu: hotplug: Adjust error path for attach hostdev scsi disk
- 5b8957b69bc5e1ef6bc4615a0775a6d18739b8d8 qemu: hotplug: Adjust error path for attach virtio disk
- 4642f2878ece6a5e08d141d13017dacc5456096d qemu: hotplug: Adjust error path for attach scsi disk
- ed74598cebabeb1e8e326db4d5ea3c3c44a0abf3 qemu: Use qemuDomainSecretInfoPtr in qemuBuildNetworkDriveURI
- 3489ff99e6a5ed76da50bbc88363ca6f77d5be99 qemu: Introduce qemuDomainSecretHostdevPrepare and Destroy
- fc4ad07285e3a3343bc9c72d9d82092faac4f990 qemu: Introduce qemuDomainHostdevPrivatePtr
- 31b66c98dcd21e38884b9925c5f2a24ef0bdfda7 qemu: Introduce qemuDomainSecretPrepare and Destroy
- 014aa6769d2c5a47693d7e908add64e5790fb157 qemu: Introduce qemuDomainSecretInfo
- cc40b4de4b792a594e64835900f5505b27e74ed4 Change virDevicePCIAddress to virPCIDeviceAddress
- a4101a1bc1c399cae10bf641dffa834a836dea6d qemu: monitor: Kill legacy PCI hotplug code
- 15957c5b49a0b72a12af256c5a0b911058d52471 qemu: hotplug: Assume QEMU_CAPS_DEVICE in qemuDomainAttachControllerDevice
- 8fbd6d350fd65a94a0fea95b1d056e0cddf06745 qemu: hotplug: Assume QEMU_CAPS_DEVICE in qemuDomainDetachNetDevice
- fa3c931c1abb6a3703faf00e970b910731d8ae7b qemu: hotplug: Assume QEMU_CAPS_DEVICE in qemuDomainDetachHostPCIDevice
- 8dc5632702f54afc1c43f156c739bea6d12755e6 qemu: hotplug: Assume QEMU_CAPS_DEVICE in qemuDomainDetachControllerDevice
- 76b03e517d4fd1eb0d3773f79a888c03776169d1 qemu: hotplug: Assume QEMU_CAPS_DEVICE in qemuDomainDetachVirtioDiskDevice
- cb8765eadd443b47f63a9f12ea57f30cd7cdde83 qemu: hotplug: Assume QEMU_CAPS_DEVICE in qemuDomainAttachHostPCIDevice
- c92825db2509e3a1a53e05682e6da562e305f00a qemu: hotplug: Assume QEMU_CAPS_DEVICE in qemuDomainAttachNetDevice
- a313e0c545c6c388e60eee64e94e79ba123762eb qemu: hotplug: Assume QEMU_CAPS_DEVICE in qemuDomainAttachVirtioDiskDevice
- 8178abddcadeaa9af6535ba94ade1dec2574394c qemu: monitor: Kill legacy USB monitor code
- e9e18e59b726c014c11744756c7777a3caf77038 qemu: hotplug: Assume QEMU_CAPS_DEVICE in qemuDomainAttachHostUSBDevice
- dc460e3f96e2fd297d8d99bc38e0dd72c262cc07 qemu: hotplug: Assume QEMU_CAPS_DEVICE in qemuDomainAttachUSBMassStorageDevice
- ba2faf3c1757ce125b6502c47cc57c7b14b0d2bb qemu: remove default case from few typecasted enums
- c56c18fedd6aa484d5fa70f57e608a8422697f83 virsh: Pass the correct live/config xml to virshDomainDetachInterface.
- 50d99cbdb75ccf60858055e42fc317d1ca506073 virsh: Introduce virshDomainDetachInterface function
- 9d34c7dda5fa83bbad95278e7a07e7c73ec6a87e send default USB controller in xml to destination during migration
- 132f69b161fab4d435da382a4ae3ff5e2fb471c5 Revert "Send the default USB controller in xml to destination during migration"
- aab1a16be83b62ae11644d23bfb32364ae9774d0 domain_conf: fix migration/managedsave with usb keyboard
- 1b7c2d64cec803ec8ed6b17d28288875dd9f3ddf Merge version 'v1.3.4' into powerkvm-v3.1.1
- 52f1874602b76ac857630be5d91e7cd19948d1a1 Release of libvirt-1.3.4
- 50fc4b4bddfd6612674a5dd63a314426cf13837f Fix minor typos in messages
- 9b643ae824756d0ee3570c1f516397055e11864f Revert "qemu domain allow to set ip address, peer address and route"
- 70aa318b828269e5bba5ea0dd5491c3303773583 Revert "lxc domain allow to set peer address"
- 1d14b13f3b7b7222b44cfe403479d43355eb90bc Revert "libvirt domain xml allow to set peer address"
- 5ba48584fbc5079c0ddbc9e9a52c96d7bcef0761 rpc: Don't leak fd via CreateXMLWithFiles
- cdbbb93a968bdf297c0aa47a3f161ffd76136dca vz: fix disk enumeration
- 4d28d0931f87177a762f6a78cfdbcc2e30d6d4af virsh: Fix support for 64 migration options
- 55320c23dd163e75eb61ed6bea2f339ccfeff4f9 qemu: Regenerate VNC socket paths

* Sun May  1 2016 Daniel Veillard <veillard@redhat.com> - 1.3.4-1
- Lot of work on documentation
- Add support for migration data compression
- many bug fixes and various improvements

* Wed Apr  6 2016 Daniel Veillard <veillard@redhat.com> - 1.3.3-1
- perf events
- post-copy migration support
- NSS module
- a lot of various improvements, and large number of bugs fixes

* Tue Mar  1 2016 Daniel Veillard <veillard@redhat.com> - 1.3.2-1
- Various improvements for the Xen libxl driver
- virt-admin improvement
- Various improvements for the RDB volumes
- many bug fixes and improvements

* Sun Jan 17 2016 Daniel Veillard <veillard@redhat.com> - 1.3.1-1
- Various improvements for the Xen libxl driver
- rbd: Add support for wiping and cloning images to storage driver
- PCI hostdev improvements and fixes
- many bug fixes and improvements

* Wed Dec  9 2015 Daniel Veillard <veillard@redhat.com> - 1.3.0-1
- virt-admin and administration API
- various improvements in virtio devices support
- log daemon, logging improvements and protocol
- many bug fixes and improvements

* Wed Nov  4 2015 Daniel Veillard <veillard@redhat.com> - 1.2.21-1
- a number of improvements and bug fixes

* Fri Oct  2 2015 Daniel Veillard <veillard@redhat.com> - 1.2.20-1
- security fixes for CVE-2015-5247
- a number of improvements and bug fixes

* Wed Sep  2 2015 Daniel Veillard <veillard@redhat.com> - 1.2.19-1
- Big improvements on ppc64 support
- New virDomainRename API
- Support for QEMU new pci emulations
- a number of improvements and bug fixes

* Mon Aug  3 2015 Daniel Veillard <veillard@redhat.com> - 1.2.18-1
- libxl: support dom0
- a number of improvements and bug fixes

* Thu Jul  2 2015 Daniel Veillard <veillard@redhat.com> - 1.2.17-1
- numerous improvements and refactoring of the parallels driver
- hardening of vcpu code
- hardening of migration code
- a lot of improvement and bug fixes

* Mon Jun  1 2015 Daniel Veillard <veillard@redhat.com> - 1.2.16-1
- Introduce pci-serial
- Introduce virDomainSetUserPassword API
- libvirt: Introduce protected key mgmt ops
- add domain vmport feature
- various bug fixes and improvements

* Mon May  4 2015 Daniel Veillard <veillard@redhat.com> - 1.2.15-1
- Implement virDomainAddIOThread and virDomainDelIOThread
- libxl: Introduce configuration file for libxl driver
- Add VIR_DOMAIN_EVENT_ID_DEVICE_ADDED event
- various improvements to parallels driver
- a lot of improvement and bug fixes

* Thu Apr  2 2015 Daniel Veillard <veillard@redhat.com> - 1.2.14-1
- qemu: Implement memory device hotplug
- Implement public API for virDomainPinIOThread
- Implement public API for virDomainGetIOThreadsInfo
- SRIOV NIC offload feature discovery
- a lot of improvement and bug fixes

* Mon Mar  2 2015 Daniel Veillard <veillard@redhat.com> - 1.2.13-1
- lot of improvements around NUMA code
- a lot of improvement and bug fixes

* Tue Jan 27 2015 Daniel Veillard <veillard@redhat.com> - 1.2.12-1
- CVE-2015-0236: qemu: Check ACLs when dumping security info from snapshots
- CVE-2015-0236: qemu: Check ACLs when dumping security info from save image
- a lot of improvement and bug fixes

* Sat Dec 13 2014 Daniel Veillard <veillard@redhat.com> - 1.2.11-1
- CVE-2014-8131: Fix possible deadlock and segfault in qemuConnectGetAllDomainStats()
- CVE-2014-7823: dumpxml: security hole with migratable flag
- Implement public API for virDomainGetFSInfo
- Add define support for the new throttle options
- a number of improvements and bug fixes

* Mon Nov  3 2014 Daniel Veillard <veillard@redhat.com> - 1.2.10-1
- vbox: various drivers improvements
- libxl: various drivers improvements
- Internal driver refactoring
- a number of improvements and bug fixes

* Wed Oct  1 2014 Daniel Veillard <veillard@redhat.com> - 1.2.9-1
- CVE-2014-3657: domain_conf: fix domain deadlock
- CVE-2014-3633: qemu: blkiotune: Use correct definition when looking up disk
- Introduce virNodeAllocPages
- event: introduce new event for tunable values
- add migration support for OpenVZ driver
- Add support for fetching statistics of completed jobs
- many improvements and bug fixes

* Tue Sep  2 2014 Daniel Veillard <veillard@redhat.com> - 1.2.8-1
- blockcopy: virDomainBlockCopy with XML destination, typed params
- Introduce API for retrieving bulk domain stats
- Introduce virDomainOpenGraphicsFD API
- storage: ZFS support
- many improvements and bug fixes

* Sun Aug  3 2014 Daniel Veillard <veillard@redhat.com> - 1.2.7-1
- Introduce virConnectGetDomainCapabilities
- many improvements and bug fixes

* Wed Jul  2 2014 Daniel Veillard <veillard@redhat.com> - 1.2.6-1
- libxl: add migration support and fixes
- various improvements and fixes for NUMA
- many improvements and bug fixes

* Mon Jun  2 2014 Daniel Veillard <veillard@redhat.com> - 1.2.5-1
- LSN-2014-0003: Don't expand entities when parsing XML (security)
- Introduce virDomain{Get,Set}Time APIs
- Introduce virDomainFSFreeze() and virDomainFSThaw() public API
- various improvements and bug fixes

* Sun May  4 2014 Daniel Veillard <veillard@redhat.com> - 1.2.4-1
- various improvements and bug fixes
- lot of internal code refactoring

* Tue Apr  1 2014 Daniel Veillard <veillard@redhat.com> - 1.2.3-1
- add new virDomainCoreDumpWithFormat API
- conf: Introduce virDomainDeviceGetInfo API
- more features and fixes on bhyve driver
- lot of cleanups and improvement on the Xen driver
- a lot of various improvements and bug fixes

* Sun Mar  2 2014 Daniel Veillard <veillard@redhat.com> - 1.2.2-1
- add LXC from native conversion tool
- vbox: add support for v4.2.20+ and v4.3.4+
- Introduce Libvirt Wireshark dissector
- Fix CVE-2013-6456: Avoid unsafe use of /proc/$PID/root in LXC
- a lot of various improvements and bug fixes

* Thu Jan 16 2014 Daniel Veillard <veillard@redhat.com> - 1.2.1-1
- Fix s CVE-2014-0028 event: filter global events by domain:getattr ACL
- Fix CVE-2014-1447 Don't crash if a connection closes early
- Fix CVE-2013-6458-1 qemu: Do not access stale data in virDomainBlockStats
- Fix CVE-2013-6457 libxl: avoid crashing if calling `virsh numatune' on inactive domain
- Fix CVE-2013-6436: fix crash in lxcDomainGetMemoryParameters
- many doc and bug fixes and improvements

* Mon Dec  2 2013 Daniel Veillard <veillard@redhat.com> - 1.2.0-1
- Separation of python binding as libvirt-python srpm
- Add support for gluster pool
- vbox: add support for 4.3 APIs
- a number of doc, bug fixes and various improvements

* Mon Nov  4 2013 Daniel Veillard <veillard@redhat.com> - 1.1.4-1
- Add support for AArch64 architecture
- Various improvements on test code and test driver
- 4 security bug fixes
- a lot of bug fixes and various improvements

* Tue Oct  1 2013 Daniel Veillard <veillard@redhat.com> - 1.1.3-1
- VMware: Initial VMware Fusion support and various improvements
- libvirt: add new public API virConnectGetCPUModelNames
- various libxl driver improvements
- LXC many container driver improvement
- ARM cpu improvements
- 3 security bug fixes
- a lot of bug and leak fixes and various improvements

* Mon Sep  2 2013 Daniel Veillard <veillard@redhat.com> - 1.1.2-1
- various improvements to libxl driver
- systemd integration improvements
- Add flag to BaselineCPU API to return detailed CPU features
- Introduce a virt-login-shell binary
- conf: add startupPolicy attribute for harddisk
- various bug fixes and improvements including localizations

* Tue Jul 30 2013 Daniel Veillard <veillard@redhat.com> - 1.1.1-1
- Adding device removal or deletion events
- Introduce new domain create APIs to pass pre-opened FDs to LXC
- Add interface versions for Xen 4.3
- Add new public API virDomainSetMemoryStatsPeriod
- Various LXC improvements
- various bug fixes and improvements including localizations

* Mon Jul  1 2013 Daniel Veillard <veillard@redhat.com> - 1.1.0-1
- CVE-2013-2218: Fix crash listing network interfaces with filters
- Fine grained ACL support for the API
- Extensible migration APIs
- various improvements in the Xen driver
- agent based vCPU hotplug support
- various bug fixes and improvements including localizations

* Mon Jun  3 2013 Daniel Veillard <veillard@redhat.com> - 1.0.6-1
- Move VirtualBox driver into libvirtd
- Support for static routes on a virtual bridge
- Various improvement for hostdev SCSI support
- Switch to VIR_STRDUP and VIR_STRNDUP
- Various cleanups and improvement in Xen and LXC drivers
- various bug fixes and improvements including localizations

* Thu May  2 2013 Daniel Veillard <veillard@redhat.com> - 1.0.5-1
- add support for NVRAM device
- Add XML config for resource partitions
- Add support for TPM
- NPIV storage migration support
- various bug fixes and improvements including localizations

* Mon Apr  1 2013 Daniel Veillard <veillard@redhat.com> - 1.0.4-1
- qemu: support passthrough for iscsi disks
- various S390 improvements
- various LXC bugs fixes and improvements
- Add API for thread cancellation
- various bug fixes and improvements

* Tue Mar  5 2013 Daniel Veillard <veillard@redhat.com> - 1.0.3-1
- Introduce virDomainMigrate*CompressionCache APIs
- Introduce virDomainGetJobStats API
- Add basic support for VDI images
- Introduce API virNodeDeviceLookupSCSIHostByWWN
- Various locking improvements
- a lot of bug fixes and overall improvements

* Wed Jan 30 2013 Daniel Veillard <veillard@redhat.com> - 1.0.2-1
- LXC improvements
- S390 architecture improvement
- Power architecture improvement
- large Coverity report cleanups and associated bug fixes
- virTypedParams* APIs to helps with those data structures
- a lot of bug fixes and overall improvements

* Fri Nov  2 2012 Daniel Veillard <veillard@redhat.com> - 1.0.0-1
- virNodeGetCPUMap: Define public API
- Add systemd journal support
- Add a qemu capabilities cache manager
- USB migration support
- various improvement and fixes when using QMP QEmu interface
- Support for Xen 4.2
- Lot of localization enhancements
- a lot of bug fixes, improvements and portability work

* Mon Sep 24 2012 Daniel Veillard <veillard@redhat.com> - 0.10.2-1
- network: define new API virNetworkUpdate
- add support for QEmu sandbox support
- blockjob: add virDomainBlockCommit
- New APIs to get/set Node memory parameters
- new API virConnectListAllSecrets
- new API virConnectListAllNWFilters
- new API virConnectListAllNodeDevices
- parallels: add support of containers to the driver
- new API virConnectListAllInterfaces
- new API virConnectListAllNetworks
- new API virStoragePoolListAllVolumes
- Add PMSUSPENDED life cycle event
- new API virStorageListAllStoragePools
- Add per-guest S3/S4 state configuration
- qemu: Support for Block Device IO Limits
- a lot of bug fixes, improvements and portability work

* Fri Aug 31 2012 Daniel Veillard <veillard@redhat.com> - 0.10.1-1
- bugfixes and a brown paper bag

* Wed Aug 29 2012 Daniel Veillard <veillard@redhat.com> - 0.10.0-1
- agent: add qemuAgentArbitraryCommand() for general qemu agent command
- Introduce virDomainPinEmulator and virDomainGetEmulatorPinInfo functions
- network: use firewalld instead of iptables, when available
- network: make network driver vlan-aware
- esx: Implement network driver
- driver for parallels hypervisor
- Various LXC improvements
- Add virDomainGetHostname
- a lot of bug fixes, improvements and portability work

* Mon Jul  2 2012 Daniel Veillard <veillard@redhat.com> - 0.9.13-1
- S390: support for s390(x)
- snapshot: implement new APIs for esx and vbox
- snapshot: new query APIs and many improvements
- virsh: Allow users to reedit rejected XML
- nwfilter: add DHCP snooping
- Enable driver modules in libvirt RPM
- Default to enable driver modules for libvirtd
- storage backend: Add RBD (RADOS Block Device) support
- sVirt support for LXC domains inprovement
- a lot of bug fixes, improvements and portability work

* Mon May 14 2012 Daniel Veillard <veillard@redhat.com> - 0.9.12-1
- qemu: allow snapshotting of sheepdog and rbd disks
- blockjob: add new APIs
- a lot of bug fixes, improvements and portability work

* Tue Apr  3 2012 Daniel Veillard <veillard@redhat.com> - 0.9.11-1
- Add support for the suspend event
- Add support for event tray moved of removable disks
- qemu: Support numad
- cpustats: API, improvements and qemu support
- qemu: support type='hostdev' network devices at domain start
- Introduce virDomainPMWakeup API
- network: support Open vSwitch
- a number of snapshot improvements
- many improvements and bug fixes

* Mon Feb 13 2012 Daniel Veillard <veillard@redhat.com> - 0.9.10-1
- Add support for sVirt in the LXC driver
- block rebase: add new API virDomainBlockRebase
- API: Add api to set and get domain metadata
- virDomainGetDiskErrors public API
- conf: add rawio attribute to disk element of domain XML
- Add new public API virDomainGetCPUStats()
- Introduce virDomainPMSuspendForDuration API
- resize: add virStorageVolResize() API
- Add a virt-host-validate command to sanity check HV config
- Add new virDomainShutdownFlags API
- QEMU guest agent support
- many improvements and bug fixes

* Sat Jan  7 2012 Daniel Veillard <veillard@redhat.com> - 0.9.9-1
- Add API virDomain{S,G}etInterfaceParameters
- Add API virDomain{G, S}etNumaParameters
- Add support for ppc64 qemu
- Support Xen domctl v8
- many improvements and bug fixes

* Thu Dec  8 2011 Daniel Veillard <veillard@redhat.com> - 0.9.8-1
- Add support for QEMU 1.0
- Add preliminary PPC cpu driver
- Add new API virDomain{Set, Get}BlockIoTune
- block_resize: Define the new API
- Add a public API to invoke suspend/resume on the host
- various improvements for LXC containers
- Define keepalive protocol and add virConnectIsAlive API
- Add support for STP and VLAN filtering
- many improvements and bug fixes

* Tue Nov  8 2011 Daniel Veillard <veillard@redhat.com> - 0.9.7-1
- esx: support vSphere 5.x
- vbox: support for VirtualBox 4.1
- Introduce the virDomainOpenGraphics API
- Add AHCI support to qemu driver
- snapshot: many improvements and 2 new APIs
- api: Add public api for 'reset'
- many improvements and bug fixes

* Thu Sep 22 2011 Daniel Veillard <veillard@redhat.com> - 0.9.6-1
- Fix the qemu reboot bug and a few others bug fixes

* Tue Sep 20 2011 Daniel Veillard <veillard@redhat.com> - 0.9.5-1
- many snapshot improvements (Eric Blake)
- latency: Define new public API and structure (Osier Yang)
- USB2 and various USB improvements (Marc-André Lureau)
- storage: Add fs pool formatting (Osier Yang)
- Add public API for getting migration speed (Jim Fehlig)
- Add basic driver for Microsoft Hyper-V (Matthias Bolte)
- many improvements and bug fixes

* Wed Aug  3 2011 Daniel Veillard <veillard@redhat.com> - 0.9.4-1
- network bandwidth QoS control
- Add new API virDomainBlockPull*
- save: new API to manipulate save file images
- CPU bandwidth limits support
- allow to send NMI and key event to guests
- new API virDomainUndefineFlags
- Implement code to attach to external QEMU instances
- bios: Add support for SGA
- various missing python binding
- many improvements and bug fixes

* Mon Jul  4 2011 Daniel Veillard <veillard@redhat.com> - 0.9.3-1
- new API virDomainGetVcpupinInfo
- Add TXT record support for virtual DNS service
- Support reboots with the QEMU driver
- New API virDomainGetControlInfo API
- New API virNodeGetMemoryStats
- New API virNodeGetCPUTime
- New API for send-key
- New API virDomainPinVcpuFlags
- support multifunction PCI device
- lxc: various improvements
- many improvements and bug fixes

* Mon Jun  6 2011 Daniel Veillard <veillard@redhat.com> - 0.9.2-1
- Framework for lock manager plugins
- API for network config change transactions
- flags for setting memory parameters
- virDomainGetState public API
- qemu: allow blkstat/blkinfo calls during migration
- Introduce migration v3 API
- Defining the Screenshot public API
- public API for NMI injection
- Various improvements and bug fixes

* Thu May  5 2011 Daniel Veillard <veillard@redhat.com> - 0.9.1-1
- support various persistent domain updates
- improvements on memory APIs
- Add virDomainEventRebootNew
- various improvements to libxl driver
- Spice: support audio, images and stream compression
- Various improvements and bug fixes

* Mon Apr  4 2011 Daniel Veillard <veillard@redhat.com> - 0.9.0-1
- Support cputune cpu usage tuning
- Add public APIs for storage volume upload/download
- Add public API for setting migration speed on the fly
- Add libxenlight driver
- qemu: support migration to fd
- libvirt: add virDomain{Get,Set}BlkioParameters
- setmem: introduce a new libvirt API (virDomainSetMemoryFlags)
- Expose event loop implementation as a public API
- Dump the debug buffer to libvirtd.log on fatal signal
- Audit support
- Various improvements and bug fixes

* Thu Feb 17 2011 Daniel Veillard <veillard@redhat.com> - 0.8.8-1
- expose new API for sysinfo extraction
- cgroup blkio weight support
- smartcard device support
- qemu: Support per-device boot ordering
- Various improvements and bug fixes

* Tue Jan  4 2011 Daniel Veillard <veillard@redhat.com> - 0.8.7-1
- Preliminary support for VirtualBox 4.0
- IPv6 support
- Add VMware Workstation and Player driver driver
- Add network disk support
- Various improvements and bug fixes

* Tue Nov 30 2010 Daniel Veillard <veillard@redhat.com> - 0.8.6-1
- Add support for iSCSI target auto-discovery
- QED: Basic support for QED images
- remote console support
- support for SPICE graphics
- sysinfo and VMBIOS support
- virsh qemu-monitor-command
- various improvements and bug fixes

* Fri Oct 29 2010 Daniel Veillard <veillard@redhat.com> - 0.8.5-1
- Enable JSON and netdev features in QEMU >= 0.13
- framework for auditing integration
- framework DTrace/SystemTap integration
- Setting the number of vcpu at boot
- Enable support for nested SVM
- Virtio plan9fs filesystem QEMU
- Memory parameter controls
- various improvements and bug fixes

* Fri Sep 10 2010 Daniel Veillard <veillard@redhat.com> - 0.8.4-1
- big improvements to UML driver
- various improvements and bug fixes

* Wed Aug  4 2010 Daniel Veillard <veillard@redhat.com> - 0.8.3-1
- esx: Support vSphere 4.1
- Qemu arbitrary monitor commands
- Qemu Monitor API entry point
- various improvements and bug fixes

* Mon Jul  5 2010 Daniel Veillard <veillard@redhat.com> - 0.8.2-1
- phyp: adding support for IVM
- libvirt: introduce domainCreateWithFlags API
- add 802.1Qbh and 802.1Qbg switches handling
- Support for VirtualBox version 3.2
- Init script for handling guests on shutdown/boot
- qemu: live migration with non-shared storage for kvm

* Fri Apr 30 2010 Daniel Veillard <veillard@redhat.com> - 0.8.1-1
- Starts dnsmasq from libvirtd with --dhcp-hostsfile
- Add virDomainGetBlockInfo API to query disk sizing
- a lot of bug fixes and cleanups

* Mon Apr 12 2010 Daniel Veillard <veillard@redhat.com> - 0.8.0-1
- Snapshotting support (QEmu/VBox/ESX)
- Network filtering API
- XenAPI driver
- new APIs for domain events
- Libvirt managed save API
- timer subselection for domain clock
- synchronous hooks
- API to update guest CPU to host CPU
- virDomainUpdateDeviceFlags new API
- migrate max downtime API
- volume wiping API
- and many bug fixes

* Fri Mar  5 2010 Daniel Veillard <veillard@redhat.com> - 0.7.7-1
- macvtap support
- async job handling
- virtio channel
- computing baseline CPU
- virDomain{Attach,Detach}DeviceFlags
- assorted bug fixes and lots of cleanups

* Wed Feb  3 2010 Daniel Veillard <veillard@redhat.com> - 0.7.6-1

* Wed Dec 23 2009 Daniel Veillard <veillard@redhat.com> - 0.7.5-1
- Add new API virDomainMemoryStats
- Public API and domain extension for CPU flags
- vbox: Add support for version 3.1
- Support QEMU's virtual FAT block device driver
- a lot of fixes

* Fri Nov 20 2009 Daniel Veillard <veillard@redhat.com> - 0.7.3-1
- udev node device backend
- API to check object properties
- better QEmu monitor processing
- MAC address based port filtering for qemu
- support IPv6 and multiple addresses per interfaces
- a lot of fixes

* Tue Sep 15 2009 Daniel Veillard <veillard@redhat.com> - 0.7.1-1
- ESX, VBox driver updates
- mutipath support
- support for encrypted (qcow) volume
- compressed save image format for Qemu/KVM
- QEmu host PCI device hotplug support
- configuration of huge pages in guests
- a lot of fixes

* Wed Aug  5 2009 Daniel Veillard <veillard@redhat.com> - 0.7.0-1
- ESX, VBox3, Power Hypervisor drivers
- new net filesystem glusterfs
- Storage cloning for LVM and Disk backends
- interface implementation based on netcf
- Support cgroups in QEMU driver
- QEmu hotplug NIC support
- a lot of fixes

* Fri Jul  3 2009 Daniel Veillard <veillard@redhat.com> - 0.6.5-1
- release of 0.6.5

* Fri May 29 2009 Daniel Veillard <veillard@redhat.com> - 0.6.4-1
- release of 0.6.4
- various new APIs

* Fri Apr 24 2009 Daniel Veillard <veillard@redhat.com> - 0.6.3-1
- release of 0.6.3
- VirtualBox driver

* Fri Apr  3 2009 Daniel Veillard <veillard@redhat.com> - 0.6.2-1
- release of 0.6.2

* Wed Mar  4 2009 Daniel Veillard <veillard@redhat.com> - 0.6.1-1
- release of 0.6.1

* Sat Jan 31 2009 Daniel Veillard <veillard@redhat.com> - 0.6.0-1
- release of 0.6.0

* Tue Nov 25 2008 Daniel Veillard <veillard@redhat.com> - 0.5.0-1
- release of 0.5.0

* Tue Sep 23 2008 Daniel Veillard <veillard@redhat.com> - 0.4.6-1
- release of 0.4.6

* Mon Sep  8 2008 Daniel Veillard <veillard@redhat.com> - 0.4.5-1
- release of 0.4.5

* Wed Jun 25 2008 Daniel Veillard <veillard@redhat.com> - 0.4.4-1
- release of 0.4.4
- mostly a few bug fixes from 0.4.3

* Thu Jun 12 2008 Daniel Veillard <veillard@redhat.com> - 0.4.3-1
- release of 0.4.3
- lots of bug fixes and small improvements

* Tue Apr  8 2008 Daniel Veillard <veillard@redhat.com> - 0.4.2-1
- release of 0.4.2
- lots of bug fixes and small improvements

* Mon Mar  3 2008 Daniel Veillard <veillard@redhat.com> - 0.4.1-1
- Release of 0.4.1
- Storage APIs
- xenner support
- lots of assorted improvements, bugfixes and cleanups
- documentation and localization improvements

* Tue Dec 18 2007 Daniel Veillard <veillard@redhat.com> - 0.4.0-1
- Release of 0.4.0
- SASL based authentication
- PolicyKit authentication
- improved NUMA and statistics support
- lots of assorted improvements, bugfixes and cleanups
- documentation and localization improvements

* Sun Sep 30 2007 Daniel Veillard <veillard@redhat.com> - 0.3.3-1
- Release of 0.3.3
- Avahi support
- NUMA support
- lots of assorted improvements, bugfixes and cleanups
- documentation and localization improvements

* Tue Aug 21 2007 Daniel Veillard <veillard@redhat.com> - 0.3.2-1
- Release of 0.3.2
- API for domains migration
- APIs for collecting statistics on disks and interfaces
- lots of assorted bugfixes and cleanups
- documentation and localization improvements

* Tue Jul 24 2007 Daniel Veillard <veillard@redhat.com> - 0.3.1-1
- Release of 0.3.1
- localtime clock support
- PS/2 and USB input devices
- lots of assorted bugfixes and cleanups
- documentation and localization improvements

* Mon Jul  9 2007 Daniel Veillard <veillard@redhat.com> - 0.3.0-1
- Release of 0.3.0
- Secure remote access support
- unification of daemons
- lots of assorted bugfixes and cleanups
- documentation and localization improvements

* Fri Jun  8 2007 Daniel Veillard <veillard@redhat.com> - 0.2.3-1
- Release of 0.2.3
- lot of assorted bugfixes and cleanups
- support for Xen-3.1
- new scheduler API

* Tue Apr 17 2007 Daniel Veillard <veillard@redhat.com> - 0.2.2-1
- Release of 0.2.2
- lot of assorted bugfixes and cleanups
- preparing for Xen-3.0.5

* Thu Mar 22 2007 Jeremy Katz <katzj@redhat.com> - 0.2.1-2.fc7
- don't require xen; we don't need the daemon and can control non-xen now
- fix scriptlet error (need to own more directories)
- update description text

* Fri Mar 16 2007 Daniel Veillard <veillard@redhat.com> - 0.2.1-1
- Release of 0.2.1
- lot of bug and portability fixes
- Add support for network autostart and init scripts
- New API to detect the virtualization capabilities of a host
- Documentation updates

* Fri Feb 23 2007 Daniel P. Berrange <berrange@redhat.com> - 0.2.0-4.fc7
- Fix loading of guest & network configs

* Fri Feb 16 2007 Daniel P. Berrange <berrange@redhat.com> - 0.2.0-3.fc7
- Disable kqemu support since its not in Fedora qemu binary
- Fix for -vnc arg syntax change in 0.9.0  QEMU

* Thu Feb 15 2007 Daniel P. Berrange <berrange@redhat.com> - 0.2.0-2.fc7
- Fixed path to qemu daemon for autostart
- Fixed generation of <features> block in XML
- Pre-create config directory at startup

* Wed Feb 14 2007 Daniel Veillard <veillard@redhat.com> 0.2.0-1.fc7
- support for KVM and QEmu
- support for network configuration
- assorted fixes

* Mon Jan 22 2007 Daniel Veillard <veillard@redhat.com> 0.1.11-1.fc7
- finish inactive Xen domains support
- memory leak fix
- RelaxNG schemas for XML configs

* Wed Dec 20 2006 Daniel Veillard <veillard@redhat.com> 0.1.10-1.fc7
- support for inactive Xen domains
- improved support for Xen display and vnc
- a few bug fixes
- localization updates

* Thu Dec  7 2006 Jeremy Katz <katzj@redhat.com> - 0.1.9-2
- rebuild against python 2.5

* Wed Nov 29 2006 Daniel Veillard <veillard@redhat.com> 0.1.9-1
- better error reporting
- python bindings fixes and extensions
- add support for shareable drives
- add support for non-bridge style networking
- hot plug device support
- added support for inactive domains
- API to dump core of domains
- various bug fixes, cleanups and improvements
- updated the localization

* Tue Nov  7 2006 Daniel Veillard <veillard@redhat.com> 0.1.8-3
- it's pkgconfig not pgkconfig !

* Mon Nov  6 2006 Daniel Veillard <veillard@redhat.com> 0.1.8-2
- fixing spec file, added %%dist, -devel requires pkgconfig and xen-devel
- Resolves: rhbz#202320

* Mon Oct 16 2006 Daniel Veillard <veillard@redhat.com> 0.1.8-1
- fix missing page size detection code for ia64
- fix mlock size when getting domain info list from hypervisor
- vcpu number initialization
- don't label crashed domains as shut off
- fix virsh man page
- blktapdd support for alternate drivers like blktap
- memory leak fixes (xend interface and XML parsing)
- compile fix
- mlock/munlock size fixes

* Fri Sep 22 2006 Daniel Veillard <veillard@redhat.com> 0.1.7-1
- Fix bug when running against xen-3.0.3 hypercalls
- Fix memory bug when getting vcpus info from xend

* Fri Sep 22 2006 Daniel Veillard <veillard@redhat.com> 0.1.6-1
- Support for localization
- Support for new Xen-3.0.3 cdrom and disk configuration
- Support for setting VNC port
- Fix bug when running against xen-3.0.2 hypercalls
- Fix reconnection problem when talking directly to http xend

* Tue Sep  5 2006 Jeremy Katz <katzj@redhat.com> - 0.1.5-3
- patch from danpb to support new-format cd devices for HVM guests

* Tue Sep  5 2006 Daniel Veillard <veillard@redhat.com> 0.1.5-2
- reactivating ia64 support

* Tue Sep  5 2006 Daniel Veillard <veillard@redhat.com> 0.1.5-1
- new release
- bug fixes
- support for new hypervisor calls
- early code for config files and defined domains

* Mon Sep  4 2006 Daniel Berrange <berrange@redhat.com> - 0.1.4-5
- add patch to address dom0_ops API breakage in Xen 3.0.3 tree

* Mon Aug 28 2006 Jeremy Katz <katzj@redhat.com> - 0.1.4-4
- add patch to support paravirt framebuffer in Xen

* Mon Aug 21 2006 Daniel Veillard <veillard@redhat.com> 0.1.4-3
- another patch to fix network handling in non-HVM guests

* Thu Aug 17 2006 Daniel Veillard <veillard@redhat.com> 0.1.4-2
- patch to fix virParseUUID()

* Wed Aug 16 2006 Daniel Veillard <veillard@redhat.com> 0.1.4-1
- vCPUs and affinity support
- more complete XML, console and boot options
- specific features support
- enforced read-only connections
- various improvements, bug fixes

* Wed Aug  2 2006 Jeremy Katz <katzj@redhat.com> - 0.1.3-6
- add patch from pvetere to allow getting uuid from libvirt

* Wed Aug  2 2006 Jeremy Katz <katzj@redhat.com> - 0.1.3-5
- build on ia64 now

* Thu Jul 27 2006 Jeremy Katz <katzj@redhat.com> - 0.1.3-4
- don't BR xen, we just need xen-devel

* Thu Jul 27 2006 Daniel Veillard <veillard@redhat.com> 0.1.3-3
- need rebuild since libxenstore is now versionned

* Mon Jul 24 2006 Mark McLoughlin <markmc@redhat.com> - 0.1.3-2
- Add BuildRequires: xen-devel

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 0.1.3-1.1
- rebuild

* Tue Jul 11 2006 Daniel Veillard <veillard@redhat.com> 0.1.3-1
- support for HVM Xen guests
- various bugfixes

* Mon Jul  3 2006 Daniel Veillard <veillard@redhat.com> 0.1.2-1
- added a proxy mechanism for read only access using httpu
- fixed header includes paths

* Wed Jun 21 2006 Daniel Veillard <veillard@redhat.com> 0.1.1-1
- extend and cleanup the driver infrastructure and code
- python examples
- extend uuid support
- bug fixes, buffer handling cleanups
- support for new Xen hypervisor API
- test driver for unit testing
- virsh --conect argument

* Mon Apr 10 2006 Daniel Veillard <veillard@redhat.com> 0.1.0-1
- various fixes
- new APIs: for Node information and Reboot
- virsh improvements and extensions
- documentation updates and man page
- enhancement and fixes of the XML description format

* Tue Feb 28 2006 Daniel Veillard <veillard@redhat.com> 0.0.6-1
- added error handling APIs
- small bug fixes
- improve python bindings
- augment documentation and regression tests

* Thu Feb 23 2006 Daniel Veillard <veillard@redhat.com> 0.0.5-1
- new domain creation API
- new UUID based APIs
- more tests, documentation, devhelp
- bug fixes

* Fri Feb 10 2006 Daniel Veillard <veillard@redhat.com> 0.0.4-1
- fixes some problems in 0.0.3 due to the change of names

* Wed Feb  8 2006 Daniel Veillard <veillard@redhat.com> 0.0.3-1
- changed library name to libvirt from libvir, complete and test the python
  bindings

* Sun Jan 29 2006 Daniel Veillard <veillard@redhat.com> 0.0.2-1
- upstream release of 0.0.2, use xend, save and restore added, python bindings
  fixed

* Wed Nov  2 2005 Daniel Veillard <veillard@redhat.com> 0.0.1-1
- created
