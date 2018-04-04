%global commit          %{?git_commit_id}
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitcommittag    .git%{shortcommit}

# Implement magicdirs for ibm8 kernel configs
##{lua:
#  sourcedir = rpm.expand("%{_sourcedir}")
#  configdir = sourcedir.."/ibm8_configs"
#  if posix.access(configdir, "x") then
#    os.execute("cd "..configdir.." && /bin/tar -zcf "..sourcedir.."/ibm8_configs.tar.gz *")
#  end
#}

# We have to override the new %%install behavior because, well... the kernel is special.
%global __spec_install_pre %{___build_pre}

# Hack to create source package.  We create the appropriate tarball right in
# the prep section manually
%define ibm_prep_post %{nil}

Summary: The Linux kernel

# The kernel tarball/base version
#define rheltarball %{version}-%{release}.el7

# What parts do we want to build?  We must build at least one kernel.
# These are the kernels that are built IF the architecture allows it.
# All should default to 1 (enabled) and be flipped to 0 (disabled)
# by later arch-specific checks.

# The following build options are enabled by default.
# Use either --without <opt> in your rpmbuild command or force values
# to 0 in here to disable them.
#
# kernel
%define with_default   %{?_without_default:   0} %{?!_without_default:   1}
# kernel-debug
%define with_debug     %{?_without_debug:     0} %{?!_without_debug:     1}
# kernel-doc
%define with_doc       %{?_without_doc:       0} %{?!_without_doc:       1}
# kernel-headers
%define with_headers   %{?_without_headers:   0} %{?!_without_headers:   1}
# perf
#define with_perf      %{?_without_perf:      0} %{?!_without_perf:      1}
%define with_perf      1
# tools
%define with_tools     %{?_without_tools:     0} %{?!_without_tools:     1}
# kernel-debuginfo
#define with_debuginfo %{?_without_debuginfo: 0} %{?!_without_debuginfo: 1}
%define with_debuginfo 1
# kernel-kdump (only for s390x)
%define with_kdump     %{?_without_kdump:     0} %{?!_without_kdump:     0}
# kernel-bootwrapper (for creating zImages from kernel + initrd)
%define with_bootwrapper %{?_without_bootwrapper: 0} %{?!_without_bootwrapper: 0}
# kernel-abi-whitelists
%define with_kernel_abi_whitelists %{?_with_kernel_abi_whitelists: 0} %{?!_with_kernel_abi_whitelists: 0}
# IBM default uImage to 0, set accordingly for ppcnf
%define with_uimage    %{?_without_uimage:    0} %{?!_without_uimage:    0}
# IBM default dtb to 0, set accordingly for arm.
%define with_dtb    %{?_without_dtb:    0} %{?!_without_dtb:    0}

# If a kernel doesn't have CONFIG_MODULES=y, don't build and package modules
%define with_modules %(case "%{?repo}" in (.ibm_snd_sdn*) echo 0;; (*) echo 1;; esac)

# In RHEL, we always want the doc build failing to build to be a failure,
# which means settings this to false.
%define doc_build_fail false

# Additional options for user-friendly one-off kernel building:
#
# Only build the base kernel (--with baseonly):
%define with_baseonly  %{?_with_baseonly:     1} %{?!_with_baseonly:     0}
# Only build the debug kernel (--with dbgonly):
%define with_dbgonly   %{?_with_dbgonly:      1} %{?!_with_dbgonly:      0}

# Control whether we perform a compat. check against published ABI.
# IBM disabling kabichk
%define with_kabichk   %{?_without_kabichk:   0} %{?!_without_kabichk:   0}

# should we do C=1 builds with sparse
%define with_sparse    %{?_with_sparse:       1} %{?!_with_sparse:       0}

# Cross compile requested?
%define with_cross    %{?_with_cross:         1} %{?!_with_cross:        0}

# Set debugbuildsenabled to 1 for production (build separate debug kernels)
#  and 0 for rawhide (all kernels are debug kernels).
# See also 'make debug' and 'make release'. RHEL only ever does 1.
%define debugbuildsenabled 1

%define make_target bzImage

# Kernel Version Release + Arch -> KVRA
%define KVRA %{version}-%{release}.%{_target_cpu}
%define hdrarch %{_target_cpu}
%define asmarch %{_target_cpu}
%define cross_target %{_target_cpu}

%if !%{debugbuildsenabled}
%define with_debug 0
%endif

%if !%{with_debuginfo}
%define _enable_debug_packages 0
%endif
%define debuginfodir /usr/lib/debug

# if requested, only build base kernel
%if %{with_baseonly}
%define with_debug 0
%define with_kdump 0
%endif

# if requested, only build debug kernel
%if %{with_dbgonly}
%define with_default 0
%define with_kdump 0
%define with_tools 0
%define with_perf 0
%endif

# These arches install vdso/ directories.
%define vdso_arches %{all_x86} x86_64 ppc ppc64 ppc64le s390 s390x

# Overrides for generic default options

# only build kernel-debug on x86_64, s390x, ppc64 ppc64le
# IBM FIXME: ifnarch x86_64 s390x ppc64 ppcnf %{arm}
%ifnarch x86_64 s390x ppc64 ppc64le ppcnf
%define with_debug 0
%endif

# only package docs noarch
%ifnarch noarch
%define with_doc 0
%define with_kernel_abi_whitelists 0
%endif

# don't build noarch kernels or headers (duh)
%ifarch noarch
%define with_default 0
%define with_headers 0
%define with_tools 0
%define with_perf 0
%define all_arch_configs kernel-%{version}-*.config
%endif

# sparse blows up on ppc64
%ifarch ppc64 ppc64le ppc
%define with_sparse 0
%endif

# Per-arch tweaks

%ifarch i686
%define asmarch x86
%define hdrarch i386
%endif

%ifarch x86_64
%define asmarch x86
%define all_arch_configs kernel-%{version}-x86_64*.config
%define image_install_path boot
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch ppc
%define asmarch powerpc
%define hdrarch powerpc
%endif

%ifarch ppc64 ppc64le
%define asmarch powerpc
%define hdrarch powerpc
%define all_arch_configs kernel-%{version}-ppc64*.config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%define with_bootwrapper 1
%define cross_target powerpc64
#define kcflags -O3
%define kcflags -mtune=power8 -mcpu=power8
%endif

%ifarch s390x
%define asmarch s390
%define hdrarch s390
%define all_arch_configs kernel-%{version}-s390x*.config
%define image_install_path boot
%define kernel_image arch/s390/boot/bzImage
%define with_tools 0
%define with_kdump 1
%endif

#cross compile make
%if %{with_cross}
%define cross_opts CROSS_COMPILE=%{cross_target}-linux-gnu-
%define with_perf 0
%define with_tools 0
%endif

# Base cross arches
%ifarch ppc476
%define asmarch powerpc
%define hdrarch powerpc
%define all_arch_configs kernel-%{version}-ppc476.config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%define with_uimage 1
%define uimage_target "zImage uImage"
%endif

%ifarch ppcnf
%define asmarch powerpc
%define hdrarch powerpc
%define all_arch_configs kernel-%{version}-ppcnf*.config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%define with_tools 0
%define with_uimage 1
%define uimage_target "zImage uImage"
%endif

%ifarch %{arm}
%define all_arch_configs kernel-%{version}-arm*.config
%define image_install_path boot
%define asmarch arm
%define hdrarch arm
%define pae lpae
%define make_target bzImage
%define kernel_image arch/arm/boot/zImage
# http://lists.infradead.org/pipermail/linux-arm-kernel/2012-March/091404.html
%define kernel_mflags KALLSYMS_EXTRA_PASS=1
%define with_tools 0
%define with_dtb 1
%endif

%if 0%{?cross_build}
%define with_fips 0
%define with_sparse 0
%endif

# IBM: override above options for Base as necessary
%if 0%{?ibm}
%global signmodules 0
%define with_doc 0
%define doc_build_fail true
%endif

# Should make listnewconfig fail if there's config options
# printed out?
# IBM will disable this for now
%define listnewconfig_fail 0

# To temporarily exclude an architecture from being built, add it to
# %%nobuildarches. Do _NOT_ use the ExclusiveArch: line, because if we
# don't build kernel-headers then the new build system will no longer let
# us use the previous build of that package -- it'll just be completely AWOL.
# Which is a BadThing(tm).

# We only build kernel-headers on the following...
%define nobuildarches i686 s390 ppc ppc476 armv7hl

%ifarch %nobuildarches
%define with_default 0
%define with_debuginfo 0
%define with_kdump 0
%define with_tools 0
%define with_perf 0
%define _enable_debug_packages 0
%endif

# Architectures we build tools/cpupower on
%define cpupowerarchs x86_64 ppc64 ppc64le

#
# Three sets of minimum package version requirements in the form of Conflicts:
# to versions below the minimum
#

#
# First the general kernel 2.6 required versions as per
# Documentation/Changes
#
%define kernel_dot_org_conflicts  ppp < 2.4.3-3, isdn4k-utils < 3.2-32, nfs-utils < 1.0.7-12, e2fsprogs < 1.37-4, util-linux < 2.12, jfsutils < 1.1.7-2, reiserfs-utils < 3.6.19-2, xfsprogs < 2.6.13-4, procps < 3.2.5-6.3, oprofile < 0.9.1-2, device-mapper-libs < 1.02.63-2, mdadm < 3.2.1-5

#
# Then a series of requirements that are distribution specific, either
# because we add patches for something, or the older versions have
# problems with the newer kernel or lack certain things that make
# integration in the distro harder than needed.
#
%define package_conflicts initscripts < 7.23, udev < 063-6, iptables < 1.3.2-1, ipw2200-firmware < 2.4, iwl4965-firmware < 228.57.2, selinux-policy-targeted < 1.25.3-14, squashfs-tools < 4.0, wireless-tools < 29-3

# We moved the drm include files into kernel-headers, make sure there's
# a recent enough libdrm-devel on the system that doesn't have those.
%define kernel_headers_conflicts libdrm-devel < 2.4.0-0.15

#
# Packages that need to be installed before the kernel is, because the %%post
# scripts use them.
#
%define kernel_prereq  fileutils, module-init-tools >= 3.16-2, initscripts >= 8.11.1-1, grubby >= 8.28-2
%define initrd_prereq  dracut >= 001-7

%define prerelease %{nil}

Name: kernel%{?variant}
Group: System Environment/Kernel
License: GPLv2
URL: http://www.kernel.org/
Version: 4.16.0
Release: 2%{?prerelease}%{?extraver}%{gitcommittag}%{?dist}
# DO NOT CHANGE THE 'ExclusiveArch' LINE TO TEMPORARILY EXCLUDE AN ARCHITECTURE BUILD.
# SET %%nobuildarches (ABOVE) INSTEAD
ExclusiveArch: noarch i686 x86_64 ppc ppc64 ppc64le s390 s390x %{arm} ppcnf ppc476
ExclusiveOS: Linux

#
# This macro does requires, provides, conflicts, obsoletes for a kernel package.
#	%%kernel_reqprovconf <subpackage>
# It uses any kernel_<subpackage>_conflicts and kernel_<subpackage>_obsoletes
# macros defined above.
#
%define kernel_reqprovconf \
Provides: kernel = %{version}-%{release}\
Provides: kernel-%{_target_cpu} = %{version}-%{release}%{?1:.%{1}}\
Provides: kernel-drm = 4.3.0\
Provides: kernel-drm-nouveau = 16\
Provides: kernel-modeset = 1\
Provides: kernel-uname-r = %{KVRA}%{?1:.%{1}}\
Requires(pre): %{kernel_prereq}\
Requires(pre): %{initrd_prereq}\
Requires(pre): linux-firmware >= 20140911\
Requires(post): %{_sbindir}/new-kernel-pkg\
Requires(preun): %{_sbindir}/new-kernel-pkg\
Conflicts: %{kernel_dot_org_conflicts}\
Conflicts: %{package_conflicts}\
%{expand:%%{?kernel%{?1:_%{1}}_conflicts:Conflicts: %%{kernel%{?1:_%{1}}_conflicts}}}\
%{expand:%%{?kernel%{?1:_%{1}}_obsoletes:Obsoletes: %%{kernel%{?1:_%{1}}_obsoletes}}}\
%{expand:%%{?kernel%{?1:_%{1}}_provides:Provides: %%{kernel%{?1:_%{1}}_provides}}}\
# We can't let RPM do the dependencies automatic because it'll then pick up\
# a correct but undesirable perl dependency from the module headers which\
# isn't required for the kernel proper to function\
AutoReq: no\
AutoProv: yes\
%{nil}


%kernel_reqprovconf

#
# List the packages used during the kernel build
#
BuildRequires: module-init-tools, patch >= 2.5.4, bash >= 2.03, sh-utils, tar
BuildRequires: xz, findutils, gzip, m4, perl, make >= 3.78, diffutils, gawk
BuildRequires: gcc >= 3.4.2, binutils >= 2.12, system-rpm-config >= 9.1.0-55
BuildRequires: hostname, net-tools, bc
BuildRequires: xmlto, asciidoc
BuildRequires: openssl
BuildRequires: openssl-devel
%{!?cross_build:BuildRequires: hmaccalc}
%{!?cross_build:BuildRequires: python-devel, perl(ExtUtils::Embed)}
BuildRequires: newt-devel
%ifarch x86_64
BuildRequires: pesign >= 0.109-4
%endif
%if %{with_sparse}
BuildRequires: sparse >= 0.4.1
%endif
%if %{with_perf}
BuildRequires: elfutils-devel zlib-devel binutils-devel bison flex
BuildRequires: audit-libs-devel
%ifnarch s390 s390x
%{!?cross_build:BuildRequires: numactl-devel}
%endif
%endif
%if %{with_tools}
BuildRequires: pciutils-devel gettext ncurses-devel
%endif
%if %{with_debuginfo}
# Fancy new debuginfo generation introduced in Fedora 8/RHEL 6.
# The -r flag to find-debuginfo.sh invokes eu-strip --reloc-debug-sections
# which reduces the number of relocations in kernel module .ko.debug files and
# was introduced with rpm 4.9 and elfutils 0.153.
BuildRequires: rpm-build >= 4.9.0-1, elfutils >= 0.153-1, lzma
%define debuginfo_args --strict-build-id -r
%endif
%ifarch s390x
# required for zfcpdump
BuildRequires: glibc-static
%endif


%if 0%{?ibm}
BuildRequires: fakeroot-tools
BuildRequires: flex
%{?cross_build:BuildRequires: uboot-tools}

# IBM: added for ease of configuration
BuildRequires: ncurses-devel
%{!?cross_build:BuildRequires: vim-minimal}
%endif

Source0: %{name}.tar.gz

Source11: x509.genkey

Source12: merge.pl
Source13: mod-extra.list
Source14: mod-extra.sh
Source18: mod-sign.sh
Source90: filter-x86_64.sh
Source91: filter-armv7hl.sh
Source92: filter-i686.sh
Source93: filter-aarch64.sh
Source95: filter-ppc64.sh
Source96: filter-ppc64le.sh
Source97: filter-s390x.sh
Source98: filter-ppc64p7.sh
Source99: filter-modules.sh
%define modsign_cmd %{SOURCE18}

Source19: Makefile.release
Source20: Makefile.config
Source21: config-debug
Source22: config-nodebug
Source23: config-generic
Source24: config-no-extra

Source30: config-x86-generic
Source31: config-i686-PAE
Source32: config-x86-32-generic

Source40: config-x86_64-generic

Source50: config-powerpc-generic
Source53: config-powerpc64
Source54: config-powerpc64p7
Source55: config-powerpc64le

Source70: config-s390x

Source100: config-arm-generic

# Unified ARM kernels
Source101: config-armv7-generic
Source102: config-armv7
Source103: config-armv7-lpae

Source110: config-arm64

# This file is intentionally left empty in the stock kernel. Its a nicety
# added for those wanting to do custom rebuilds with altered config opts.
Source1000: config-local
Source1001: hostos-minimal.config

# Sources for kernel-tools
Source2000: cpupower.service
Source2001: cpupower.config

BuildRoot: %{_tmppath}/kernel-%{KVRA}-root

#atch999: fix.script.location.patch

%description
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system: memory allocation, process allocation, device
input and output, etc.


%package doc
Summary: Various documentation bits found in the kernel source
Group: Documentation
%description doc
This package contains documentation files from the kernel
source. Various bits of information about the Linux kernel and the
device drivers shipped with it are documented in these files.

You'll want to install this package if you need a reference to the
options that can be passed to Linux kernel modules at load time.


%package headers
Summary: Header files for the Linux kernel for use by glibc
Group: Development/System
Obsoletes: glibc-kernheaders < 3.0-46
Provides: glibc-kernheaders = 3.0-46
%description headers
Kernel-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package bootwrapper
Summary: Boot wrapper files for generating combined kernel + initrd images
Group: Development/System
Requires: gzip binutils
%description bootwrapper
Kernel-bootwrapper contains the wrapper code which makes bootable "zImage"
files combining both kernel and initial ramdisk.

%package debuginfo-common-%{_target_cpu}
Summary: Kernel source files used by %{name}-debuginfo packages
Group: Development/Debug
AutoReqProv: no
%description debuginfo-common-%{_target_cpu}
This package is required by %{name}-debuginfo subpackages.
It provides the kernel source files common to all builds.

%if %{with_perf}
%package -n perf
Summary: Performance monitoring for the Linux kernel
Group: Development/System
License: GPLv2
%description -n perf
This package contains the perf tool, which enables performance monitoring
of the Linux kernel.

%package -n perf-debuginfo
Summary: Debug information for package perf
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n perf-debuginfo
This package provides debug information for the perf package.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{_bindir}/perf(\.debug)?|.*%%{_libexecdir}/perf-core/.*|XXX' -o perf-debuginfo.list}

%if ! 0%{?cross_build}

%package -n python-perf
Summary: Python bindings for apps which will manipulate perf events
Group: Development/Libraries
%description -n python-perf
The python-perf package contains a module that permits applications
written in the Python programming language to use the interface
to manipulate perf events.

%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%package -n python-perf-debuginfo
Summary: Debug information for package perf python bindings
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n python-perf-debuginfo
This package provides debug information for the perf python bindings.

# the python_sitearch macro should already be defined from above
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{python_sitearch}/perf.so(\.debug)?|XXX' -o python-perf-debuginfo.list}

%endif # ! cross_build
%endif # with_perf

%if %{with_tools}

%package -n kernel-tools
Summary: Assortment of tools for the Linux kernel
Group: Development/System
License: GPLv2
Provides:  cpupowerutils = 1:009-0.6.p1
Obsoletes: cpupowerutils < 1:009-0.6.p1
Provides:  cpufreq-utils = 1:009-0.6.p1
Provides:  cpufrequtils = 1:009-0.6.p1
Obsoletes: cpufreq-utils < 1:009-0.6.p1
Obsoletes: cpufrequtils < 1:009-0.6.p1
Obsoletes: cpuspeed < 1:2.0
Requires: kernel-tools-libs = %{version}-%{release}
%description -n kernel-tools
This package contains the tools/ directory from the kernel source
and the supporting documentation.

%package -n kernel-tools-libs
Summary: Libraries for the kernels-tools
Group: Development/System
License: GPLv2
%description -n kernel-tools-libs
This package contains the libraries built from the tools/ directory
from the kernel source.

%package -n kernel-tools-libs-devel
Summary: Assortment of tools for the Linux kernel
Group: Development/System
License: GPLv2
Requires: kernel-tools = %{version}-%{release}
Provides:  cpupowerutils-devel = 1:009-0.6.p1
Obsoletes: cpupowerutils-devel < 1:009-0.6.p1
Requires: kernel-tools-libs = %{version}-%{release}
Provides: kernel-tools-devel
%description -n kernel-tools-libs-devel
This package contains the development files for the tools/ directory from
the kernel source.

%package -n kernel-tools-debuginfo
Summary: Debug information for package kernel-tools
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n kernel-tools-debuginfo
This package provides debug information for package kernel-tools.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{_bindir}/centrino-decode(\.debug)?|.*%%{_bindir}/powernow-k8-decode(\.debug)?|.*%%{_bindir}/cpupower(\.debug)?|.*%%{_libdir}/libcpupower.*|.*%%{_libdir}/libcpupower.*|.*%%{_bindir}/turbostat(\.debug)?|.*%%{_bindir}/x86_energy_perf_policy(\.debug)?|.*%%{_bindir}/tmon(\.debug)?|XXX' -o kernel-tools-debuginfo.list}

%endif # with_tools


#
# This macro creates a kernel-<subpackage>-debuginfo package.
#	%%kernel_debuginfo_package <subpackage>
#
%define kernel_debuginfo_package() \
%package %{?1:%{1}-}debuginfo\
Summary: Debug information for package %{name}%{?1:-%{1}}\
Group: Development/Debug\
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}\
Provides: %{name}%{?1:-%{1}}-debuginfo-%{_target_cpu} = %{version}-%{release}\
AutoReqProv: no\
%description -n %{name}%{?1:-%{1}}-debuginfo\
This package provides debug information for package %{name}%{?1:-%{1}}.\
This is required to use SystemTap with %{name}%{?1:-%{1}}-%{KVRA}.\
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '/.*/%%{KVRA}%{?1:\.%{1}}/.*|/.*%%{KVRA}%{?1:\.%{1}}(\.debug)?' -o debuginfo%{?1}.list}\
%{nil}

#
# This macro creates a kernel-<subpackage>-devel package.
#	%%kernel_devel_package <subpackage> <pretty-name>
#
%define kernel_devel_package() \
%package %{?1:%{1}-}devel\
Summary: Development package for building kernel modules to match the %{?2:%{2} }kernel\
Group: System Environment/Kernel\
Provides: kernel%{?1:-%{1}}-devel-%{_target_cpu} = %{version}-%{release}\
Provides: kernel-devel-%{_target_cpu} = %{version}-%{release}%{?1:.%{1}}\
Provides: kernel-devel-uname-r = %{KVRA}%{?1:.%{1}}\
AutoReqProv: no\
Requires(pre): /usr/bin/find\
Requires: perl\
%description -n kernel%{?variant}%{?1:-%{1}}-devel\
This package provides kernel headers and makefiles sufficient to build modules\
against the %{?2:%{2} }kernel package.\
%{nil}

#
# This macro creates a kernel-<subpackage> and its -devel and -debuginfo too.
#	%%define variant_summary The Linux kernel compiled for <configuration>
#	%%kernel_variant_package [-n <pretty-name>] <subpackage>
#
%define kernel_variant_package(n:) \
%package %1\
Summary: %{variant_summary}\
Group: System Environment/Kernel\
%kernel_reqprovconf\
%{expand:%%kernel_devel_package %1 %{!?-n:%1}%{?-n:%{-n*}}}\
%{expand:%%kernel_debuginfo_package %1}\
%{nil}


# First the auxiliary packages of the main kernel package.
%kernel_devel_package
%kernel_debuginfo_package


# Now, each variant package.

%define variant_summary The Linux kernel compiled with extra debugging enabled
%kernel_variant_package debug
%description debug
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system:  memory allocation, process allocation, device
input and output, etc.

This variant of the kernel has numerous debugging options enabled.
It should only be installed when trying to gather additional information
on kernel bugs, as some of these options impact performance noticably.

%define variant_summary A minimal Linux kernel compiled for crash dumps
%kernel_variant_package kdump
%description kdump
This package includes a kdump version of the Linux kernel. It is
required only on machines which will use the kexec-based kernel crash dump
mechanism.

%prep

# do a few sanity-checks for --with *only builds
%if %{with_baseonly}
%if !%{with_default}
echo "Cannot build --with baseonly, default kernel build is disabled"
exit 1
%endif
%endif

tar xzf %{SOURCE0}
mv %{name} kernel-%{KVRA}
#setup -q -n kernel -c


#mv linux-%{rheltarball} linux-%{KVRA}
cd kernel-%{KVRA}

# Drop some necessary files from the source dir into the buildroot
#cp $RPM_SOURCE_DIR/kernel-%{version}-*.config .
%define make make %{?cross_opts}
cp %{SOURCE1001} .
cp %{SOURCE1001} .config

#/usr/bin/patch -p1 < $RPM_SOURCE_DIR/fix.script.location.patch

# Any further pre-build tree manipulations happen here.
make olddefconfig

chmod +x scripts/checkpatch.pl

# This Prevents scripts/setlocalversion from mucking with our version numbers.
touch .scmversion


# get rid of unwanted files resulting from patch fuzz
# IBM does this prior to creating source package
find . \( -name "*.orig" -o -name "*~" \) -exec rm -f {} \; >/dev/null

# remove unnecessary SCM files
find . -name .gitignore -exec rm -f {} \; >/dev/null

tar -cjf %{_tmppath}/%{name}-ibmsource.tar.bz2 .
# OK, proceed with the rest of the prep now

# only deal with configs if we are going to build for the arch
#%ifnarch %nobuildarches

#if [ -L configs ]; then
#	rm -f configs
#	mkdir configs
#fi

# Remove configs not for the buildarch
#for cfg in kernel-%{version}-*.config; do
#  if [ `echo %{all_arch_configs} | grep -c $cfg` -eq 0 ]; then
#    rm -f $cfg
#  fi
#done

# IBM: Get the right config for the customer
#dist_no_dot=$(echo %{?repo} | sed -e 's/^\.//')
#if [ -f kernel-%{version}-%{_target_cpu}-${dist_no_dot}.config ] ; then
  # The projects that include separate configs like this use
  # full configs.
#  cp kernel-%{version}-%{_target_cpu}-${dist_no_dot}.config kernel-%{version}-%{_target_cpu}.config
#fi
#if [ -f kernel-%{version}-%{_target_cpu}-${dist_no_dot}-debug.config ] ; then
  # If there's a customer-specific debug config, let's get it too
#  cp kernel-%{version}-%{_target_cpu}-${dist_no_dot}-debug.config kernel-%{version}-%{_target_cpu}-debug.config
#fi

#%if !%{debugbuildsenabled}
#rm -f kernel-%{version}-*debug.config
#%endif

# now run oldconfig over all the config files
#for i in *.config
#do
#  mv $i .config
#  Arch=`head -1 .config | cut -b 3-`
#  make ARCH=$Arch listnewconfig | grep -E '^CONFIG_' >.newoptions || true
#%if %{listnewconfig_fail}
#  if [ -s .newoptions ]; then
#    cat .newoptions
#    exit 1
#  fi
#%endif
#  rm -f .newoptions
#  make ARCH=$Arch oldnoconfig
#  echo "# $Arch" > configs/$i
#  cat .config >> configs/$i
#done
# end of kernel config
#%endif

cd ..

# BZ 83628: need timestamp when prep finished to capture all SOURCES
# in source subpackage. Do this manually.
find %{_sourcedir} -type f -exec touch -a {} \; && touch %{_tmppath}/%{name}-ibmsource.prepped
sleep 2

# IBM: need to touch these files for nobuildarches and noarch to keep source consistent
touch %{SOURCE11} # x509.genkey
touch %{SOURCE1001} # hostos-minimal.config
touch %{SOURCE13} # mod-extra.list
touch %{SOURCE14} # mod-extra.sh
#touch %{SOURCE12} # extra_certificates
#touch %{SOURCE15} # rheldup3.x509
#touch %{SOURCE16} # rhelkpatch1.x509
touch %{SOURCE90}
touch %{SOURCE91}
touch %{SOURCE92}
touch %{SOURCE93}
touch %{SOURCE95}
touch %{SOURCE96}
touch %{SOURCE97}
touch %{SOURCE98}
touch %{SOURCE99}

###
### build
###
%build

%if %{with_sparse}
%define sparse_mflags	C=1
%endif

%if %{with_debuginfo}
# This override tweaks the kernel makefiles so that we run debugedit on an
# object before embedding it.  When we later run find-debuginfo.sh, it will
# run debugedit again.  The edits it does change the build ID bits embedded
# in the stripped object, but repeating debugedit is a no-op.  We do it
# beforehand to get the proper final build ID bits into the embedded image.
# This affects the vDSO images in vmlinux, and the vmlinux image in bzImage.
export AFTER_LINK='sh -xc "/usr/lib/rpm/debugedit -b $$RPM_BUILD_DIR -d /usr/src/debug -i $@ > $@.id"'
%endif

#%if 0%{?cross_build}
#Strip=%{_tool_triplet}-strip
#%else
#Strip=eu-strip
#%endif

cp_vmlinux()
{
  eu-strip --remove-comment -o "$2" "$1"
}

BuildKernel() {
    MakeTarget=$1
    KernelImage=$2
    Flavour=$3
    InstallName=${4:-vmlinuz}

    # Pick the right config file for the kernel we're building
    Config=kernel-%{version}-%{_target_cpu}${Flavour:+-${Flavour}}.config
    DevelDir=/usr/src/kernels/%{KVRA}${Flavour:+.${Flavour}}

    # When the bootable image is just the ELF kernel, strip it.
    # We already copy the unstripped file into the debuginfo package.
    if [ "$KernelImage" = vmlinux ]; then
      CopyKernel=cp_vmlinux
    else
      CopyKernel=cp
    fi

    KernelVer=%{KVRA}${Flavour:+.${Flavour}}
    echo BUILDING A KERNEL FOR ${Flavour} %{_target_cpu}...

    # make sure EXTRAVERSION says what we want it to say
    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}.%{_target_cpu}${Flavour:+.${Flavour}}/" Makefile

    # and now to start the build process
    export CC=%{__cc}

    # During cross, set the following envar to the _tool_triplet rpmmacro set in
    # cross-rpm-config's toolconf.arch. linux/Makefile will prefix tools with this.
    %if 0%{?cross_build}
    export CROSS_COMPILE=%{_tool_triplet}-
    %endif

    make -s mrproper
    cp %{SOURCE1001} .config

    cp %{SOURCE11} .	# x509.genkey
    #cp %{SOURCE12} .	# extra_certificates
    #cp %{SOURCE15} .	# rheldup3.x509
    #cp %{SOURCE16} .	# rhelkpatch1.x509

    #cp configs/$Config .config

    #Arch=`head -1 .config | cut -b 3- | tr -d [:cntrl:]`
    Arch=powerpc
    echo USING ARCH=$Arch

%ifarch s390x
    if [ "$Flavour" == "kdump" ]; then
        pushd arch/s390/boot
        %{__cc} -static -o zfcpdump zfcpdump.c
        popd
    fi
%endif

    # Define distro_id
    buildtime=`date +%Y:%m:%d:%H%M%%S`
    project=`echo %{repo} | cut -d . -f 2`
    DISTRO_ID="3:$project:$buildtime:%{ibm}"

    make -s ARCH=$Arch BASE_DISTRO_ID=$DISTRO_ID oldnoconfig >/dev/null
    make -s ARCH=$Arch BASE_DISTRO_ID=$DISTRO_ID V=1 %{?_smp_mflags} KCFLAGS="%{?kcflags}" $MakeTarget %{?sparse_mflags}
%if %{with_uimage}
    make -s ARCH=$Arch BASE_DISTRO_ID=$DISTRO_ID V=1 %{uimage_target} %{?sparse_mflags}
%endif

%if %{with_modules}
    if [ "$Flavour" != "kdump" ]; then
        make -s ARCH=$Arch V=1 %{?_smp_mflags} KCFLAGS="%{?kcflags}" modules %{?sparse_mflags} || exit 1
    fi
%endif

%if %{with_dtb}
	make -s ARCH=$Arch V=1 dtbs
	mkdir -p $RPM_BUILD_ROOT/%{image_install_path}/dtb-$KernelVer
	install -m 644 arch/$Arch/boot/dts/*.dtb $RPM_BUILD_ROOT/%{image_install_path}/dtb-$KernelVer/
	rm -f arch/$Arch/boot/dts/*.dtb
%endif

    # Start installing the results
%if %{with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/boot
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/%{image_install_path}
%endif
    mkdir -p $RPM_BUILD_ROOT/%{image_install_path}
    install -m 644 .config $RPM_BUILD_ROOT/boot/config-$KernelVer
    install -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-$KernelVer

    # We estimate the size of the initramfs because rpm needs to take this size
    # into consideration when performing disk space calculations. (See bz #530778)
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initramfs-$KernelVer.img bs=1M count=20

    if [ -f arch/$Arch/boot/zImage.stub ]; then
      cp arch/$Arch/boot/zImage.stub $RPM_BUILD_ROOT/%{image_install_path}/zImage.stub-$KernelVer || :
    fi
%if %{with_uimage}
    for img in `ls -1 arch/$Arch/boot/{cu,u,tree}Image* | egrep -v Image\\\.\\\w*\\\.` ;
    do
      uimage=`basename $img`
      cp arch/$Arch/boot/$uimage $RPM_BUILD_ROOT/%{image_install_path}/$uimage-$KernelVer || :
    done
%endif
# EFI SecureBoot signing, x86_64-only
%if 0%{?signmodules:0}
%ifarch x86_64
    %pesign -s -i $KernelImage -o $KernelImage.signed -a %{SOURCE13} -c %{SOURCE13}
    mv $KernelImage.signed $KernelImage
%endif
%endif
    $CopyKernel $KernelImage $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    chmod 755 $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer

    # hmac sign the kernel for FIPS
    echo "Creating hmac file: $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac"
    ls -l $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    sha512hmac $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer | sed -e "s,$RPM_BUILD_ROOT,," > $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac;

%if %{with_modules}
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/kernel
    if [ "$Flavour" != "kdump" ]; then
        # Override $(mod-fw) because we don't want it to install any firmware
        # we'll get it from the linux-firmware package and we don't want conflicts
        make -s ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_install KERNELRELEASE=$KernelVer mod-fw=
    fi
%endif
%ifarch %{vdso_arches}
    make -s ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT vdso_install KERNELRELEASE=$KernelVer
    if [ ! -s ldconfig-kernel.conf ]; then
      echo > ldconfig-kernel.conf "\
# Placeholder file, no vDSO hwcap entries used in this kernel."
    fi
    %{__install} -D -m 444 ldconfig-kernel.conf $RPM_BUILD_ROOT/etc/ld.so.conf.d/kernel-$KernelVer.conf
%endif

%if %{with_modules}
    # And save the headers/makefiles etc for building modules against
    #
    # This all looks scary, but the end result is supposed to be:
    # * all arch relevant include/ files
    # * all Makefile/Kconfig files
    # * all script/ files

    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/source
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    (cd $RPM_BUILD_ROOT/lib/modules/$KernelVer ; ln -s build source)
    # dirs for additional modules per module-init-tools, kbuild/modules.txt
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/extra
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/updates
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/weak-updates
    # first copy everything
    cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp Module.symvers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp System.map $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -s Module.markers ]; then
      cp Module.markers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    fi

    # create the kABI metadata for use in packaging
    # NOTENOTE: the name symvers is used by the rpm backend
    # NOTENOTE: to discover and run the /usr/lib/rpm/fileattrs/kabi.attr
    # NOTENOTE: script which dynamically adds exported kernel symbol
    # NOTENOTE: checksums to the rpm metadata provides list.
    # NOTENOTE: if you change the symvers name, update the backend too
    echo "**** GENERATING kernel ABI metadata ****"
    gzip -c9 < Module.symvers > $RPM_BUILD_ROOT/boot/symvers-$KernelVer.gz

%if %{with_kabichk}
    echo "**** kABI checking is enabled in kernel SPEC file. ****"
    chmod 0755 $RPM_SOURCE_DIR/check-kabi
    if [ -e $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu}$Flavour ]; then
        cp $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu}$Flavour $RPM_BUILD_ROOT/Module.kabi
        $RPM_SOURCE_DIR/check-kabi -k $RPM_BUILD_ROOT/Module.kabi -s Module.symvers || exit 1
        rm $RPM_BUILD_ROOT/Module.kabi # for now, don't keep it around.
    else
        echo "**** NOTE: Cannot find reference Module.kabi file. ****"
    fi
%endif

    # then drop all but the needed Makefiles/Kconfig files
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Documentation
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    cp .config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -d arch/$Arch/scripts ]; then
      cp -a arch/$Arch/scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch} || :
    fi
    if [ -f arch/$Arch/*lds ]; then
      cp -a arch/$Arch/*lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch}/ || :
    fi
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*.o
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*/*.o
%ifarch ppc64 ppc64le ppcnf ppc476
    cp -a --parents arch/powerpc/lib/crtsavres.[So] $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    if [ -d arch/%{asmarch}/include ]; then
      cp -a --parents arch/%{asmarch}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
    cp -a include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include

    # Make sure the Makefile and version.h have a matching timestamp so that
    # external modules can be built
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/generated/uapi/linux/version.h
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/generated/autoconf.h
    # Copy .config to include/config/auto.conf so "make prepare" is unnecessary.
    cp $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/config/auto.conf

%if %{with_debuginfo}
    if test -s vmlinux.id; then
      cp vmlinux.id $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/vmlinux.id
    else
      echo >&2 "*** ERROR *** no vmlinux build ID! ***"
      #exit 1
    fi

    #
    # save the vmlinux file for kernel debugging into the kernel-debuginfo rpm
    #
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
    cp vmlinux $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
%endif

    find $RPM_BUILD_ROOT/lib/modules/$KernelVer -name "*.ko" -type f >modnames

    # mark modules executable so that strip-to-file can strip them
    xargs --no-run-if-empty chmod u+x < modnames

    # Generate a list of modules for block and networking.

    grep -F /drivers/ modnames | xargs --no-run-if-empty nm -upA |
    sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef

    collect_modules_list()
    {
      sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef |
      LC_ALL=C sort -u > $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
      if [ ! -z "$3" ]; then
        sed -r -e "/^($3)\$/d" -i $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
      fi
    }

    collect_modules_list networking 'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register|rt2x00(pci|usb)_probe|register_netdevice'
    collect_modules_list block 'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_alloc_queue|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler|blk_queue_physical_block_size' 'pktcdvd.ko|dm-mod.ko'
    collect_modules_list drm 'drm_open|drm_init'
    collect_modules_list modesetting 'drm_crtc_init'

    # detect missing or incorrect license tags
    rm -f modinfo
    while read i
    do
      echo -n "${i#$RPM_BUILD_ROOT/lib/modules/$KernelVer/} " >> modinfo
      /sbin/modinfo -l $i >> modinfo
    done < modnames

    grep -E -v 'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' modinfo && exit 1

    rm -f modinfo modnames

    # Save off the .tmp_versions/ directory.  We'll use it in the
    # __debug_install_post macro below to sign the right things
%if 0%{?signmodules:0}
    # Also save the signing keys so we actually sign the modules with the
    # right key.
    cp -r .tmp_versions .tmp_versions.sign${Flavour:+.${Flavour}}
    cp signing_key.priv signing_key.priv.sign${Flavour:+.${Flavour}}
    cp signing_key.x509 signing_key.x509.sign${Flavour:+.${Flavour}}
%endif

    # remove files that will be auto generated by depmod at rpm -i time
    for i in alias alias.bin builtin.bin ccwmap dep dep.bin ieee1394map inputmap isapnpmap ofmap pcimap seriomap symbols symbols.bin usbmap
    do
      rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$i
    done

    # Call the modules-extra script to move things around
    %{SOURCE14} $RPM_BUILD_ROOT/lib/modules/$KernelVer %{SOURCE13}

    # Find all the module files and filter them out into the core and modules
    # lists.  This actually removes anything going into -modules from the dir.
    find lib/modules/$KernelVer/kernel -name *.ko | sort -n > modules.list
	cp $RPM_SOURCE_DIR/filter-*.sh .
    %{SOURCE99} modules.list %{_target_cpu}
	rm filter-*.sh

%endif # with_modules
    # Move the devel headers out of the root file system
    mkdir -p $RPM_BUILD_ROOT/usr/src/kernels
%if %{with_modules}
    mv $RPM_BUILD_ROOT/lib/modules/$KernelVer/build $RPM_BUILD_ROOT/$DevelDir
    ln -sf $DevelDir $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
%endif

    # prune junk from kernel-devel
    find $RPM_BUILD_ROOT/usr/src/kernels -name ".*.cmd" -exec rm -f {} \;
}

###
# DO it...
###

# prepare directories
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/boot
mkdir -p $RPM_BUILD_ROOT%{_libexecdir}

cd kernel-%{KVRA}

%if %{with_default}
BuildKernel %make_target %kernel_image
%endif

%if %{with_debug}
BuildKernel %make_target %kernel_image debug
%endif

%if %{with_kdump}
BuildKernel %make_target %kernel_image kdump
%endif

%if 0%{?cross_build}
%global perf_make make %{?_smp_mflags} -C tools/perf -s ARCH=%{hdrarch} CROSS_COMPILE=%{_tool_triplet}- V=1 NO_LIBPERL=1 NO_LIBPYTHON=1 NO_DEMANGLE=1 WERROR=0 NO_LIBUNWIND=1 HAVE_CPLUS_DEMANGLE=0 NO_GTK2=1 NO_STRLCPY=1 prefix=%{_prefix} lib=%{_lib}
%else
%global perf_make make %{?_smp_mflags} -C tools/perf -s V=1 WERROR=0 NO_LIBUNWIND=1 HAVE_CPLUS_DEMANGLE=1 NO_GTK2=1 NO_STRLCPY=1 prefix=%{_prefix} lib=%{_lib}
%endif
%if %{with_perf}
# perf
%{perf_make} all
%if ! 0%{?cross_build}
%{perf_make} man || %{doc_build_fail}
%endif
%endif

%if %{with_tools}
%ifarch %{cpupowerarchs}
# cpupower
# make sure version-gen.sh is executable.
chmod +x tools/power/cpupower/utils/version-gen.sh
make %{?_smp_mflags} -C tools/power/cpupower CPUFREQ_BENCH=false
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    make %{?_smp_mflags} centrino-decode powernow-k8-decode
    popd
%endif
%ifarch x86_64
   pushd tools/power/x86/x86_energy_perf_policy/
   make
   popd
   pushd tools/power/x86/turbostat
   make
   popd
%endif #turbostat/x86_energy_perf_policy
%endif
pushd tools
make tmon
popd
%endif

%if %{with_doc}
# Make the HTML and man pages.
make htmldocs mandocs || %{doc_build_fail}

# sometimes non-world-readable files sneak into the kernel source tree
chmod -R a=rX Documentation
find Documentation -type d | xargs chmod u+w
%endif

# In the modsign case, we do 3 things.  1) We check the "flavour" and hard
# code the value in the following invocations.  This is somewhat sub-optimal
# but we're doing this inside of an RPM macro and it isn't as easy as it
# could be because of that.  2) We restore the .tmp_versions/ directory from
# the one we saved off in BuildKernel above.  This is to make sure we're
# signing the modules we actually built/installed in that flavour.  3) We
# grab the arch and invoke 'make modules_sign' and the mod-extra-sign.sh
# commands to actually sign the modules.
#
# We have to do all of those things _after_ find-debuginfo runs, otherwise
# that will strip the signature off of the modules.
#
# Finally, pick a module at random and check that it's signed and fail the build
# if it isn't.

%define __modsign_install_post \
  if [ "%{signmodules}" == "1" ]; then \
    if [ "%{with_debug}" -ne "0" ]; then \
      Arch=`head -1 configs/kernel-%{version}-%{_target_cpu}-debug.config | cut -b 3-` \
      rm -rf .tmp_versions \
      mv .tmp_versions.sign.debug .tmp_versions \
      mv signing_key.priv.sign.debug signing_key.priv \
      mv signing_key.x509.sign.debug signing_key.x509 \
      %{modsign_cmd} $RPM_BUILD_ROOT/lib/modules/%{KVRA}.debug || exit 1 \
    fi \
      if [ "%{with_default}" -ne "0" ]; then \
      Arch=`head -1 configs/kernel-%{version}-%{_target_cpu}.config | cut -b 3-` \
      rm -rf .tmp_versions \
      mv .tmp_versions.sign .tmp_versions \
      mv signing_key.priv.sign signing_key.priv \
      mv signing_key.x509.sign signing_key.x509 \
      %{modsign_cmd} $RPM_BUILD_ROOT/lib/modules/%{KVRA} || exit 1 \
    fi \
  fi \
%{nil}

###
### Special hacks for debuginfo subpackages.
###

# This macro is used by %%install, so we must redefine it before that.
%define debug_package %{nil}

%if %{with_debuginfo}

%define __debug_install_post \
  /usr/lib/rpm/find-debuginfo.sh %{debuginfo_args} %{_builddir}/%{?buildsubdir}\
%{nil}

%ifnarch noarch
%global __debug_package 1
%files -f debugfiles.list debuginfo-common-%{_target_cpu}
%defattr(-, root, root)
%endif

%endif

%if %{with_modules}
#
# Disgusting hack alert! We need to ensure we sign modules *after* all
# invocations of strip occur, which is in __debug_install_post if
# find-debuginfo.sh runs, and __os_install_post if not.
#
%define __spec_install_post \
  %{?__debug_package:%{__debug_install_post}}\
  %{__arch_install_post}\
  %{__os_install_post}\
  %{?__ibm_source:%{ibm_install_post}} \
  %{__modsign_install_post}
%endif

###
### install
###

%install

cd kernel-%{KVRA}

%if %{with_doc}
docdir=$RPM_BUILD_ROOT%{_datadir}/doc/kernel-doc-%{version}
man9dir=$RPM_BUILD_ROOT%{_datadir}/man/man9

# copy the source over
mkdir -p $docdir
tar -f - --exclude=man --exclude='.*' -c Documentation | tar xf - -C $docdir

# Install man pages for the kernel API.
mkdir -p $man9dir
find Documentation/DocBook/man -name '*.9.gz' -print0 |
xargs -0 --no-run-if-empty %{__install} -m 444 -t $man9dir $m
ls $man9dir | grep -q '' || > $man9dir/BROKEN
%endif # with_doc

# We have to do the headers install before the tools install because the
# kernel headers_install will remove any header files in /usr/include that
# it doesn't install itself.

%if %{with_headers}
# Install kernel headers
make ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_install

# Do headers_check but don't die if it fails.
make ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_check > hdrwarnings.txt || :
if grep -q exist hdrwarnings.txt; then
   sed s:^$RPM_BUILD_ROOT/usr/include/:: hdrwarnings.txt
   # Temporarily cause a build failure if header inconsistencies.
   # exit 1
fi

find $RPM_BUILD_ROOT/usr/include \( -name .install -o -name .check -o -name ..install.cmd -o -name ..check.cmd \) | xargs rm -f

%endif

%if %{with_modules}
%if %{with_kernel_abi_whitelists}
# kabi directory
INSTALL_KABI_PATH=$RPM_BUILD_ROOT/lib/modules/
mkdir -p $INSTALL_KABI_PATH

# install kabi releases directories
tar xjvf %{SOURCE25} -C $INSTALL_KABI_PATH
%endif  # with_kernel_abi_whitelists
%endif # with_modules

%if %{with_perf}
# perf tool binary and supporting scripts/binaries
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install
# remove the 'trace' symlink.
rm -f $RPM_BUILD_ROOT/%{_bindir}/trace

%if ! 0%{?cross_build}
# perf-python extension
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-python_ext

# perf man pages (note: implicit rpm magic compresses them later)
%{perf_make} DESTDIR=$RPM_BUILD_ROOT try-install-man || %{doc_build_fail}
%endif
%endif

%if %{with_tools}
%ifarch %{cpupowerarchs}
make -C tools/power/cpupower DESTDIR=$RPM_BUILD_ROOT libdir=%{_libdir} mandir=%{_mandir} CPUFREQ_BENCH=false install
rm -f %{buildroot}%{_libdir}/*.{a,la}
%find_lang cpupower
mv cpupower.lang ../
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    install -m755 centrino-decode %{buildroot}%{_bindir}/centrino-decode
    install -m755 powernow-k8-decode %{buildroot}%{_bindir}/powernow-k8-decode
    popd
%endif
chmod 0755 %{buildroot}%{_libdir}/libcpupower.so*
mkdir -p %{buildroot}%{_unitdir} %{buildroot}%{_sysconfdir}/sysconfig
install -m644 %{SOURCE2000} %{buildroot}%{_unitdir}/cpupower.service
install -m644 %{SOURCE2001} %{buildroot}%{_sysconfdir}/sysconfig/cpupower
%ifarch %{ix86} x86_64
   mkdir -p %{buildroot}%{_mandir}/man8
   pushd tools/power/x86/x86_energy_perf_policy
   make DESTDIR=%{buildroot} install
   popd
   pushd tools/power/x86/turbostat
   make DESTDIR=%{buildroot} install
   popd
%endif #turbostat/x86_energy_perf_policy
pushd tools/thermal/tmon
make INSTALL_ROOT=%{buildroot} install
popd
%endif

%endif

%if %{with_bootwrapper}
make DESTDIR=$RPM_BUILD_ROOT bootwrapper_install WRAPPER_OBJDIR=%{_libdir}/kernel-wrapper WRAPPER_DTSDIR=%{_libdir}/kernel-wrapper/dts
%endif

%if %{with_doc}
# Red Hat UEFI Secure Boot CA cert, which can be used to authenticate the kernel
mkdir -p $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/%{version}-%{release}
install -m 0644 %{SOURCE13} $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/%{version}-%{release}/kernel-signing-ca.cer
%endif

# IBM: touch these for arches that don't build kernel-tools so source is consistent.
%ifnarch cpupowerarchs
touch -a %{SOURCE2000}
touch -a %{SOURCE2001}
%endif

%ifnarch noarch
 mkdir -p $RPM_BUILD_ROOT/usr/src/kernels/%{KVRA}%{?2:.%{2}}/arch/powerpc/tools
 install -m 0755  arch/powerpc/tools/gcc-check-mprofile-kernel.sh $RPM_BUILD_ROOT/usr/src/kernels/%{KVRA}%{?2:.%{2}}/arch/powerpc/tools/gcc-check-mprofile-kernel.sh
%endif

###
### clean
###

%clean
rm -rf $RPM_BUILD_ROOT

###
### scripts
###


%if %{with_tools}
%post -n kernel-tools
/sbin/ldconfig

%postun -n kernel-tools
/sbin/ldconfig
%endif

#
# This macro defines a %%post script for a kernel*-devel package.
#	%%kernel_devel_post [<subpackage>]
#
%define kernel_devel_post() \
%{expand:%%post %{?1:%{1}-}devel}\
if [ -f /etc/sysconfig/kernel ]\
then\
    . /etc/sysconfig/kernel || exit $?\
fi\
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ]\
then\
    (cd /usr/src/kernels/%{KVRA}%{?1:.%{1}} &&\
     /usr/bin/find . -type f | while read f; do\
       hardlink -c /usr/src/kernels/*.%{?dist}.*/$f $f\
     done)\
fi\
%{nil}


# This macro defines a %%posttrans script for a kernel package.
#	%%kernel_variant_posttrans [<subpackage>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_posttrans() \
%{expand:%%posttrans %{?1}}\
if [ -x %{_sbindir}/weak-modules ]\
then\
    %{_sbindir}/weak-modules --add-kernel %{KVRA}%{?1:.%{1}} || exit $?\
fi\
%{_sbindir}/new-kernel-pkg --package kernel%{?-v:-%{-v*}} --mkinitrd --dracut --depmod --update %{KVRA}%{?-v:.%{-v*}} || exit $?\
%{_sbindir}/new-kernel-pkg --package kernel%{?1:-%{1}} --rpmposttrans %{KVRA}%{?1:.%{1}} || exit $?\
%{nil}

#
# This macro defines a %%post script for a kernel package and its devel package.
#	%%kernel_variant_post [-v <subpackage>] [-r <replace>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_post(v:r:) \
%{expand:%%kernel_devel_post %{?-v*}}\
%{expand:%%kernel_variant_posttrans %{?-v*}}\
%{expand:%%post %{?-v*}}\
%{-r:\
if [ `uname -i` == "x86_64" ] &&\
   [ -f /etc/sysconfig/kernel ]; then\
  /bin/sed -r -i -e 's/^DEFAULTKERNEL=%{-r*}$/DEFAULTKERNEL=kernel%{?-v:-%{-v*}}/' /etc/sysconfig/kernel || exit $?\
fi}\
%{expand:\
%{_sbindir}/new-kernel-pkg --package kernel%{?-v:-%{-v*}} --install %{KVRA}%{?-v:.%{-v*}} || exit $?\
}\
%{nil}

#
# This macro defines a %%preun script for a kernel package.
#	%%kernel_variant_preun <subpackage>
#
%define kernel_variant_preun() \
%{expand:%%preun %{?1}}\
%{_sbindir}/new-kernel-pkg --rminitrd --rmmoddep --remove %{KVRA}%{?1:.%{1}} || exit $?\
if [ -x %{_sbindir}/weak-modules ]\
then\
    %{_sbindir}/weak-modules --remove-kernel %{KVRA}%{?1:.%{1}} || exit $?\
fi\
%{nil}

%kernel_variant_preun
%kernel_variant_post

%kernel_variant_preun debug
%kernel_variant_post -v debug

%ifarch s390x
%postun kdump
    # Create softlink to latest remaining kdump kernel.
    # If no more kdump kernel is available, remove softlink.
    if [ "$(readlink /boot/zfcpdump)" == "/boot/vmlinuz-%{KVRA}.kdump" ]
    then
        vmlinuz_next=$(ls /boot/vmlinuz-*.kdump 2> /dev/null | sort | tail -n1)
        if [ $vmlinuz_next ]
        then
            ln -sf $vmlinuz_next /boot/zfcpdump
        else
            rm -f /boot/zfcpdump
        fi
    fi

%post kdump
    ln -sf /boot/vmlinuz-%{KVRA}.kdump /boot/zfcpdump
%endif # s390x

if [ -x /sbin/ldconfig ]
then
    /sbin/ldconfig -X || exit $?
fi

###
### file lists
###

%if %{with_headers}
%files headers
%defattr(-, root, root)
/usr/include/*
%endif

%if %{with_bootwrapper}
%files bootwrapper
%defattr(-, root, root)
/usr/sbin/*
%{_libdir}/kernel-wrapper
%endif

# only some architecture builds need kernel-doc
%if %{with_doc}
%files doc
%defattr(-, root, root)
%{_datadir}/doc/kernel-doc-%{version}/Documentation/*
%dir %{_datadir}/doc/kernel-doc-%{version}/Documentation
%dir %{_datadir}/doc/kernel-doc-%{version}
%{_datadir}/man/man9/*
%{_datadir}/doc/kernel-keys/%{version}-%{release}/kernel-signing-ca.cer
%dir %{_datadir}/doc/kernel-keys/%{version}-%{release}
%dir %{_datadir}/doc/kernel-keys
%endif

%if %{with_modules}
%if %{with_kernel_abi_whitelists}
%files -n kernel-abi-whitelists
%defattr(-, root, root, -)
/lib/modules/kabi-*
%endif
%endif

%if %{with_perf}
%files -n perf
%defattr(-, root, root)
%{_bindir}/perf
%dir %{_libexecdir}/perf-core
%{_libexecdir}/perf-core/*
/usr/share/perf-core/strace/groups/file
%{_libdir}/traceevent
%{_docdir}/perf-tip/tips.txt
%{_mandir}/man[1-8]/perf*
%{_sysconfdir}/bash_completion.d/perf

%if ! 0%{?cross_build}
%files -n python-perf
%defattr(-, root, root)
%{python_sitearch}
%endif

%if %{with_debuginfo}
%files -f perf-debuginfo.list -n perf-debuginfo
%defattr(-, root, root)

%if ! 0%{?cross_build}
%files -f python-perf-debuginfo.list -n python-perf-debuginfo
%defattr(-, root, root)
%endif # ! cross_build
%endif # with_debuginfo
%endif # with_perf

%if %{with_tools}
%files -n kernel-tools -f cpupower.lang
%defattr(-, root, root)

%ifarch %{cpupowerarchs}
%{_bindir}/cpupower
%ifarch x86_64
%{_bindir}/centrino-decode
%{_bindir}/powernow-k8-decode
%endif
%{_unitdir}/cpupower.service
%{_mandir}/man[1-8]/cpupower*
%config(noreplace) %{_sysconfdir}/sysconfig/cpupower
%ifarch %{ix86} x86_64
%{_bindir}/x86_energy_perf_policy
%{_mandir}/man8/x86_energy_perf_policy*
%{_bindir}/turbostat
%{_mandir}/man8/turbostat*
%endif
%endif
%{_bindir}/tmon
%if %{with_debuginfo}
%files -f kernel-tools-debuginfo.list -n kernel-tools-debuginfo
%defattr(-, root, root)
%endif

%ifarch %{cpupowerarchs}
%files -n kernel-tools-libs
%defattr(-, root, root)
%{_libdir}/libcpupower.so.0
%{_libdir}/libcpupower.so.0.0.1

%files -n kernel-tools-libs-devel
%defattr(-, root, root)
%{_libdir}/libcpupower.so
%{_includedir}/cpufreq.h
%endif

%endif # with_tools

# This is %%{image_install_path} on an arch where that includes ELF files,
# or empty otherwise.
%define elf_image_install_path %{?kernel_image_elf:%{image_install_path}}

#
# This macro defines the %%files sections for a kernel package
# and its devel and debuginfo packages.
#	%%kernel_variant_files [-k vmlinux] <condition> <subpackage>
#
%define kernel_variant_files(k:) \
%if %{1}\
%{expand:%%files %{?2}}\
%defattr(-, root, root)\
/%{image_install_path}/%{?-k:%{-k*}}%{!?-k:vmlinuz}-%{KVRA}%{?2:.%{2}}\
%if %{with_uimage} \
/%{image_install_path}/%{?-k:%{-k*}}%{!?-k:*Image*}-%{KVRA}%{?2:.%{2}}\
%endif \
%if %{with_dtb} \
/%{image_install_path}/dtb-%{KVRA}%{?2:+%{2}} \
%endif\
/%{image_install_path}/.vmlinuz-%{KVRA}%{?2:.%{2}}.hmac \
%attr(600, root, root) /boot/System.map-%{KVRA}%{?2:.%{2}}\
%if %{with_modules}\
/boot/symvers-%{KVRA}%{?2:.%{2}}.gz\
%endif\
/boot/config-%{KVRA}%{?2:.%{2}}\
%if %{with_modules}\
%dir /lib/modules/%{KVRA}%{?2:.%{2}}\
/lib/modules/%{KVRA}%{?2:.%{2}}/kernel\
/lib/modules/%{KVRA}%{?2:.%{2}}/build\
/lib/modules/%{KVRA}%{?2:.%{2}}/source\
/lib/modules/%{KVRA}%{?2:.%{2}}/extra\
/lib/modules/%{KVRA}%{?2:.%{2}}/updates\
/lib/modules/%{KVRA}%{?2:.%{2}}/weak-updates\
%endif\
%ifarch %{vdso_arches}\
/lib/modules/%{KVRA}%{?2:.%{2}}/vdso\
/etc/ld.so.conf.d/kernel-%{KVRA}%{?2:.%{2}}.conf\
%endif\
%if %{with_modules}\
/lib/modules/%{KVRA}%{?2:.%{2}}/modules.*\
%endif\
%ghost /boot/initramfs-%{KVRA}%{?2:.%{2}}.img\
%{expand:%%files %{?2:%{2}-}devel}\
%defattr(-, root, root)\
%if %{with_modules}\
/usr/src/kernels/%{KVRA}%{?2:.%{2}}\
%endif\
%if %{with_debuginfo}\
%ifnarch noarch\
%{expand:%%files -f debuginfo%{?2}.list %{?2:%{2}-}debuginfo}\
%defattr(-, root, root)\
%endif\
%endif\
%endif\
%{nil}

%kernel_variant_files %{with_default}
%kernel_variant_files %{with_debug} debug
%kernel_variant_files %{with_kdump} kdump


%changelog
* Wed Apr 04 2018 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.16.0-2.git
- Updating to b24758c Merge tag v4.16 into hostos-devel

* Thu Mar 29 2018 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.16.0-1.rc7.git
- Version update
- Updating to 58079f0 Merge remote-tracking branch remotes/powerpc/topic/ppc-kvm into hostos-devel

* Wed Feb 14 2018 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.15.0-5.git
- Updating to 33f711f KVM: PPC: Book3S: Fix compile error that occurs with some
  gcc versions

* Fri Feb 09 2018 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.15.0-4.git
- Updating to a707e6c Merge branch kvm-ppc-next into hostos-devel

* Wed Jan 31 2018 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.15.0-3.git
- Updating to d34a158 KVM: PPC: Book3S HV: Drop locks before reading guest
  memory

* Wed Jan 24 2018 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.15.0-2.rc9.git
- Updating to 03552b2 Merge tag v4.15-rc9 into hostos-devel

* Sat Jan 20 2018 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.15.0-1.rc8.git
- Version update
- Updating to a99d06c Merge branch kvm-ppc-next into hostos-devel

* Fri Nov 17 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.14.0-3.git
- Updating to 68b4afb Merge tag v4.14 into hostos-devel

* Wed Nov 08 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.14.0-2.rc8.git
- Updating to cc4bf22 Merge tag v4.14-rc8 into hostos-devel

* Sat Oct 21 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.14.0-1.rc4.git
- Version update
- Updating to b27fc5c Merge branch kvm-ppc-fixes into hostos-devel

* Wed Oct 04 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.13.0-5.git
- Updating to af16eac powerpc/pseries: Check memory device state before
  onlining/offlining

* Tue Sep 19 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.13.0-4.git
- Updating to 49564cb KVM: PPC: Book3S HV: Handle unexpected interrupts better

* Mon Aug 14 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 4.13.0-3.rc3.git
- Bump release

* Mon Aug 07 2017 Fabiano Rosas <farosas@linux.vnet.ibm.com> - 4.13.0-2.rc3.git
- Add extraver macro to Release field

* Wed Aug 02 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.13.0-1.rc3.git
- Version update
- Updating to ec0d270 Merge tag v4.13-rc3 into hostos-devel

* Wed Jul 12 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.11.0-7.git
- Updating to d255e14 KVM: PPC: Book3S: Fix typo in XICS-on-XIVE state saving
  code

* Mon Jun 19 2017 Murilo Opsfelder Araujo <muriloo@linux.vnet.ibm.com> - 4.11.0-6.git
- Pack unpacked files
- Bump release

* Mon Jun 19 2017 Murilo Opsfelder Araujo <muriloo@linux.vnet.ibm.com> - 4.11.0-5.git
- Enable uprobes-based dynamic events
- Bump release

* Wed Jun 07 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.11.0-4.git
- Updating to 8caa70f KVM: PPC: Book3S HV: Context-switch EBB registers properly

* Thu Jun 01 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.11.0-3.git
- Updating to 3e6fda8 KVM: PPC: Book3S HV: Virtualize doorbell facility on
  POWER9

* Wed May 24 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.11.0-2.git
- Updating to 1ee4641 KVM: PPC: Book3S HV: Add radix checks in real-mode
  hypercall handlers

* Wed May 03 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.11.0-1.git
- Version update
- Updating to 4a6869a Merge branch kvm-ppc-next into hostos-devel

* Thu Mar 23 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.10.0-7.git
- Updating to b729957 power/mm: update pte_write and pte_wrprotect to handle
  savedwrite

* Wed Mar 15 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.10.0-6.gitfb71dea
- fb71deab42a6d5f6dd631386f0defc954ad7eb19 vfio-pci: Allow to expose MSI-X table to userspace if interrupt remapping is enabled
- 2465b36e24d89ae2e6b312bcd77d9502b267c8dd Revert vfio-pci: Allow to expose MSI-X table to userspace if interrupt remapping is enabled
- 4b6cdf6a8d5b0debadfb8c67f607c5f54031ce39 powerpc/powernv/ioda2: Update iommu table base on ownership change

* Wed Mar 08 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.10.0-5.gitb0bad18
- b0bad18237cef1541a5d98067a4008772a80f724 PCI: Disable IOV before pcibios_sriov_disable()
- 7c2a09b55febc2ac36257e0183f304c1f8cada70 PCI: Lock each enable/disable num_vfs operation in sysfs
- 6c25973efba804c78ef09c9047c6484bf89a3631 powerpc: Update to new option-vector-5 format for CAS
- aeed990c0b088fbd1002c5bdf4ee5ce106dacc6c Revert powerpc/CAS: Update to new option-vector-5 format for CAS

* Wed Mar 01 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.10.0-4.git8f27d36
- 8f27d36a72398378566cda5afe6a066b8e6b58f9 KVM: PPC: Book3S HV: Dont use ASDR for real-mode HPT faults on POWER9
- 05a77197a94399fb24c1c6cd4bf7623481302a8d KVM: PPC: Book3S HV: Fix POWER9 DD1 SLB workaround
- e56637d6e0c2b811ebb83c9b943cf94314e3ccc7 KVM: PPC: Book3S HV: Fix software walk of guest process page tables
- 3421f2effa9ca74dbe2291c0007f54caaf12c921 powerpc/64: Invalidate process table caching after setting process table
- ba3f7517e2b58331c056c6c83972f6b347e4dcb3 PCI: Dont apply default alignment when PCI_PROBE_ONLY is set
- 37f590f50c1593be9d03b98a87449762dfbf01bc powerpc/CAS: Update to new option-vector-5 format for CAS
- bd850866b2477fc4fb07210685ab3ff64f1d7c7e powerpc/prom_init: Parse the command line before calling CAS
- 617a91762714f1c1d997e67142e4b2c6eea651cf PCI: A fix for caculating bridge windows size and alignment
- 3212c4c3f81860c073d8ddd50e068cf4847fe069 powerpc: Add POWER9 architected mode to cputable
- 152490356ea89026dd2665bb4670d95dc89cadee powerpc/64: Fix checksum folding in csum_add
- b0b8bcc67ead2e486dca161a7aa27ac67495d263 powerpc/64: Clear UPRT on POWER9 when initializing HPT
- a136365d53aef9a6a43f16f0fadf0529123b0a34 powerpc: P9 DD1 SLB invalidate workaround with P8 mode fix
- 0330b51a096dc55c255be2dcfcd729381b8fdb36 powerpc/mm: Update PROTFAULT handling in the page fault path

* Wed Feb 22 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.10.0-3.giteaaddb6
- eaaddb6b7ab31c5fd71db37d0f681bd6a88c2e22 powernv: Pass PSSCR value and mask to power9_idle_stop
- 4bfb3830d13ed553d9adf0621f34440669b2e8e0 cpuidle:powernv: Add helper function to populate powernv idle states.
- 63e525efa4ccdc9b5fa2d19ac132469c26e32211 powernv:stop: Rename pnv_arch300_idle_init to pnv_power9_idle_init
- e557702be29484cdfe5d98437337a732842f8897 powernv:idle: Add IDLE_STATE_ENTER_SEQ_NORET macro
- 1491d41907969885e164a36282d7887c5a32e6dc Merge tag v4.10 into hostos-devel
- fda8051665b5d8b65d17a4d8cf667e0447c800c5 Merge branch kvm-ppc-next into hostos-devel
- 95084d98def7bf448e9793ccc99bb28bebf454bf PCI: Dont extend devices size when using default alignment for all devices
- 19e8df5107af6f5f77ab2ffd277530819b2a9a8f PCI: Add a macro to set default alignment for all PCI devices
- c470abd4fde40ea6a0846a2beab642a578c0b8cd Linux 4.10
- 137d01df511b3afe1f05499aea05f3bafc0fb221 Fix missing sanity check in /dev/sg
- fd3fc0b4d7305fa7246622dcc0dec69c42443f45 scsi: dont BUG_ON() empty DMA transfers
- 00ea1ceebe0d9f2dc1cc2b7bd575a00100c27869 ipv6: release dst on error in ip6_dst_lookup_tail
- 2763f92f858f7c4c3198335c0542726eaed07ba3 Merge tag fixes-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/arm/arm-soc
- b92ce305fcbc8d85d1732fecf17c823c760868bd Merge branch fixes of git://git.armlinux.org.uk/~rmk/linux-arm
- 17a984bccde4c9ea34d78de1535760a25ad87993 Merge branch x86-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 244ff16fb4717708491fa1b3b2a68f9074742d71 Merge branch locking-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- e602e700842104096e96a7deee453183e4ed278a Merge branch timers-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 3dd9c12726ffd1d548ad5264731dfe7a785768ed Merge git://git.kernel.org/pub/scm/linux/kernel/git/davem/net
- fc98c3c8c9dcafd67adcce69e6ce3191d5306c9c printk: use rcuidle console tracepoint
- 69e05170ef0d0c00e1098dd6a625b44f39903a6a ARM: multi_v7_defconfig: enable Qualcomm RPMCC
- bcd3bb63dbc87a3bbb21e95a09cd26bb6479c332 KVM: PPC: Book3S HV: Disable HPT resizing on POWER9 for now
- 4c03b862b12f980456f9de92db6d508a4999b788 irda: Fix lockdep annotations in hashbin_delete().
- 6dc39c50e4aeb769c8ae06edf2b1a732f3490913 Merge branch for-linus of git://git.kernel.dk/linux-block
- 22f0708a718daea5e79de2d29b4829de016a4ff4 vxlan: fix oops in dev_fill_metadata_dst
- 5edabca9d4cff7f1f2b68f0bac55ef99d9798ba4 dccp: fix freeing skb too early for IPV6_RECVPKTINFO
- 2fe1e8a7b2f4dcac3fcb07ff06b0ae7396201fd6 Merge tag powerpc-4.10-5 of git://git.kernel.org/pub/scm/linux/kernel/git/powerpc/linux
- a0d5ef457393a240869d837cda1ccb22bbbe3dc2 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/dtor/input
- 444a034d390da1b636bb2c5f02ebaa08cdbe8de1 Merge branch i2c/for-current of git://git.kernel.org/pub/scm/linux/kernel/git/wsa/linux
- 6adfd6aceba0b315406b56a48733610aa24c70f8 Merge tag mmc-v4.10-rc8 of git://git.kernel.org/pub/scm/linux/kernel/git/ulfh/mmc
- 7ed1b1255919ac46c4b2aab87d1220ec3bd4cbae Merge tag ntb-4.10-bugfixes of git://github.com/jonmason/ntb
- 785f35775d968e0f45231b754e945fcb3ed6bded dpaa_eth: small leak on error
- 6fe1bfc46cad54a4ef337f9935f764a90865236b Merge tag reset-for-4.10-fixes of https://git.pengutronix.de/git/pza/linux into fixes
- 2bd624b4611ffee36422782d16e1c944d1351e98 packet: Do not call fanout_release from atomic contexts
- 3a4f17608162bbbdcdd9680789b1bc61017cefa3 KVM: PPC: Book3S HV: Turn KVM guest htab message into a debug message
- e5a1dadec3648019a838b85357b67f241fbb02e8 reset: fix shared reset triggered_count decrement on error
- 939ada5fb587840ae4db47846087be4162477b13 ntb: ntb_hw_intel: link_poll isnt clearing the pending status properly
- 8fcd0950c021d7be8493280541332b924b9de962 ntb_transport: Pick an unused queue
- 9644347c5240d0ee3ba7472ef332aaa4ff4db398 ntb: ntb_perf missing dmaengine_unmap_put
- dd62245e73de9138333cb0e7a42c8bc1215c3ce6 NTB: ntb_transport: fix debugfs_remove_recursive
- 4da934dc6515afaa1db4e02548803de0cd279734 KVM: PPC: Book3S PR: Ratelimit copy data failure error messages
- 0722f57bfae9abbc673b9dbe495c7da2f64676ea Merge tag drm-fixes-for-v4.10-final of git://people.freedesktop.org/~airlied/linux
- 18a0de8816766a0da7537ef82156b5418ba5cd6e Merge branch drm-fixes-4.10 of git://people.freedesktop.org/~agd5f/linux into drm-fixes
- 558e8e27e73f53f8a512485be538b07115fe5f3c Revert nohz: Fix collision between tick and other hrtimers
- 4695daefba8df8a11fa0b0edd595eedae9ea59ae Merge tag media/v4.10-5 of git://git.kernel.org/pub/scm/linux/kernel/git/mchehab/linux-media
- 5a81e6a171cdbd1fa8bc1fdd80c23d3d71816fac vfs: fix uninitialized flags in splice_to_pipe()
- 58f6eaee7bef8faa1259784d72ee2f51bacead4d Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/mszeredi/fuse
- aa6fba55cc5fac205768f6c7b94276390ee74052 Merge tag pci-v4.10-fixes-4 of git://git.kernel.org/pub/scm/linux/kernel/git/helgaas/pci
- 3c7a9f32f9392c9dfce24f33bdc6799852903e27 Merge git://git.kernel.org/pub/scm/linux/kernel/git/davem/net
- d74c67dd7800fc7aae381f272875c337f268806c drm/radeon: Use mode h/vdisplay fields to hide out of bounds HW cursor
- 9e3440481845b2ec22508f60837ee2cab2b6054f ARM: 8658/1: uaccess: fix zeroing of 64-bit get_user()
- 32b143637e8180f5d5cea54320c769210dea4f19 ARM: 8657/1: uaccess: consistently check object sizes
- 5d7f5ce15156af205e175e8fa5c669ba40bf0c5e cfq-iosched: dont call wbt_disable_default() with IRQs disabled
- 84588a93d097bace24b9233930f82511d4f34210 fuse: fix uninitialized flags in pipe_buffer
- 5b73d6347eb82cd2a26698fc339607e25e0ad917 KVM: PPC: Book3S HV: Prevent double-free on HPT resize commit path
- bf3f14d6342cfb37eab8f0cddd0e4d4063fd9fc9 rhashtable: Revert nested table changes.
- b7a26998590c5efb371562fb8a84bc93094009f5 Merge tag drm-misc-fixes-2017-02-15 of git://anongit.freedesktop.org/git/drm-misc into drm-fixes
- 3f91a89d424a79f8082525db5a375e438887bb3e powerpc/64: Disable use of radix under a hypervisor
- 75224c93fa985f4a6fb983f53208f5c5aa555fbf ibmvnic: Fix endian errors in error reporting output
- 28f4d16570dcf440e54a4d72666d5be452f27d0e ibmvnic: Fix endian error when requesting device capabilities
- 7627ae6030f56a9a91a5b3867b21f35d79c16e64 net: neigh: Fix netevent NETEVENT_DELAY_PROBE_TIME_UPDATE notification
- acf138f1b00bdd1b7cd9894562ed0c2a1670888e net: xilinx_emaclite: fix freezes due to unordered I/O
- cd224553641848dd17800fe559e4ff5d208553e8 net: xilinx_emaclite: fix receive buffer overflow
- afe3e4d11bdf50a4c3965eb6465ba6bebbcf5dcf PCI/PME: Restore pcie_pme_driver.remove
- ee10689117c0186fd4fe7feca8d48c7316f65d70 Merge branch kvm-ppc-next of git://git.kernel.org/pub/scm/linux/kernel/git/paulus/powerpc into HEAD
- f222449c9dfad7c9bb8cb53e64c5c407b172ebbc timekeeping: Use deferred printk() in debug code
- bb08c04dc867b5f392caec635c097d5d5fcd8c9f drm/dp/mst: fix kernel oops when turning off secondary monitor
- 6ba4d2722d06960102c981322035239cd66f7316 fuse: fix use after free issue in fuse_dev_do_read()
- 5463b3d043826ff8ef487edbd1ef1bfffb677437 bpf: kernel header files need to be copied into the tools directory
- e70ac171658679ecf6bea4bbd9e9325cd6079d2b tcp: tcp_probe: use spin_lock_bh()
- a725eb15db80643a160310ed6bcfd6c5a6c907f2 uapi: fix linux/if_pppol2tp.h userspace compilation errors
- 12688dc21f71f4dcc9e2b8b5556b0c6cc8df1491 Revert i2c: designware: detect when dynamic tar update is possible
- f9c85ee67164b37f9296eab3b754e543e4e96a1c [media] siano: make it work again with CONFIG_VMAP_STACK
- d199fab63c11998a602205f7ee7ff7c05c97164b packet: fix races in fanout_add()
- f39f0d1e1e93145a0e91d9a7a639c42fd037ecc3 ibmvnic: Fix initial MTU settings
- a60ced990e309666915d21445e95347d12406694 net: ethernet: ti: cpsw: fix cpsw assignment in resume
- cd27b96bc13841ee7af25837a6ae86fee87273d6 kcm: fix a null pointer dereference in kcm_sendmsg()
- 01f8902bcf3ff124d0aeb88a774180ebcec20ace net: fec: fix multicast filtering hardware setup
- 144adc655fac089d485ee66354d402b319cff6d2 Merge branch ipv6-v4mapped
- 052d2369d1b479cdbbe020fdd6d057d3c342db74 ipv6: Handle IPv4-mapped src to in6addr_any dst.
- ec5e3b0a1d41fbda0cc33a45bc9e54e91d9d12c7 ipv6: Inhibit IPv4-mapped src address on the wire.
- fed06ee89b78d3af32e235e0e89ad0d946fcb95d net/mlx5e: Disable preemption when doing TC statistics upcall
- 747ae0a96f1a78b35c5a3d93ad37a16655e16340 Merge tag media/v4.10-4 of git://git.kernel.org/pub/scm/linux/kernel/git/mchehab/linux-media
- 3d4ef329757cfd5e0b23cce97cdeca7e2df89c99 mmc: core: fix multi-bit bus width without high-speed mode
- 1541574f477d4478079ef7a13f6038f4f15ec480 powerpc/mm/radix: Skip ptesync in pte update helpers
- e174793ca9c4ef4494158d9355877443e1675639 powerpc/mm/radix: Use ptep_get_and_clear_full when clearing pte for full mm
- 2dba87682a436e6289aa8dff74f6ab1abe344b8e powerpc/mm/radix: Update pte update sequence for pte clear case
- 3634bf18238eba79caa2b4e7ded6d61ae0f68ed7 Merge tag v4.10-rc8 into hostos-devel
- 0c8ef291d976221319f70753c62e18b48d892590 Merge branch rhashtable-allocation-failure-during-insertion
- 40137906c5f55c252194ef5834130383e639536f rhashtable: Add nested tables
- 9dbbfb0ab6680c6a85609041011484e6658e7d3c tipc: Fix tipc_sk_reinit race conditions
- 6a25478077d987edc5e2f880590a2bc5fcab4441 gfs2: Use rhashtable walk interface in glock_hash_walk
- 4872e57c812dd312bf8193b5933fa60585cda42f NET: Fix /proc/net/arp for AX.25
- ebf692f85ff78092cd238166d8d7ec51419f9c02 xen-netback: vif counters from int/long to u64
- 3ba5b5ea7dc3a10ef50819b43a9f8de2705f4eec x86/vm86: Fix unused variable warning if THP is disabled
- 0c59d28121b96d826c188280f367e754b5d83350 MAINTAINERS: Remove old e-mail address
- 42980da2eb7eb9695d8efc0c0ef145cbbb993b2c [media] cec: initiator should be the same as the destination for, poll
- 35879ee4769099905fa3bda0b21e73d434e2df6a [media] videodev2.h: go back to limited range YCbCr for SRGB and, ADOBERGB
- 25f71d1c3e98ef0e52371746220d66458eac75bc futex: Move futex_init() to core_initcall
- 202461e2f3c15dbfb05825d29ace0d20cdf55fa4 tick/broadcast: Prevent deadlock on tick_broadcast_lock
- 8b74d439e1697110c5e5c600643e823eb1dd0762 net/llc: avoid BUG_ON() in skb_orphan()
- 7f677633379b4abb3281cdbe7e7006f049305c03 bpf: introduce BPF_F_ALLOW_OVERRIDE flag
- 722c5ac708b4f5c1fcfad5fed4c95234c8b06590 Input: elan_i2c - add ELAN0605 to the ACPI table
- 7089db84e356562f8ba737c29e472cc42d530dbc Linux 4.10-rc8
- e722af6391949e8851310441bb0cec157d25611d ibmvnic: Call napi_disable instead of napi_enable in failure path
- db5d0b597bc27bbddf40f2f8359a73be4eb77104 ibmvnic: Initialize completion variables before starting work
- 1ce42845f987e92eabfc6e026d44d826c25c74a5 Merge branch x86-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- fdb0ee7c65781464168e2943a3fd6f1e66a397c9 Merge branch timers-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- d5b76bef01047843cc65bd018046c76182b1fc81 Merge branch perf-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 4e4f74a7eebbc52eaa1dc3c0be6b3c68c0875b09 Merge branch locking-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 21a7061c5ec300a8a12a0d6468eb7094e9c54a32 Merge branch irq-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 2b95550a4323e501e133dac1c9c9cad6ff17f4c1 Merge branch for-linus-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/mason/linux-btrfs
- 13ebfd0601228fbbd92707ce4944ab1a09a4d821 Merge tag scsi-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/jejb/scsi
- 6e78b3f7a193546b1c00a6d084596e774f147169 Btrfs: fix btrfs_decompress_buf2page()
- 1ee18329fae936089c6c599250ae92482ff2b81f Merge git://git.kernel.org/pub/scm/linux/kernel/git/davem/net
- a9dbf5c8d4c90f54777f89daf0e34d390808b672 Merge tag for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/dledford/rdma
- aca9fa0c8d225b1446dbed798b1d2f20e37e52cf Merge branch i2c/for-current of git://git.kernel.org/pub/scm/linux/kernel/git/wsa/linux
- fc6f41ba8b2e705f91324db158c3cc28209a15b1 Merge tag mmc-v4.10-rc7 of git://git.kernel.org/pub/scm/linux/kernel/git/ulfh/mmc
- 1f369d1655c1de415a186c6ce9004e40ca790989 Merge tag sound-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/tiwai/sound
- 7fe654dca20892f37226c31bdd2d5b932f8d843a Merge tag nfsd-4.10-3 of git://linux-nfs.org/~bfields/linux
- 3ebc7033168d43d12e4941f48a6f257d3f1ea1b5 Merge tag powerpc-4.10-4 of git://git.kernel.org/pub/scm/linux/kernel/git/powerpc/linux
- 72fb96e7bdbbdd4421b0726992496531060f3636 l2tp: do not use udp_ioctl()
- f3c7bfbda7ce03c603b4292efddc944228dccc55 Merge branch for-chris of git://git.kernel.org/pub/scm/linux/kernel/git/kdave/linux into for-linus-4.10
- 74470954857c264168d2b5a113904cf0cfd27d18 xen-netfront: Delete rx_refill_timer in xennet_disconnect_backend()
- 7ba1b689038726d34e3244c1ac9e2e18c2ea4787 NET: mkiss: Fix panic
- b85ea006b6bebb692628f11882af41c3e12e1e09 net: hns: Fix the device being used for dma mapping during TX
- d128dfb514f55af040c38a6b3b131d72b6f115d0 Merge tag irqchip-fixes-4.10 of git://git.infradead.org/users/jcooper/linux into irq/urgent
- 146fbb766934dc003fcbf755b519acef683576bf x86/mm/ptdump: Fix soft lockup in page table walker
- 5f2e71e71410ecb858cfec184ba092adaca61626 x86/tsc: Make the TSC ADJUST sanitizing work for tsc_reliable
- f2e04214ef7f7e49d1e06109ad1b2718155dab25 x86/tsc: Avoid the large time jump when sanitizing TSC ADJUST
- 7bdb59f1ad474bd7161adc8f923cdef10f2638d1 tick/nohz: Fix possible missing clock reprog after tick soft restart
- 451d24d1e5f40bad000fa9abe36ddb16fc9928cb perf/core: Fix crash in perf_event_read()

* Wed Feb 15 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.10.0-2.rc7.gitd8e9273
- d8e9273fa27a343d48cdb9652def3ae3d06848ec PCI: Revert remaining pieces of BAR alignment patchset
- 1492b8884389a4f2fe7b77101844046fd3808a1a Revert PCI: Ignore enforced alignment when kernel uses existing firmware setup
- b38e722a9ecaec84b607fc17c7f39c6eca655bd1 Revert PCI: Ignore enforced alignment to VF BARs
- 58b5a4ba9e4b7a902fbb8dfdacdd0197940369c5 Revert PCI: Do not disable memory decoding in pci_reassigndev_resource_alignment()
- 14dd54b500cecad060592c92e39506688673268d Merge tag v4.10-rc7 into hostos-devel
- cf4fbae24593a53617ef9f0f14545fad31f60680 Merge branch kvm-ppc-next into hostos-devel
- a4a741a04814170358f470d7103f8b13ceb6fefc Merge remote-tracking branch remotes/powerpc/topic/ppc-kvm into kvm-ppc-next
- ab9bad0ead9ab179ace09988a3f1cfca122eb7c2 powerpc/powernv: Remove separate entry for OPAL real mode calls
- 2337d207288f163e10bd8d4d7eeb0c1c75046a0c powerpc/64: CONFIG_RELOCATABLE support for hmi interrupts
- d5adbfcd5f7bcc6fa58a41c5c5ada0e5c826ce2c Linux 4.10-rc7
- a572a1b999489efb591287632279c6c9eca3e4ed Merge branch irq-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 24bc5fe716855e5e608c515340b3ceacfb143bcc Merge tag for-linus of git://git.kernel.org/pub/scm/virt/kvm/kvm
- 412e6d3fec247b2bc83106514b0fb3b17e2eb7fe Merge tag char-misc-4.10-rc7 of git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/char-misc
- 252bf9f4c43fd58f96587a97866cb7cc980e7544 Merge tag staging-4.10-rc7 of git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/staging
- 8fcdcc42a5268f298ac91962a5e816294435006f Merge tag usb-4.10-rc7 of git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/usb
- a0a28644c1cf191e514dd64bf438e69c178b8440 Merge tag scsi-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/jejb/scsi
- a49e6f584e29785f9e5eb8dd31435746818dd5c4 Merge tag for_linus of git://git.kernel.org/pub/scm/linux/kernel/git/mst/vhost
- e9f7f17d53003ee46ccbaf057f7820bfb6e76b9d Merge tag vfio-v4.10-rc7 of git://github.com/awilliam/linux-vfio
- 7a92cc6bcbc90bf72e57eff2dc29900a636c2d0d Merge branch akpm (patches from Andrew)
- 5abf186a30a89d5b9c18a6bf93a2c192c9fd52f6 mm, fs: check for fatal signals in do_generic_file_read()
- d1908f52557b3230fbd63c0429f3b4b748bf2b6d fs: break out of iomap_file_buffered_write on fatal signals
- a96dfddbcc04336bbed50dc2b24823e45e09e80c base/memory, hotplug: fix a kernel oops in show_valid_zones()
- deb88a2a19e85842d79ba96b05031739ec327ff4 mm/memory_hotplug.c: check start_pfn in test_pages_in_a_zone()
- 35f860f9ba6aac56cc38e8b18916d833a83f1157 jump label: pass kbuild_cflags when checking for asm goto support
- 253fd0f02040a19c6fe80e4171659fa3482a422d shmem: fix sleeping from atomic context
- 4f40c6e5627ea73b4e7c615c59631f38cc880885 kasan: respect /proc/sys/kernel/traceoff_on_warning
- d7b028f56a971a2e4d8d7887540a144eeefcd4ab zswap: disable changing params if init fails
- 3f67790d2b7e322bcf363ec717085dd78c3ea7cd Merge tag regulator-fix-v4.10-rc6 of git://git.kernel.org/pub/scm/linux/kernel/git/broonie/regulator
- 79134d11d030b886106bf45a5638c1ccb1f0856c MAINTAINERS: update email address for Amit Shah
- cda8bba0f99d25d2061c531113c14fa41effc3ae vhost: fix initialization for vq->is_le
- 0d5415b489f68b58e1983a53793d25d53098ed4b Revert vring: Force use of DMA API for ARM-based systems with legacy devices
- 424414947da3dd5cb0d60e4f299f7c51e472ae77 Merge tag usb-serial-4.10-rc7 of git://git.kernel.org/pub/scm/linux/kernel/git/johan/usb-serial into usb-linus
- cd44691f7177b2c1e1509d1a17d9b198ebaa34eb Merge tag mmc-v4.10-rc6 of git://git.kernel.org/pub/scm/linux/kernel/git/ulfh/mmc
- 79c9089f97d37ffac88c3ddb6d359b2cf75058b7 Merge tag drm-fixes-for-v4.10-rc7 of git://people.freedesktop.org/~airlied/linux
- 57480b98af696795ab0daff0a6ed572172060a0f Merge tag powerpc-4.10-3 of git://git.kernel.org/pub/scm/linux/kernel/git/powerpc/linux
- 2d47b8aac7ba697ffe05f839a3b4c3c628b4e430 Merge tag trace-v4.10-rc2-2 of git://git.kernel.org/pub/scm/linux/kernel/git/rostedt/linux-trace
- 2cb54ce9ee92ae627bc1cef8bea236905910a86d Merge branch modversions (modversions fixes for powerpc from Ard)
- 29905b52fad0854351f57bab867647e4982285bf log2: make order_base_2() behave correctly on const input value zero
- 00c87e9a70a17b355b81c36adedf05e84f54e10d KVM: x86: do not save guest-unsupported XSAVE state
- 4b9eee96fcb361a5e16a8d2619825e8a048f81f7 module: unify absolute krctab definitions for 32-bit and 64-bit
- 71810db27c1c853b335675bee335d893bc3d324b modversions: treat symbol CRCs as 32 bit quantities
- 56067812d5b0e737ac2063e94a50f76b810d6ca3 kbuild: modversions: add infrastructure for emitting relative CRCs
- 206c4720092d2a24bfefc041b377e889a220ffbf Merge remote-tracking branches regulator/fix/fixed and regulator/fix/twl6040 into regulator-linus
- f63cf464fc379382a271f94ddef36e8c5a0628eb Merge branch drm-fixes-4.10 of git://people.freedesktop.org/~agd5f/linux into drm-fixes
- a20def95401112358bcc90242f252a96084a2d47 Merge tag topic/vma-fix-for-4.10-2017-02-02 of git://anongit.freedesktop.org/git/drm-intel into drm-fixes
- 34e00accf612bc5448ae709245c2b408edf39f46 Merge branch x86-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 891aa1e0f13c3aaa756c69b343d6ab6f3357009b Merge branch perf-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- c67b42f3a3f03e68bf915f32c8f7be0b726fec1a Merge branch efi-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 027eb72cbcf81561867a764074964e2ce9828398 Merge branch core-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 1fc576b82b96d9bb033ff0098e1c0bf68de282b2 Merge tag nfsd-4.10-2 of git://linux-nfs.org/~bfields/linux
- e4178c75049c581114998a850ecdfa5a2811cde6 Merge tag xtensa-20170202 of git://github.com/jcmvbkbc/linux-xtensa
- f2557779e1a9cfbf69c99b74da26cc1b2b10e752 Merge tag pci-v4.10-fixes-2 of git://git.kernel.org/pub/scm/linux/kernel/git/helgaas/pci
- 51964e9e12d0a054002a1a0d1dec4f661c7aaf28 drm/radeon: Fix vram_size/visible values in DRM_RADEON_GEM_INFO ioctl
- 57bcd0a6364cd4eaa362d7ff1777e88ddf501602 drm/amdgpu/si: fix crash on headless asics
- 26a346f23c5291d1d9521e72763103daf2c6f0d1 tracing/kprobes: Fix __init annotation
- c8f325a59cfc718d13a50fbc746ed9b415c25e92 efi/fdt: Avoid FDT manipulation after ExitBootServices()
- 6d04dfc8966019b8b0977b2cb942351f13d2b178 Merge git://git.kernel.org/pub/scm/linux/kernel/git/davem/net
- 2883aaea363f7a897ff06d2e6c73ae7aae285bcb Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/viro/vfs
- 06425c308b92eaf60767bc71d359f4cbc7a561f8 tcp: fix 0 divide in __tcp_select_window()
- 63117f09c768be05a0bf465911297dc76394f686 ipv6: pointer math error in ip6_tnl_parse_tlv_enc_lim()
- e387dc122fc7c70c2a5df2567f4e2d1114f5a5da Merge branch linus of git://git.kernel.org/pub/scm/linux/kernel/git/herbert/crypto-2.6
- 35609502ac5dea2b149ec0368791d9c0e246bd65 Merge tag dmaengine-fix-4.10-rc7 of git://git.infradead.org/users/vkoul/slave-dma
- 1a2a14444d32b89b28116daea86f63ced1716668 net: fix ndo_features_check/ndo_fix_features comment ordering
- fd62d9f5c575f0792f150109f1fd24a0d4b3f854 net/sched: matchall: Fix configuration race
- 2da64d20a0b20046d688e44f4033efd09157e29d vfio/spapr: Fix missing mutex unlock when creating a window
- c325b3533730016ca5cdaf902d62550b4243fe43 Merge tag pinctrl-v4.10-4 of git://git.kernel.org/pub/scm/linux/kernel/git/linusw/linux-pinctrl
- 4993b39ab04b083ff6ee1147e7e7f120feb6bf7f be2net: fix initial MAC setting
- e8fe4f4b2b7b93048729538321c681c0cff33b39 drm/i915: Track pinned vma in intel_plane_state
- eeee74a4f6625b77c3e8db0693c2d4546507ba0d drm/atomic: Unconditionally call prepare_fb.
- fff4b87e594ad3d2e4f51e8d3d86a6f9d3d8b654 perf/x86/intel/uncore: Make package handling more robust
- 1aa6cfd33df492939b0be15ebdbcff1f8ae5ddb6 perf/x86/intel/uncore: Clean up hotplug conversion fallout
- dd86e373e09fb16b83e8adf5c48c421a4ca76468 perf/x86/intel/rapl: Make package handling more robust
- 4b3e6f2ef3722f1a6a97b6034ed492c1a21fd4ae xtensa: fix noMMU build on cores with MMU
- a2ca3d617944417e9dd5f09fc8a4549cda115f4f Merge tag trace-4.10-rc2 of git://git.kernel.org/pub/scm/linux/kernel/git/rostedt/linux-trace
- 52b679f60e2a68af88411f12318675a2424a0e14 Merge tag drm-misc-fixes-2017-01-31 of git://anongit.freedesktop.org/git/drm-misc into drm-fixes
- 283725af0bd2a4a8600bbe5edeb9d7c72780d3a2 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/dtor/input
- f1774f46d49f806614d81854321ee9e5138135e5 Merge branch for-4.10-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/tj/cgroup
- 298a2d87518ec01bb36070fafe31da7746556db0 Merge branch for-4.10-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/tj/percpu
- 52e02f2797cf44e00da987a7736cc0f5192132f7 Merge branch for-4.10-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/tj/libata
- c9194b99ae1825bdbafc701965442a47739ff0ad Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/jikos/hid
- 0becc0ae5b42828785b589f686725ff5bc3b9b25 x86/mce: Make timer handling more robust
- 415f9b71d17d294c2f2075b3fc7717d72e5e48f9 Merge branch for-next of git://git.samba.org/sfrench/cifs-2.6
- edc67410449c668434b183bb0f770b7bf456c750 Merge branch linux-4.10 of git://github.com/skeggsb/linux into drm-fixes
- aaaec6fc755447a1d056765b11b24d8ff2b81366 x86/irq: Make irq activate operations symmetric
- e26bfebdfc0d212d366de9990a096665d5c0209a fscache: Fix dead object requeue
- 6bdded59c8933940ac7e5b416448276ac89d1144 fscache: Clear outstanding writes when disabling a cookie
- 62deb8187d116581c88c69a2dd9b5c16588545d4 FS-Cache: Initialise stores_lock in netfs cookie
- 90427ef5d2a4b9a24079889bf16afdcdaebc4240 ipv6: fix flow labels when the traffic class is non-0
- c73e44269369e936165f0f9b61f1f09a11dae01c net: thunderx: avoid dereferencing xcv when NULL
- 034dd34ff4916ec1f8f74e39ca3efb04eab2f791 svcrpc: fix oops in absence of krb5 module
- 41f53350a0f36a7b8e31bec0d0ca907e028ab4cd nfsd: special case truncates some more
- d19fb70dd68c4e960e2ac09b0b9c79dfdeefa726 NFSD: Fix a null reference case in find_or_create_lock_stateid()
- d07830db1bdb254e4b50d366010b219286b8c937 USB: serial: pl2303: add ATEN device ID
- 79c6f448c8b79c321e4a1f31f98194e4f6b6cae7 tracing: Fix hwlat kthread migration
- 92c715fca907686f5298220ece53423e38ba3aed drm/atomic: Fix double free in drm_atomic_state_default_clear
- 8e9faa15469ed7c7467423db4c62aeed3ff4cae3 HID: cp2112: fix gpio-callback error handling
- 7a7b5df84b6b4e5d599c7289526eed96541a0654 HID: cp2112: fix sleep-while-atomic

* Thu Feb 02 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.10.0-1.rc6
- Version update
- bbbdfd8db1fce91da2c7625742f80c268d6671be Merge branch kvm-ppc-next into hostos-devel
- 050f23390f6bdbfa7dd2800884d32490489851b7 KVM: PPC: Book3S HV: Advertise availablity of HPT resizing on KVM HV
- b5baa68773150772c275b4af1bb31327200cfc05 KVM: PPC: Book3S HV: KVM-HV HPT resizing implementation
- 5e9859699aba74c0e297645e7d1734cd4b964de7 KVM: PPC: Book3S HV: Outline of KVM-HV HPT resizing implementation
- 639e459768845924705933db9142baef545ff5fc KVM: PPC: Book3S HV: Create kvmppc_unmap_hpte_helper()
- f98a8bf9ee201b7e22fc05e27150b1e481d4949f KVM: PPC: Book3S HV: Allow KVM_PPC_ALLOCATE_HTAB ioctl() to change HPT size
- aae0777f1e8224b4fbb78b2c692060852ee750c8 KVM: PPC: Book3S HV: Split HPT allocation from activation
- 3d089f84c6f9b7b0eda993142d73961a44b553d2 KVM: PPC: Book3S HV: Dont store values derivable from HPT order
- 3f9d4f5a5f35e402e91bedf0c15e29cef187a29d KVM: PPC: Book3S HV: Gather HPT related variables into sub-structure
- db9a290d9c3c596e5325e2a42133594435e5de46 KVM: PPC: Book3S HV: Rename kvm_alloc_hpt() for clarity
- ef1ead0c3b1dfb43d33caa4f50c8d214f86b6bc8 KVM: PPC: Book3S HV: HPT resizing documentation and reserved numbers
- ccc4df4e2c3825919456c13b153d2a67bbf328dc Documentation: Correct duplicate section number in kvm/api.txt
- 167c76e05591c2b656c0f329282f453dd46f4ea5 Merge remote-tracking branch remotes/powerpc/topic/ppc-kvm into kvm-ppc-next
- 8cf4ecc0ca9bd9bdc9b4ca0a99f7445a1e74afed KVM: PPC: Book3S HV: Enable radix guest support
- f11f6f79b606fb54bb388d0ea652ed889b2fdf86 KVM: PPC: Book3S HV: Invalidate ERAT on guest entry/exit for POWER9 DD1
- 53af3ba2e8195f504d6a3a0667ccb5e7d4c57599 KVM: PPC: Book3S HV: Allow guest exit path to have MMU on
- a29ebeaf5575d03eef178bb87c425a1e46cae1ca KVM: PPC: Book3S HV: Invalidate TLB on radix guest vcpu movement
- 65dae5403a162fe6ef7cd8b2835de9d23c303891 KVM: PPC: Book3S HV: Make HPT-specific hypercalls return error in radix mode
- 8f7b79b8379a85fb8dd0c3f42d9f452ec5552161 KVM: PPC: Book3S HV: Implement dirty page logging for radix guests
- 01756099e0a5f431bbada9693d566269acfb51f9 KVM: PPC: Book3S HV: MMU notifier callbacks for radix guests
- 5a319350a46572d073042a3194676099dd2c135d KVM: PPC: Book3S HV: Page table construction and page faults for radix guests
- f4c51f841d2ac7d36cacb84efbc383190861f87c KVM: PPC: Book3S HV: Modify guest entry/exit paths to handle radix guests
- 9e04ba69beec372ddf857c700ff922e95f50b0d0 KVM: PPC: Book3S HV: Add basic infrastructure for radix guests
- ef8c640cb9cc865a461827b698fcc55b0ecaa600 KVM: PPC: Book3S HV: Use ASDR for HPT guests on POWER9
- 468808bd35c4aa3cf7d9fde0ebb010270038734b KVM: PPC: Book3S HV: Set process table for HPT guests on POWER9
- c92701322711682de89b2bd0f32affad040b6e86 KVM: PPC: Book3S HV: Add userspace interfaces for POWER9 MMU
- bc3551257af837fc603d295e59f9e32953525b98 powerpc/64: Allow for relocation-on interrupts from guest to host
- 16ed141677c5a1a796408e74ccd0a6f6554c3f21 powerpc/64: Make type of partition table flush depend on partition type
- ba9b399aee6fb70cbe988f0750d6dd9f6677293b powerpc/64: Export pgtable_cache and pgtable_cache_add for KVM
- dbcbfee0c81c7938e40d7d6bc659a5191f490b50 powerpc/64: More definitions for POWER9
- cc3d2940133d24000e2866b21e03ce32adfead0a powerpc/64: Enable use of radix MMU under hypervisor on POWER9
- 3f4ab2f83b4e443c66549206eb88a9fa5a85d647 powerpc/pseries: Fixes for the ibm,architecture-vec-5 options
- 18569c1f134e1c5c88228f043c09678ae6052b7c powerpc/64: Dont try to use radix MMU under a hypervisor
- a97a65d53d9f53b6897dc1b2aed381bc1707136b KVM: PPC: Book3S: 64-bit CONFIG_RELOCATABLE support for interrupts
- 98c4aedd3de6d6d6b7fc29b7b34eb4250b429729 Merge tag v4.10-rc6 into hostos-devel
- 566cf877a1fcb6d6dc0126b076aad062054c2637 Linux 4.10-rc6
- 39cb2c9a316e77f6dfba96c543e55b6672d5a37e drm/i915: Check for NULL i915_vma in intel_unpin_fb_obj()
- 2c5d9555d6d937966d79d4c6529a5f7b9206e405 Merge branch parisc-4.10-3 of git://git.kernel.org/pub/scm/linux/kernel/git/deller/parisc-linux
- 53cd1ad1a68fd10f677445e04ed63aa9ce39b36b Merge branch i2c/for-current of git://git.kernel.org/pub/scm/linux/kernel/git/wsa/linux
- 2ad5d52d42810bed95100a3d912679d8864421ec parisc: Dont use BITS_PER_LONG in userspace-exported swab.h header
- 83b5d1e3d3013dbf90645a5d07179d018c8243fa parisc, parport_gsc: Fixes for printk continuation lines
- d56a5ca366e785f463b4782f65daac883612a2b2 Merge tag nfs-for-4.10-4 of git://git.linux-nfs.org/projects/trondmy/linux-nfs
- dd553962675ab5747e887f89aea1ece90e6a802e Merge tag md/4.10-rc6 of git://git.kernel.org/pub/scm/linux/kernel/git/shli/md
- 64a172d265643b345007ddaafcc523f6e5373b69 Merge tag arm64-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/arm64/linux
- ef1dce990b06a3f5bf4f71100891686b5d3f7c7e Merge tag arc-4.10-rc6 of git://git.kernel.org/pub/scm/linux/kernel/git/vgupta/arc
- 1b1bc42c1692e9b62756323c675a44cb1a1f9dbd Merge git://git.kernel.org/pub/scm/linux/kernel/git/davem/net
- 3365135d43f861003555c963b309672d053a2228 Merge tag xfs-for-linus-4.10-rc6-5 of git://git.kernel.org/pub/scm/fs/xfs/xfs-linux
- 5906374446386fd16fe562b042429d905d231ec3 Merge branch for-linus-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/mason/linux-btrfs
- 2fb78e89405f4321b86274a0c24b30896dd50529 Merge branch for-linus of git://git.kernel.dk/linux-block
- dd3b9f25c867cb2507a45e436d6ede8eb08e7b05 Merge tag for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/dledford/rdma
- 69978aa0f21f43529e11f924504dadb6ce2f229a Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/s390/linux
- 2b4321503e62523e701405163a034875e92d68cf Merge branch stable/for-linus-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/konrad/swiotlb
- 3aebae061cea6f6627ab882a73de7b0b21af3127 Merge tag vfio-v4.10-rc6 of git://github.com/awilliam/linux-vfio
- b4cfe3971f6eab542dd7ecc398bfa1aeec889934 RDMA/cma: Fix unknown symbol when CONFIG_IPV6 is not enabled
- c14024dbb156c8392908aaa822097d27c6af8ec8 Merge branch stable/for-jens-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/konrad/xen into for-linus
- 9aed02feae57bf7a40cb04ea0e3017cb7a998db4 ARC: [arcompact] handle unaligned access delay slot corner case
- 9d1d166f18f8f0f332573b8d2e28e5b3291f09c5 Merge tag media/v4.10-2 of git://git.kernel.org/pub/scm/linux/kernel/git/mchehab/linux-media
- b84f02795e3bcf197ae13a7e3ac6cc9d66d2feaa Merge tag mmc-v4.10-rc5 of git://git.kernel.org/pub/scm/linux/kernel/git/ulfh/mmc
- ed4d50c42d67769138b49de7dc672b76c88ee1c8 Merge branch for-rc of git://git.kernel.org/pub/scm/linux/kernel/git/rzhang/linux
- e0d76fa4475ef2cf4b52d18588b8ce95153d021b xfs: prevent quotacheck from overloading inode lru
- 950eabbd6ddedc1b08350b9169a6a51b130ebaaf ISDN: eicon: silence misleading array-bounds warning
- 9d162ed69f51cbd9ee5a0c7e82aba7acc96362ff net: phy: micrel: add support for KSZ8795
- 95120ebf647180fbcfba3172677f18116f9231d5 Merge branch gtp-fixes
- 3ab1b469e847ba425af3c5ad5068cc94b55b38d0 gtp: fix cross netns recv on gtp socket
- c6ce1d08eede4c2968ed08aafa3165e8e183c5a1 gtp: clear DF bit on GTP packet tx
- ab729823ec16aef384f09fd2cffe0b3d3f6e6cba gtp: add genl family modules alias
- 92e55f412cffd016cc245a74278cb4d7b89bb3bc tcp: dont annotate mark on control socket from tcp_v6_send_response()
- 606f42265d384b9149bfb953c5dfc6d4710fef4c arm64: skip register_cpufreq_notifier on ACPI-based systems
- fcd4f3c6d150357a02af8526e69bfebb82dd5d46 KVM: PPC: Book3S PR: Refactor program interrupt related code into separate function
- 8464c8842de2249061d3c5abc2ccce1bbbd10e7a KVM: PPC: Book3S HV: Fix H_PROD to actually wake the target vcpu
- 7ede531773ea69fa56b02a873ed83ce3507eb8d5 KVM: PPC: Book3S: Move 64-bit KVM interrupt handler out from alt section
- d3918e7fd4a27564f93ec46d0359a9739c5deb8d KVM: PPC: Book3S: Change interrupt call to reduce scratch space use on HV
- fd694aaa46c7ed811b72eb47d5eb11ce7ab3f7f1 Merge tag drm-fixes-for-v4.10-rc6-part-two of git://people.freedesktop.org/~airlied/linux
- 736a1494e27a0e0f2e09d0b218c1475771807f8f Merge tag drm-intel-fixes-2017-01-26 of git://anongit.freedesktop.org/git/drm-intel into drm-fixes
- 2287a240a6b1c39fd06f94e57b8c0189c497efe5 Merge tag acpi-4.10-rc6 of git://git.kernel.org/pub/scm/linux/kernel/git/rafael/linux-pm
- 7d3a0fa52e4d9fa2cfe04a5f6e21d1d78169edb5 Merge tag pm-4.10-rc6 of git://git.kernel.org/pub/scm/linux/kernel/git/rafael/linux-pm
- 15266ae38fe09dae07bd8812cb7a7717b1e1d992 drm/nouveau: Handle fbcon suspend/resume in seperate worker
- cae9ff036eea577856d5b12860b4c79c5e71db4a drm/nouveau: Dont enabling polling twice on runtime resume
- 6c971c09f38704513c426ba6515f22fb3d6c87d5 drm/ast: Fixed system hanged if disable P2A
- e996598b282d2ebafe705d297d3fee9044286dc6 Merge tag drm-vc4-fixes-2017-01-23 of https://github.com/anholt/linux into drm-fixes
- 1fb2d35411364a329557e4c02fbb42a6adbfa567 Merge branch drm-fixes-4.10 of git://people.freedesktop.org/~agd5f/linux into drm-fixes
- 99f300cf1f3877ad8ea923127de817a460b787bd Merge tag drm-misc-fixes-2017-01-23 of git://anongit.freedesktop.org/git/drm-misc into drm-fixes
- 57b59ed2e5b91e958843609c7884794e29e6c4cb Btrfs: remove ->{get, set}_acl() from btrfs_dir_ro_inode_operations
- 1fdf41941b8010691679638f8d0c8d08cfee7726 Btrfs: disable xattr operations on subvolume directories
- 67ade058ef2c65a3e56878af9c293ec76722a2e5 Btrfs: remove old tree_root case in btrfs_read_locked_inode()
- a47b70ea86bdeb3091341f5ae3ef580f1a1ad822 ravb: unmap descriptors when freeing rings
- 0389227dde3abae442521948caf5c173e696cdca Merge branches acpica and acpi-video
- 21acd0e4df04f02176e773468658c3cebff096bb KVM: PPC: Book 3S: XICS: Dont lock twice when checking for resend
- 17d48610ae0fa218aa386b16a538c792991a3652 KVM: PPC: Book 3S: XICS: Implement ICS P/Q states
- bf5a71d53835110d46d33eb5335713ffdbff9ab6 KVM: PPC: Book 3S: XICS: Fix potential issue with duplicate IRQ resends
- 37451bc95dee0e666927d6ffdda302dbbaaae6fa KVM: PPC: Book 3S: XICS: correct the real mode ICP rejecting counter
- 5efa6605151b84029edeb2e07f2d2d74b52c106f KVM: PPC: Book 3S: XICS cleanup: remove XICS_RM_REJECT
- ff7e593c9cf3ccceaab7ac600cbd52cb9ff4c57a Merge branches pm-sleep and pm-cpufreq
- 3deda5e50c893be38c1b6b3a73f8f8fb5560baa4 KVM: PPC: Book3S HV: Dont try to signal cpu -1
- ee6625a948d2e47267ec8fd97307fdd67d0f8a5b pNFS: Fix a reference leak in _pnfs_return_layout
- 406dab8450ec76eca88a1af2fc15d18a2b36ca49 nfs: Fix Dont increment lock sequence ID after NFS4ERR_MOVED
- 086cb6a41264b5af33928b82e09ae7f0f8bbc291 Merge git://git.kernel.org/pub/scm/linux/kernel/git/pablo/nf
- c364b6d0b6cda1cd5d9ab689489adda3e82529aa xfs: fix bmv_count confusion w/ shared extents
- ff9f8a7cf935468a94d9927c68b00daae701667e sysctl: fix proc_doulongvec_ms_jiffies_minmax()
- 928d336a93534df66c0448db61cc4d22705e5b9e Merge tag pinctrl-v4.10-3 of git://git.kernel.org/pub/scm/linux/kernel/git/linusw/linux-pinctrl
- 08965c2eba135bdfb6e86cf25308e01421c7e0ce Revert sd: remove __data_len hack for WRITE SAME
- 0d4ee015d5ea50febb882d00520d62c6de3f725c Merge branch nvme-4.10-fixes of git://git.infradead.org/nvme into for-linus
- bed7b016091d2f9bdc3f3c28899b33adab7c4786 Merge tag drm-fixes-for-v4.10-rc6-revert-one of git://people.freedesktop.org/~airlied/linux
- 19e420bb4076ace670addc55300e3b8c4a02dfc6 nvme-fc: use blk_rq_nr_phys_segments
- 748ff8408f8e208f279ba221e5c12612fbb4dddb nvmet-rdma: Fix missing dma sync to nvme data structures
- 23a8ed4a624324dc696c328f09bd502c4a3816f0 nvmet: Call fatal_error from keep-alive timout expiration
- 06406d81a2d7cfb8abcc4fa6cdfeb8e5897007c5 nvmet: cancel fatal error and flush async work before free controller
- 344770b07b7ae70639ebf110010eb6156a6e55e9 nvmet: delete controllers deletion upon subsystem release
- c81e55e057b6458aac6d96a6429ef021b7f6f62c nvmet_fc: correct logic in disconnect queue LS handling
- 2aa6ba7b5ad3189cc27f14540aa2f57f0ed8df4b xfs: clear _XBF_PAGES from buffers when readahead page
- 214767faa2f31285f92754393c036f13b55474a6 Merge tag batadv-net-for-davem-20170125 of git://git.open-mesh.org/linux-merge
- 529ec6ac26656378435eb0396a780f017d51e105 virtio_net: reject XDP programs using header adjustment
- b68df015609eac67f045c155cb3195e5a1061d66 virtio_net: use dev_kfree_skb for small buffer XDP receive
- 7480888f27e080ad5addb51456b2e03514721c3a Merge branch r8152-napi-fixes
- 7489bdadb7d17d3c81e39b85688500f700beb790 r8152: check rx after napi is enabled
- 248b213ad908b88db15941202ef7cb7eb137c1a0 r8152: re-schedule napi for tx
- de9bf29dd6e4a8a874cb92f8901aed50a9d0b1d3 r8152: avoid start_xmit to schedule napi when napi is disabled
- 26afec39306926654e9cd320f19bbf3685bb0997 r8152: avoid start_xmit to call napi_schedule during autosuspend
- e13fe92bb58cf9b8f709ec18267ffc9e6ffeb016 i2c: imx-lpi2c: add VLLS mode support
- b9b487e494712c8e5905b724e12f5ef17e9ae6f9 Revert drm/radeon: always apply pci shutdown callbacks
- 0e1929dedea36781e25902118c93edd8d8f09af1 i2c: i2c-cadence: Initialize configuration before probing devices
- 54a07c7bb0da0343734c78212bbe9f3735394962 Revert drm/probe-helpers: Drop locking from poll_enable
- f154be241d22298d2b63c9b613f619fa1086ea75 net: dsa: Bring back device detaching in dsa_slave_suspend()
- d5bdc021ecc8b273259a02ff83ab13b2de9b9717 Merge branch phy-truncated-led-names
- 3c880eb0205222bb062970085ebedc73ec8dfd14 net: phy: leds: Fix truncated LED trigger names
- d6f8cfa3dea294eabf8f302e90176dd6381fb66e net: phy: leds: Break dependency of phy.h on phy_led_triggers.h
- 8a87fca8dd5879eb05a0903cb7ea4fd2a3876ae0 net: phy: leds: Clear phy_num_led_triggers on failure to avoid crash
- 8b901f6bbcf12a20e43105d161bedde093431e61 net-next: ethernet: mediatek: change the compatible string
- 61976fff20f92aceecc3670f6168bfc57a79e047 Documentation: devicetree: change the mediatek ethernet compatible string
- c0d9665f0819837afced95247f230fdc8b041658 Merge branch bnxt_en-rtnl-fixes
- 90c694bb71819fb5bd3501ac397307d7e41ddeca bnxt_en: Fix RTNL lock usage on bnxt_get_port_module_status().
- 0eaa24b971ae251ae9d3be23f77662a655532063 bnxt_en: Fix RTNL lock usage on bnxt_update_link().
- a551ee94ea723b4af9b827c7460f108bc13425ee bnxt_en: Fix bnxt_reset() in the slow path task.
- 49e555a932de57611eb27edf2d1ad03d9a267bdd Merge tag for_linus of git://git.kernel.org/pub/scm/linux/kernel/git/mst/vhost
- 56d806222ace4c3aeae516cd7a855340fb2839d8 tcp: correct memory barrier usage in tcp_check_space()
- 5207f3996338e1db71363fe381c81aaf1e54e4e3 sctp: sctp gso should set feature with NETIF_F_SG when calling skb_segment
- 6f29a130613191d3c6335169febe002cba00edf5 sctp: sctp_addr_id2transport should verify the addr before looking up assoc
- 493611ebd62673f39e2f52c2561182c558a21cb6 xfs: extsize hints are not unlikely in xfs_bmap_btalloc
- 5a93790d4e2df73e30c965ec6e49be82fc3ccfce xfs: remove racy hasattr check from attr ops
- 76d771b4cbe33c581bd6ca2710c120be51172440 xfs: use per-AG reservations for the finobt
- 4dfa2b84118fd6c95202ae87e62adf5000ccd4d0 xfs: only update mount/resv fields on success in __xfs_ag_resv_init
- fd25ea29093e275195d0ae8b2573021a1c98959f Revert ACPI / video: Add force_native quirk for HP Pavilion dv6
- 45d9f43911a96c23ebd08efea0ff57af7016eb32 Merge tag gvt-fixes-2017-01-25 of https://github.com/01org/gvt-linux into drm-intel-fixes
- 2f5db26c2ecb248bdc319feb2990453cb02fc950 drm/i915: reinstate call to trace_i915_vma_bind
- 6f0f02dc56f18760b46dc1bf5b3f7386869d4162 drm/i915: Move atomic state free from out of fence release
- 6d1d427a4e24c403b4adf928d61994bdaa0ca03a drm/i915: Check for NULL atomic state in intel_crtc_disable_noatomic()
- 3781bd6e7d64d5f5bea9fdee11ab9460a700c0e4 drm/i915: Fix calculation of rotated x and y offsets for planar formats
- 21d6e0bde50713922a6520ef84e5fd245b05d468 drm/i915: Dont init hpd polling for vlv and chv from runtime_suspend()
- c34f078675f505c4437919bb1897b1351f16a050 drm/i915: Dont leak edid in intel_crt_detect_ddc()
- a38a7bd1766b42ea0ed14b99be23a653922ed5c8 drm/i915: Release temporary load-detect state upon switching
- 27892bbdc9233f33bf0f44e08aab8f12e0dec142 drm/i915: prevent crash with .disable_display parameter
- b78671591a10218ab18bbea120fd05df7a002e88 drm/i915: Avoid drm_atomic_state_put(NULL) in intel_display_resume
- ba7addcd805e5c83e201b118a2693b921a980b44 MAINTAINERS: update new mail list for intel gvt driver
- 7283accfaef66e6a64f7d3ec0672596dd8e5b144 drm/i915/gvt: Fix kmem_cache_create() name
- bdbfd5196d24a6d0845b549eba6ce8e6fa8bb3d0 drm/i915/gvt/kvmgt: mdev ABI is available_instances, not available_instance
- 3feb479cea37fc623cf4e705631b2e679cbfbd7a Revert thermal: thermal_hwmon: Convert to hwmon_device_register_with_info()
- 883af14e67e8b8702b5560aa64c888c0cd0bd66c Merge branch akpm (patches from Andrew)
- aab45453ff5c77200c6da4ac909f7a4392aed17e MAINTAINERS: add Dan Streetman to zbud maintainers
- 534c9dc982aca01b630297ad5637f6e95e94c1e2 MAINTAINERS: add Dan Streetman to zswap maintainers
- 3277953de2f31dd03c6375e9a9f680ac37fc9d27 mm: do not export ioremap_page_range symbol for external module
- 3705ccfdd1e8b539225ce20e3925a945cc788d67 mn10300: fix build error of missing fpu_save()
- f598f82e204ec0b17797caaf1b0311c52d43fb9a romfs: use different way to generate fsid for BLOCK or MTD
- 4180c4c170a5a33b9987b314d248a9d572d89ab0 frv: add missing atomic64 operations
- e47483bca2cc59a4593b37a270b16ee42b1d9f08 mm, page_alloc: fix premature OOM when racing with cpuset mems update
- 5ce9bfef1d27944c119a397a9d827bef795487ce mm, page_alloc: move cpuset seqcount checking to slowpath
- 16096c25bf0ca5d87e4fa6ec6108ba53feead212 mm, page_alloc: fix fast-path race with cpuset update or removal
- ea57485af8f4221312a5a95d63c382b45e7840dc mm, page_alloc: fix check for NULL preferred_zone
- ff7a28a074ccbea999dadbb58c46212cf90984c6 kernel/panic.c: add missing \n
- 2dc705a9930b4806250fbf5a76e55266e59389f2 fbdev: color map copying bounds checking
- 545d58f677b21401f6de1ac12c25cc109f903ace frv: add atomic64_add_unless()
- d51e9894d27492783fc6d1b489070b4ba66ce969 mm/mempolicy.c: do not put mempolicy before using its nodemask
- dd040b6f6d5630202e185399a2ff7ab356ed469c radix-tree: fix private list warnings
- bbd88e1d53a84df9f57a2e37acc15518c3d304db Documentation/filesystems/proc.txt: add VmPin
- 3674534b775354516e5c148ea48f51d4d1909a78 mm, memcg: do not retry precharge charges
- 3ba4bceef23206349d4130ddf140819b365de7c8 proc: add a schedule point in proc_pid_readdir()
- 424f6c4818bbf1b8ccf58aa012ecc19c0bb9b446 mm: alloc_contig: re-allow CMA to compact FS pages
- aa2efd5ea4041754da4046c3d2e7edaac9526258 mm/slub.c: trace free objects at KERN_INFO
- 15a77c6fe494f4b1757d30cd137fe66ab06a38c3 userfaultfd: fix SIGBUS resulting from false rwsem wakeups
- de182cc8e882f74af2a112e09f148ce646937232 drivers/memstick/core/memstick.c: avoid -Wnonnull warning
- b94f51183b0617e7b9b4fb4137d4cf1cab7547c2 kernel/watchdog: prevent false hardlockup on overloaded system
- 6affb9d7b137fc93d86c926a5587e77b8bc64255 dax: fix build warnings with FS_DAX and !FS_IOMAP
- 8310d48b125d19fcd9521d83b8293e63eb1646aa mm/huge_memory.c: respect FOLL_FORCE/FOLL_COW for thp
- 8a1f780e7f28c7c1d640118242cf68d528c456cd memory_hotplug: make zone_can_shift() return a boolean value
- c7070619f3408d9a0dffbed9149e6f00479cf43b vring: Force use of DMA API for ARM-based systems with legacy devices
- f7f6634d23830ff74335734fbdb28ea109c1f349 virtio_mmio: Set DMA masks appropriately
- 0516ffd88fa0d006ee80389ce14a9ca5ae45e845 vhost/vsock: handle vhost_vq_init_access() error
- 78f824d4312a8944f5340c6b161bba3bf2c81096 ARCv2: smp-boot: wake_flag polling by non-Masters needs to be uncached
- ec221a17a638dec4d9b0ba3e5817113f249dd194 Merge branch lwt-module-unload
- 85c814016ce3b371016c2c054a905fa2492f5a65 lwtunnel: Fix oops on state free after encap module unload
- 88ff7334f25909802140e690c0e16433e485b0a0 net: Specify the owning module for lwtunnel ops
- 2d4b21e0a2913612274a69a3ba1bfee4cffc6e77 IB/rxe: Prevent from completer to operate on non valid QP
- f39f775218a7520e3700de2003c84a042c3b5972 IB/rxe: Fix rxe dev insertion to rxe_dev_list
- 04d7f1fb7d25256d8c21b78c7d46193b4a7fabfe Merge branch tipc-topology-fixes
- 35e22e49a5d6a741ebe7f2dd280b2052c3003ef7 tipc: fix cleanup at module unload
- 4c887aa65d38633885010277f3482400681be719 tipc: ignore requests when the connection state is not CONNECTED
- 9dc3abdd1f7ea524e8552e0a3ef01219892ed1f4 tipc: fix nametbl_lock soft lockup at module exit
- fc0adfc8fd18b61b6f7a3f28b429e134d6f3a008 tipc: fix connection refcount error
- d094c4d5f5c7e1b225e94227ca3f007be3adc4e8 tipc: add subscription refcount to avoid invalid delete
- 93f955aad4bacee5acebad141d1a03cd51f27b4e tipc: fix nametbl_lock soft lockup at node/link events
- b2c11e4b9536ebab6b39929e1fe15f57039ab445 netfilter: nf_tables: bump set->ndeact on set flush
- de70185de0333783154863278ac87bfbbc54e384 netfilter: nf_tables: deconstify walk callback function
- 35d0ac9070ef619e3bf44324375878a1c540387b netfilter: nf_tables: fix set->nelems counting with no NLM_F_EXCL
- 5ce6b04ce96896e8a79e6f60740ced911eaac7a4 netfilter: nft_log: restrict the log prefix length to 127
- 828f6fa65ce7e80f77f5ab12942e44eb3d9d174e IB/umem: Release pid in error and ODP flow
- 0263d4ebd94b36280608e296cba39b924b6e832b Merge tag platform-drivers-x86-v4.10-4 of git://git.infradead.org/linux-platform-drivers-x86
- f449c7a2d822c2d81b5bcb2c50eec80796766726 RDMA/qedr: Dispatch port active event from qedr_add
- 9c1e0228ab35e52d30abf4b5629c28350833fbcb RDMA/qedr: Fix and simplify memory leak in PD alloc
- af2b14b8b8ae21b0047a52c767ac8b44f435a280 RDMA/qedr: Fix RDMA CM loopback
- 1a59075197976611bacaa383a6673f9e57e9e98b RDMA/qedr: Fix formatting
- 27a4b1a6d6fcf09314359bacefa1e106927ae21b RDMA/qedr: Mark three functions as static
- 933e6dcaa0f65eb2f624ad760274020874a1f35e RDMA/qedr: Dont reset QP when queues arent flushed
- c78c31496111f497b4a03f955c100091185da8b6 RDMA/qedr: Dont spam dmesg if QP is in error state
- 91bff997db2ec04f9ba761a55c21642f9803b06c RDMA/qedr: Remove CQ spinlock from CM completion handlers
- 59e8970b3798e4cbe575ed9cf4d53098760a2a86 RDMA/qedr: Return max inline data in QP query result
- 865cea40b69741c3da2574176876463233b2b67c RDMA/qedr: Return success when not changing QP state
- 20f5e10ef8bcf29a915642245b66e5a132e38fc4 RDMA/qedr: Add uapi header qedr-abi.h
- 097b615965fb1af714fbc2311f68839b1086ebcb RDMA/qedr: Fix MTU returned from QP query
- d3f4aadd614c4627244452ad64eaf351179f2c31 RDMA/core: Add the function ib_mtu_int_to_enum
- c929ea0b910355e1876c64431f3d5802f95b3d75 SUNRPC: cleanup ida information when removing sunrpc module
- 294628c1fe660b5c4ba4127df05ff2aa8c09a08a Merge branch alx-mq-fixes
- 185aceefd80f98dc5b9d73eb6cbb70739a5ce4ea alx: work around hardware bug in interrupt fallback path
- 37187a016c37d7e550544544dba25399ce4589c9 alx: fix fallback to msi or legacy interrupts
- f1db5c101cd48b5555ed9e061dcc49ed329812ea alx: fix wrong condition to free descriptor memory
- 5b9f57516337b523f7466a53939aaaea7b78141b qmi_wwan/cdc_ether: add device ID for HP lt2523 (Novatel E371) WWAN card
- 83d230eb5c638949350f4761acdfc0af5cb1bc00 xfs: verify dirblocklog correctly
- 19ca2c8fecb1592d623fe5e82d6796f8d446268d Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/ebiederm/user-namespace
- 23d28a859fb847fd7fcfbd31acb3b160abb5d6ae ibmveth: Add a proper check for the availability of the checksum features
- 7d6556ac66eeb430a574e9e3381a3110965d17aa Merge branch vxlan-fdb-fixes
- efb5f68f32995c146944a9d4257c3cf8eae2c4a1 vxlan: do not age static remote mac entries
- 8b3f9337e17aaf710c79e65fd0a3c572a075f498 vxlan: dont flush static fdb entries on admin down
- a824d0b83109eb3e3ad44c489543831bc15f7166 Merge branch ip6_tnl_parse_tlv_enc_lim-fixes
- fbfa743a9d2a0ffa24251764f10afc13eb21e739 ipv6: fix ip6_tnl_parse_tlv_enc_lim()
- 21b995a9cb093fff33ec91d7cb3822b882a90a1e ip6_tunnel: must reload ipv6h in ip6ip6_tnl_xmit()
- d0fa28f00052391b5df328f502fbbdd4444938b7 virtio_net: fix PAGE_SIZE > 64k
- 0fb44559ffd67de8517098b81f675fa0210f13f0 af_unix: move unix_mknod() out of bindlock
- 2e38a37f23c98d7fad87ff022670060b8a0e2bf5 md/r5cache: disable write back for degraded array
- 07e83364845e1e1c7e189a01206a9d7d33831568 md/r5cache: shift complex rmw from read path to write path
- a85dd7b8df52e35d8ee3794c65cac5c39128fd80 md/r5cache: flush data only stripes in r5l_recovery_log()
- ba02684daf7fb4a827580f909b7c7db61c05ae7d md/raid5: move comment of fetch_block to right location
- 86aa1397ddfde563b3692adadb8b8e32e97b4e5e md/r5cache: read data into orig_page for prexor of cached data
- d46d29f072accb069cb42b5fbebcc77d9094a785 md/raid5-cache: delete meaningless code
- ff89b070b7c98eb6782361310ca7a15186f15b2c IB/vmw_pvrdma: Fix incorrect cleanup on pvrdma_pci_probe error path
- 7d211c81e97ef8505610ef82e14e302ab415bad1 IB/vmw_pvrdma: Dont leak info from alloc_ucontext
- bf02454a741b58682a82c314a9a46bed930ed2f7 ARC: smp-boot: Decouple Non masters waiting API from jump to entry point
- 517e7610d2ce04d1b8d8b6c6d1a36dcce5cac6ab ARCv2: MCIP: update the BCR per current changes
- 36425cd67052e3becf325fd4d3ba5691791ef7e4 ARC: udelay: fix inline assembler by adding LP_COUNT to clobber list
- a59b7e0246774e28193126fe7fdbbd0ae9c67dcc mlxsw: spectrum_router: Correctly reallocate adjacency entries
- 6a0b76c04ec157c88ca943debf78a8ee58469f2d r8152: dont execute runtime suspend if the tx is not empty
- 7630ea4bda18df2ee1c64dfdca1724a9cc32f920 Documentation: net: phy: improve explanation when to specify the PHY ID
- 92fdb527eecff7e5eb945a3fbf4743110f5c1171 ARCv2: MCIP: Deprecate setting of affinity in Device Tree
- a430607b2ef7c3be090f88c71cfcb1b3988aa7c0 NFSv4.0: always send mode in SETATTR after EXCLUSIVE4
- 059aa734824165507c65fd30a55ff000afd14983 nfs: Dont increment lock sequence ID after NFS4ERR_MOVED
- f39aac7e839368e3895dff952f3bfa0a22e20060 net: phy: marvell: Add Wake from LAN support for 88E1510 PHY
- b1a27eac7fefff33ccf6acc919fc0725bf9815fb IB/cxgb3: fix misspelling in header guard
- bd00fdf198e2da475a2f4265a83686ab42d998a8 vfio/spapr: fail tce_iommu_attach_group() when iommu_data is null
- 83236f0157feec0f01bf688a1474b889bdcc5ad0 IB/iser: remove unused variable from iser_conn struct
- 1e5db6c31ade4150c2e2b1a21e39f776c38fea39 IB/iser: Fix sg_tablesize calculation
- 7b9e1d89e1b6a3b99a8fdd949aa0f98dd5bf2f6b MAINTAINERS: Add myself to X86 PLATFORM DRIVERS as a co-maintainer
- 0a475ef4226e305bdcffe12b401ca1eab06c4913 IB/srp: fix invalid indirect_sg_entries parameter value
- ad8e66b4a80182174f73487ed25fd2140cf43361 IB/srp: fix mr allocation when the device supports sg gaps
- baae29d653f899fca20bc23770a0dcc0195ebf4f Merge tag mac80211-for-davem-2017-01-24 of git://git.kernel.org/pub/scm/linux/kernel/git/jberg/mac80211
- 115865fa0826ed18ca04717cf72d0fe874c0fe7f mac80211: dont try to sleep in rate_control_rate_init()
- 0d6da872d3e4a60f43c295386d7ff9a4cdcd57e9 s390/mm: Fix cmma unused transfer from pgste into pte
- 690e5325b8c7d5db05fc569c0f7b888bb4248272 block: fix use after free in __blkdev_direct_IO
- 9dce990d2cf57b5ed4e71a9cdbd7eae4335111ff s390/ptrace: Preserve previous registers for short regset write
- 8ac092519ad91931c96d306c4bfae2c6587c325f NFSv4.1: Fix a deadlock in layoutget
- b2fbd04498789def80ceba3d5bbc5af7f2f70a5f netfilter: nf_tables: validate the name size when possible
- a4685d2f58e2230d4e27fb2ee581d7ea35e5d046 Merge branch stable of git://git.kernel.org/pub/scm/linux/kernel/git/cmetcalf/linux-tile
- 3a1d19a29670aa7eb58576a31883d0aa9fb77549 drm/amdgpu: fix unload driver issue for virtual display
- c5f21c9f878b8dcd54d0b9739c025ca73cb4c091 drm/amdgpu: check ring being ready before using
- 6302118226830c8f0aa0ec6afc8ef0cad84faa5f Merge tag gpio-v4.10-3 of git://git.kernel.org/pub/scm/linux/kernel/git/linusw/linux-gpio
- 3258943ddb90157a5b220656712394bd91bd47f1 Merge tag drm-fixes-for-v4.10-rc6 of git://people.freedesktop.org/~airlied/linux
- 4078b76cac68e50ccf1f76a74e7d3d5788aec3fe net: dsa: Check return value of phy_connect_direct()
- eab127717a6af54401ba534790c793ec143cd1fc net: phy: Avoid deadlock during phy_error()
- d2b3964a0780d2d2994eba57f950d6c9fe489ed8 xfs: fix COW writeback race
- 3b4f18843e511193e7eb616710e838f5852e661d xen-blkfront: correct maximum segment accounting
- b32728ffef7f233dbdabb3f11814bdf692aaf501 xen-blkfront: feature flags handling adjustments
- 9f427a0e474a67b454420c131709600d44850486 net: mpls: Fix multipath selection for LSR use case
- 880a38547ff08715ce4f1daf9a4bb30c87676e68 userns: Make ucounts lock irq-safe
- e9748e0364fe82dc037d22900ff13a62d04518bf mmc: dw_mmc: force setup bus if active slots exist
- 932790109f62aa52bdb4bb62aa66653c0b51bc75 Merge tag drm-qemu-20170110 of git://git.kraxel.org/linux into drm-fixes
- 2f39258e5744d34db5db27a1272fd41ac9d2397d Merge branch drm-etnaviv-fixes of https://git.pengutronix.de/git/lst/linux into drm-fixes
- 2e76f85690a9e8ee8428b42588cdb22e5000f63b Merge branch exynos-drm-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/daeinki/drm-exynos into drm-fixes
- 484205df6baa8207683ad30a1679bafc26100658 Merge branch drm-fixes-4.10 of git://people.freedesktop.org/~agd5f/linux into drm-fixes
- b310348530c44bcfe98ea29c97274562853b4583 Merge branch msm-fixes-4.10-rc4 of git://people.freedesktop.org/~robclark/linux into drm-fixes
- 78337c0697e669554c28b8b48c644bbaad0ffc5e Merge tag drm-misc-fixes-2017-01-13 of git://anongit.freedesktop.org/git/drm-misc into drm-fixes
- f1750e144a2f01b011bd3155fcf8b6dff299fe68 Merge tag drm-intel-fixes-2017-01-19 of git://anongit.freedesktop.org/git/drm-intel into drm-fixes
- a5b9b5a2d3d305598b70ed69dd40754e26516182 Merge branch amd-xgbe-fixes
- 738f7f647371ff4cfc9646c99dba5b58ad142db3 amd-xgbe: Check xgbe_init() return code
- 4eccbfc36186926b570310bfbd44f4216cd05c63 amd-xgbe: Add a hardware quirk for register definitions
- 7a308bb3016f57e5be11a677d15b821536419d36 Linux 4.10-rc5
- 095cbe66973771fecd8e8b1e8763181363ef703e Merge branch x86-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 24b86839fab8e8059d2b16e0067dc86a1a0d3514 Merge branch smp-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 585457fc8383e373ab923e46cd1f70bbfe46763f Merge tag for_linus of git://git.kernel.org/pub/scm/linux/kernel/git/mst/vhost
- bb6c01c2dde67b165cf7c808b0f00677b6f94b96 Merge branch for-rc of git://git.kernel.org/pub/scm/linux/kernel/git/rzhang/linux
- cfee5d63767b2e7997c1f36420d008abbe61565c platform/x86: ideapad-laptop: handle ACPI event 1
- c497f8d17246720afe680ea1a8fa6e48e75af852 Merge tag usb-4.10-rc5 of git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/usb
- f68d8531cceabb6683a8f949d2d933cd854da141 Merge branch libnvdimm-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/nvdimm/nvdimm
- f5e8c0ff563e6bf1633e5a35b0d9b8fe4c7560b8 Merge tag clk-fixes-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/clk/linux
- 455a70cbe72906db2797b2725cabc7e0897857f5 Merge tag arc-4.10-rc5 of git://git.kernel.org/pub/scm/linux/kernel/git/vgupta/arc
- 83fd57a740bb19286959b3085eb93532f3e7ef2c Merge tag powerpc-4.10-2 of git://git.kernel.org/pub/scm/linux/kernel/git/powerpc/linux
- 5a00b6c2438460b870a451f14593fc40d3c7edf6 platform/x86: intel_mid_powerbtn: Set IRQ_ONESHOT
- e95ac4574b23a5fd8f5c5f2c19ef69ac15b7252c platform/x86: surface3-wmi: fix uninitialized symbol
- 44e6861646748a21b55725adc0780342f4440066 platform/x86: surface3-wmi: Shut up unused-function warning
- 63d762b88cb5510f2bfdb5112ced18cde867ae61 platform/x86: mlx-platform: free first dev on error
- 4c9eff7af69c61749b9eb09141f18f35edbf2210 Merge tag for-linus of git://git.kernel.org/pub/scm/virt/kvm/kvm
- 5116226496e898ae3ddbe540ca5ff4f843c56bbe Merge branch scsi-target-for-v4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/bvanassche/linux
- e3737b9145636e884d7185176cbe76a3f2c645e2 Merge branch for-linus of git://git.kernel.dk/linux-block
- cca112ecf259e24096bc18b736c3ae985e81ac72 Merge tag spi-fix-v4.10-rc4 of git://git.kernel.org/pub/scm/linux/kernel/git/broonie/spi
- e90665a5d38b17fdbe484a85fbba917a7006522d Merge tag ceph-for-4.10-rc5 of git://github.com/ceph/ceph-client
- b6677449dff674cf5b81429b11d5c7f358852ef9 bridge: netlink: call br_changelink() during br_dev_newlink()
- 56ef18829e559e592b0f0cf756aac56996a8259a Merge branch overlayfs-linus of git://git.kernel.org/pub/scm/linux/kernel/git/mszeredi/vfs
- eefa9feb7dad40c45259f7bcbed054508564fa7d Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/mszeredi/fuse
- f09ff1de63a20bc049af66d2a758a6ded4f7bdf3 Merge tag scsi-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/jejb/scsi
- f8f2d4bdb52e67139b0b3e5ae16da04e71ebc1a6 Merge tag arm64-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/arm64/linux
- 90c311b0eeead647b708a723dbdde1eda3dcad05 xen-netfront: Fix Rx stall during network stress and OOM
- e048fc50d7bde23136e098e04a324d7e3404408d net/mlx5e: Do not recycle pages from emergency reserve
- cdb749cef16bceb74950fc8668f2632ff7cac9aa bpf: fix samples xdp_tx_iptunnel and tc_l2_redirect with fake KBUILD_MODNAME
- fec969012314ec452620516f8251f512f9b534ac Merge tag kvm-s390-master-4.10-1 of git://git.kernel.org/pub/scm/linux/kernel/git/kvms390/linux
- df384d435a5c034c735df3d9ea87a03172c59b56 bcm63xx_enet: avoid uninitialized variable warning
- 0629a330cf55454962168dd3ee46fad53a39323e qed: avoid possible stack overflow in qed_ll2_acquire_connection
- 91e744653cb80554f3fdfd1d31c5ddf7b6169f37 Revert net: sctp: fix array overrun read on sctp_timer_tbl
- 0e73fc9a56f22f2eec4d2b2910c649f7af67b74d net: sctp: fix array overrun read on sctp_timer_tbl
- e363116b90906f326c9cde5473b4b9a99ba476df ipv6: seg6_genl_set_tunsrc() must check kmemdup() return value
- 2c561b2b728ca4013e76d6439bde2c137503745e r8152: fix rtl8152_post_reset function
- 6391a4481ba0796805d6581e42f9f0418c099e34 virtio-net: restore VIRTIO_HDR_F_DATA_VALID on receiving
- 04478197416e3a302e9ebc917ba1aa884ef9bfab KVM: s390: do not expose random data via facility bitmap
- 488dc164914ff5ce5e913abd32048d28fc0d06b8 xhci: remove WARN_ON if dma mask is not set for platform devices
- f1225ee4c8fcf09afaa199b8b1f0450f38b8cd11 swiotlb-xen: update dev_addr after swapping pages
- bad94f8068122b6342a73a218dad7d41e6ea907b Merge branches thermal-core and thermal-soc into for-rc
- 11d8bcef7a0399e1d2519f207fd575fc404306b4 drm/exynos/decon5433: set STANDALONE_UPDATE_F on output enablement
- 1202a096328ed3de59e2a722038c4d80ec59a958 drm/exynos/decon5433: fix CMU programming
- 4151e9a61c26bc86a356edfea713c0f913582760 drm/exynos/decon5433: do not disable video after reset
- 178f358208ceb8b38e5cff3f815e0db4a6a70a07 powerpc: Ignore reserved field in DCSR and PVR reads and writes
- b34ca60148c53971d373643195cc5c4d5d20be78 powerpc/ptrace: Preserve previous TM fprs/vsrs on short regset write
- 99dfe80a2a246c600440a815741fd2e74a8b4977 powerpc/ptrace: Preserve previous fprs/vsrs on short regset write
- 7a37052adb5e843bcfff6c98aee9b60bb087b910 ACPICA: Tables: Fix hidden logic related to acpi_tb_install_standard_table()
- 1443ebbacfd7f8d84fbbbf629ef66a12dc8a4b4e cpufreq: intel_pstate: Fix sysfs limits enforcement for performance policy
- e326ce013a8e851193eb337aafb1aa396c533a61 Revert PM / sleep / ACPI: Use the ACPI_FADT_LOW_POWER_S0 flag
- 44b4b461a0fb407507b46ea76a71376d74de7058 Merge tag armsoc-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/arm/arm-soc
- 6e0362b3a84bb6c3fd33af3a3e440360e561156d Merge tag xfs-for-linux-4.10-rc5-1 of git://git.kernel.org/pub/scm/fs/xfs/xfs-linux
- 43849785e1079f6606a31cb7fda92d1200849728 ARM: dts: da850-evm: fix read access to SPI flash
- 0db1dba5dfaf70fb3baf07973996db2078528cde virtio/s390: virtio: constify virtio_config_ops structures
- 99240622bdde46f159a89e72199779d3c5a08b98 virtio/s390: add missing \n to end of dev_err message
- 7d3ce5ab9430504b6d91027919529f68fd14af9b virtio/s390: support READ_STATUS command for virtio-ccw
- 47a4c49af6cc1982ce613c8ee79aab459d04c44c tools/virtio/ringtest: tweaks for s390
- 21f5eda9b8671744539c8295b9df62991fffb2ce tools/virtio/ringtest: fix run-on-all.sh for offline cpus
- 8379cadf71c3ee8173a1c6fc1ea7762a9638c047 virtio_console: fix a crash in config_work_handler
- 532e15af105a0b86211f515bd5fec1f4cdd9f27b vhost/scsi: silence uninitialized variable warning
- 1d822a40b81568becba8777b525a1ed255a8078c vhost: scsi: constify target_core_fabric_ops structures
- d61b7f972dab2a7d187c38254845546dfc8eed85 nbd: only set MSG_MORE when we have more to send
- 81aaeaac461071c591cbd188748ad875e0efae7e Merge tag pci-v4.10-fixes-1 of git://git.kernel.org/pub/scm/linux/kernel/git/helgaas/pci
- 2ed5e5af2f9d5fb583ac1d36ba819f787bafbda6 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/jikos/hid
- 4a1cc2e879c9fdfe1137060ce6de3bbe413630f6 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/s390/linux
- 086675779097c6fe95e94058072462196ffd1870 Merge tag for-linus-4.10-rc4-tag of git://git.kernel.org/pub/scm/linux/kernel/git/xen/tip
- 91298eec05cd8d4e828cf7ee5d4a6334f70cf69a Btrfs: fix truncate down when no_holes feature is enabled
- 97dcdea076ecef41ea4aaa23d4397c2f622e4265 Btrfs: Fix deadlock between direct IO and fast fsync
- 47b5d64691350e116093c9b47b55ca6b9433bc50 btrfs: fix false enospc error when truncating heavily reflinked file
- 69fed99baac186013840ced3524562841296034f gianfar: Do not reuse pages from emergency reserve
- 0dbd7ff3ac5017a46033a9d0a87a8267d69119d9 tcp: initialize max window for a new fastopen socket
- ad05df399f3343b10664827a3860669a8a80782d net/mlx5e: Remove unused variable
- 03e4deff4987f79c34112c5ba4eb195d4f9382b0 ipv6: addrconf: Avoid addrconf_disable_change() using RCU read-side lock
- 59cfa789d04c35b6c647aacf4cc89b3d4d430cfe MAINTAINERS: update cxgb4 maintainer
- 7d9e8f71b989230bc613d121ca38507d34ada849 arm64: avoid returning from bad_mode
- e5072053b09642b8ff417d47da05b84720aea3ee netfilter: conntrack: refine gc worker heuristics, redux
- 524b698db06b9b6da7192e749f637904e2f62d7b netfilter: conntrack: remove GC_MAX_EVICTS break
- a9ce7856cad1bf43de5c43888e4076e77371d51b HID: wacom: Fix sibling detection regression
- df1539c25cce98e2ac69881958850c6535240707 pinctrl: uniphier: fix Ethernet (RMII) pin-mux setting for LD20
- b27e36482c02a94194fec71fb29696f4c8e9241c pinctrl: meson: fix uart_ao_b for GXBB and GXL/GXM
- 739e6f5945d88dcee01590913f6886132a10c215 gpio: provide lockdep keys for nested/unnested irqchips
- d0e73e2ac6a6b157159e1e62f981c06d29f42336 ARC: Revert ARC: mm: IOC: Dont enable IOC by default
- 76894a72a0d7e0759de272bf3f4d2279ebd86d0b ARC: mm: split arc_cache_init to allow __init reaping of bulk
- e47a8b172972ef10246e72e9277d27e3119e35ab Merge tag omap-for-v4.10/fixes-rc4 of git://git.kernel.org/pub/scm/linux/kernel/git/tmlind/linux-omap into fixes
- e497c8e52a83ebb5309ab41c8851c9cb53f28b73 ARCv2: IOC: Use actual memory size to setup aperture size
- 8c47f83ba45928ce9495fcf1b29e828c28e3c839 ARCv2: IOC: Adhere to progamming model guidelines to avoid DMA corruption
- d4911cdd3270da45d3a1c55bf28e88a932bbba7b ARCv2: IOC: refactor the IOC and SLC operations into own functions
- 88a7503376f4f3bf303c809d1a389739e1205614 blk-mq: Remove unused variable
- d407bd25a204bd66b7346dde24bd3d37ef0e0b05 bpf: dont trigger OOM killer under pressure with map alloc
- 9ed59592e3e379b2e9557dc1d9e9ec8fcbb33f16 lwtunnel: fix autoload of lwt modules
- 719ca8111402aa6157bd83a3c966d184db0d8956 bnxt_en: Fix uninitialized variable bug in TPA code path.
- fb1d8e0e2c50f374cfc244564decfc3f0a336cb4 Merge tag upstream-4.10-rc5 of git://git.infradead.org/linux-ubifs
- cd33b3e0da43522ff8e8f2b2b71d3d08298512b0 net: phy: bcm63xx: Utilize correct config_intr function
- fd29f7af75b7adf250beccffa63746c6a88e2b74 xfs: fix xfs_mode_to_ftype() prototype
- 7be2c82cfd5d28d7adb66821a992604eb6dd112e net: fix harmonize_features() vs NETIF_F_HIGHDMA
- d89ede6d8f029d3435d8a1602d21e5be68831369 Merge branch xen-netback-leaks
- f16f1df65f1cf139ff9e9f84661e6573d6bb27fc xen-netback: protect resource cleaning on XenBus disconnect
- 9a6cdf52b85ea5fb21d2bb31e4a7bc61b79923a7 xen-netback: fix memory leaks on XenBus disconnect
- 3fd0b634de7d6b9a85f34a4cf9d8afc1df465cc9 netfilter: ipt_CLUSTERIP: fix build error without procfs
- 6acbe3716034a159f2e9a810631e40bc85af0458 Merge branch ethtool-set-channels-fix
- 639e9e94160e59469305fc2c5e6f9c2733744958 net/mlx5e: Remove unnecessary checks when setting num channels
- e91ef71dfe834e11b57411f1715cd2e2bb4401f1 net/mlx4_en: Remove unnecessary checks when setting num channels
- 31a86d137219373c3222ca5f4f912e9a4d8065bb net: ethtool: Initialize buffer when querying device channel settings
- fa19a769f82fb9a5ca000b83cacd13fcaeda51ac Merge branch fixes of git://git.armlinux.org.uk/~rmk/linux-arm
- eb1357d942e5d96de6b4c20a8ffa55acf96233a2 ARC: module: Fix !CONFIG_ARC_DW2_UNWIND builds
- ca92e6c7e6329029d7188487a5c32e86ef471977 Merge branch smp-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 0b75f821ec8be459dd4dec77be39595d989d77ac Merge branch timers-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 49b550fee80b5f36b961640666f7945d7ec63000 Merge branch rcu-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 9da96f99f15169b8bf77a1f27ed6d926f82ea59f Merge branch perf-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- ad9e202aa1ce571b1d7fed969d06f66067f8a086 arm64/ptrace: Reject attempts to set incomplete hardware breakpoint fields
- aeb1f39d814b2e21e5e5706a48834bfd553d0059 arm64/ptrace: Avoid uninitialised struct padding in fpr_set()
- a672401c00f82e4e19704aff361d9bad18003714 arm64/ptrace: Preserve previous registers for short regset write
- 9dd73f72f218320c6c90da5f834996e7360dc227 arm64/ptrace: Preserve previous registers for short regset write
- 9a17b876b573441bfb3387ad55d98bf7184daf9d arm64/ptrace: Preserve previous registers for short regset write
- 6df8c9d80a27cb587f61b4f06b57e248d8bc3f86 ceph: fix bad endianness handling in parse_reply_info_extra
- fe2ed42517533068ac03eed5630fffafff27eacf ceph: fix endianness bug in frag_tree_split_cmp
- 1097680d759918ce4a8705381c0ab2ed7bd60cf1 ceph: fix endianness of getattr mask in ceph_d_revalidate
- 124f930b8cbc4ac11236e6eb1c5f008318864588 libceph: make sure ceph_aes_crypt() IV is aligned
- 6e09d0fb64402cec579f029ca4c7f39f5c48fc60 ceph: fix ceph_get_caps() interruption
- 003ecadd2e5686d39630f89fa72102c28d91c475 Merge tag linux-can-fixes-for-4.10-20170118 of git://git.kernel.org/pub/scm/linux/kernel/git/mkl/linux-can
- 020eb3daaba2857b32c4cf4c82f503d6a00a67de x86/ioapic: Restore IO-APIC irq_chip retrigger callback
- 3bfdfdcbce2796ce75bf2d85fd8471858d702e5d drm/i915: Ignore bogus plane coordinates on SKL when the plane is not visible
- 4fc020d864647ea3ae8cb8f17d63e48e87ebd0bf drm/i915: Remove WaDisableLSQCROPERFforOCL KBL workaround.
- 4c7d0c9cb713a28b133b265d595de2a93ee09712 ovl: fix possible use after free on redirect dir lookup
- befa60113ce7ea270cb51eada28443ca2756f480 can: ti_hecc: add missing prepare and unprepare of the clock
- c97c52be78b8463ac5407f1cf1f22f8f6cf93a37 can: c_can_pci: fix null-pointer-deref in c_can_start() - set device pointer
- 1c8a946bf3754a59cba1fc373949a8114bfe5aaa arm64: mm: avoid name clash in __page_to_voff()
- 0fec9557fd0c5349e3bd1a2141612a60bc20bb71 cpu/hotplug: Remove unused but set variable in _cpu_down()
- 27593d72c4ad451ed13af35354b941bcd0abcec6 powerpc/perf: Use MSR to report privilege level on P9 DD1
- df21d2fa733035e4d414379960f94b2516b41296 selftest/powerpc: Wrong PMC initialized in pmc56_overflow test
- 387bbc974f6adf91aa635090f73434ed10edd915 powerpc/eeh: Enable IO path on permanent error
- d89f473ff6f84872e761419f7233d6e00f99c340 powerpc/perf: Fix PM_BRU_CMPL event code for power9
- 20717e1ff52672e31f9399c45d88936bbbc7e175 powerpc/mm: Fix little-endian 4K hugetlb
- ff8b85796dad5de869dc29903c95664fb444bbcc powerpc/mm/hugetlb: Dont panic when we dont find the default huge page size
- bf5ca68dd2eef59a936969e802d811bdac4709c2 powerpc: Fix pgtable pmd cache init
- 0aa0313f9d576affd7747cc3f179feb097d28990 Merge tag modules-for-v4.10-rc5 of git://git.kernel.org/pub/scm/linux/kernel/git/jeyu/linux
- 9208b75e048dda0d285904de9be7ab654a4b94fc Merge remote-tracking branch mkp-scsi/fixes into fixes
- 1ea6af3216b092ec97129ac81bd95cf254c4b140 ARM: dts: omap3: Fix Card Detect and Write Protect on Logic PD SOM-LV
- 93b43fd137cd8865adf9978ab9870a344365d3af net: phy: dp83848: add DP83620 PHY support
- 3fbfadce6012e7bb384b2e9ad47869d5177f7209 bpf: Fix test_lru_sanity5() in test_lru_map.c
- 17324b6add82d6c0bf119f1d1944baef392a4e39 drm/amdgpu: add support for new hainan variants
- 4e6e98b1e48c9474aed7ce03025ec319b941e26e drm/radeon: add support for new hainan variants
- ca581e45335c6aa45e5b27999bc13bdefb7e84d9 drm/amdgpu: change clock gating mode for uvd_v4.
- 50a1ebc70a2803deb7811fc73fb55d70e353bc34 drm/amdgpu: fix program vce instance logic error.
- e05208ded1905e500cd5b369d624b071951c68b9 drm/amdgpu: fix bug set incorrect value to vce register
- d5ff72d9af73bc3cbaa3edb541333a851f8c7295 vxlan: fix byte order of vxlan-gpe port number
- f7bcd4b6f6983d668b057dc166799716690423a4 ARM64: dts: meson-gxbb-odroidc2: Disable SCPI DVFS
- 657bdfb7f5e68ca5e2ed009ab473c429b0d6af85 xfs: dont wrap ID in xfs_dq_get_next_id
- a324cbf10a3c67aaa10c9f47f7b5801562925bc2 xfs: sanity check inode di_mode
- fab8eef86c814c3dd46bc5d760b6e4a53d5fc5a6 xfs: sanity check inode mode when creating new dentry
- 1fc4d33fed124fb182e8e6c214e973a29389ae83 xfs: replace xfs_mode_to_ftype table with switch statement
- b597dd5373a1ccc08218665dc8417433b1c09550 xfs: add missing include dependencies to xfs_dir2.h
- 3c6f46eacd876bd723a9bad3c6882714c052fd8e xfs: sanity check directory inode di_size
- bf46ecc3d8cca05f2907cf482755c42c2b11a79d xfs: make the ASSERT() condition likely
- ffb58456589443ca572221fabbdef3db8483a779 scsi: mpt3sas: fix hang on ata passthrough commands
- 300af14bdb28157090f0c6f89d244fda940082da qla2xxx: Disable out-of-order processing by default in firmware
- 4f060736f29a960aba8e781a88837464756200a8 qla2xxx: Fix erroneous invalid handle message
- 200ffb159b2f48857aa18c0502a4d29b102d013b qla2xxx: Reduce exess wait during chip reset
- 5f35509db179ca7ed1feaa4b14f841adb06ed220 qla2xxx: Terminate exchange if corrupted
- fc1ffd6cb38a1c1af625b9833c41928039e733f5 qla2xxx: Fix crash due to null pointer access
- 8d3c9c230818aa3c27edb4fd126494479d35d3d5 qla2xxx: Collect additional information to debug fw dump
- c0f6462754f050e9bc960662992c029c5ef88f34 qla2xxx: Reset reserved field in firmware options to 0
- 2a47c68529e99e5631af0ac337fb8519c4eadb3f qla2xxx: Set tcm_qla2xxx version to automatically track qla2xxx version
- 1cbb91562df536eac6e06d7bd2df5965ffd67803 qla2xxx: Include ATIO queue in firmware dump when in target mode
- bb1181c9a8b46b6f10e749d9ed94480336445d7f qla2xxx: Fix wrong IOCB type assumption
- 91f42b33e5b48a956a352ce10da52b77f4277d5f qla2xxx: Avoid that building with W=1 triggers complaints about set-but-not-used variables
- 61778a1c5a4556da1a1e005d506f89f009031e62 qla2xxx: Move two arrays from header files to .c files
- ca825828a5c797d431f6ec6a83c912787ffbb8af qla2xxx: Declare an array with file scope static
- c2a5d94ffd042db6aaee17b767c43502da3bd8f5 qla2xxx: Fix indentation
- 8667f515952feefebb3c0f8d9a9266c91b101a46 scsi: lpfc: Set elsiocb contexts to NULL after freeing it
- a249708bc2aa1fe3ddf15dfac22bee519d15996b stmmac: add missing of_node_put
- 501db511397fd6efff3aa5b4e8de415b55559550 virtio: dont set VIRTIO_NET_HDR_F_DATA_VALID on xmit
- 68af412c7713b55c01ffc4312320abd10ca70e77 scsi: sd: Ignore zoned field for host-managed devices
- 26f2819772af891dee2843e1f8662c58e5129d5f scsi: sd: Fix wrong DPOFUA disable in sd_read_cache_type
- 4633773799940b1b8b3ff98ea05e6c1ef072febd scsi: bfa: fix wrongly initialized variable in bfad_im_bsg_els_ct_request()
- 9373eba6cfae48911b977d14323032cd5d161aae scsi: ses: Fix SAS device detection in enclosure
- 5eb7c0d04f04a667c049fe090a95494a8de2955c taint/module: Fix problems when out-of-kernel driver defines true or false
- 52cc720c568efd8fd454053b98fe4b4fd94688fe Merge remote-tracking branch spi/fix/sh-msiof into spi-linus
- 3f95ba38e44b27a5c2e8c416c460a961c2bed9ec Merge remote-tracking branches spi/fix/armada, spi/fix/axi, spi/fix/davinci, spi/fix/dw, spi/fix/fsl-dspi and spi/fix/pxa2xx into spi-linus
- a5b0e4062fb225155189e593699bbfcd0597f8b5 ibmvscsis: Fix sleeping in interrupt context
- 387b978cb0d12cf3720ecb17e652e0a9991a08e2 ibmvscsis: Fix max transfer length
- 4b19a9e20bf99d62e1c47554f8eb2d9f520642ba Merge git://git.kernel.org/pub/scm/linux/kernel/git/davem/net
- 203f80f1c4187b2d5b3a282586fa6cc6d9503d4b Merge branch stable/for-linus-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/konrad/swiotlb
- 7e84b3035592b58872f476cdeff61d4bbcbb3452 Merge tag mmc-v4.10-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/ulfh/mmc
- a17f32270af1e1054bbc8858b0f27226a2c859ba kvm: x86: Expose Intel VPOPCNTDQ feature to guest
- a9ff720e0fee2f64c279e71c1bf86e93804295d2 Merge branch x86/cpufeature of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip into next
- 7d8b8c09d71dab6747c519d869cc93352b359af3 Merge tag for-linus-20170116 of git://git.infradead.org/linux-mtd
- 31f5260a7653e6042ac28578db1c61e84f2d7898 Merge tag perf-urgent-for-mingo-4.10-20170117 of git://git.kernel.org/pub/scm/linux/kernel/git/acme/linux into perf/urgent
- 4d191b1b63c209e37bf27938ef365244d3c41084 PCI/MSI: pci-xgene-msi: Fix CPU hotplug registration handling
- ce2e852ecc9a42e4b8dabb46025cfef63209234a KVM: x86: fix fixing of hypercalls
- 1b1973ef9a6a951903c1d7701f0c420b27e77cf3 Merge tag kvm-arm-for-4.10-rc4 of git://git.kernel.org/pub/scm/linux/kernel/git/kvmarm/kvmarm
- 1cb51a15b576ee325d527726afff40947218fd5e ubifs: Fix journal replay wrt. xattr nodes
- 3d4b2fcbc980879a1385d5d7d17a4ffd0ee9aa1f ubifs: remove redundant checks for encryption key
- a75467d910135905de60b3af3f11b3693625781e ubifs: allow encryption ioctls in compat mode
- 404e0b63312ea294b058b4d5c964d064d321ea32 ubifs: add CONFIG_BLOCK dependency for encryption
- 507502adf0f415108ef0b87a0acbb84d1839007f ubifs: fix unencrypted journal write
- e8f19746e4b1e8c3118d240dba51f06153a37b07 ubifs: ensure zero err is returned on successful return
- 524dabe1c68e0bca25ce7b108099e5d89472a101 arm64: Fix swiotlb fallback allocation
- 6b8ac63847bc2f958dd93c09edc941a0118992d9 drm/vc4: Return -EINVAL on the overflow checks failing.
- 0f2ff82e11c86c05d051cae32b58226392d33bbf drm/vc4: Fix an integer overflow in temporary allocation layout.
- 21ccc32496b2f63228f5232b3ac0e426e8fb3c31 drm/vc4: fix a bounds check
- 7622b25543665567d8830a63210385b7d705924b drm/vc4: Fix memory leak of the CRTC state.
- 4e71de7986386d5fd3765458f27d612931f27f5e perf/x86/intel: Handle exclusive threadid correctly on CPU hotplug
- 833674a45ec7506f67eca93d51741ba5bc9c93f9 Merge tag fixes-for-v4.10-rc5 of git://git.kernel.org/pub/scm/linux/kernel/git/balbi/usb into usb-linus
- bc7c36eedb0c7004aa06c2afc3c5385adada8fa3 clocksource/exynos_mct: Clear interrupt when cpu is shut down
- 62f0a11e2339e1ba154600d1f49ef5d5d84eaae4 drm/i915/gvt: Fix relocation of shadow bb
- 58c744da9dcc82a4b55a18e05149ae0e32624d11 drm/i915/gvt: Enable the shadow batch buffer
- 6c75a5d1131eba90fcf04adc586167e65afc79b0 Merge branch fixes of git://git.kernel.org/pub/scm/linux/kernel/git/evalenti/linux-soc-thermal into thermal-soc
- 941d3156e9a5d6826b17d451ccac876aa2f7a0d2 Merge tag ux500-fix-for-armsoc of git://git.kernel.org/pub/scm/linux/kernel/git/linusw/linux-stericsson into fixes
- dcde6b16eb6fda3f6434074e08b141c3d1f93308 Merge tag arm-soc/for-4.10/devicetree-fixes of http://github.com/Broadcom/stblinux into fixes
- e577969aee3681866fd0d3b54a2ec5e2a8005523 Merge tag arm-soc/for-4.10/defconfig-fixes of http://github.com/Broadcom/stblinux into fixes
- 9fab907f3de67b6124b0337f11efe384c325d49d Merge tag samsung-fixes-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/krzk/linux into fixes
- 927867a4b78b86d9eac48fe805e9af50cfd55da0 Merge tag sunxi-fixes-for-4.10 of https://git.kernel.org/pub/scm/linux/kernel/git/mripard/linux into fixes
- a11f4706d102ddf82ba38f1db93ac2a61b4685e7 Merge tag imx-fixes-4.10-2 of git://git.kernel.org/pub/scm/linux/kernel/git/shawnguo/linux into fixes
- db8318865e2c04dbe3d95089c7215b94a5b879b7 thermal: rockchip: fixes the conversion table
- 9728a7c8ab2f7a1c8d5c95278d2e4f4ac1285385 powerpc/icp-opal: Fix missing KVM case and harden replay
- 0faa9cb5b3836a979864a6357e01d2046884ad52 net sched actions: fix refcnt when GETing of action after bind
- 32b53c012e0bfe20b2745962a89db0dc72ef3270 powerpc/mm: Fix memory hotplug BUG() on radix
- 7e9081c5aac73b8a0bc22e0b3e7a12c3e9cf5256 drm/fence: fix memory overwrite when setting out_fence fd
- 67d35e70af9cabb663c827e03bc5c1e89b43db72 scsi: libfc: Fix variable name in fc_set_wwpn
- 5cf7a0f3442b2312326c39f571d637669a478235 Merge tag nfs-for-4.10-3 of git://git.linux-nfs.org/projects/trondmy/linux-nfs
- 617125e759673873e6503481d7dabaee6ded7af8 Merge branch mlx4-core-fixes
- 9577b174cd0323d287c994ef0891db71666d0765 net/mlx4_core: Eliminate warning messages for SRQ_LIMIT under SRIOV
- 7c3945bc2073554bb2ecf983e073dee686679c53 net/mlx4_core: Fix when to save some qp context flags for dynamic VST to VGT transitions
- 291c566a28910614ce42d0ffe82196eddd6346f4 net/mlx4_core: Fix racy CQ (Completion Queue) free
- b618ab4561d40664492cf9f9507f19a1c8272970 net: stmmac: dont use netdev_[dbg, info, ..] before net_device is registered
- abeffce90c7f6ce74de9794ad0977a168edf8ef6 net/mlx5e: Fix a -Wmaybe-uninitialized warning
- 06b35d93af0a5904aa832f58733be84ddbfe2e04 x86/cpufeature: Add AVX512_VPOPCNTDQ feature
- 8a367e74c0120ef68c8c70d5a025648c96626dff ax25: Fix segfault after sock connection timeout
- f1f7714ea51c56b7163fb1a5acf39c6a204dd758 bpf: rework prog_digest into prog_tag
- 613f050d68a8ed3c0b18b9568698908ef7bbc1f7 perf probe: Fix to probe on gcc generated functions in modules
- 3e96dac7c956089d3f23aca98c4dfca57b6aaf8a perf probe: Add error checks to offline probe post-processing
- 57d5f64d83ab5b5a5118b1597386dd76eaf4340d tipc: allocate user memory with GFP_KERNEL flag
- 34c55cf2fc75f8bf6ba87df321038c064cf2d426 net: phy: dp83867: allow RGMII_TXID/RGMII_RXID interface types
- 02ca0423fd65a0a9c4d70da0dbb8f4b8503f08c7 ip6_tunnel: Account for tunnel header in tunnel MTU
- d2d4edbebe07ddb77980656abe7b9bc7a9e0cdf7 perf probe: Fix to show correct locations for events on modules
- 1666d49e1d416fcc2cce708242a52fe3317ea8ba mld: do not remove mld souce list info when set link down
- 2eabb8b8d68bc9c7779ba8b04bec8d4f8baed0bc Merge tag nfsd-4.10-1 of git://linux-nfs.org/~bfields/linux
- 90f92c631b210c1e97080b53a9d863783281a932 ARM: 8613/1: Fix the uaccess crash on PB11MPCore
- 34393529163af7163ef8459808e3cf2af7db7f16 be2net: fix MAC addr setting on privileged BE3 VFs
- 6d928ae590c8d58cfd5cca997d54394de139cbb7 be2net: dont delete MAC on close on unprivileged BE3 VFs
- fe68d8bfe59c561664aa87d827aa4b320eb08895 be2net: fix status check in be_cmd_pmac_add()
- d43e6fb4ac4abfe4ef7c102833ed02330ad701e0 cpmac: remove hopeless #warning
- 8ec3e8a192ba6f13be4522ee81227c792c86fb1a ravb: do not use zero-length alignment DMA descriptor
- 0d7f4f0594fc38531e37b94a73ea3ebcc9d9bc11 MAINTAINERS: update rmks entries
- 8cf699ec849f4ca1413cea01289bd7d37dbcc626 mlx4: do not call napi_schedule() without care
- 507191952406c90290fb605ebd4ebfe34b7303b9 Merge branch for-upstream of git://git.kernel.org/pub/scm/linux/kernel/git/bluetooth/bluetooth
- ee6ff743e3a4b697e8286054667d7e4e1b56510d mmc: core: Restore parts of the polling policy when switch to HS/HS DDR
- e4670b058af64639ec1aef4db845c39bfdfff7c4 netfilter: Fix typo in NF_CONNTRACK Kconfig option description
- d21e540b4dd74a26df7a66ebab75c693a4a6a861 netfilter: nf_tables: fix possible oops when dumping stateful objects
- 6443ebc3fdd6f3c766d9442c18be274b3d736050 netfilter: rpfilter: fix incorrect loopback packet judgment
- d7f5762c5e532dfe8247ce1bc60d97af27ff8d00 netfilter: nf_tables: fix spelling mistakes
- 4205e4786d0b9fc3b4fec7b1910cf645a0468307 cpu/hotplug: Provide dynamic range for prepare stage
- efe357f4633a12ca89bdf9bbdd8aaf5a7a0cc3c0 usb: dwc2: host: fix Wmaybe-uninitialized warning
- ca02954ada711b08e5b0d84590a631fd63ed39f9 usb: dwc2: gadget: Fix GUSBCFG.USBTRDTIM value
- f80c2fb63295b371bd3c179d987a44c41f077856 Merge tag gvt-fixes-2017-01-16 of https://github.com/01org/gvt-linux into drm-intel-fixes
- 3e4f7a4956e54143f7fc15c636158ad4166d219d Merge branch rcu/urgent of git://git.kernel.org/pub/scm/linux/kernel/git/paulmck/linux-rcu into rcu/urgent
- 1d9995771fcbdd70d975b8dac4a201e76c9a2537 s390: update defconfigs
- e991c24d68b8c0ba297eeb7af80b1e398e98c33f s390/ctl_reg: make __ctl_load a full memory barrier
- 1a717fcf8bbeadc0e94da66b2d1f1099faeaa89b Merge tag mac80211-for-davem-2017-01-13 of git://git.kernel.org/pub/scm/linux/kernel/git/jberg/mac80211
- 75f01a4c9cc291ff5cb28ca1216adb163b7a20ee openvswitch: maintain correct checksum state in conntrack actions
- 49def1853334396f948dcb4cedb9347abb318df5 Linux 4.10-rc4
- 99421c1cb27fb837e93b517036fab4500fe39de5 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/ebiederm/user-namespace
- c92816275674c1491ce228ee49aa030a5fa1be04 Merge tag char-misc-4.10-rc4 of git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/char-misc
- 2d5a7101a140adcf7a5d8677649847fbb2dd5a2f Merge tag driver-core-4.10-rc4 of git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/driver-core
- 7f138b9706f5f3528d598aefd35337d54a8c1afb Merge tag tty-4.10-rc4 of git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/tty
- 793e039ea07191946b5ec136db00f8b03ee4a13e Merge tag usb-4.10-rc4 of git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/usb
- aa2797b30c322531981f24833b082446072d3c79 Merge branch i2c/for-current of git://git.kernel.org/pub/scm/linux/kernel/git/wsa/linux
- 83346fbc07d267de777e2597552f785174ad0373 Merge branch x86-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- a11ce3a4ac0ad78618cddb9ce16def7486f2707d Merge branch timers-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 79078c53baabee12dfefb0cfe00ca94cb2c35570 Merge branch perf-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 255e6140fa76ec9d0e24f201427e7e9a9573f681 Merge branch efi-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 602d9858f07c72eab64f5f00e2fae55f9902cfbe swiotlb: ensure that page-sized mappings are page-aligned
- 52d7e48b86fc108e45a656d8e53e4237993c481d rcu: Narrow early boot window of illegal synchronous grace periods
- f466ae66fa6a599f9a53b5f9bafea4b8cfffa7fb rcu: Remove cond_resched() from Tiny synchronize_sched()
- f4d3935e4f4884ba80561db5549394afb8eef8f7 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/viro/vfs
- 34241af77b8696120a9735bb2579ec7044199a8b Merge branch for-linus of git://git.kernel.dk/linux-block
- b9dc6f65bc5e232d1c05fe34b5daadc7e8bbf1fb fix a fencepost error in pipe_advance()
- 4d22c75d4c7b5c5f4bd31054f09103ee490878fd coredump: Ensure proper size of sparse core files
- a12f1ae61c489076a9aeb90bddca7722bf330df3 aio: fix lock dep warning
- f0ad17712b9f71c24e2b8b9725230ef57232377f Merge tag dmaengine-fix-4.10-rc4 of git://git.infradead.org/users/vkoul/slave-dma
- 0100a3e67a9cef64d72cd3a1da86f3ddbee50363 efi/x86: Prune invalid memory map entries and fix boot regression
- c7334ce814f7e5d8fc1f9b3126cda0640c2f81b3 Revert driver core: Add deferred_probe attribute to devices in sysfs
- 18e7a45af91acdde99d3aa1372cc40e1f8142f7b perf/x86: Reject non sampling events with precise_ip
- 475113d937adfd150eb82b5e2c5507125a68e7af perf/x86/intel: Account interrupts for PEBS errors
- 321027c1fe77f892f4ea07846aeae08cefbbb290 perf/core: Fix concurrent sys_perf_event_open() vs. move_group race
- 63cae12bce9861cec309798d34701cf3da20bc71 perf/core: Fix sys_perf_event_open() vs. hotplug
- 453828625731d0ba7218242ef6ec88f59408f368 x86/mpx: Use compatible types in comparison to fix sparse error
- 695085b4bc7603551db0b3da897b8bf9893ca218 x86/tsc: Add the Intel Denverton Processor to native_calibrate_tsc()
- e96f8f18c81b2f5b290206fc0da74b551e82646d Merge branch for-linus-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/mason/linux-btrfs
- 04e396277b5f171f8676defc5b720084f1cc0948 Merge tag ceph-for-4.10-rc4 of git://github.com/ceph/ceph-client
- af54efa4f5275b0594da50c68bfa8159a8cda0f5 Merge tag vfio-v4.10-rc4 of git://github.com/awilliam/linux-vfio
- 406732c932d47715395345ba036a3d58341cad55 Merge tag for-linus of git://git.kernel.org/pub/scm/virt/kvm/kvm
- a65c92597dc7556eaa219a70336d66c058a9627c Merge tag arm64-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/arm64/linux
- bef13315e990fd3d3fb4c39013aefd53f06c3657 block: dont try to discard from __blkdev_issue_zeroout
- f80de881d8df967488b7343381619efa15019493 sd: remove __data_len hack for WRITE SAME
- b131c61d62266eb21b0f125f63f3d07e5670d726 nvme: use blk_rq_payload_bytes
- fd102b125e174edbea34e6e7a2d371bc7901c53d scsi: use blk_rq_payload_bytes
- 2e3258ecfaebace1ceffaa14e0ea94775d54f46f block: add blk_rq_payload_bytes
- c79d47f14fbadce94af3b606a54984a3f25ea558 Merge tag scsi-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/jejb/scsi
- 6d90b4f99d62e6cf7643c7d8b48a9d7c005455bd Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/dtor/input
- c6180a6237174f481dc856ed6e890d8196b6f0fb NFSv4: Fix client recovery when server reboots multiple times
- da72ff5bfcb02c6ac8b169a7cf597a3c8e6c4de1 partially revert xen: Remove event channel notification through Xen PCI platform device
- 1f19b983a8877f81763fab3e693c6befe212736d libnvdimm, namespace: fix pmem namespace leak, delete when size set to zero
- 003c941057eaa868ca6fedd29a274c863167230d tcp: fix tcp_fastopen unaligned access complaints on sparc
- fa79581ea66ca43d56ef065346ac5be767fcb418 ipv6: sr: fix several BUGs when preemption is enabled
- 148d3d021cf9724fcf189ce4e525a094bbf5ce89 net: systemport: Decouple flow control from __bcm_sysport_tx_reclaim
- 87cb12910a2ab6ed41ae951ea4d9c1cc1120199a ARM: dts: OMAP5 / DRA7: indicate that SATA port 0 is available.
- 69bcc0b7140c30de552aa3ef08322295862e8e2f Revert drm/amdgpu: Only update the CUR_SIZE register when necessary
- ed79c9d34f4f4c5842b66cab840315e7ac29f666 ARM: put types.h in uapi
- 210675270caa33253e4c33f3c5e657e7d6060812 fuse: fix time_to_jiffies nsec sanity check
- 94a6fa899d2cb5ee76933406df32996576a562e4 vfio/type1: Remove pid_namespace.h include
- de85d2b35ac74f6be769573d4a8708c823219900 drm/msm: fix potential null ptr issue in non-iommu case
- c57a94ffd0105d58ab104fe383148c5eda5aa033 drm/msm/mdp5: rip out plane->pending tracking
- 2f5a31456ee80b37ef1170319fa134af0a1dfcc4 Merge remote-tracking branch mkp-scsi/4.10/scsi-fixes into fixes
- dbef53621116474bb883f76f0ba6b7640bc42332 mac80211: prevent skb/txq mismatch
- 1193e6aeecb36c74c48c7cd0f641acbbed9ddeef KVM: arm/arm64: vgic: Fix deadlock on error handling
- 488f94d7212b00a2ec72fb886b155f1b04c5aa98 KVM: arm64: Access CNTHCTL_EL2 bit fields correctly on VHE systems
- 63e41226afc3f7a044b70325566fa86ac3142538 KVM: arm/arm64: Fix occasional warning from the timer work function
- a8a86d78d673b1c99fe9b0064739fde9e9774184 fuse: clear FR_PENDING flag when moving requests out of pending queue
- 7a546af50eb78ab99840903083231eb635c8a566 HID: corsair: fix control-transfer error handling
- 6d104af38b570d37aa32a5803b04c354f8ed513d HID: corsair: fix DMA buffers on stack
- 43071d8fb3b7f589d72663c496a6880fb097533c mac80211: initialize SMPS field in HT capabilities
- 821b40b79db7dedbfe15ab330dfd181e661a533f drm/exynos/decon5433: set STANDALONE_UPDATE_F also if planes are disabled
- f65a7c9cb3770ed4d3e7c57c66d7032689081b5e drm/exynos/decon5433: update shadow registers iff there are active windows
- c34eaa8d0f9d9ae26a4a6af7bc3aca57310cf483 drm/i915/gvt: rewrite gt reset handler using new function intel_gvt_reset_vgpu_locked
- cfe65f4037cedb911a840ebcf6dafc5b69e535b4 drm/i915/gvt: fix vGPU instance reuse issues by vGPU reset function
- 97d58f7dd0ff12e5fddeffb40aed845daa628149 drm/i915/gvt: introduce intel_vgpu_reset_mmio() to reset mmio space
- cdcc43479c9b929940a1955d2e7bae696d2b9496 drm/i915/gvt: move mmio init/clean function to mmio.c
- c64ff6c774413fdbffd7f0f3ef5b04127d461cf4 drm/i915/gvt: introduce intel_vgpu_reset_cfg_space to reset configuration space
- 536fc234074b09adae1763d8fb5b2d947847ad1d drm/i915/gvt: move cfg space inititation function to cfg_space.c
- b611581b375ce28536ab50be9cd507bb6092fb1e drm/i915/gvt: introuduce intel_vgpu_reset_gtt() to reset gtt
- d22a48bf7302ef064295749fa79cd47093c5a000 drm/i915/gvt: introudce intel_vgpu_reset_resource() to reset vgpu resource state
- 3139dc8ded6f27552a248d23fe9f086e3027fa12 dmaengine: rcar-dmac: unmap slave resource when channel is freed
- d47d1d27fd6206c18806440f6ebddf51a806be4f pmem: return EIO on read_pmem() failure
- 6771e01f7965ea13988d0a5a7972f97be4e46452 ARM: dts: NSP: Fix DT ranges error
- 91546c56624a79f4a8fd80bede6b5a38c0f0ad78 ARM: multi_v7_defconfig: set bcm47xx watchdog
- 321012faf5975a4679771d7478b22ed42095aa9d ARM: multi_v7_defconfig: fix config typo
- d1b333d12cde9cabe898160b6be9769d3382d81c vfio iommu type1: fix the testing of capability for remote task
- 557ed56cc75e0a33c15ba438734a280bac23bd32 Merge tag sound-4.10-rc4 of git://git.kernel.org/pub/scm/linux/kernel/git/tiwai/sound
- ab8db87b8256e13a62f10af1d32f5fc233c398cc drm/amd/powerplay: refine vce dpm update code on Cz.
- a844764751275e0e5d381958e3c7e6e0fe739e25 drm/amdgpu: fix vm_fault_stop on gfx6
- 3731d12dce83d47b357753ffc450ce03f1b49688 drm/amd/powerplay: fix vce cg logic error on CZ/St.
- a628392cf03e0eef21b345afbb192cbade041741 drm/radeon: drop the mclk quirk for hainan
- 3a69adfe5617ceba04ad3cff0f9ccad470503fb2 drm/radeon: drop oland quirks
- 5cc6f520ace3aa0086747e08417c2627374af1d7 drm/amdgpu: drop the mclk quirk for hainan
- 89d5595a6f53eba4d274c1d577d649db47620601 drm/amdgpu: drop oland quirks
- f1d877be65d36806c581c32b4687d4acefa55960 drm/amdgpu/si: load special ucode for certain MC configs
- ef736d394e85b1bf1fd65ba5e5257b85f6c82325 drm/radeon/si: load special ucode for certain MC configs
- 8e2329ead748a85f4ae103d71a0575ef364c30a0 ARM: dts: dra72-evm-revc: fix typo in ethernet-phy node
- 7aa4865506a26c607e00bd9794a85785b55ebca7 net: thunderx: acpi: fix LMAC initialization
- 36b29eb30ee0f6c99f06bea406c23a3fd4cbb80b soc: ti: wkup_m3_ipc: Fix error return code in wkup_m3_ipc_probe()
- ce1ca7d2d140a1f4aaffd297ac487f246963dd2f svcrdma: avoid duplicate dma unmapping during error recovery
- 8e38b7d4d71479b23b77f01cf0e5071610b8f357 ieee802154: atusb: fix driver to work with older firmware versions
- f301606934b240fb54d8edf3618a0483e36046fc at86rf230: Allow slow GPIO pins for rstn
- 5eb35a6ccea61648a55713c076ab65423eea1ac0 ieee802154: atusb: do not use the stack for address fetching to make it DMA able
- 2fd2b550a5ed13b1d6640ff77630fc369636a544 ieee802154: atusb: make sure we set a randaom extended address if fetching fails
- 05a974efa4bdf6e2a150e3f27dc6fcf0a9ad5655 ieee802154: atusb: do not use the stack for buffers to make them DMA able
- 546125d1614264d26080817d0c8cddb9b25081fa sunrpc: dont call sleeping functions from the notifier block callbacks
- 78794d1890708cf94e3961261e52dcec2cc34722 svcrpc: dont leak contexts on PROC_DESTROY
- dcd208697707b12adeaa45643bab239c5e90ef9b nfsd: fix supported attributes for acl & labels
- d3129ef672cac81c4d0185336af377c8dc1091d3 NFSv4: update_changeattr should update the attribute timestamp
- c40d52fe1c2ba25dcb8cd207c8d26ef5f57f0476 NFSv4: Dont call update_changeattr() unless the unlink is successful
- c733c49c32624f927f443be6dbabb387006bbe42 NFSv4: Dont apply change_info4 twice on rename within a directory
- 2dfc61736482441993bfb7dfaa971113b53f107c NFSv4: Call update_changeattr() from _nfs4_proc_open only if a file was created
- 8a430ed50bb1b19ca14a46661f3b1b35f2fb5c39 net: ipv4: fix table id in getroute response
- 994c5483e7f6dbf9fea622ba2031b9d868feb4b9 net: qcom/emac: grab a reference to the phydev on ACPI systems
- ea7a80858f57d8878b1499ea0f1b8a635cc48de7 net: lwtunnel: Handle lwtunnel_fill_encap failure
- 701dc207bf551d9fe6defa36e84a911e880398c3 i2c: piix4: Avoid race conditions with IMC
- 3846fd9b86001bea171943cc3bb9222cb6da6b42 drm/probe-helpers: Drop locking from poll_enable
- 2659161dd40dbb599a19f320164373093df44a89 i2c: fix spelling mistake: insufficent -> insufficient
- e28ac1fc31299d826b5dbf1d67e74720a95cda48 Merge tag xfs-for-linus-4.10-rc4-1 of git://git.kernel.org/pub/scm/fs/xfs/xfs-linux
- 6f724fb3039522486fce2e32e4c0fbe238a6ab02 i2c: print correct device invalid address
- 331c34255293cd02d395b7097008b509ba89e60e i2c: do not enable fall back to Host Notify by default
- 30f939feaeee23e21391cfc7b484f012eb189c3c i2c: fix kernel memory disclosure in dev interface
- 9ca277eba05ad99c6e7caa51cdaa93102875c026 Merge tag rproc-v4.10-fixes of git://github.com/andersson/remoteproc
- 1d865da79e3ba09362ef474807981d0634881f1d Merge tag rpmsg-v4.10-fixes of git://github.com/andersson/remoteproc
- 95ce13138e9074b12d9de50024ae1428317eee39 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/jikos/hid
- cb38b45346f17f4b0a105b9315b030a2e24fb7e6 Merge branch scsi-target-for-v4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/bvanassche/linux
- 84fcc2d2bd6cbf621e49e1d0f7eaef2e3c666b40 ceph: fix get_oldest_context()
- cc8e8342930129aa2c9b629e1653e4681f0896ea ceph: fix mds cluster availability check
- 607ae5f26920b8dfedbbf882c0f9edd3b9aa6cf7 Merge tag md/4.10-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/shli/md
- 41c066f2c4d436c535616fe182331766c57838f0 arm64: assembler: make adr_l work in modules under KASLR
- 4b09ec4b14a168bf2c687e1f598140c3c11e9222 nfs: Dont take a reference on fl->fl_file for LOCK operation
- c5a2a394835f473ae23931eda5066d3771d7b2f8 spi: davinci: use dma_mapping_error()
- 97f9c5f211d1f063b1745370e6b4fd64d6adaeff Merge tag usb-serial-4.10-rc4 of git://git.kernel.org/pub/scm/linux/kernel/git/johan/usb-serial into usb-linus
- 18a3ed59d09cf81a6447aadf6931bf0c9ffec5e0 ravb: Remove Rx overflow log messages
- f99e86485cc32cd16e5cc97f9bb0474f28608d84 block: Rename blk_queue_zone_size and bdev_zone_size
- 608edabd4e00915c36c27af3b16b92264fc111c5 Merge branch mlxsw-fixes
- 28e46a0f2e03ab4ed0e23cace1ea89a68c8c115b mlxsw: pci: Fix EQE structure definition
- 400fc0106dd8c27ed84781c929c1a184785b9c79 mlxsw: switchx2: Fix memory leak at skb reallocation
- 36bf38d158d3482119b3e159c0619b3c1539b508 mlxsw: spectrum: Fix memory leak at skb reallocation
- 33ab91103b3415e12457e3104f0e4517ce12d0f3 KVM: x86: fix emulation of MOV SS, null selector
- 19c816e8e455f58da9997e4c6626f06203d8fbf0 capability: export has_capability
- 546d87e5c903a7f3ee7b9f998949a94729fbc65b KVM: x86: fix NULL deref in vcpu_scan_ioapic
- 4f3dbdf47e150016aacd734e663347fcaa768303 KVM: eventfd: fix NULL deref irqbypass consumer
- 129a72a0d3c8e139a04512325384fe5ac119e74d KVM: x86: Introduce segmented_write_std
- cef84c302fe051744b983a92764d3fcca933415d KVM: x86: flush pending lapic jump label updates on module unload
- b6416e61012429e0277bd15a229222fd17afc1c1 jump_labels: API for flushing deferred jump label updates
- f0e8faa7a5e894b0fc99d24be1b18685a92ea466 ARM: ux500: fix prcmu_is_cpu_in_wfi() calculation
- 01167c7b9cbf099c69fe411a228e4e9c7104e123 mmc: mxs-mmc: Fix additional cycles after transmission stop
- e1d070c3793a2766122865a7c2142853b48808c5 mmc: sdhci-acpi: Only powered up enabled acpi child devices
- ff3f7e2475bbf9201e95824e72698fcdc5c3d47a x86/entry: Fix the end of the stack for newly forked tasks
- 2c96b2fe9c57b4267c3f0a680d82d7cc52e1c447 x86/unwind: Include __schedule() in stack traces
- 84936118bdf37bda513d4a361c38181a216427e0 x86/unwind: Disable KASAN checks for non-current tasks
- 900742d89c1b4e04bd373aec8470b88e183f08ca x86/unwind: Silence warnings for non-current tasks
- e4621b73b6b472fe2b434b4f0f76b8f33ee26a73 drm/i915: Fix phys pwrite for struct_mutex-less operation
- e88893fea17996018b2d68a22e677ea04f3baadf drm/i915: Clear ret before unbinding in i915_gem_evict_something()
- 32856eea7bf75dfb99b955ada6e147f553a11366 usb: gadget: udc: atmel: remove memory leak
- 8ae584d1951f241efd45499f8774fd7066f22823 usb: dwc3: exynos fix axius clock error path to do cleanup
- 866932e2771f35d20ed2f1865bcf6af8dba765bb usb: dwc2: Avoid suspending if were in gadget mode
- b2f92f0ff0a26a6d758ce85167a77d7d1268ca36 usb: dwc2: use u32 for DT binding parameters
- 08f37148b6a915a6996c7dbef87769b9efee2dba usb: gadget: f_fs: Fix iterations on endpoints.
- 9383e084a88d04d442ea2dce128edff05f344e5c usb: dwc2: gadget: Fix DMA memory freeing
- 990758c53eafe5a220a780ed12e7b4d51b3df032 usb: gadget: composite: Fix function used to free memory
- 581d3c2025632f838fb08e5160dab752b3a1f527 pinctrl: amd: avoid maybe-uninitalized warning
- 49c03096263871a68c9dea3e86b7d1e163d2fba8 pinctrl: baytrail: Do not add all GPIOs to IRQ domain
- cd60be4916ae689387d04b86b6fc15931e4c95ae scsi: lpfc: avoid double free of resource identifiers
- 98624c4fed0abd848b291fbd3da18c2251b79429 scsi: qla2xxx: remove irq_affinity_notifier
- 17e5fc58588b5e3df8220c90a9d8af55201d6b45 scsi: qla2xxx: fix MSI-X vector affinity
- 0719e72ccb801829a3d735d187ca8417f0930459 netvsc: add rcu_read locking to netvsc callback
- 4ecb1d83f6abe8d49163427f4d431ebe98f8bd5f vxlan: Set ports in flow key when doing route lookups
- 19c0f40d4fca3a47b8f784a627f0467f0138ccc8 r8152: fix the sw rx checksum is unavailable
- a89af4abdf9b353cdd6f61afc0eaaac403304873 HID: i2c-hid: Add sleep between POWER ON and RESET
- ba836a6f5ab1243ff5e08a941a2d1de8b31244e1 Merge branch akpm (patches from Andrew)
- 73da4268fdbae972f617946d1c690f2136964802 vfio-mdev: remove some dead code
- 5c677869e0abbffbade2cfd82d46d0eebe823f34 vfio-mdev: buffer overflow in ioctl()
- 6ed0993a0b859ce62edf2930ded683e452286d39 vfio-mdev: return -EFAULT if copy_to_user() fails
- 6cf4569ce3561dec560147e6051959d6896b23d1 Merge tag asoc-fix-v4.10-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/broonie/sound into for-linus
- 0a417b8dc1f10b03e8f558b8a831f07ec4c23795 xfs: Timely free truncated dirty pages
- cff3b2c4b3d2112eb9bb344e96d3d6aa66f2c13c Merge git://git.kernel.org/pub/scm/linux/kernel/git/davem/net
- a6b6e6165057f55c4cd35780520275d3c46e4c82 Merge branch linus of git://git.kernel.org/pub/scm/linux/kernel/git/herbert/crypto-2.6
- fdf35a6b22247746a7053fc764d04218a9306f82 drm: Fix broken VT switch with video=1366x768 option
- b5a10c5f7532b7473776da87e67f8301bbc32693 nvme: apply DELAY_BEFORE_CHK_RDY quirk at probe time too
- 1392370ee7de8aa3f69936f55bea6bfcc9879c59 nvme-rdma: fix nvme_rdma_queue_is_ready
- d6169d04097fd9ddf811e63eae4e5cd71e6666e2 xhci: fix deadlock at host remove by running watchdog correctly
- ad5013d5699d30ded0cdbbc68b93b2aa28222c6e perf/x86/intel: Use ULL constant to prevent undefined shift behaviour
- d2941df8fbd9708035d66d889ada4d3d160170ce mac80211: recalculate min channel width on VHT opmode changes
- 96aa2e7cf126773b16c6c19b7474a8a38d3c707e mac80211: calculate min channel width correctly
- 06f7c88c107fb469f4f1344142e80df5175c6836 cfg80211: consider VHT opmode on station update
- d7f842442f766db3f39fc5d166ddcc24bf817056 mac80211: fix the TID on NDPs sent as EOSP carrier
- 51ebfc92b72b4f7dac1ab45683bf56741e454b8c PCI: Enumerate switches below PCI-to-PCIe bridges
- 89e9f7bcd8744ea25fcf0ac671b8d72c10d7d790 x86/PCI: Ignore _CRS on Supermicro X8DTH-i/6/iF/6F
- c38c39bf7cc04d688291f382469e84ec2a8548a4 mac80211: Fix headroom allocation when forwarding mesh pkt
- 24c63bbc18e25d5d8439422aa5fd2d66390b88eb net: vrf: do not allow table id 0
- a13c06525ab9ff442924e67df9393a5efa914c56 net: phy: marvell: fix Marvell 88E1512 used in SGMII mode
- eb004603c857f3e3bfcda437b6c68fd258c54960 sctp: Fix spelling mistake: Atempt -> Attempt
- 7a18c5b9fb31a999afc62b0e60978aa896fc89e9 net: ipv4: Fix multipath selection with vrf
- 73b351473547e543e9c8166dd67fd99c64c15b0b cgroup: move CONFIG_SOCK_CGROUP_DATA to init/Kconfig
- 0bf70aebf12d8fa0d06967b72ca4b257eb6adf06 Merge branch tracepoint-updates-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/kdave/linux into for-linus-4.10
- 7cfd5fd5a9813f1430290d20c0fead9b4582a307 gro: use min_t() in skb_gro_reset_offset()
- 04ff5a095d662e0879f0eb04b9247e092210aeff pinctrl: baytrail: Rectify debounce support
- 17fab473693e8357a9aa6fee4fbed6c13a34bd81 pinctrl: intel: Set pin direction properly
- ecc8995363ee6231b32dad61c955b371b79cc4cf pinctrl: broxton: Use correct PADCFGLOCK offset
- 6d6daa20945f3f598e56e18d1f926c08754f5801 perf/x86/intel/uncore: Fix hardcoded socket 0 assumption in the Haswell init code
- 2d5a9c72d0c4ac73cf97f4b7814ed6c44b1e49ae USB: serial: ch341: fix control-message error handling
- 69d012345a1a32d3f03957f14d972efccc106a98 arm64: hugetlb: fix the wrong return value for huge_ptep_set_access_flags
- c8a6a09c1c617402cc9254b2bc8da359a0347d75 vme: Fix wrong pointer utilization in ca91cx42_slave_get
- 24b91e360ef521a2808771633d76ebc68bd5604b nohz: Fix collision between tick and other hrtimers
- 3546fb0cdac25a79c89d87020566fab52b92867d drm/etnaviv: trick drm_mm into giving out a low IOVA
- 546cf3ef9c92b76ff0037c871b939e63caea98b3 auxdisplay: fix new ht16k33 build errors
- 802c03881f29844af0252b6e22be5d2f65f93fd0 sysrq: attach sysrq handler correctly for 32-bit kernel
- 0fa2c8eb270413160557babda519aa3c21e2bfaf ppdev: dont print a freed string
- 5b11ebedd6a8bb4271b796e498cd15c0fe1133b6 extcon: return error code on failure
- 6741f551a0b26479de2532ffa43a366747e6dbf3 Revert tty: serial: 8250: add CON_CONSDEV to flags
- 2bed8a8e70729f996af92042d3ad0f11870acc1f Clearing FIFOs in RS485 emulation mode causes subsequent transmits to break
- c130b666a9a711f985a0a44b58699ebe14bb7245 8250_pci: Fix potential use-after-free in error path
- b389f173aaa1204d6dc1f299082a162eb0491545 tty/serial: atmel: RS485 half duplex w/DMA: enable RX after TX is done
- 89d8232411a85b9a6b12fd5da4d07d8a138a8e0c tty/serial: atmel_serial: BUG: stop DMA from transmitting in stop_tx
- 488debb9971bc7d0edd6d8080ba78ca02a04f6c4 drivers: char: mem: Fix thinkos in kmem address checks
- 7ee7f45a763bd68c3a606595a8c1bb08c3e6146b mei: bus: enable OS version only for SPT and newer
- 6c711c8691bf91d0e830ff4215b08e51c0626769 Merge branch mlx5-fixes
- 5e44fca5047054f1762813751626b5245e0da022 net/mlx5: Only cancel recovery work when cleaning up device
- 0bbcc0a8fc394d01988fe0263ccf7fddb77a12c3 net/mlx5e: Remove WARN_ONCE from adaptive moderation code
- 3deef8cea3efcaeeae240bb00541de66abb9bfa0 net/mlx5e: Un-register uplink representor on nic_disable
- 5e86397abe10aa4c884478a45e9a35b6a37d8d5d net/mlx5e: Properly handle FW errors while adding TC rules
- a757d108dc1a053722215ee89116f8af9bba1525 net/mlx5e: Fix kbuild warnings for uninitialized parameters
- 0827444d052ba5347900376dbdbf5d9065d091d4 net/mlx5e: Set inline mode requirements for matching on IP fragments
- 2e72eb438ce5ea9fa118edfd9a5f628c2a69111a net/mlx5e: Properly get address type of encapsulation IP headers
- a42485eb0ee458da3a0df82b0e42ab58ce76be05 net/mlx5e: TC ipv4 tunnel encap offload error flow fixes
- 2fcd82e9be133e4ec777f66fd67a8fb8e7748b1b net/mlx5e: Warn when rejecting offload attempts of IP tunnels
- cd3776638003b3362d9d7d1f27bcb80c276e2c28 net/mlx5e: Properly handle offloading of source udp port for IP tunnels
- 575b1967e10a1f3038266244d2c7a3ca6b99fed8 timerfd: export defines to userspace
- e5bbc8a6c992901058bc09e2ce01d16c111ff047 mm/hugetlb.c: fix reservation race when freeing surplus pages
- c4e490cf148e85ead0d1b1c2caaba833f1d5b29f mm/slab.c: fix SLAB freelist randomization duplicate entries
- b09ab054b69b07077bd3292f67e777861ac796e5 zram: support BDI_CAP_STABLE_WRITES
- e7ccfc4ccb703e0f033bd4617580039898e912dd zram: revalidate disk under init_lock
- f05714293a591038304ddae7cb0dd747bb3786cc mm: support anonymous stable page
- 4d09d0f45dd5d78b3a301c238272211d1ea7d9e6 mm: add documentation for page fragment APIs
- 2976db8018532b624c4123ae662fbc0814877abf mm: rename __page_frag functions to __page_frag_cache, drop order from drain
- 8c2dd3e4a4bae78093c4a5cee6494877651be3c9 mm: rename __alloc_page_frag to page_frag_alloc and __free_page_frag to page_frag_free
- b4536f0c829c8586544c94735c343f9b5070bd01 mm, memcg: fix the active list aging for lowmem requests when memcg is enabled
- f073bdc51771f5a5c7a8d1191bfc3ae371d44de7 mm: dont dereference struct page fields of invalid pages
- 9ebf73b275f06b114586af27cda3fd72e149d5ba mailmap: add codeaurora.org names for nameless email commits
- 2d39b3cd34e6d323720d4c61bd714f5ae202c022 signal: protect SIGNAL_UNKILLABLE from unintentional clearing.
- 20f664aabeb88d582b623a625f83b0454fa34f07 mm: pmd dirty emulation in page fault handler
- c626bc46edb0fec289adfc86b02e07d34127ef6c ipc/sem.c: fix incorrect sem_lock pairing
- da0510c47519fe0999cffe316e1d370e29f952be lib/Kconfig.debug: fix frv build failure
- 41b6167e8f746b475668f1da78599fc4284f18db mm: get rid of __GFP_OTHER_NODE
- 2df26639e708a88dcc22171949da638a9998f3bc mm: fix remote numa hits statistics
- f931ab479dd24cf7a2c6e2df19778406892591fb mm: fix devm_memremap_pages crash, use mem_hotplug_{begin, done}
- e7ee2c089e94067d68475990bdeed211c8852917 ocfs2: fix crash caused by stale lvb with fsdlm plugin
- 7984c27c2c5cd3298de8afdba3e1bd46f884e934 bpf: do not use KMALLOC_SHIFT_MAX
- bb1107f7c6052c863692a41f78c000db792334bf mm, slab: make sure that KMALLOC_MAX_SIZE will fit into MAX_ORDER
- f729c8c9b24f0540a6e6b86e68f3888ba90ef7e7 dax: wrprotect pmd_t in dax_mapping_entry_mkclean
- 097963959594c5eccaba42510f7033f703211bda mm: add follow_pte_pmd()
- d670ffd87509b6b136d8ed6f757851a8ebe442b2 mm/thp/pagecache/collapse: free the pte page table on collapse for thp page cache.
- 965d004af54088d138f806d04d803fb60d441986 dax: fix deadlock with DAX 4k holes
- 5771f6ea8d5ccc0df4d02ae65833413150a1b829 MAINTAINERS: remove duplicate bug filling description
- 57ea52a865144aedbcd619ee0081155e658b6f7d gro: Disable frag0 optimization on IPv6 ext headers
- 1272ce87fa017ca4cf32920764d879656b7a005a gro: Enter slow-path if there is no tailroom
- 9f9b74ef896792399dc7b5121896b9c963db80fb mlx4: Return EOPNOTSUPP instead of ENOTSUPP
- dc5367bcc556e97555fc94a32cd1aadbebdff47e net/af_iucv: dont use paged skbs for TX on HiperSockets
- 5d722b3024f6762addb8642ffddc9f275b5107ae net: add the AF_QIPCRTR entries to family name tables
- 3512a1ad56174308a9fd3e10f4b1e3e152e9ec01 net: qrtr: Mark buf as little endian
- faf3a932fbeb77860226a8323eacb835edc98648 net: dsa: Ensure validity of dst->ds[0]
- ddc37832a1349f474c4532de381498020ed71d31 ARM: 8634/1: hw_breakpoint: blacklist Scorpion CPUs
- 270c8cf1cacc69cb8d99dea812f06067a45e4609 ARM: 8632/1: ftrace: fix syscall name matching
- 807b93e995d1f44dd94b4ec50d3a864e72296416 Merge tag linux-kselftest-4.10-rc4-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/shuah/linux-kselftest
- 6bf6b0aa3da84a3d9126919a94c49c0fb7ee2fb3 virtio_blk: fix panic in initialization error path
- 25b4acfc7de0fc4da3bfea3a316f7282c6fbde81 nbd: blk_mq_init_queue returns an error code on failure, not NULL
- a14d749fcebe97ddf6af6db3d1f6ece85c9ddcb9 virtio_blk: avoid DMA to stack for the sense buffer
- dd545b52a3e1efd9f2c6352dbe95ccd0c53461cc do_direct_IO: Use inode->i_blkbits to compute block count to be cleaned
- ecd43afdbe72017aefe48080631eb625e177ef4d ARCv2: save r30 on kernel entry as gcc uses it for code-gen
- 3bcf96e0183f5c863657cb6ae9adad307a0f6071 iw_cxgb4: do not send RX_DATA_ACK CPLs after close/abort
- c12a67fec8d99bb554e8d4e99120d418f1a39c87 iw_cxgb4: free EQ queue memory on last deref
- 4fe7c2962e110dfd58e61888514726aac419562f iw_cxgb4: refactor sq/rq drain logic
- d9584d8ccc06ba98f4fad8ec720de66b6659fd35 net: skb_flow_get_be16() can be static
- 3116d37651d77125bf50f81f859b1278e02ccce6 ARM: dts: sunxi: Change node name for pwrseq pin on Olinuxino-lime2-emmc
- 7c9d8d0c41b3e24473ac7648a7fc2d644ccf08ff ibmvscsis: Fix srp_transfer_data fail return code
- 661ccdc1a95f18ab6c1373322fde09afd5b90a1f ARM: dts: sun8i: Support DTB build for NanoPi M1
- 6b546c2a15f9d8d3b1fb22adeb4063d497b08265 ARM: dts: sun6i: hummingbird: Enable display engine again
- 205ac7b33e556bde7e3374042b4ca9989e245d89 ARM: dts: sun6i: Disable display pipeline by default
- 7b6c1b4c0e1e44544aa18161dba6a741c080a7ef usb: musb: fix runtime PM in debugfs
- 2f8225e834618b9b93eaff5cea8aabbd42f04c84 Merge branch r8152-fix-autosuspend
- 75dc692eda114cb234a46cb11893a9c3ea520934 r8152: fix rx issue for runtime suspend
- 8fb280616878b81c0790a0c33acbeec59c5711f4 r8152: split rtl8152_suspend function
- 87156518da94a696f2b27ab8945d531af2f1d339 target: support XCOPY requests without parameters
- f94fd098f674b78c29f482da1999d8de0c93c74e target: check for XCOPY parameter truncation
- 66640d35c1e4ef3c96ba5edb3c5e2ff8ab812e7a target: use XCOPY segment descriptor CSCD IDs
- f184210bca6c9d0091ff5e5629dea4cbb8a17c0f target: check XCOPY segment descriptor CSCD IDs
- 94aae4caacda89a1bdb7198b260f4ca3595b7ed7 target: simplify XCOPY wwn->se_dev lookup helper
- c243849720ac237e9e7191fe57f619bb3a871d4c target: return UNSUPPORTED TARGET/SEGMENT DESC TYPE CODE sense
- 7d38706669ce00603b187f667a4eb67c94eac098 target: bounds check XCOPY total descriptor list length
- af9f62c1686268c0517b289274d38f3a03bebd2a target: bounds check XCOPY segment descriptor list
- 61c359194c46cbffec9a1f2c59c1c4011222ad84 target: use XCOPY TOO MANY TARGET DESCRIPTORS sense
- e864212078ded276bdb272b2e0ee6a979357ca8a target: add XCOPY target/segment desc sense codes
- dc647ec88e029307e60e6bf9988056605f11051a net: socket: Make unnecessarily global sockfs_setattr() static
- 2bc979f27378350465ab4eb9179ab267c8ea9074 Merge tag wireless-drivers-for-davem-2017-01-10 of git://git.kernel.org/pub/scm/linux/kernel/git/kvalo/wireless-drivers
- 620f1a632ebcc9811c2f8009ba52297c7006f805 wusbcore: Fix one more crypto-on-the-stack bug
- 146cc8a17a3b4996f6805ee5c080e7101277c410 USB: serial: kl5kusb105: fix line-state error handling
- a782b5f986c3fa1cfa7f2b57941200c6a5809242 PCI: designware: Check for iATU unroll only on platforms that use ATU
- af3076e67c31ceb3e314933dd61cb68a1d5120cf drm: flip cirrus driver status to obsolete.
- 0c19f97f12bbb1c2370cb62e31d0f749642937ee drm: update MAINTAINERS for qemu drivers (bochs, cirrus, qxl, virtio-gpu)
- 71d3f6ef7f5af38dea2975ec5715c88bae92e92d drm/virtio: fix framebuffer sparse warning
- 19a91dd4e39e755d650444da7f3a571b40a11093 MMC: meson: avoid possible NULL dereference
- 42e0ebdef53d91891939a475c6ef23970829ff99 Merge remote-tracking branches asoc/fix/nau8825, asoc/fix/rt5645, asoc/fix/tlv320aic3x and asoc/fix/topology into asoc-linus
- 1c681a1921e55628abd9cde2431c166ef8a6b993 Merge remote-tracking branches asoc/fix/arizona, asoc/fix/dpcm, asoc/fix/dwc, asoc/fix/fsl-ssi and asoc/fix/hdmi-codec into asoc-linus
- df3c63d39dc95dcfd70d891238b4deccac8259d6 Merge remote-tracking branch asoc/fix/rcar into asoc-linus
- 7dfe7e18b5585719a5cc0da8bf3bf4490b36724a Merge remote-tracking branch asoc/fix/intel into asoc-linus
- 01c2a84c491cf1cceaf696c69870667d9563f7d0 Merge remote-tracking branch asoc/fix/component into asoc-linus
- 2e40795c3bf344cfb5220d94566205796e3ef19a ALSA: usb-audio: Add a quirk for Plantronics BT600
- 68f458eec7069d618a6c884ca007426e0cea411b drm: Schedule the output_poll_work with 1s delay if we have delayed event
- 79b11b6437bd31b315f5fda72fe1a00baf98e804 Merge tag gvt-fixes-2017-01-10 of https://github.com/01org/gvt-linux into drm-intel-fixes
- 497de07d89c1410d76a15bec2bb41f24a2a89f31 tmpfs: clear S_ISGID when setting posix ACLs
- 527a27591312e4b3a0f8179f321f9e85c0850df0 dmaengine: omap-dma: Fix the port_window support
- 21d25f6a4217e755906cb548b55ddab39d0e88b9 dmaengine: iota: ioat_alloc_chan_resources should not perform sleeping allocations.
- c3c4239465e11b2cc25fcf375c7909a342bcf4dc scsi: qla2xxx: Fix apparent cut-n-paste error.
- c7702b8c22712a06080e10f1d2dee1a133ec8809 scsi: qla2xxx: Get mutex lock before checking optrom_state
- 64cbff449a8ad11d72c2b437cb7412e70fc99654 ARM, ARM64: dts: drop arm,amba-bus in favor of simple-bus part 3
- 9511ecab0762bf4df35cfc05adbc3ada09ad7075 Merge tag zynmp-dt-fixes-for-4.10 of https://github.com/Xilinx/linux-xlnx into fixes
- 37530e74609a28ae3a3b51e7685fe54a00b1e2f2 ARM: dts: imx6qdl-nitrogen6_som2: fix sgtl5000 pinctrl init
- 6ab5c2b662e2dcbb964099bf7f19e9dbc9ae5a41 ARM: dts: imx6qdl-nitrogen6_max: fix sgtl5000 pinctrl init
- 93362fa47fe98b62e4a34ab408c4a418432e7939 sysctl: Drop reference added by grab_header in proc_sys_readdir
- add7c65ca426b7a37184dd3d2172394e23d585d6 pid: fix lockdep deadlock warning due to ucount_lock
- 75422726b0f717d67db3283c2eb5bc14fa2619c5 libfs: Modify mount_pseudo_xattr to be clear it is not a userspace mount
- 3895dbf8985f656675b5bde610723a29cbce3fa7 mnt: Protect the mountpoint hashtable with mount_lock
- 318fa46cc60d37fec1e87dbf03a82aca0f5ce695 clk/samsung: exynos542x: mark some clocks as critical
- 9afe69d5a9495f8b023017e4c328fa717e00f092 Merge tag drm-misc-fixes-2017-01-09 of git://anongit.freedesktop.org/git/drm-misc into drm-fixes
- 2e86222c67bb5d942da68e8415749b32db208534 x86/microcode/intel: Use correct buffer size for saving microcode data
- 9fcf5ba2ef908af916e9002891fbbca20ce4dc98 x86/microcode/intel: Fix allocation size of struct ucode_patch
- 4167709bbf826512a52ebd6aafda2be104adaec9 x86/microcode/intel: Add a helper which gives the microcode revision
- f3e2a51f568d9f33370f4e8bb05669a34223241a x86/microcode: Use native CPUID to tickle out microcode revision
- 5dedade6dfa243c130b85d1e4daba6f027805033 x86/CPU: Add native CPUID variants returning a single datum
- 32cd7cbbacf700885a2316275f188f2d5739b5f4 md/raid5: Use correct IS_ERR() variation on pointer check
- 84a4620cfe97c9d57e39b2369bfb77faff55063d xfs: dont print warnings when xfs_log_force fails
- 12ef830198b0d71668eb9b59f9ba69d32951a48a xfs: dont rely on ->total in xfs_alloc_space_available
- 54fee133ad59c87ab01dd84ab3e9397134b32acb xfs: adjust allocation length in xfs_alloc_space_available
- 255c516278175a6dc7037d1406307f35237d8688 xfs: fix bogus minleft manipulations
- 5149fd327f16e393c1d04fa5325ab072c32472bf xfs: bump up reserved blocks in xfs_alloc_set_aside
- 6bb629db5e7daa619f5242b6ad93e4dd9bf7432c tcp: do not export tcp_peer_is_proven()
- 2ebae8bd60188f57e26e95e7fde6b8943297d348 net: phy: Add Meson GXL PHY hardware dependency
- ce7e40c432ba84da104438f6799d460a4cad41bc net/appletalk: Fix kernel memory disclosure
- b007f09072ca8afa118ade333e717ba443e8d807 ipv4: make tcp_notsent_lowat sysctl knob behave as true unsigned int
- 67c408cfa8862fe7e45b3a1f762f7140e03b7217 ipv6: fix typos
- bd5d7428f5e50cc10b98cf0abc13ccac391e1e33 Merge tag drm-fixes-for-v4.10-rc4 of git://people.freedesktop.org/~airlied/linux
- 756a7334f2b8a7fee56c221580ce75e2eb182d62 Merge tag gpio-v4.10-2 of git://git.kernel.org/pub/scm/linux/kernel/git/linusw/linux-gpio
- 811a919135b980bac8009d042acdccf10dc1ef5e phy state machine: failsafe leave invalid RUNNING state
- c92f5bdc4b9ba509a93f9e386fbb1fa779d4b0d6 Merge git://git.kernel.org/pub/scm/linux/kernel/git/davem/net
- bf99b4ded5f8a4767dbb9d180626f06c51f9881f tcp: fix mark propagation with fwmark_reflect enabled
- cc31d43b4154ad5a7d8aa5543255a93b7e89edc2 netfilter: use fwmark_reflect in nf_send_reset
- 55fa15b5987db22b4f35d3f0798928c126be5f1c USB: serial: ch341: fix baud rate and line-control handling
- 3cca8624b6624e7ffb87dcd8a0a05bef9b50e97b USB: serial: ch341: fix line settings after reset-resume
- ce5e292828117d1b71cbd3edf9e9137cf31acd30 USB: serial: ch341: fix resume after reset
- f2950b78547ffb8475297ada6b92bc2d774d5461 USB: serial: ch341: fix open error handling
- 030ee7ae52a46a2be52ccc8242c4a330aba8d38e USB: serial: ch341: fix modem-control and B0 handling
- a20047f36e2f6a1eea4f1fd261aaa55882369868 USB: serial: ch341: fix open and resume after B0
- 4e2da44691cffbfffb1535f478d19bc2dca3e62b USB: serial: ch341: fix initial modem-control state
- 21e7fbe7db2a983c046a05f12419d88c554a0f5a kvm: nVMX: Reorder error checks for emulated VMXON
- 4d82d12b39132e820b9ac4aa058ccc733db98917 KVM: lapic: do not scan IRR when delivering an interrupt
- 26fbbee5815e9352187ac18f0aa53534f62567ff KVM: lapic: do not set KVM_REQ_EVENT unnecessarily on PPR update
- b3c045d33218fe291b04d30e24b6eab0431987e6 KVM: lapic: remove unnecessary KVM_REQ_EVENT on PPR update
- eb90f3417a0cc4880e979ccc84e41890d410ea5b KVM: vmx: speed up TPR below threshold vmexits
- 0f1e261ead16ce09169bf2d223d4c8803576f85e KVM: x86: add VCPU stat for KVM_REQ_EVENT processing
- 0f89b207b04a1a399e19d35293658e3a571da3d7 kvm: svm: Use the hardware provided GPA instead of page walk
- 5bd5db385b3e13c702365574c0b7350c6ea45e84 KVM: x86: allow hotplug of VCPU with APIC ID over 0xff
- b4535b58ae0df8b7cf0fe92a0c23aa3cf862e3cc KVM: x86: make interrupt delivery fast and slow path behave the same
- 6e50043912d9c9c119e3c9c5378869d019df70a9 KVM: x86: replace kvm_apic_id with kvm_{x,x2}apic_id
- f98a3efb284a7950745d6c95be489193e6d4c657 KVM: x86: use delivery to self in hyperv synic
- 63dbe14d39b0505e3260bed92e5f4905f49c09d9 kvm: x86: mmu: Update documentation for fast page fault mechanism
- f160c7b7bb322bf079a5bb4dd34c58f17553f193 kvm: x86: mmu: Lockless access tracking for Intel CPUs without EPT A bits.
- 37f0e8fe6b10ee2ab52576caa721ee1282de74a6 kvm: x86: mmu: Do not use bit 63 for tracking special SPTEs
- f39a058d0ea2f58b9c69cfcf7c93184f33302c98 kvm: x86: mmu: Introduce a no-tracking version of mmu_spte_update
- 83ef6c8155c0ecb4c1a7e6bfbe425c85f7cb676d kvm: x86: mmu: Refactor accessed/dirty checks in mmu_spte_update/clear
- 97dceba29a6acbb28d16c8c5757ae9f4e1e482ea kvm: x86: mmu: Fast Page Fault path retries
- ea4114bcd3a8c84f0eb0b52e56d348c27ddede2e kvm: x86: mmu: Rename spte_is_locklessly_modifiable()
- 27959a4415a5a00881a7b9353ab9b1274da2ca47 kvm: x86: mmu: Use symbolic constants for EPT Violation Exit Qualifications
- 114df303a7eeae8b50ebf68229b7e647714a9bea kvm: x86: reduce collisions in mmu_page_hash
- f3414bc77419463c0d81eaa2cea7ee4ccb447c7d kvm: x86: export maximum number of mmu_page_hash collisions
- 826da32140dada1467f4216410525511393317e8 KVM: x86: simplify conditions with split/kernel irqchip
- 8231f50d9853274ed104aac86b6b6263ca666c4d KVM: x86: prevent setup of invalid routes
- e5dc48777dcc898210e2f16d80d44718db38cdc3 KVM: x86: refactor pic setup in kvm_set_routing_entry
- 099413664c71fcf9d0099eba4f8a4dd59653d5a3 KVM: x86: make pic setup code look like ioapic setup
- 49776faf93f8074bb4990beac04781a9507d3650 KVM: x86: decouple irqchip_in_kernel() and pic_irqchip()
- 35e6eaa3df55822d0cb1df3bf08e6cb816737131 KVM: x86: dont allow kernel irqchip with split irqchip
- 02c5c03283c52157d336abf5e44ffcda10579fbf ASoC: rt5645: set sel_i2s_pre_div1 to 2
- 9620ca90115d4bd700f05862d3b210a266a66efe spi: spi-axi: Free resources on error path
- fac69d0efad08fc15e4dbfc116830782acc0dc9a x86/boot: Add missing declaration of string functions
- 562a7a07bf61e2949f7cbdb6ac7537ad9e2794d1 btrfs: make tracepoint format strings more compact
- 7856654842bdbebc0fbcbf51573da5d70a787aba Btrfs: add truncated_len for ordered extent tracepoints
- 92a1bf76a89ad338f00eb9a2c7689a3907fbcaad Btrfs: add inode for extent map tracepoint
- ac0c7cf8be00f269f82964cf7b144ca3edc5dbc4 btrfs: fix crash when tracepoint arguments are freed by wq callbacks
- eeb0d56fab4cd7848cf2be6704fa48900dbc1381 mac80211: implement multicast forwarding on fast-RX path
- 9631739f8196ec80b5d9bf955f79b711490c0205 drm/i915/gvt: cleanup GFP flags
- f0a8b49c03d22a511a601dc54b2a3425a41e35fa drm/bridge: analogix dp: Fix runtime PM state on driver bind
- a47fff1056376fab0929661e8cc85f90572cf55a Merge remote-tracking branch mkp-scsi/fixes into fixes
- 5753394b64a07dd502cb288a5fd52e71fb01fc5d drm/i915/gvt/kvmgt: return meaningful error for vgpu creating failure
- 03551e971f6e52c8dedd5741bf48631e65675759 drm/i915/gvt: cleanup opregion memory allocation code
- 4e5378918b5b96e6b93fcadf1ab84a8486ca60a1 drm/i915/gvt: destroy the allocated idr on vgpu creating failures
- 59c0573dfbd5f66e3aa54c2ce0bebcb0953d4db4 drm/i915/gvt: init/destroy vgpu_idr properly
- 440a9b9fae37dfd7e4c7d76db34fada57f9afd92 drm/i915/gvt: dec vgpu->running_workload_num after the workload is really done
- 2e51ef32b0d66fcd5fe45c437cf7c6aef8350746 drm/i915/gvt: fix use after free for workload
- 2fcdb66364ee467d69228a3d2ea074498c177211 drm/i915/gvt: remove duplicated definition
- 888530b57f88f2bc856f181479df732c9622fa22 drm/i915/gvt: adjust high memory size for default vGPU type
- 901a14b721feef1b37cfe6362ee103e135133677 drm/i915/gvt: print correct value for untracked mmio
- 905a5035ebe79e89712cda0bed1887c73aa8e9bb drm/i915/gvt: always use readq and writeq
- 39762ad437f1149b904e6baeaf28824da34a89c1 drm/i915/gvt: fix return value in mul_force_wake_write
- a12010534d0984f91bc5bdcf9e27bd55e20d82da drm/i915/gvt: fix error handing of tlb_control emulation
- 3e70c5d6ea510e38f612d07fa0fd7487277b7087 drm/i915/gvt: verify functions types in new_mmio_info()
- 03430fa10b99e95e3a15eb7c00978fb1652f3b24 Merge branch bcm_sf2-fixes
- 2cfe8f8290bd28cf1ee67db914a6e76cf8e6437b net: dsa: bcm_sf2: Utilize nested MDIO read/write
- a4c61b92b3a4cbda35bb0251a5063a68f0861b2c net: dsa: bcm_sf2: Do not clobber b53_switch_ops
- 6edd870bca30b3aa69370a99bcefc1e5f2b8b190 Merge branch drm-fixes-4.10 of git://people.freedesktop.org/~agd5f/linux into drm-fixes
- a2cd64f30140c5aebd9359f66c00c19d5c6bece6 net: stmmac: fix maxmtu assignment to be within valid range
- 6906407eeb690ed31b183a38ae10db2907cc3a58 Merge branch msm-fixes-4.10 of git://people.freedesktop.org/~robclark/linux into drm-fixes
- 90e5d2d45776451e58989361a182c067008d5941 Merge tag meson-drm-fixes-for-4.10 of git://people.freedesktop.org/~narmstrong/linux into drm-fixes
- 13fe46b589c216f3a0c8e142282125c782a175f5 Merge tag tilcdc-4.10-fixes of https://github.com/jsarha/linux into drm-fixes
- e1ef6f71e347655f3ffbcc40d7ced8ea754114b7 Merge tag drm-misc-fixes-2017-01-04 of git://anongit.freedesktop.org/git/drm-misc into drm-fixes
- a121103c922847ba5010819a3f250f1f7fc84ab8 Linux 4.10-rc3
- 9d5ecb09d525469abd1a10c096cb5a17206523f2 bpf: change back to orig prog on too many passes
- 83280e90ef001f77a64e2ce59c25ab66e47ab1f0 Merge tag usb-4.10-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/usb
- cc250e267bd56c531b0bee455fc724d50af83fac Merge tag char-misc-4.10-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/char-misc
- 6ea17ed15d9a343c2d17d76b99501fcad204f309 Merge tag staging-4.10-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/staging
- f5992b72ebe0dde488fa8f706b887194020c66fc tg3: Fix race condition in tg3_get_stats64().
- 6052cd1af86f9833b6b0b60d5d4787c4a06d65ea be2net: fix unicast list filling
- ea07b862ac8ef9b8c8358517d2e39f847dda6659 mm: workingset: fix use-after-free in shadow node shrinker
- b0b9b3df27d100a975b4e8818f35382b64a5e35c mm: stop leaking PageTables
- 87bc610730a944b49f1c53ab9f4230d85f35df0c Merge branch rc-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/mmarek/kbuild
- 01d0f715869161dc70e2bf66fcdf6533a6a782cd MAINTAINERS: add greybus subsystem mailing list
- 20b1e22d01a4b0b11d3a1066e9feb04be38607ec x86/efi: Dont allocate memmap through memblock after mm_init()
- 1d0f110a2c6c4bca3dbcc4b0e27f1e3dc2d44a2c be2net: fix accesses to unicast list
- bcd5e1a49f0d54afd3c5411bed2f59996e1c53e4 netlabel: add CALIPSO to the list of built-in protocols
- 308c470bc482c46b5acbb2c2072df303d6526250 Merge tag sound-4.10-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/tiwai/sound
- d72f0ded89cc78598b8eb0570890234eba167588 Merge tag clk-fixes-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/clk/linux
- baaf031521b7f67be45f07593023b6ba47f07d15 Merge tag hwmon-for-linus-v4.10-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/groeck/linux-staging
- 08289086b0ab0379f54e1590ceb5e1b04d239c07 Merge tag for-linus of git://git.kernel.org/pub/scm/virt/kvm/kvm
- b1ee51702e12a99d35d7c11d1d2b5cd324001ee2 Merge tag arm64-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/arm64/linux
- 7192c54a68013f6058b1bb505645fcd07015191c drm/amdgpu: drop verde dpm quirks
- 8a08403bcb39f5d0e733bcf59a8a74f16b538f6e drm/radeon: drop verde dpm quirks
- 6458bd4dfd9414cba5804eb9907fe2a824278c34 drm/radeon: update smc firmware selection for SI
- 5165484b02f2cbedb5bf3a41ff5e8ae16069016c drm/amdgpu: update si kicker smc firmware
- 70fd80d6f7e37bf637331c682fafcce1112750ac drm/amd/powerplay: extend smus response timeout time.
- d6df71e125b4e4ab8932349ce81e09ef73304b91 drm/amdgpu: remove static integer for uvd pp state
- fc8e9c54699e42754094ff475da46440778d8f19 drm/amd/amdgpu: add Polaris12 PCI ID
- f4309526576db325264b6dc9ee150ee70b330a42 drm/amdgpu/powerplay: add Polaris12 support
- c4642a479fac9f5c224ff7425d86c427b94011af drm/amd/amdgpu: add Polaris12 support (v3)
- 7f4c4f80fd22ec7722e778c1d099e828d2b5dc40 MAINTAINERS: Update mailing list for radeon and amdgpu
- 219a808fa1829a82a29197561dc8dd12b7005cad Merge tag mac80211-for-davem-2017-01-06 of git://git.kernel.org/pub/scm/linux/kernel/git/jberg/mac80211
- 93e246f783e6bd1bc64fdfbfe68b18161f69b28e vti6: fix device register to report IFLA_INFO_KIND
- 5ca7d1ca77dc23934504b95a96d2660d345f83c2 net: phy: dp83867: fix irq generation
- 896b4db685cf06bd7d50ed22c53ebd069e0b90e9 amd-xgbe: Fix IRQ processing when running in single IRQ mode
- 0f1f9cbc04dbb3cc310f70a11cba0cf1f2109d9c sh_eth: R8A7740 supports packet shecksumming
- 978d3639fd13d987950e4ce85c8737ae92154b2c sh_eth: fix EESIPR values for SH77{34|63}
- fd7c99142d77dc4a851879a66715abf12a3193fb tile/ptrace: Preserve previous registers for short regset write
- 5824f92463e978f27985b748c69d94ee7caa8230 Merge tag vfio-v4.10-rc3 of git://github.com/awilliam/linux-vfio
- 2fd8774c79a455a1f12f75208d96f2f0cc3728c9 Merge branch stable/for-linus-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/konrad/swiotlb
- 65cdc405b37a0f43af9c0fb6cf011304b3959ef8 Merge tag iommu-fixes-v4.10-rc2 of git://git.kernel.org/pub/scm/linux/kernel/git/joro/iommu
- 7397e1e838228a0957043613c265a611e09c05f3 Merge tag acpi-4.10-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/rafael/linux-pm
- b937a8697b81e2e385642853b90647e1b4aef85e Merge tag pm-4.10-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/rafael/linux-pm
- 9f169b9f52a4afccdab7a7d2311b0c53a78a1e6b ASoC: dpcm: Avoid putting stream state to STOP when FE stream is paused
- bc65a326c579e93a5c2120a65ede72f11369ee5a ASoC: Intel: Skylake: Release FW ctx in cleanup
- 7453c549f5f6485c0d79cad7844870dcc7d1b34d swiotlb: Export swiotlb_max_segment to users
- 657279778af54f35e54b07b6687918f254a2992c ARM: OMAP1: DMA: Correct the number of logical channels
- 1ebb71143758f45dc0fa76e2f48429e13b16d110 HID: hid-cypress: validate length of report
- f1dabf0b0975f9e71344b5c8c0ab39c4d58d9274 Merge branches acpi-scan, acpi-sysfs, acpi-wdat and acpi-tables
- 7e2b9d85550ee267ec3b5aba6362fdaeb1559f46 Merge branches pm-domains, pm-docs and pm-devfreq
- 3baad65546b0d6b2695b1de384130125495bc545 Merge branch pm-cpufreq
- a33d331761bc5dd330499ca5ceceb67f0640a8e6 x86/CPU/AMD: Fix Bulldozer topology
- 88ba6cae15e38f609aba4f3881e1c404c432596c Merge tag platform-drivers-x86-v4.10-3 of git://git.infradead.org/users/dvhart/linux-platform-drivers-x86
- 6989606a7224a2d5a925df22a49e4f7a0bfed0d6 Merge branch stable-4.10 of git://git.infradead.org/users/pcmoore/audit
- f53345e8cf027d03187b9417f1f8883c516e1a5b thermal: core: move tz->device.groups cleanup to thermal_release
- 2d1148f0f45079d25a0fa0d67e4fdb2a656d12fb scsi: bfa: Increase requested firmware version to 3.2.5.1
- 0371adcdaca92912baaa3256ed13e058a016e62d scsi: snic: Return error code on memory allocation failure
- 9698b6f473555a722bf81a3371998427d5d27bde scsi: fnic: Avoid sending reset to firmware when another reset is in progress
- ed40875dd4b4c7b5c991db9e06c984180ab0b3ce Merge tag drm-intel-fixes-2017-01-05 of git://anongit.freedesktop.org/git/drm-intel
- 1c3415a06b1016a596bfe59e0cfee56c773aa958 Input: elants_i2c - avoid divide by 0 errors on bad touchscreen data
- 7738789fba09108a28a5fb4739595d9a0a2f85fe selftests: x86/pkeys: fix spelling mistake: itertation -> iteration
- 3659f98b5375d195f1870c3e508fe51e52206839 selftests: do not require bash to run netsocktests testcase
- d979e13a3fa9067c8cd46e292ed859626d443996 selftests: do not require bash to run bpf tests
- a2b1e8a20c992b01eeb76de00d4f534cbe9f3822 selftests: do not require bash for the generated test
- 394ed8e4743b0cfc5496fe49059fbfc2bc8eae35 md: cleanup mddev flag clear for takeover
- 99f17890f04cff0262de7393c60a2f6d9c9c7e71 md/r5cache: fix spelling mistake on recoverying
- d2250f105f18a43fdab17421bd80b0ffc9fcc53f md/r5cache: assign conf->log before r5l_load_log()
- 3c66abbaaf69671dfd3eb9fa7740b5d7ec688231 md/r5cache: simplify handling of sh->log_start in recovery
- 28ca833ecf89c585a9543fb21aef6b2bdbbaa48a md/raid5-cache: removes unnecessary write-through mode judgments
- 0a8fd1346254974c3a852338508e4a4cddbb35f1 USB: fix problems with duplicate endpoint addresses
- c433eb70f37de2514f3ae3d43dd7e4a75493fe48 Merge tag pinctrl-v4.10-2 of git://git.kernel.org/pub/scm/linux/kernel/git/linusw/linux-pinctrl
- 8f12dc24490bde0d604b8bdfca05ea4b06a624a7 usb: ohci-at91: use descriptor-based gpio APIs correctly
- b40079273279999d0a259e78d9ecb53ad82d042f Merge tag armsoc-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/arm/arm-soc
- 383378d115ab6e702d77896071d36056875602db Merge tag for-linus-4.10-rc2-tag of git://git.kernel.org/pub/scm/linux/kernel/git/xen/tip
- 421463b80b40e919dc57483f967ebd41674a81ff hyper-v: Add myself as additional MAINTAINER
- 674aea07e38200ea6f31ff6d5f200f0cf6cdb325 usb: storage: unusual_uas: Add JMicron JMS56x to unusual device
- 3bc02bce908c7250781376052248f5cd60a4e3d4 usb: hub: Move hub_port_disable() to fix warning if PM is disabled
- 5563bb5743cb09bde0d0f4660a5e5b19c26903bf usb: musb: blackfin: add bfin_fifo_offset in bfin_ops
- c8bd2ac3b4c6c84c4a7cdceaed626247db698ab2 usb: musb: fix compilation warning on unused function
- 8c300fe282fa254ea730c92cb0983e2642dc1fff usb: musb: Fix trying to free already-free IRQ 4
- c48400baa02155a5ddad63e8554602e48782278c usb: musb: dsps: implement clear_ep_rxintr() callback
- 6def85a396ce7796bd9f4561c6ae8138833f7a52 usb: musb: core: add clear_ep_rxintr() to musb_platform_ops
- 9e3596b0c6539e28546ff7c72a06576627068353 kbuild: initramfs cleanup, set target from Kconfig
- ae30ab4cd711a147cafaf5674c333c5a84fe53fb kbuild: initramfs fix dependency checking for compressed target
- 5bdee5496978c6738dd90869b54c0f30c0344ccf Merge tag nand/fixes-for-4.10-rc3 of github.com:linux-nand/linux
- 6ca36a455e2730a3195a5596d53c900c9cd00838 ARM: dts: am335x-icev2: Remove the duplicated pinmux setting
- a3ac350793d90d1da631c8beeee9352387974ed5 ARM: OMAP2+: Fix WL1283 Bluetooth Baud Rate
- d896b3120b3391a2f95b2b8ec636e3f594d7f9c4 Merge git://git.kernel.org/pub/scm/linux/kernel/git/pablo/nf
- c8d204b38a558d74fafb6915e2593602b7f4b823 Merge tag usb-serial-4.10-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/johan/usb-serial into usb-linus
- 9b60047a9c950e3fde186466774ffd1ab1104d4e r8169: fix the typo in the comment
- 696c7f8e0373026e8bfb29b2d9ff2d0a92059d4d ACPI / DMAR: Avoid passing NULL to acpi_put_table()
- 69130ea1e6b9167d2459e2bab521196d0a0c0e68 KVM: VMX: remove duplicated declaration
- 32eb12a6c11034867401d56b012e3c15d5f8141e KVM: MIPS: Flush KVM entry code from icache globally
- 4c881451d3017033597ea186cf79ae41a73e1ef8 KVM: MIPS: Dont clobber CP0_Status.UX
- 08f9572671c8047e7234cbf150869aa3c3d59a97 HID: ignore Petzl USB headlamp
- 60448b077ed93d227e6c117a9e87db76ff0c1911 ASoC: Intel: bytcr-rt5640: fix settings in internal clock mode
- c7858bf16c0b2cc62f475f31e6df28c3a68da1d6 asm-prototypes: Clear any CPP defines before declaring the functions
- 753aacfd2e95df6a0caf23c03dc309020765bea9 nl80211: fix sched scan netlink socket owner destruction
- 74545f63890e38520eb4d1dbedcadaa9c0dbc824 perf/x86: Set pmu->module in Intel PMU modules
- 159d3726db12b3476bc59ea0ab0a702103d466b5 x86/platform/intel-mid: Rename spidev to mrfld_spidev
- 754c73cf4d2463022b2c9ae208026bf22564ed06 x86/cpu: Fix typo in the comment for Anniedale
- dd853fd216d1485ed3045ff772079cc8689a9a4a x86/cpu: Fix bootup crashes by sanitizing the argument of the clearcpuid= command-line option
- e4f34cf6d59160818dcdcf41f4116cc88093ece3 Revert ALSA: firewire-lib: change structure member with proper type
- 4e06d4f083d6b485d689948479d5b2052917373d Merge tag perf-urgent-for-mingo-4.10-20170104 of git://git.kernel.org/pub/scm/linux/kernel/git/acme/linux into perf/urgent
- 13a6c8328e6056932dc680e447d4c5e8ad9add17 ALSA: usb-audio: test EP_FLAG_RUNNING at urb completion
- 1d0f953086f090a022f2c0e1448300c15372db46 ALSA: usb-audio: Fix irq/process data synchronization
- e02003b515e8d95f40f20f213622bb82510873d2 Merge tag xfs-for-linus-4.10-rc3 of git://git.kernel.org/pub/scm/fs/xfs/xfs-linux
- e51d5d02f688c45b6f644f472f0c80fdfa73f0cb ARCv2: IRQ: Call entry/exit functions for chained handlers in MCIP
- 2163266c2704aa44211b6b61924a0fa570fe0d4b ARC: IRQ: Use hwirq instead of virq in mask/unmask
- fa84d7310d19e0b77979019df82e357b1e8443e3 ARC: mmu: clarify the MMUv3 programming model
- e11b6293a8fcd3f29376808910f49bd82f72b69a cpufreq: dt: Add support for APM X-Gene 2
- 4cf184638bcf2bdd1bcbc661f4717b648ad4ce40 Merge git://git.kernel.org/pub/scm/linux/kernel/git/davem/net
- 71eae1ca77fd6be218d8a952d97bba827e56516d sh_eth: enable RX descriptor word 0 shift on SH7734
- c7efff9284dfde95a11aaa811c9d8ec8167f0f6e ALSA: hda - Apply asus-mode8 fixup to ASUS X71SL
- c6ef7fd40eddad38a8825cbd6bb2ce8bdbba88f5 vfio-mdev: fix non-standard ioctl return val causing i386 build fail
- cf9e1672a66c49ed8903c01b4c380a2f2dc91b40 mtd: nand: lpc32xx: fix invalid error handling of a requested irq
- 4fdda95893de776a8efdf661bbf0e338f2f13dcb sfc: dont report RX hash keys to ethtool when RSS wasnt enabled
- aa9773be2ad5afe7acc186aedbf3b4857611d4ed Merge branch dpaa_eth-fixes
- 0fbb0f24dde8759925fc56e9dbc6a5b2cbba99c4 dpaa_eth: Initialize CGR structure before init
- 3fe61f0940d9c7892462c893602fdccfe8b24e8c dpaa_eth: cleanup after init_phy() failure
- a2dd8af00ca7fff4972425a4a6b19dd1840dc807 spi: pxa2xx: add missed break
- c030af878f04b77011f6876e8c4f0530c26ed6d4 Merge branch systemport-padding-and-TSB-insertion
- 38e5a85562a6cd911fc26d951d576551a688574c net: systemport: Pad packet before inserting TSB
- bb7da333d0a9f3bddc08f84187b7579a3f68fd24 net: systemport: Utilize skb_put_padto()
- 4ee437fbf626b5ad756889d8bc0fcead3d66dde7 ASoC: fsl_ssi: set fifo watermark to more reliable value
- cd7aeb1f9706b665ad8659df8ff036e7bc0097f4 LiquidIO VF: s/select/imply/ for PTP_1588_CLOCK
- a9a8cdb368d99bb655b5cdabea560446db0527cc libcxgb: fix error check for ip6_route_output()
- 63dfb0dac9055145db85ce764355aef2f563739a net: usb: asix_devices: add .reset_resume for USB PM
- b577fafc4366eb82334518c552912652328c74fa nvmem: fix nvmem_cell_read() return type doc
- 14ba972842f9e84e6d3264bc0302101b8a792288 nvmem: imx-ocotp: Fix wrong register size
- 01d0d2c42a14cee8f619d3e9d571ce3469f5ef51 nvmem: qfprom: Allow single byte accesses for read/write
- e09ee853c92011860a4bd2fbdf6126f60fc16bd3 mei: move write cb to completion on credentials failures
- 5026c9cb0744a9cd40242743ca91a5d712f468c6 mei: bus: fix mei_cldev_enable KDoc
- 62f8c40592172a9c3bc2658e63e6e76ba00b3b45 Merge branch for-linus of git://git.kernel.dk/linux-block
- 9f7445197a263c99ddb898f3609fed21673ae24c Merge tag fbdev-v4.10-rc2 of git://github.com/bzolnier/linux
- 99b9be77632734363913e5cf22c06bb66d7f71d8 Merge tag gcc-plugins-v4.10-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/kees/linux
- 9d84fb27fa135c99c9fe3de33628774a336a70a8 arm64: restore get_current() optimisation
- 6ef4fb387d50fa8f3bffdffc868b57e981cdd709 arm64: mm: fix show_pte KERN_CONT fallout
- 1b9ec81258827001c869f003e0b8dd2ddc104717 Merge tag davinci-fixes-for-v4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/nsekhar/linux-davinci into fixes
- e9b2aefa88c5d9e4ea8fc950da9b105981ad60ec Merge tag amlogic-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/khilman/linux-amlogic into fixes
- 5c6ec6a02c1378ba0e3ac530f8c80523ea74e5de Merge tag psci-fixes-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/lpieralisi/linux into fixes
- 46db9914c3bf9d7aa292bc03eb2061a553a057d7 Merge tag juno-fixes-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/sudeep.holla/linux into fixes
- e19f32da5ded958238eac1bbe001192acef191a2 vfio-pci: Handle error from pci_iomap
- f53c1e6464d3c24583be4f1c1668c54813695da3 Merge tag vexpress-fixes-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/sudeep.holla/linux into fixes
- d293dbaa540b5800817cc10832d764b17cc211b5 vfio-mdev: fix some error codes in the sample code
- 43a8df78dc1a95c24a08f6b776dc86820c117160 Merge tag scpi-fixes-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/sudeep.holla/linux into fixes
- ad040d8df6eb3a6d4b85ef69448d370d0065843c Merge tag imx-fixes-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/shawnguo/linux into fixes
- fcf14b8889d5da38bac9b1fb9718f98706d90e59 Merge tag qcom-arm-fixes-for-4.10-rc2 of git://git.kernel.org/pub/scm/linux/kernel/git/agross/linux into fixes
- 46a3bf80712711ac2675bc176b08a95940ed1c42 Merge tag omap-for-v4.10/fixes-rc1 of git://git.kernel.org/pub/scm/linux/kernel/git/tmlind/linux-omap into fixes
- d4032ccc406f325dbbda637fbb10746e9a441aa4 Merge tag samsung-soc-4.10-2 of git://git.kernel.org/pub/scm/linux/kernel/git/krzk/linux into fixes
- cb2cc43681dacbd74f3c1f96fde5ee21524fed54 Merge tag qcom-fixes-for-4.10-rc1 of git://git.kernel.org/pub/scm/linux/kernel/git/agross/linux into fixes
- 84cc8ca1fd7b966830d2d904e914d7d3a33ef02e Merge tag renesas-fixes-for-v4.10 of https://git.kernel.org/pub/scm/linux/kernel/git/horms/renesas into fixes
- 8a937a25a7e3c19d5fb3f9d92f605cf5fda219d8 perf probe: Fix to probe on gcc generated symbols for offline kernel
- 432abf68a79332282329286d190e21fe3ac02a31 iommu/amd: Fix the left value check of cmd buffer
- 65ca7f5f7d1cdde6c25172fe6107cd16902f826f iommu/vt-d: Fix pasid table size encoding
- eebc509b20881b92d62e317b2c073e57c5f200f0 perf probe: Fix --funcs to show correct symbols for offline module
- aec0e86172a79eb5e44aff1055bb953fe4d47c59 iommu/vt-d: Flush old iommu caches for kdump when the device gets context mapped
- cf1716e9dae5b21b9bbcfe5eb0106c3b0aee37e8 spi: dw-mid: switch to new dmaengine_terminate_* API (part 2)
- 4dcd19bfabaee8f9f4bcf203afba09b98ccbaf76 video: fbdev: cobalt_lcdfb: Handle return NULL error from devm_ioremap
- 04f6152d9fbad5bb78bccd05e798fa2d66c571e9 MAINTAINERS: add myself as maintainer of fbdev
- 5db60ea93d4fbf146c8f7ca286b8b2a091761460 drm/meson: Fix CVBS VDAC disable
- 0c931a290cc0377c99a8cd970a49e736dbb23e0e drm/meson: Fix CVBS initialization when HDMI is configured by bootloader
- 3dda13a8ad787f3d4c4f18c8c05f8eebc7ea135a Merge branch misc-4.10 into for-chris-4.10-20170104
- 85bcf96caba8b4a7c0805555638629ba3c67ea0c ALSA: hda - Fix up GPIO for ASUS ROG Ranger
- aebe55c2d4b998741c0847ace1b4af47d73c763b drm: Clean up planes in atomic commit helper failure path
- ef079936d3cd09e63612834fe2698eeada0d8e3f USB: serial: ti_usb_3410_5052: fix NULL-deref at open
- cc0909248258f679c4bb4cd315565d40abaf6bc6 USB: serial: spcp8x5: fix NULL-deref at open
- f09d1886a41e9063b43da493ef0e845ac8afd2fa USB: serial: quatech2: fix sleep-while-atomic in close
- 76ab439ed1b68778e9059c79ecc5d14de76c89a8 USB: serial: pl2303: fix NULL-deref at open
- 5afeef2366db14587b65558bbfd5a067542e07fb USB: serial: oti6858: fix NULL-deref at open
- a5bc01949e3b19d8a23b5eabc6fc71bb50dc820e USB: serial: omninet: fix NULL-derefs at open and disconnect
- 472d7e55d559aa1cbf58c73b14fcfc4651b1a9f5 USB: serial: mos7840: fix misleading interrupt-URB comment
- fc43e651bf39ef174a86fde4c4593f796b1474c1 USB: serial: mos7840: remove unused write URB
- 5c75633ef751dd4cd8f443dc35152c1ae563162e USB: serial: mos7840: fix NULL-deref at open
- 9da049bcedf43e20e8cb77ee00a1239497ed9fa2 USB: serial: mos7720: remove obsolete port initialisation
- fde1faf872ed86d88e245191bc15a8e57368cd1c USB: serial: mos7720: fix parallel probe
- 75dd211e773afcbc264677b0749d1cf7d937ab2d USB: serial: mos7720: fix parport use-after-free on probe errors
- 91a1ff4d53c5184d383d0baeeaeab6f9736f2ff3 USB: serial: mos7720: fix use-after-free on probe errors
- b05aebc25fdc5aeeac3ee29f0dc9f58dd07c13cc USB: serial: mos7720: fix NULL-deref at open
- 21ce57840243c7b70fbc1ebd3dceeb70bb6e9e09 USB: serial: kobil_sct: fix NULL-deref in write
- 5d9b0f859babe96175cd33d7162a9463a875ffde USB: serial: keyspan_pda: verify endpoints at probe
- 90507d54f712d81b74815ef3a4bbb555cd9fab2f USB: serial: iuu_phoenix: fix NULL-deref at open
- e35d6d7c4e6532a89732cf4bace0e910ee684c88 USB: serial: io_ti: bind to interface after fw download
- 2330d0a853da260d8a9834a70df448032b9ff623 USB: serial: io_ti: fix I/O after disconnect
- 4f9785cc99feeb3673993b471f646b4dbaec2cc1 USB: serial: io_ti: fix another NULL-deref at open
- a323fefc6f5079844dc62ffeb54f491d0242ca35 USB: serial: io_ti: fix NULL-deref at open
- 0dd408425eb21ddf26a692b3c8044c9e7d1a7948 USB: serial: io_edgeport: fix NULL-deref at open
- c4ac4496e835b78a45dfbf74f6173932217e4116 USB: serial: garmin_gps: fix memory leak on failed URB submit
- 3dca01114dcecb1cf324534cd8d75fd1306a516b USB: serial: cyberjack: fix NULL-deref at open
- f97fd383d9a10fd125bcdafba03240685aed5608 drm: tilcdc: simplify the recovery from sync lost error on rev1
- 4ea33ef0f9e95b69db9131d7afd98563713e81b0 batman-adv: Decrease hardif refcnt on fragmentation send error
- ff97f2399edac1e0fb3fa7851d5fbcbdf04717cf xfs: fix max_retries _show and _store functions
- 7611fb68062f8d7f416f3272894d1edf7bbff29c thermal: thermal_hwmon: Convert to hwmon_device_register_with_info()
- 721a0edfbe1f302b93274ce75e0d62843ca63e0d xfs: update MAINTAINERS
- a1b7a4dea6166cf46be895bce4aac67ea5160fe8 xfs: fix crash and data corruption due to removal of busy COW extents
- 20e73b000bcded44a91b79429d8fa743247602ad xfs: use the actual AG length when reserving blocks
- 7a21272b088894070391a94fdd1c67014020fa1d xfs: fix double-cleanup when CUI recovery fails
- 926d93a33e59b2729afdbad357233c17184de9d2 net: vrf: Add missing Rx counters
- 7158339d4c1ede786c48fa5c062fa68df366ba94 block: fix up io_poll documentation
- be29d20f3f5db1f0b4e49a4f6eeedf840e2bf9b1 audit: Fix sleep in atomic
- 01427fe7c4b956b878e55e966690624a3624e991 Input: adxl34x - make it enumerable in ACPI environment
- 47e3a5edc6538d66e470aaed3b7c57255cb37ca1 Input: ALPS - fix TrackStick Y axis handling for SS5 hardware
- 81d873a87114b05dbb74d1fbf0c4322ba4bfdee4 gcc-plugins: update gcc-common.h for gcc-7
- 9988f4d577f42f43b7612d755477585f35424af7 latent_entropy: fix ARM build error on earlier gcc
- 7934c98a6e04028eb34c1293bfb5a6b0ab630b66 perf symbols: Robustify reading of build-id from sysfs
- 30a9c6444810429aa2b7cbfbd453ce339baaadbf perf tools: Install tools/lib/traceevent plugins with install-bin
- 074859184d770824f4437dca716bdeb625ae8b1c tools lib traceevent: Fix prev/next_prio for deadline tasks
- 0f64df30124018de92c7f22a044b975da8dd52cc Merge branch parisc-4.10-2 of git://git.kernel.org/pub/scm/linux/kernel/git/deller/parisc-linux
- 0b47a6bd1150f4846b1d61925a4cc5a96593a541 Xen: ARM: Zero reserved fields of xatp before making hypervisor call
- 32d53d1baf874caabe66ba565699ed5853fa2b6f MAINTAINERS: extend PSCI entry to cover the newly add PSCI checker code
- 4309cfe334af9c3565d39e1ce3f9c62183cc67e4 drivers: psci: annotate timer on stack to silence odebug messages
- fcdaf1a2a7a042a290f4c7de28bcdebd5de18445 ARM64: defconfig: enable DRM_MESON as module
- fafdbdf767891081de5f1063c984a94a59bac3c4 ARM64: dts: meson-gx: Add Graphic Controller nodes
- 1cf3df8a9ca73e736404e308b099459948c1e902 ARM64: dts: meson-gxl: fix GPIO include
- bb5f1ed70bc3bbbce510907da3432dab267ff508 md/raid10: Refactor raid10_make_request
- 3b046a97cbd35a73e1eef968dbfb1a0aac745a77 md/raid1: Refactor raid1_make_request
- 29fc1aa454d0603493b47a8e2410ae6e9ab20258 usb: host: xhci: handle COMP_STOP from SETUP phase too
- 6c97cfc1a097b1e0786c836e92b7a72b4d031e25 usb: xhci: apply XHCI_PME_STUCK_QUIRK to Intel Apollo Lake
- 1c111b6c3844a142e03bcfc2fa17bfbdea08e9dc xhci: Fix race related to abort operation
- cb4d5ce588c5ff68e0fdd30370a0e6bc2c0a736b xhci: Use delayed_work instead of timer for command timeout
- 4dea70778c0f48b4385c7720c363ec8d37a401b4 usb: xhci: hold lock over xhci_abort_cmd_ring()
- a5a1b9514154437aa1ed35c291191f82fd3e941a xhci: Handle command completion and timeout race
- 2a7cfdf37b7c08ac29df4c62ea5ccb01474b6597 usb: host: xhci: Fix possible wild pointer when handling abort command
- 2b985467371a58ae44d76c7ba12b0951fee6ed98 usb: xhci: fix possible wild pointer
- 28bedb5ae463b9f7e5195cbc93f1795e374bdef8 usb: return error code when platform_get_irq fails
- 90797aee5d6902b49a453c97d83c326408aeb5a8 usb: xhci: fix return value of xhci_setup_device()
- ee8665e28e8d90ce69d4abe5a469c14a8707ae0e xhci: free xhci virtual devices with leaf nodes first
- c2931667c83ded6504b3857e99cc45b21fa496fb Btrfs: adjust outstanding_extents counter properly when dio write is split
- e7c9a3d9e432200fd4c17855c2c23ac784d6e833 staging: octeon: Call SET_NETDEV_DEV()
- 3b48ab2248e61408910e792fe84d6ec466084c1a drop_monitor: consider inserted data in genlmsg_end
- 096de2f83ebc8e0404c5b7e847a4abd27b9739da benet: stricter vxlan offloading check in be_features_check
- 5350d54f6cd12eaff623e890744c79b700bd3f17 ipv4: Do not allow MAIN to be alias for new LOCAL w/ custom rules
- 515028fe29d84a15f77d071a13b2d34eb3d137af net: macb: Updated resource allocation function calls to new version of API.
- a2962b08f414555db46146f207ba9184dc28437f Merge branch dwmac-oxnas-leaks
- a8de4d719dfc12bc22192d7daef7c7ae6cfb8b80 net: stmmac: dwmac-oxnas: use generic pm implementation
- 6b4c212b95ce6a586473a772fb2d28ab22a38f0e net: stmmac: dwmac-oxnas: fix fixed-link-phydev leaks
- 8f87e626b059f1b82b017f53c5ee91fbc4486e36 net: stmmac: dwmac-oxnas: fix of-node leak
- 781feef7e6befafd4d9787d1f7ada1f9ccd504e4 Btrfs: fix lockdep warning about log_mutex
- e321f8a801d7b4c40da8005257b05b9c2b51b072 Btrfs: use down_read_nested to make lockdep silent
- d0280996437081dd12ed1e982ac8aeaa62835ec4 btrfs: fix locking when we put back a delayed ref thats too new
- aa7c8da35d1905d80e840d075f07d26ec90144b5 btrfs: fix error handling when run_delayed_extent_op fails
- 60437ac02f398e0ee0927748d4798dd5534ac90d perf record: Fix --switch-output documentation and comment
- efd21307119d5a23ac83ae8fd5a39a5c7aeb8493 perf record: Make __record_options static
- b66fb1da5a8cac3f5c3cdbe41937c91efc4e76a4 tools lib subcmd: Add OPT_STRING_OPTARG_SET option
- f9751a60f17eb09e1d1bd036daaddc3ea3a8bed6 xen: events: Replace BUG() with BUG_ON()
- 8d6bbff67796262b5296b745989e4c9d9f2b4894 Merge tag fixes-for-v4.10-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/balbi/usb into usb-linus
- 43aef5c2ca90535b3227e97e71604291875444ed usb: gadget: Fix copy/pasted error message
- 9418ee15f718939aa7e650fd586d73765eb21f20 usb: dwc3: gadget: Fix full speed mode
- 8043d25b3c0fa0a8f531333707f682f03b6febdb mtd: nand: tango: Reset pbus to raw mode in probe
- 6b7e95d1336b9eb0d4c6db190ce756480496bd13 ALSA: firewire-lib: change structure member with proper type
- 6a2a2f45560a9cb7bc49820883b042e44f83726c ALSA: firewire-tascam: Fix to handle error from initialization of stream data
- e2eb31d72156c58b717396383496a7c93aa01b75 ALSA: fireworks: fix asymmetric API call at unit removal
- 2471eb5fb6e1433e28426ece235e3730348019ec drm/i915: Prevent timeline updates whilst performing reset
- 64d1461ce0c3b8ecc1c6b61f4ad1c1d10ce971a3 drm/i915: Silence allocation failure during sg_trim()
- c3f923b5545306570eff00d11ca051bd67699a23 drm/i915: Dont clflush before release phys object
- 9169757ae67bc927750ae907624e65cc15b4fe5a drm/i915: Fix oops in overlay due to frontbuffer tracking
- b72eb5ffa6d8601d9ba72619d75fb5b27723743a drm/i915: Fix oopses in the overlay code due to i915_gem_active stuff
- a6d3e7d35d088b2aabad1688b740e17bfdf566c5 drm/i915: Initialize overlay->last_flip properly
- 00b2b7288299a8c73c0c37b531a075ba5c849e67 drm/i915: Move the min_pixclk[] handling to the end of readout
- 8581f1b5ee0837e55197f036406bc99746ac94b2 drm/i915: Force VDD off on the new power seqeuencer before starting to use it
- dcafc45dcb6d8bb6d159ed0a903bd0f3de597fac drm/meson: Fix plane atomic check when no crtc for the plane
- 7165b8ad36f8bda42a5a8aa059b9a5071acc2210 mtd: nand: tango: Update DT binding description
- 5c9e6c2b2ba3ec3a442e2fb5b4286498f8b4dcb7 dmaengine: pl330: Fix runtime PM support for terminated transfers
- f53243b563e8966fb5a5cd8f27d48b832d3b1c43 MAINTAINERS: dmaengine: Update + Hand over the at_hdmac driver to Ludovic
- 836c3ce2566fb8c1754f8d7c9534cad9bc8a6879 dmaengine: omap-dma: Fix dynamic lch_map allocation
- 116dad7d4339d0965169df8a864fc829f684794d ARM: dts: imx6: Disable weim node in the dtsi files
- c8b4ec8351d21da3299b045b37920e5cf5590793 Merge tag fscrypt-for-stable of git://git.kernel.org/pub/scm/linux/kernel/git/tytso/fscrypt
- 32dd7731699765f21dbe6df9020e613d4ed73fc3 PM / devfreq: exynos-bus: Fix the wrong return value
- 73613b16cb5c5d5a659fc8832eff99eead3f9afb PM / devfreq: Fix the bug of devfreq_add_device when governor is NULL
- 9932ef3ca7f481af59d85cec6023fc7ff1588f04 MAINTAINERS: Add myself as reviewer for DEVFREQ subsystem support
- 6e092c8c04632dde947208f95537ec6eaaa89d8a PM / docs: Drop confusing kernel-doc references from infrastructure.rst
- c2a6bbaf0c5f90463a7011a295bbdb7e33c80b51 ACPI / scan: Prefer devices without _HID/_CID for _ADR matching
- 4e5da369df64628358e25ffedcf80ac43af3793d Documentation/networking: fix typo in mpls-sysctl
- da2875673660c114dc7d65edcd1f97023d0ed624 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/jikos/hid
- 3ef01c968fbfb21c2f16281445d30a865ee4412c ARM: s3c2410_defconfig: Fix invalid values for NF_CT_PROTO_*
- e9572fdd13e299cfba03abbfd2786c84ac055249 hwmon: (lm90) fix temp1_max_alarm attribute
- 7ababb782690e03b78657e27bd051e20163af2d6 igmp: Make igmp group member RFC 3376 compliant
- d0af683407a26a4437d8fa6e283ea201f2ae8146 flow_dissector: Update pptp handling to avoid null pointer deref.
- 94ba998b63c41e92da1b2f0cd8679e038181ef48 Merge tag mac80211-for-davem-2017-01-02 of git://git.kernel.org/pub/scm/linux/kernel/git/jberg/mac80211
- 1f2ed153b916c95a49a1ca9d7107738664224b7f perf probe: Fix to get correct modname from elf header
- 74e5c265a4955d6a01adc40783346b716271170b Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/s390/linux
- b4a9eb4cd5966c8aad3d007d206a2cbda97d6928 parisc: Add line-break when printing segfault info
- 71a332e5603e000b907e66d172eae0e7a8c2c653 Merge tag openrisc-for-linus of git://github.com/openrisc/linux
- 9eca53508a157c6b6fdb6e06796902cf8a920d29 block: Avoid that sparse complains about context imbalance in __wbt_wait()
- 542b9f0759ed74ca0f1a9f3ff090c95ea73eba91 ARM: dts: qcom: apq8064: Add missing scm clock
- f2e0a0b292682dd94274d6793d76656b41526147 block: Make wbt_wait() definition consistent with declaration
- 6c006a9d94bfb5cbcc5150e8fd7f45d3f92f3ee8 clean_bdev_aliases: Prevent cleaning blocks that are not in block range
- 890b73af6b008a7d59bdbab2dd59bd7b212dbc60 Merge tag iio-fixes-for-4.10a of git://git.kernel.org/pub/scm/linux/kernel/git/jic23/iio into staging-linus
- c415f9e8304a1d235ef118d912f374ee2e46c45d ARM64: zynqmp: Fix i2c nodes compatible string
- 4ea2a6be9565455f152c12f80222af1582ede0c7 ARM64: zynqmp: Fix W=1 dtc 1.4 warnings
- 143fca77cce906d35f7a60ccef648e888df589f2 HID: sensor-hub: Move the memset to sensor_hub_get_feature()
- 8aa2cc7e747881d1fd52db28261b201d4e3e5565 HID: usbhid: Add quirk for Mayflash/Dragonrise DolphinBar.
- f83f90cf7ba68deb09406ea9da80852a64c4db29 HID: usbhid: Add quirk for the Futaba TOSD-5711BB VFD
- d1df1e01af1d7c91e48204b9eb8b9f20cdb90700 ARM: davinci: da8xx: Fix sleeping function called from invalid context
- 48cd30b49527f04078ef7de217cc188157f76ba6 ARM: davinci: Make __clk_{enable,disable} functions public
- 35f432a03e41d3bf08c51ede917f94e2288fbe8c mac80211: initialize fast-xmit info later
- 427157631648c980e8bba4d73a21508b9e1a47ec USB: serial: f81534: detect errors from f81534_logic_to_phy_port()
- ef37427ac5677331145ab27a17e6f5f1b43f0c11 ARM: davinci: da850: dont add emac clock to lookup table twice
- 5d45b011c14a791ef23555a59ff7a3e6d213530f ARM: davinci: da850: fix infinite loop in clk_set_rate()
- f0fcdc506b76e924c60fa607bba5872ca4745476 mtd: nand: oxnas_nand: fix build errors on arch/um, require HAS_IOMEM
- 7b01738112608ce47083178ae2b9ebadf02d32cc usb: gadget: udc: core: fix return code of usb_gadget_probe_driver()
- 8f8983a5683623b62b339d159573f95a1fce44f3 usb: dwc3: pci: add Intel Gemini Lake PCI ID
- 86e881e7d769f40bd5ed08677e503bc15d89dec6 usb: dwc2: fix flags for DMA descriptor allocation in dwc2_hsotg_ep_enable
- 0eae2fde164caaa013a3f7341fd3e7e36e8e2865 usb: dwc3: pci: Add linux,sysdev_is_parent property
- 12a7f17fac5b370bec87259e4c718faf563ce900 usb: dwc3: omap: fix race of pm runtime with irq handler in probe
- 890e6c236dcda6d45c5f0bdd23665636376f6831 USB: gadgetfs: remove unnecessary assignment
- 1c069b057dcf64fada952eaa868d35f02bb0cfc2 USB: gadgetfs: fix checks of wTotalLength in config descriptors
- add333a81a16abbd4f106266a2553677a165725f USB: gadgetfs: fix use-after-free bug
- faab50984fe6636e616c7cc3d30308ba391d36fd USB: gadgetfs: fix unbounded memory allocation bug
- b3ce3ce02d146841af012d08506b4071db8ffde3 usb: gadget: f_fs: Fix possibe deadlock
- d7fd41c6dbcc547578a8a56cc52d6f2d36e505bc usb: dwc3: skip interrupt when ep disabled
- 0994b0a257557e18ee8f0b7c5f0f73fe2b54eec1 usb: gadgetfs: restrict upper bound on device configuration size
- bcdbeb844773333d2d1c08004f3b3e25921040e5 USB: dummy-hcd: fix bug in stop_activity (handle ep0)
- 354bc45bf329494ef6051f3229ef50b9e2a7ea2a usb: gadget: f_fs: Fix ExtCompat descriptor validation
- 96a420d2d37cc019d0fbb95c9f0e965fa1080e1f usb: gadget: f_fs: Document eventfd effect on descriptor format.
- 7e4da3fcf7c9fe042f2f7cb7bf23861a899b4a8f usb: gadget: composite: Test get_alt() presence instead of set_alt()
- 51c1685d956221576e165dd88a20063b169bae5a usb: dwc3: pci: Fix dr_mode misspelling
- e71d363d9c611c99fb78f53bfee99616e7fe352c usb: dwc3: core: avoid Overflow events
- d62145929992f331fdde924d5963ab49588ccc7d usb: dwc3: gadget: always unmap EP0 requests
- 19ec31230eb3084431bc2e565fd085f79f564274 usb: dwc3: ep0: explicitly call dwc3_ep0_prepare_one_trb()
- 7931ec86c1b738e4e90e58c6d95e5f720d45ee56 usb: dwc3: ep0: add dwc3_ep0_prepare_one_trb()
- efc95b2ca42424de222119a3a260624f3a050f8e usb: dwc2: gadget: fix default value for gadget-dma-desc
- 6118d0647b10eaca06b278dee2022602d8f2f07a usb: dwc2: fix default value for DMA support
- de02238d6a7982a71682fe8da2996993a5a5eee7 usb: dwc2: fix dwc2_get_device_property for u8 and u16
- f3419735279564d40467ebe4147d8a41cef00685 usb: dwc2: Do not set host parameter in peripheral mode
- a2724663494f7313f53da10d8c0a729c5e3c4dea mtd: nand: xway: fix build because of module functions
- 73529c872a189c747bdb528ce9b85b67b0e28dec mtd: nand: xway: disable module support
- d7da1ccfa2c26d54230ee6aae28902dd10b325a7 ARM: i.MX: remove map_io callback
- 4c51de4570d6881e2a4a7f56d55385336de0bd51 ARM: dts: vf610-zii-dev-rev-b: Add missing newline
- db9e188674ec53fe7bf7d9322ffb0256974c8ec7 ARM: dts: imx6qdl-nitrogen6x: remove duplicate iomux entry
- af92305e567b7f4c9cf48b9e46c1f48ec9ffb1fb ARM: dts: imx31: fix AVIC base address
- 75bdc7f31a3a6e9a12e218b31a44a1f54a91554c dmaengine: ti-dma-crossbar: Add some of_node_put() in error path.
- 57b5a32135c813f2ab669039fb4ec16b30cb3305 dmaengine: stm32-dma: Fix null pointer dereference in stm32_dma_tx_status
- 7e96304d99477de1f70db42035071e56439da817 dmaengine: stm32-dma: Set correct args number for DMA request from DT
- eb7903bb83cc1db31a9124d4cc8a1bddebe26e33 Merge branch l2tp-socket-lookup-fixes
- a9b2dff80be979432484afaf7f8d8e73f9e8838a l2tp: take remote address into account in l2tp_ip and l2tp_ip6 socket lookups
- 97b84fd6d91766ea57dcc350d78f42639e011c30 l2tp: consider :: as wildcard address in l2tp_ip6 socket lookup
- 4200462d88f47f3759bdf4705f87e207b0f5b2e4 drop_monitor: add missing call to genlmsg_end
- 1032471b3ec823bce7687034ac5af78a8ac99a9c dmaengine: dw: fix typo in Kconfig
- 34a31f0af84158955a9747fb5c6712da5bbb5331 dmaengine: ioatdma: workaround SKX ioatdma version
- 1594c18fd297a8edcc72bc4b161f3f52603ebb92 dmaengine: ioatdma: Add Skylake PCI Dev ID
- 086cc1c31a0ec075dac02425367c871bb65bc2c9 openrisc: Add _text symbol to fix ksym build error
- 0c744ea4f77d72b3dcebb7a8f2684633ec79be88 Linux 4.10-rc2
- 4759d386d55fef452d692bf101167914437e848e Merge branch libnvdimm-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/nvdimm/nvdimm
- e1a3a60a2ebe991605acb14cd58e39c0545e174e net: socket: dont set sk_uid to garbage value in ->setattr()
- ab51e6ba0059f92036a08e41ba5cc70e77ce02df PM / domains: Fix may be used uninitialized build warning
- 111b8b3fe4fae35d4a85e9f524b077f5c4951e65 cpufreq: intel_pstate: Always keep all limits settings in sync
- cad30467963267509d5b0d7d3c9bd1af3b91e720 cpufreq: intel_pstate: Use locking in intel_cpufreq_verify_policy()
- aa439248ab71bcd2d26a01708dead4dd56616499 cpufreq: intel_pstate: Use locking in intel_pstate_resume()
- a1792cda51300e15b03549cccf0b09f3be82e697 ASoC: nau8825: fix invalid configuration in Pre-Scalar of FLL
- a33b56a6a824fa5cd89c74f85cbeb9af1dcef87e ASoC: nau8825: correct the function name of register
- 91ce54978ccece323aa6df930249ff84a7d233c7 ASoC: Intel: Skylake: Fix to fail safely if module not available in path
- 13288bdf4adbaa6bd1267f10044c1bc25d90ce7f spi: dw: Make debugfs name unique between instances
- 63c3194b82530bd71fd49db84eb7ab656b8d404a ASoC: tlv320aic3x: Mark the RESET register as volatile
- d2e3a1358c37cd82eef92b5e908b4f0472194481 ASoC: Fix binding and probing of auxiliary components
- 65e4345c8ef8811bbb4860fe5f2df10646b7f2e1 iio: accel: st_accel: fix LIS3LV02 reading and scaling
- 65c8aea07de11b6507efa175edb44bd8b4488218 iio: common: st_sensors: fix channel data parsing
- 42d97eb0ade31e1bc537d086842f5d6e766d9d51 fscrypt: fix renaming and linking special files
- b4e8a0eb718749455601fa7b283febc42cca8957 iio: max44000: correct value in illuminance_integration_time_available
- 1a38de880992764d4bd5bccbd306b87d860e377d ARM: dts: am572x-idk: Add gpios property to control PCIE_RESETn
- 238d1d0f79f619d75c2cc741d6770fb0986aef24 Merge tag docs-4.10-rc1-fix of git://git.lwn.net/linux
- f3de082c12e5e9ff43c58a7561f6ec3272d03a48 Merge branch linus of git://git.kernel.org/pub/scm/linux/kernel/git/herbert/crypto-2.6
- 14221cc45caad2fcab3a8543234bb7eda9b540d5 bridge: netfilter: Fix dropping packets that moving through bridge interface
- b1448ea9cd95868e3e91313b643818d18917b382 iio: adc: TI_AM335X_ADC should depend on HAS_DMA
- 1dff32d7df7ff5d80194ebce7ab5755b32564e13 arm64: dts: vexpress: Support GICC_DIR operations
- 45e869714489431625c569d21fc952428d761476 vfio-pci: use 32-bit comparisons for register address for gcc-4.5
- 99e3123e3d72616a829dad6d25aa005ef1ef9b13 vfio-mdev: Make mdev_device private and abstract interfaces
- 9372e6feaafb65d88f667ffb5b7b425f8568344f vfio-mdev: Make mdev_parent private
- 42930553a7c11f06351bc08b889808d0f6020f08 vfio-mdev: de-polute the namespace, rename parent_device & parent_ops
- 49550787a90b5bfa44d8dc424d11824dbe21473d vfio-mdev: Fix remove race
- 6c38c055cc4c0a5da31873d173b2de3085f43f33 vfio/type1: Restore mapping performance with mdev support
- 08c1a4ef7cccd5632526be923c5b6eaca59d8b01 vfio-mdev: Fix mtty sample driver building
- 368400e242dc04963ca5ff0b70654f1470344a0a ARM: dts: vexpress: Support GICC_DIR operations
- a766347b15c01507db9bf01f9b7021be5a776691 firmware: arm_scpi: fix reading sensor values on pre-1.0 SCPI firmwares
- 60f59ce0278557f7896d5158ae6d12a4855a72cc rtlwifi: rtl_usb: Fix missing entry in USB drivers private data
- 1259feddd0f83649d5c48d730c140b4f7f3fa288 pinctrl: samsung: Fix the width of PINCFG_TYPE_DRV bitfields for Exynos5433
- 570b90fa230b8021f51a67fab2245fe8df6fe37d orinoco: Use shash instead of ahash for MIC calculations
- a0c10687ec9506b5e14fe3dd47832a77f2f2500c Revert remoteproc: Merge table_ptr and cached_table pointers
- c81c0e0710f031cb09eb7cbf0e75e6754d1d8346 remoteproc: fix vdev reference management
- 63447646ac657fde00bb658ce21a3431940ae0ad rpmsg: virtio_rpmsg_bus: fix channel creation
- 01d1f7a99e457952aa51849ed7c1cc4ced7bca4b iio: bmi160: Fix time needed to sleep after command execution
- 07825f0acd85dd8b7481d5ef0eb024b05364d892 crypto: aesni - Fix failure when built-in with modular pcbc
- 5018ada69a04c8ac21d74bd682fceb8e42dc0f96 gpio: Move freeing of GPIO hogs before numbing of the device
- abc8d5832fd142d565fbfca163348f33b08bc1fe gpio: mxs: remove __init annotation
- f5a0aab84b74de68523599817569c057c7ac1622 net: ipv4: dst for local input routes should use l3mdev if relevant
- 2344ef3c86a7fe41f97bf66c7936001b6132860b sh_eth: fix branch prediction in sh_eth_interrupt()
- 98473f9f3f9bd404873cd1178c8be7d6d619f0d1 mm/filemap: fix parameters to test_bit()
- 1fe0a7e0bc52024a445945c9e7691551aba97390 parisc: Drop TIF_RESTORE_SIGMASK and switch to generic code
- 41744213602a206f24adcb4a2b7551db3c700e72 parisc: Mark cr16 clocksource unstable on SMP systems
- f24d311f92b516a8aadef5056424ccabb4068e7b pinctrl: meson: fix gpio request disabling other modes
- 2983f296f2327bc517e3b29344fce82271160197 pinctrl/amd: Set the level based on ACPI tables
- a6cb3b864b21b7345f824a4faa12b723c8aaf099 drm/msm: Verify that MSM_SUBMIT_BO_FLAGS are set
- 6490abc4bc35fa4f3bdb9c7e49096943c50e29ea drm/msm: Put back the vaddr in submit_reloc()
- 88b333b0ed790f9433ff542b163bf972953b74d3 drm/msm: Ensure that the hardware write pointer is valid
- e400b7977e7c014bc0c298b2d834311770a777ac Merge branch mlx4-misc-fixes
- 10b1c04e92229ebeb38ccd0dcf2b6d3ec73c0575 net/mlx4_core: Fix raw qp flow steering rules under SRIOV
- 61b6034c6cfdcb265bb453505c3d688e7567727a net/mlx4_en: Fix type mismatch for 32-bit systems
- c1d5f8ff80ea84768f5fae1ca9d1abfbb5e6bbaa net/mlx4: Remove BUG_ON from ICM allocation routine
- 6496bbf0ec481966ef9ffe5b6660d8d1b55c60cc net/mlx4_en: Fix bad WQE issue
- 3b01fe7f91c8e4f9afc4fae3c5af72c14958d2d8 net/mlx4_core: Use-after-free causes a resource leak in flow-steering detach
- f0c16ba8933ed217c2688b277410b2a37ba81591 net: fix incorrect original ingress device index in PKTINFO
- 4775cc1f2d5abca894ac32774eefc22c45347d1c rtnl: stats - add missing netlink message size checks
- b91e1302ad9b80c174a4855533f7e3aa2873355e mm: optimize PageWaiters bit use for unlock_page()
- 72f0991354b24b9860ddc57b12d5c39bd8e3c962 Merge branch synaptics-rmi4 into for-linus
- b2eb09af7370fedc6b9d9f05762f01625438467a net: stmmac: Fix error path after register_netdev move
- e4c5e13aa45c23692e4acf56f0b3533f328199b2 ipv6: Should use consistent conditional judgement for ip6 fragment between __ip6_append_data and ip6_finish_output
- e9112936f240856c925321fd2bd91adc7c00399c arm64: dts: msm8996: Add required memory carveouts
- 60133867f1f111aaf3a8c00375b8026142a9a591 net: wan: slic_ds26522: fix spelling mistake: configurated -> configured
- 9dd0f896d2cc5815d859e945db90915071cd44b3 net: atm: Fix warnings in net/atm/lec.c when !CONFIG_PROC_FS
- 4b52416a3f15df80af46d97d41f32ef5dde6e5fb Merge branch mlx5-fixes
- 37f304d10030bb425c19099e7b955d9c3ec4cba3 net/mlx5e: Disable netdev after close
- 610e89e05c3f28a7394935aa6b91f99548c4fd3c net/mlx5e: Dont sync netdev state when not registered
- 4525a45bfad55a00ef218c5fbe5d98a3d8170bf5 net/mlx5e: Check ets capability before initializing ets settings
- 1efbd205b3cc5882a8c386c58a57134044e9d5ba Revert net/mlx5: Add MPCNT register infrastructure
- 465db5dab86d6688fa5132edd1237102f4a20e84 Revert net/mlx5e: Expose PCIe statistics to ethtool
- ccce1700263d8b5b219359d04180492a726cea16 net/mlx5: Prevent setting multicast macs for VFs
- 9b8c514291a83e53c073b473bdca6267f17a02c2 net/mlx5: Release FTE lock in error flow
- 077b1e8069b9b74477b01d28f6b83774dc19a142 net/mlx5: Mask destination mac value in ethtool steering rules
- d151d73dcc99de87c63bdefebcc4cb69de1cdc40 net/mlx5: Avoid shadowing numa_node
- 689a248df83b6032edc57e86267b4e5cc8d7174e net/mlx5: Cancel recovery work in remove flow
- 883371c453b937f9eb581fb4915210865982736f net/mlx5: Check FW limitations on log_max_qp before setting it
- 9da34cd34e85aacc55af8774b81b1f23e86014f9 net/mlx5: Disable RoCE on the e-switch management port under switchdev mode
- 0df0f207aab4f42e5c96a807adf9a6845b69e984 net/sched: cls_flower: Fix missing addr_type in classify
- 6f96d639915f9f2bc43b538aedd4bffacd24ceeb MAINTAINERS: Add Patchwork URL to Samsung Exynos entry
- b6f4c66704b875aba9b8c912532323e3cc89824c samples/bpf trace_output_user: Remove duplicate sys/ioctl.h include
- a608a9d52fa4168efd478d684039ed545a69dbcd platform/x86: fujitsu-laptop: use brightness_set_blocking for LED-setting callbacks
- f6c5c1f96d976e1fb9d71fb824629c450ee0a122 platform/x86: fix surface3_button build errors
- abfb7b686a3e5be27bf81db62f9c5c895b76f5d1 efi/libstub/arm*: Pass latest memory map to the kernel
- 5701659004d68085182d2fd4199c79172165fa65 net: stmmac: Fix race between stmmac_drv_probe and stmmac_open
- 2d706e790f0508dff4fb72eca9b4892b79757feb Merge branch linus of git://git.kernel.org/pub/scm/linux/kernel/git/herbert/crypto-2.6
- ee12996c9d392ec61241ab6c74d257bc2122e0bc samples/bpf sock_example: Avoid getting ethhdr from two includes
- 9396c9cb0d9534ca67bda8a34b2413a2ca1c67e9 perf sched timehist: Show total scheduling time
- fe4f6c801c03bc13113d0dc32f02d4ea8ed89ffd fscrypt: fix the test_dummy_encryption mount option
- 8f18e4d03ed8fa5e4a300c94550533bd8ce4ff9a Merge git://git.kernel.org/pub/scm/linux/kernel/git/davem/net
- d7ddad0acc4add42567f7879b116a0b9eea31860 Input: synaptics-rmi4 - fix F03 build error when serio is module
- b6fc513da50c5dbc457a8ad6b58b046a6a68fd9d Input: xpad - use correct product id for x360w controllers
- 36f671be1db1b17d3d4ab0c8b47f81ccb1efcb75 Documentation/unaligned-memory-access.txt: fix incorrect comparison operator
- 66115335fbb411365c23349b2fbe7e041eabbaf2 docs: Fix build failure
- 54ab6db0909061ab7ee07233d3cab86d29f86e6c Merge tag v4.10-rc1 into docs-next
- 74de7126fc53fff311c5e213f896a56dbabc9149 Merge branch omap-for-v4.10/legacy into omap-for-v4.10/fixes
- 9a6b6f75d9daa892ae8f6e5ed6ae0ab49b9586cb ARM: OMAP2+: PRM: Delete an error message for a failed memory allocation
- 4cf48f1d7520a4d325af58eded4d8090e1b40be7 ARM: dts: n900: Mark eMMC slot with no-sdio and no-sd flags
- 1a177cf72b3a6226f01652df8292d07edf67e7af ARM: dts: dra72-evm-tps65917: Add voltage supplies to usb_phy, mmc, dss
- 5acd016c88937be3667ba4e6b60f0f74455b5e80 ARM: dts: am57xx-idk: Put USB2 port in peripheral mode
- 10d27dfaf6b6ce3bd7598b1e20e58446c5697a50 ARM: dts: am57xx-idk: Support VBUS detection on USB2 port
- 820381572fc015baa4f5744f5d4583ec0c0f1b82 dt-bindings: input: Specify the interrupt number of TPS65217 power button
- 81d7358d7038dd1001547950087e5b0641732f3f dt-bindings: power/supply: Update TPS65217 properties
- be53e38f0df21c3d45cdf4cede37ee73554cdbb8 dt-bindings: mfd: Remove TPS65217 interrupts
- 30aa2e48962c6e4cd5258840f55f2f413b0bdbb4 ARM: dts: am335x: Fix the interrupt name of TPS65217
- 5066d5296ff2db20625e5f46e7338872c90c649f ARM: omap2+: fixing wrong strcat for Non-NULL terminated string
- f86a2c875fd146d9b82c8fdd86d31084507bcf4c ARM: omap2+: am437x: rollback to use omap3_gptimer_timer_init()
- 7245f67f86e847769f41dacad26bb8f5b5d74bf4 ARM: dts: omap3: Add DTS for Logic PD SOM-LV 37xx Dev Kit
- 7f6c857b12911ed56b2056f9d5491e16b5fc95ea ARM: dts: dra7: Add an empty chosen node to top level DTSI
- 6ed80b3a232e61da6d0189bbbe2b2b9afaefe3b3 ARM: dts: dm816x: Add an empty chosen node to top level DTSI
- 9536fd30d41ae4f30d04762676e5f5f602e16aa8 ARM: dts: dm814x: Add an empty chosen node to top level DTSI
- 5799fc905930f866c7d32aaf81b31f8027297506 net: stmmac: fix incorrect bit set in gmac4 mdio addr register
- 610c908773d30907c950ca3b2ee8ac4b2813537b r8169: add support for RTL8168 series add-on card.
- be26727772cd86979255dfaf1eea967338dc0c9b net: xdp: remove unused bfp_warn_invalid_xdp_buffer()
- df30f7408b187929dbde72661c7f7c615268f1d0 openvswitch: upcall: Fix vlan handling.
- 56ab6b93007e5000a8812985aec1833c4a6a9ce0 ipv4: Namespaceify tcp_tw_reuse knob
- ce95077d0cdfcc8e40dea10a1680249831ccec77 ARM: dts: am4372: Add an empty chosen node to top level DTSI
- 1d8d6d3f2f7d553c479f24ab93767974a8c2dfad ARM: dts: am33xx: Add an empty chosen node to top level DTSI
- c9faa84cb9c34852ad70cb175457ae21fc06f39b ARM: dts: omap5: Add an empty chosen node to top level DTSI
- 6c565d1a63ce241a0100f5d327c48dde87b4df76 ARM: dts: omap4: Add an empty chosen node to top level DTSI
- 23ab4c6183ac0679d80888b5c4cc1d528fcc21c2 ARM: dts: omap3: Add an empty chosen node to top level DTSI
- 3d37d41a148c32389ed360e10a9f8a7cd37ce166 ARM: dts: omap2: Add an empty chosen node to top level DTSI
- ade4d4410f8b8816a8e9d85bfdb4bdcc9464065a Merge tag gvt-fixes-2016-12-26 of https://github.com/01org/gvt-linux into drm-intel-fixes
- 7e164ce4e8ecd7e9a58a83750bd3ee03125df154 perf/x86/amd/ibs: Fix typo after cleanup state names in cpu/hotplug
- 02608e02fbec04fccf2eb0cc8d8082f65c0a4286 crypto: testmgr - Use heap buffer for acomp test input
- db27edf80c894e89b9710d20a8d0f02327f36ca0 Merge remote-tracking branch mkp-scsi/4.10/scsi-fixes into fixes
- 1db175428ee374489448361213e9c3b749d14900 ext4: Simplify DAX fault path
- 9f141d6ef6258a3a37a045842d9ba7e68f368956 dax: Call ->iomap_begin without entry lock during dax fault
- f449b936f1aff7696b24a338f493d5cee8d48d55 dax: Finish fault completely when loading holes
- e3fce68cdbed297d927e993b3ea7b8b1cee545da dax: Avoid page invalidation races and unnecessary radix tree traversals
- c6dcf52c23d2d3fb5235cec42d7dd3f786b87d55 mm: Invalidate DAX radix tree entries only if appropriate
- e568df6b84ff05a22467503afc11bee7a6ba0700 ext2: Return BH_New buffers for zeroed blocks
- 366430b5c2f61a75d45b9fc00886ffff12f395ab cpufreq: intel_pstate: Do not expose PID parameters in passive mode
- 0dad3a3014a0b9e72521ff44f17e0054f43dcdea x86/mce/AMD: Make the init code more robust
- b9d9d6911bd5c370ad4b3aa57d758c093d17aed5 smp/hotplug: Undo tglxs brainfart
- c6e2c1e1138fa5cb5bb99381132855bbaf712029 ACPI / watchdog: Print out error number when device creation fails
- 9c4aa1eecb48cfac18ed5e3aca9d9ae58fbafc11 ACPI / sysfs: Provide quirk mechanism to prevent GPE flooding
- 709f94ff018a4403d0bb32643254058d5d9cfa24 ACPI: Drop misplaced acpi_dma_deconfigure() call from acpi_bind_one()
- b4b8664d291ac1998e0f0bcdc96b6397f0fe68b3 arm64: dont pull uaccess.h into *.S
- e6afb1ad88feddf2347ea779cfaf4d03d3cd40b6 net: korina: Fix NAPI versus resources freeing
- 628185cfddf1dfb701c4efe2cfd72cf5b09f5702 net, sched: fix soft lockup in tc_classify
- 0e0694ff1a7791274946b7f51bae692da0001a08 Merge branch patchwork into v4l_for_linus
- 4e0203ba11e735694600d7c704d7d56f069f9eb6 drm/i915/gvt: fix typo in cfg_space range check
- 34700631bd465de3e555e5964f36a0919c466aa8 drm/i915/gvt: fix an issue in emulating cfg space PCI_COMMAND
- 8ff842fd9eab69f8cf99fdd21ce25a5a0411473e drm/i915/gvt/kvmgt: trival: code cleanup
- 364fb6b789ffce44c1b5429086c47b0df6c36aff drm/i915/gvt/kvmgt: prevent double-release of vgpu
- faaaa53bdc6750c438887d44f99b60ad97ec74b4 drm/i915/gvt/kvmgt: check returned slot for gfn
- bfeca3e5716a16b95a1fb7104e477ca3bd5ed59e drm/i915/gvt/kvmgt: dereference the pointer within lock
- d650ac06023796ade7cb5ec4d5650c67dc494ed0 drm/i915/gvt: reset the GGTT entry when vGPU created
- b8395cc7a454efc616e335c22af22d8513abdafc drm/i915/gvt: fix an error in opregion handling
- 7ce7d89f48834cefece7804d38fc5d85382edf77 Linux 4.10-rc1
- 8ae679c4bc2ea2d16d92620da8e3e9332fa4039f powerpc: Fix build warning on 32-bit PPC
- d33d5a6c88fcd53fec329a1521010f1bc55fa191 avoid spurious may be used uninitialized warning
- 3ddc76dfc786cc6f87852693227fb0b1f124f807 Merge branch timers-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- b272f732f888d4cf43c943a40c9aaa836f9b7431 Merge branch smp-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 10bbe7599e2755d3f3e100103967788b8b5a4bce Merge branch turbostat of git://git.kernel.org/pub/scm/linux/kernel/git/lenb/linux
- 62906027091f1d02de44041524f0769f60bb9cf3 mm: add PageWaiters indicating tasks are waiting for a page bit
- 6326fec1122cde256bd2a8c63f2606e08e44ce1d mm: Use owner_priv bit for PageSwapCache, valid when PageSwapBacked
- 1f3a8e49d8f28f498b8694464623ac20aebfe62a ktime: Get rid of ktime_equal()
- 8b0e195314fabd58a331c4f7b6db75a1565535d7 ktime: Cleanup ktime_set() usage
- 2456e855354415bfaeb7badaa14e11b3e02c8466 ktime: Get rid of the union
- a5a1d1c2914b5316924c7893eb683a5420ebd3be clocksource: Use a plain u64 instead of cycle_t
- 008b69e4d52f2cbee3ed0d0502edd78155000b1a irqchip/armada-xp: Consolidate hotplug state space
- 6896bcd198df04777820cab4acc70142e87d5ce0 irqchip/gic: Consolidate hotplug state space
- 36e5b0e39194b09a10f19697fb9ea4ccc44eb166 coresight/etm3/4x: Consolidate hotplug state space
- 73c1b41e63f040e92669e61a02c7893933bfe743 cpu/hotplug: Cleanup state names
- 530e9b76ae8f863dfdef4a6ad0b38613d32e8c3f cpu/hotplug: Remove obsolete cpu hotplug register/unregister functions
- 7b737965b33188bd3dbb44e938535c4006d97fbb staging/lustre/libcfs: Convert to hotplug state machine
- e210faa2359f92eb2e417cd8462eb980a4dbb172 scsi/bnx2i: Convert to hotplug state machine
- c53b005dd64bdcf5acac00bd55ecf94dda22dc4f scsi/bnx2fc: Convert to hotplug state machine
- dc280d93623927570da279e99393879dbbab39e7 cpu/hotplug: Prevent overwriting of callbacks
- 59fefd0890f12716b39de1d4e5482fd739316262 x86/msr: Remove bogus cleanup from the error path
- 26242b330093fd14c2e94fb6cbdf0f482ab26576 bus: arm-ccn: Prevent hotplug callback leak
- 834fcd298003c10ce450e66960c78893cb1cc4b5 perf/x86/intel/cstate: Prevent hotplug callback leak
- a051f220d6b9bf9367695e2c319ccc3712b631ee ARM/imx/mmcd: Fix broken cpu hotplug handling
- a98d1a0ca6d3fd6197f18749972d4cc21195b724 scsi: qedi: Convert to hotplug state machine
- 6886fee4d7a3afaf905a8e0bec62dc8fdc39878d tools/power turbostat: remove obsolete -M, -m, -C, -c options
- 388e9c8134be6bbc3751ba7072f5fa9bc8ecbe01 tools/power turbostat: Make extensible via the --add parameter
- 7c0f6ba682b9c7632072ffbedf8d328c8f3c42ba Replace <asm/uaccess.h> with <linux/uaccess.h> globally
- 1dd5c6b15372c7c127c509afa9a816bad5feed3b Merge branch for-next of git://git.samba.org/sfrench/cifs-2.6
- 3a77fa854477a12fc543a69d00ff8a42adefc586 Merge tag watchdog-for-linus-v4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/groeck/linux-staging
- 01e0d6037de687fd3bb8b45ab1376e8322c1fcc9 Merge tag ntb-4.10 of git://github.com/jonmason/ntb
- 6ef4e07ecd2db21025c446327ecf34414366498b KVM: x86: reset MMU on KVM_SET_VCPU_EVENTS
- 6ac3bb167fed0b3d02b4fd3daa0d819841d5f6f4 Merge branch x86-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- eb3e8d9de28a5385f75e5c42eba5fb5b0c7625be Merge branch timers-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 00198dab3b825ab264424a052beea5acb859754f Merge branch perf-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 9004fda59577d439564d44d6d1db52d262fe3f99 Merge branch irq-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- eb9def61be7197669cab51f43789b53aa7a69509 net/mlx4_en: Fix user prio field in XDP forward
- 693c56491fb720087437a635e6eaf440659b922f tipc: dont send FIN message from connectionless socket
- e252536068efd1578c6e23e7323527c5e6e980bd ipvlan: fix multicast processing
- b1227d019fa98c43381ad8827baf7efbe2923ed1 ipvlan: fix various issues in ipvlan_process_multicast()
- e3ba730702af370563f66cb610b71aa0ca67955e fsnotify: Remove fsnotify_duplicate_mark()
- dfb7d24c5ad5c986f2417f52784738b67cfedd4d ntb_transport: Remove unnecessary call to ntb_peer_spad_read
- 28734e8f69395de4c2aea50fcb74d87720e8537b NTB: Fix request_irq() and free_irq() inconsistancy
- 09e71a6f13445974fe9b70b6d4b68ac362cd68b6 ntb: fix SKX NTB config space size register offsets
- 5c43c52d5fb6163120ae5d9a281c3b757ca6119c NTB: correct ntb_peer_spad_read for case when callback is not supplied.
- bc034e52627a242bcf4343b791cbd263f65cfdcc MAINTAINERS: Change in maintainer for AMD NTB
- b17faba03fc72091f4d040b879def004316952ec ntb_transport: Limit memory windows based on available, scratchpads
- 872deb21038e90903a40ab6a29b9d0652a6ebc8d NTB: Register and offset values fix for memory window
- e5b0d2d1ba92a8e424e7395537a96e8a373d0267 NTB: add support for hotplug feature
- 783dfa6cc41b710b8b0c1979c6100417d0d6c3b2 ntb: Adding Skylake Xeon NTB support
- c280f7736ab26a601932b1ce017a3840dbedcfdc Revert x86/unwind: Detect bad stack return address
- 3705b97505bcbf6440f38119c0e7d6058f585b54 Merge tag perf-urgent-for-mingo-20161222 of git://git.kernel.org/pub/scm/linux/kernel/git/acme/linux into perf/urgent
- 50b17cfb1917b207612327d354e9043dbcbde431 Merge git://git.kernel.org/pub/scm/linux/kernel/git/davem/net
- 61033e089cde41464f820c8c381ce170d89470f0 xen: remove stale xs_input_avail() from header
- 9a6161fe73bdd3ae4a1e18421b0b20cb7141f680 xen: return xenstore command failures via response instead of rc
- 639b08810d6ad74ded2c5f6e233c4fcb9d147168 xen: xenbus driver must not accept invalid transaction ids
- 1636098c46ac52c7fec384fe629144e8e03487b1 sctp: fix recovering from 0 win with small data chunks
- 58b94d88deb9ac913740e7778f2005f3ce6d0443 sctp: do not loose window information if in rwnd_over
- a307d0a0074c18bcbea5dec368c9f047be9dade3 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/viro/vfs
- e57cbe48a6b7a9a05a058aee5336d25407ad1c2c Merge branch virtio-net-xdp-fixes
- bb91accf27335c6dc460e202991ca140fa21e1b5 virtio-net: XDP support for small buffers
- c47a43d3004ad6ff2a94a670cb3274cd6338d41e virtio-net: remove big packet XDP codes
- 92502fe86c7c9b3f8543f29641a3c71805e82757 virtio-net: forbid XDP when VIRTIO_NET_F_GUEST_UFO is support
- 5c33474d41af09f09c98f1df70f267920587bec0 virtio-net: make rx buf size estimation works for XDP
- b00f70b0dacb3d2e009afce860ebc90219072f5c virtio-net: unbreak csumed packets for XDP_PASS
- 1830f8935f3b173d229b86e9927b3b6d599aa1f6 virtio-net: correctly handle XDP_PASS for linearized packets
- 56a86f84b8332afe8c6fcb4b09d09d9bf094e2db virtio-net: fix page miscount during XDP linearizing
- 275be061b33b945cfb120ee8a570f78c3ccafe56 virtio-net: correctly xmit linearized page on XDP_TX
- 73b62bd085f4737679ea9afc7867fa5f99ba7d1b virtio-net: remove the warning before XDP linearizing
- fc26901b12f1deedc351bbe9fd9a018d61485c57 Merge tag befs-v4.10-rc1 of git://github.com/luisbg/linux-befs
- 01302aac12c782bf7cadfd9d902cd382359dca93 Merge tag drm-fixes-for-4.10-rc1 of git://people.freedesktop.org/~airlied/linux
- 296915912d89d1ed2f47472b67fc594b15383d71 Merge tag for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/dledford/rdma
- f290cbacb697b7bc8fc67d3988e330bec0e502ea Merge tag scsi-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/jejb/scsi
- 42e0372c0e7ea3617a4ab28c7f83ce66cb0f868d Merge tag arc-4.10-rc1-part2 of git://git.kernel.org/pub/scm/linux/kernel/git/vgupta/arc
- d3a51d6cbc8a31bf924be1fe116e461138b1cddc Merge branch mlxsw-router-fixes
- 58312125da5806308bd69e075fedae30f8cf7794 mlxsw: spectrum_router: Correctly remove nexthop groups
- 93a87e5e794fb71a51f97fbde6c0010680b62d70 mlxsw: spectrum_router: Dont reflect dead neighs
- 53f800e3baf980827c197a9332f63effe80d4809 neigh: Send netevent after marking neigh as dead
- a98f91758995cb59611e61318dddd8a6956b52c3 ipv6: handle -EFAULT from skb_copy_bits
- 39b2dd765e0711e1efd1d1df089473a8dd93ad48 inet: fix IP(V6)_RECVORIGDSTADDR for udp sockets
- 9aa340a5c36eafa847861336db446886a5ed1962 Merge branch cls_flower-act_tunnel_key-fixes
- d9724772e69cb8076231202292665ca74eec13e1 net/sched: cls_flower: Mandate mask when matching on flags
- dc594ecd4185831031d3fef2853ee76908428107 net/sched: act_tunnel_key: Fix setting UDP dst port in metadata under IPv6
- 567be786597ca24b13906a552ad2159316c6fe7d stmmac: CSR clock configuration fix
- 6c5d5cfbe3c59429e6d6f66477a7609aacf69751 netfilter: ipt_CLUSTERIP: check duplicate config when initializing
- faf0dcebd7b387187f29ff811d47df465ea4c9f9 Merge branch work.namespace into for-linus
- 128394eff343fc6d2f32172f03e24829539c5835 sg_write()/bsg_write() is not fit to be called under KERNEL_DS
- f698cccbc89e33cda4795a375e47daaa3689485e ufs: fix function declaration for ufs_truncate_blocks
- 613cc2b6f272c1a8ad33aefa21cad77af23139f7 fs: exec: apply CLOEXEC before changing dumpable task flags
- e522751d605d99a81508e58390a8f51ee96fb662 seq_file: reset iterator to first record for zero offset
- 22725ce4e4a00fbc37694e25dc5c8acef8ad1c28 vfs: fix isize/pos/len checks for reflink & dedupe
- 33844e665104b169a3a7732bdcddb40e4f82b335 [iov_iter] fix iterate_all_kinds() on empty iterators
- c00d2c7e89880036f288a764599b2b8b87c0a364 move aio compat to fs/aio.c
- 3eff4c782857d284dc3b11c6db0cab4a263427b7 Merge branch misc into for-linus
- bdd75729e5d279d734e8d3fb41ef4818ac1598ab perf sched timehist: Fix invalid period calculation
- 4fa0d1aa2711a5053fb2422331bdf6bce99b5f87 perf sched timehist: Remove hardcoded comm_width check at print_summary
- 9b8087d72086b249ff744cee237ad12cc5e9255d perf sched timehist: Enlarge default comm_width
- 0e6758e8231d5905c2e267566e9bd679a68a7b00 perf sched timehist: Honour comm_width when aligning the headers
- 4a401ceeef7bf3bc55f5e913cbf19d6038cf83c6 Merge tag drm-intel-next-fixes-2016-12-22 of git://anongit.freedesktop.org/git/drm-intel into drm-fixes
- d043835d08b297a41275e4dd499a33dd57243dee Merge tag drm-misc-fixes-2016-12-22 of git://anongit.freedesktop.org/git/drm-misc into drm-fixes
- 6df383cf9010feed788bf8ce555d77bcc03ed3a8 Merge branch drm-next-4.10 of git://people.freedesktop.org/~agd5f/linux into drm-fixes
- 8e5d31eb02c08d94262e1281adc8574134af65fd Merge branch nvme-4.10 of git://git.infradead.org/nvme into for-linus
- 72c5296f9d64d8f5f27c2133e5f108a45a353d71 genhd: remove dead and duplicated scsi code
- 64d656a162d7ba49d6d1863e41407b0f95e19258 block: add back plugging in __blkdev_direct_IO
- 50f6584e4c626b8fa39edb66f33fec27bab3996c Merge tag leds_for_4.10_email_update of git://git.kernel.org/pub/scm/linux/kernel/git/j.anaszewski/linux-leds
- af22941ae126b528a80c7e1149fa22b31815c826 Merge branch for-linus of git://git.kernel.dk/linux-block
- 9be962d5258ebb5a0f1edd3ede26bfd847c4ebe6 Merge tag acpi-extra-4.10-rc1 of git://git.kernel.org/pub/scm/linux/kernel/git/rafael/linux-pm
- 85ba70b6ceff7a2880f29b94e789cee436bc572f Merge tag pm-fixes-4.10-rc1 of git://git.kernel.org/pub/scm/linux/kernel/git/rafael/linux-pm
- 8d86cf8879e374fb395f6b15150dd702275ca989 Merge tag mmc-v4.10-3 of git://git.kernel.org/pub/scm/linux/kernel/git/ulfh/mmc
- 67327145c4af673d9c4ef06537ca8c5818f97668 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/jmorris/linux-security
- eb254f323bd50ab7e3cc385f2fc641a595cc8b37 Merge branch x86-cache-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 305335b9079426e4619de175ea8d35c669426567 MAINTAINERS: Update Jacek Anaszewskis email address
- 1134c2b5cb840409ffd966d8c2a9468f64e6a494 perf/x86: Fix overlap counter scheduling bug
- daa864b8f8e34477bde817f26d736d89dc6032f3 perf/x86/pebs: Fix handling of PEBS buffer overflows
- cef4402d7627f14a08571e7c816b199edf8cc24b x86/paravirt: Mark unused patch_default label
- 5cc8fabc5e4c588c75a5ec21423e7c3425f69f48 IB/rxe: Dont check for null ptr in send()
- cbf1f9a46c9c5903e34b0b110ca40b1e7d4b2ab1 IB/rxe: Drop future atomic/read packets rather than retrying
- 37b36193946e4fe7af2c3965e394eb311ab6601d IB/rxe: Use BTH_PSN_MASK when ACKing duplicate sends
- 74c3875c3d9aad356ae27fc4f4176d4dc89c457b qedr: Always notify the verb consumer of flushed CQEs
- 27035a1b37fc284b59a2bca4cf2f910ebf03717f qedr: clear the vendor error field in the work completion
- 922d9a40d3baeb30bfecb59b2c083ccec4b349d7 qedr: post_send/recv according to QP state
- 8b0cabc650a95a4f44de99aae6e8c128d70a40cd qedr: ignore inline flag in read verbs
- b4c2cc48aa0be767281669bff9f230e81ef27c56 qedr: modify QP state to error when destroying it
- d6ebbf29c3015bdccef388a860ac4ef6772531f8 qedr: return correct value on modify qp
- a121135973ca816821f4ff07aed523df82a91b8e qedr: return error if destroy CQ failed
- c7eb3bced78fe83119b90d730ab58a572eb80e29 qedr: configure the number of CQEs on CQ creation
- 61f51b7b20f631ef8fe744bc0412d4eb5194b6a9 i40iw: Set 128B as the only supported RQ WQE size
- fba332b079029c2f4f7e84c1c1cd8e3867310c90 IB/cma: Fix a race condition in iboe_addr_get_sgid()
- 2e3d5fa44f0f6e71ada2c4ed212ac23ca7ff0064 Merge tag wireless-drivers-for-davem-2016-12-22 of git://git.kernel.org/pub/scm/linux/kernel/git/kvalo/wireless-drivers
- 7d99569460eae28b187d574aec930a4cf8b90441 net: ipv4: Dont crash if passing a null sk to ip_do_redirect.
- 7b99f1aeed37196ad54099c30c2f154a7d6e91e0 Merge branch pm-cpufreq
- c8e008e2a6f9ec007a0e22e18eeb5bace5bf16c8 Merge branches acpica and acpi-scan
- ac632f5b6301c4beb19f9ea984ce0dc67b6e5874 befs: add NFS export support
- e60f749b60979e333764b8e9143aad7a7bdea0fa befs: remove trailing whitespaces
- 50b00fc468ddf9cb47a00b62c25fcbf86fcce56f befs: remove signatures from comments
- 12ecb38d03cff0c6d09262f0334f4ded3242ae87 befs: fix style issues in header files
- 62b80719dfe126f73e417d7011dfb5ef53c6a203 befs: fix style issues in linuxvfs.c
- 1ca7087e59cba48a58bf5e6594a67e8ccbead7e2 befs: fix typos in linuxvfs.c
- 4c7df6455923ac9bc78379ed07f34477f7ef1b4d befs: fix style issues in io.c
- 85a06b302a9dbe06e4bcfed715875e42b07531f6 befs: fix style issues in inode.c
- a83179a8e95ec70a84d3a9a04b6062fa1884aebf befs: fix style issues in debug.c
- 2f60b28831c7e63759b59113898e6fe4dc90dd43 xen/evtchn: use rb_entry()
- 7ecec8503af37de6be4f96b53828d640a968705f xen/setup: Dont relocate p2m over existing one
- 3868f132cce6abab089fd6b12d6a7333712ade83 clk: stm32f4: Use CLK_OF_DECLARE_DRIVER initialization method
- e2a33c34ddff22ee208d80abdd12b88a98d6cb60 clk: renesas: mstp: Support 8-bit registers for r7s72100
- f79f7b1b4f910e03fa20092759c79fc2e53f2eff CREDITS: Remove outdated address information
- 551cde192343a10c8fbd57c4cc8f0c4b6cd307e4 net: fddi: skfp: use %p format specifier for addresses rather than %x
- 0a9648f1293966c838dc570da73c15a76f4c89d6 tcp: add a missing barrier in tcp_tasklet_func()
- 52bce91165e5f2db422b2b972e83d389e5e4725c splice: reinstate SIGPIPE/EPIPE handling
- 0c961c5511fe48834c73215d2203bdac3353dcae Merge branch parisc-4.10-1 of git://git.kernel.org/pub/scm/linux/kernel/git/deller/parisc-linux
- bc1ecd626bedfa6b8cb09bacd56756ad18aed08f Merge tag nfs-for-4.10-2 of git://git.linux-nfs.org/projects/trondmy/linux-nfs
- 8354491c9d5b06709384cea91d13019bf5e61449 net: mvpp2: fix dma unmapping of TX buffers for fragments
- f217bfde24077b6684e625dd618e3a522e6f272a net: ethernet: stmmac: dwmac-rk: make clk enablement first in powerup
- 76b15923b777aa2660029629179550124c1fc40e be2net: Increase skb headroom size to 256 bytes
- d5db84a871f815968e4d2933b9dd6f8ab83f80d1 Merge branch scsi-target-for-v4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/bvanassche/linux
- b428018a065b62191b9f8a3f553ebf4423017a78 KVM: nVMX: fix instruction skipping during emulated vm-entry
- f8114f8583bb18a467c04ddc1e8978330e445801 Revert ALSA: usb-audio: Fix race at stopping the stream
- bfc5e3a6af397dcf9c99a6c1872458e7867c4680 selinux: use the kernel headers when building scripts/selinux
- 22b68b93ae2506bd56ee3bf232a51bc8ab955b56 rtlwifi: Fix kernel oops introduced with commit e49656147359
- d1f1c0e289e1bc46cd6873ba6dd6c627f459e7fa ath9k: do not return early to fix rcu unlocking
- 7c3a23b85cac5f3caa531f369c1e3a5f1a8b555f nvmet/fcloop: remove some logically dead code performing redundant ret checks
- 6c73f949300f17851f53fa80c9d1611ccd6909d3 nvmet: fix KATO offset in Set Features
- 17a1ec08ce7074f05795e5c32a3e5bc9a797bbf8 nvme/fc: simplify error handling of nvme_fc_create_hw_io_queues
- c703489885218900579279cec4b4ab8e7fce383b nvme/fc: correct some printk information
- 2c473a9d02fbe881506d5d43bc7edb776f2f46f5 nvme/scsi: Remove START STOP emulation
- ff13b39ecf726715a96fcd3c23e50eb792ef6516 nvme/pci: Delete misleading queue-wrap comment
- 9fa196e7fc7a0f12329d5346164abb27f026991c nvme/pci: Fix whitespace problem
- e6282aef7b89a11d26e731060c4409b7aac278bf nvme: simplify stripe quirk
- b508fc354f6d168ec18673d99d3bce9d6c1d9475 nvme: update maintainers information
- 8877ebdd3f9a3ffc84c4b67562d257c5f553bc49 x86/microcode/AMD: Reload proper initrd start address
- c739c0a7c3c2472d7562b8f802cdce44d2597c8b [media] s5k4ecgx: select CRC32 helper
- 4dd19196c5539c377beaa9850fac30c18318c7a1 [media] dvb: avoid warning in dvb_net
- 79d6205a3f741c9fb89cfc47dfa0eddb1526726d [media] v4l: tvp5150: Dont override output pinmuxing at stream on/off time
- b4b2de386bbb6589d81596999d4a924928dc119b [media] v4l: tvp5150: Fix comment regarding output pin muxing
- aff808e813fc2d311137754165cf53d4ee6ddcc2 [media] v4l: tvp5150: Reset device at probe time, not in get/set format handlers
- 48775cb73c2e26b7ca9d679875a6e570c8b8e124 [media] pctv452e: move buffer to heap, no mutex
- 78ccbf9ff89bd7a20d36be039cb3eab71081648c [media] media/cobalt: use pci_irq_allocate_vectors
- f60f35609f89ef4fee73776bc1ef697923251995 [media] cec: fix race between configuring and unconfiguring
- d3d64bc7408f1ff0b0ff8354056e2a48eda5886d [media] cec: move cec_report_phys_addr into cec_config_thread_func
- 52bc30fda9622f492427d484bd4dd8ee42cc4667 [media] cec: replace cec_report_features by cec_fill_msg_report_features
- 7af26f889eb67db272021a939f7d4a57e96dd961 [media] cec: update log_addr[] before finishing configuration
- a24f56d47930492c94ef6875bf45adf7607ca1a4 [media] cec: CEC_MSG_GIVE_FEATURES should abort for CEC version < 2
- 120476123646ba3619c90db7bcbc6f8eea53c990 [media] cec: when canceling a message, dont overwrite old status info
- f3854973f196baad5be6b62d8f5ea24b0346b63f [media] cec: fix report_current_latency
- 4bfb934b0067b7f6a24470682c5f7254fd4d8282 [media] smiapp: Make suspend and resume functions __maybe_unused
- 9447082ae666fbf3adbe9c9152117daa31a8b737 [media] smiapp: Implement power-on and power-off sequences without runtime PM
- e85baa8868b016513c0f5738362402495b1a66a5 mmc: sd: Meet alignment requirements for raw_ssr DMA
- adec57c61c2421d9d06c1fa8dd1ff7ed4fd2ca1b cpufreq: s3c64xx: remove incorrect __init annotation
- 2a8fa123d9a1d2ca391eefc81fea747108a5081f cpufreq: Remove CPU hotplug callbacks only if they were initialized
- 1358e038fac2628730842c817c7c156647166461 CPU/hotplug: Clarify description of __cpuhp_setup_state() return value
- 8d3523fb3b727478ac528b307cb84460faa1c39e ACPI / osl: Remove deprecated acpi_get_table_with_size()/early_acpi_os_unmap_memory()
- 6b11d1d677132816252004426ef220ccd3c92d2f ACPI / osl: Remove acpi_get_table_with_size()/early_acpi_os_unmap_memory() users
- 66360faa4333babc53836c7b59a0cff68cb0a9c6 ACPICA: Tables: Allow FADT to be customized with virtual address
- 174cc7187e6f088942c8e74daa7baff7b44b33c9 ACPICA: Tables: Back port acpi_get_table_with_size() and early_acpi_os_unmap_memory() from Linux kernel
- f8d9422ef80c5126112284493e69c88753c56ad1 drm/amdgpu: update tile table for oland/hainan
- 3548f9a829738db1df2643c1db1a134d84b00fc4 drm/amdgpu: update tile table for verde
- f815b29cea0968df400f8c9f8b770ec02ec66906 drm/amdgpu: update rev id for verde
- dae5c2985da969074df03b9ff5226432be9e3293 drm/amdgpu: update golden setting for verde
- 8fd74cb4a0e563b2025b521accc7a5963f60cdb1 drm/amdgpu: update rev id for oland
- 6b7985efc3b56dba3a49221464e7ef65688cda76 drm/amdgpu: update golden setting for oland
- 05319478dad476841282a0eab66a00da425e0914 drm/amdgpu: update rev id for hainan
- bd27b678c26ea9f6d6efdbea139f38fba426aaac drm/amdgpu: update golden setting for hainan
- e285a9a64d64e65a10e97c6ae1e9385c9595b563 drm/amdgpu: update rev id for pitcairn
- 1245a694617ebc39342f12d55ed3e6561fcb9f4a drm/amdgpu: update golden setting for pitcairn
- 7c0a705e0326a7eed2149eb0b7b30e23897becda drm/amdgpu: update golden setting/tiling table of tahiti
- ba6d973f78eb62ffebb32f6ef3334fc9a3b33d22 Merge git://git.kernel.org/pub/scm/linux/kernel/git/davem/net
- 3eb86259eca6a363ed7bb13ecea5cda809f7b97d Merge branch akpm (patches from Andrew)
- f95adbc1f7cef521d1d6b9146691d5971a660614 Merge branch mailbox-for-next of git://git.linaro.org/landing-teams/working/fujitsu/integration
- 74f65bbf46da4f32ddeab221e2de6d6e15f806bd Merge branch i2c/for-current of git://git.kernel.org/pub/scm/linux/kernel/git/wsa/linux
- 1351522b5f627f06e44e781805b5bd5c01566cf3 Merge tag doc-4.10-3 of git://git.lwn.net/linux
- d5379e5eddc09f8d172d9d6aa0e5a269a89dc60a Merge tag microblaze-4.10-rc1 of git://git.monstr.eu/linux-2.6-microblaze
- 7961d53d22375bb9e8ae8063533b9059102ed39d scsi: qedi: fix build, depends on UIO
- ec92b88c3c05dd9bc75379014858c504ebb9ecbc Merge tag xtensa-20161219 of git://github.com/jcmvbkbc/linux-xtensa
- 7dbbf0fa1bf14c17900bb8057986b06db3822239 scsi: scsi-mq: Wait for .queue_rq() if necessary
- 160494d381373cfa21208484aea4e5db2d3cb0a8 parisc: Optimize timer interrupt function
- a763f78cea845c91b8d91f93dabf70c407635dc5 RDS: use rb_entry()
- 7f7cd56c33937c6afa8a3d1f10a804c314e5b308 net_sched: sch_netem: use rb_entry()
- e124557d60ccefacbda79934af816526cc08aeb7 net_sched: sch_fq: use rb_entry()
- f7fb138389aac97fe165c9b8fe4dcfeb97a78d06 net/mlx5: use rb_entry()
- ae99b639ce79f73fe4d1c44da8aa2d96b0f13253 ethernet: sfc: Add Kconfig entry for vendor Solarflare
- b794e252f5c1c640097348566dd85d463698ce90 Merge branch sctp-fixes
- b8607805dd157d5f93372f338b3f3b9018c507d7 sctp: not copying duplicate addrs to the assocs bind address list
- 165f2cf6405a9e2153b69302845c7d5c9f3cb23b sctp: reduce indent level in sctp_copy_local_addr_list
- 037569172083a59c0cc5b66c5e1cf80dcf27ebb7 Merge tag perf-core-for-mingo-20161220 of git://git.kernel.org/pub/scm/linux/kernel/git/acme/linux into perf/urgent
- 92f95322c65fef330cc0a6bb6ed3e7966f8635d5 Merge branch hix5hd2_gmac-compatible-string
- 48fed73ab6d2ef59d266e362afaabb73d9b1a2d6 ARM: dts: hix5hd2: dont change the existing compatible string
- f7ca8e3b945366259e82ed50961809ad4262933f net: hix5hd2_gmac: fix compatible strings name
- 87e159c59d9f325d571689d4027115617adb32e6 openvswitch: Add a missing break statement.
- 4c0ef2319a6cc3506db2a546b9e6294ec635eb90 net: netcp: ethss: fix 10gbe host port tx pri map configuration
- e9838ef2d6f3f3ccb058514d4ac03a6f6155ecc2 net: netcp: ethss: fix errors in ethtool ops
- 04fddde37642dd270ecb430b879f311536cfd6a5 Merge branch fsl-fixes
- 2e3db5a4b9ee704f841d6356a32428830c7079e6 fsl/fman: enable compilation on ARM64
- 1e33099540b1e13d0e9674bc97c15d3fac050f6f fsl/fman: A007273 only applies to PPC SoCs
- ae6021d4fc2bcc9e3193a007b2c9d31392ac641b powerpc: fsl/fman: remove fsl,fman from of_device_ids[]
- 606987b04e6c0dd8027ea331f2eeae35a5f4413c fsl/fman: fix 1G support for QSGMII interfaces
- fb3dc5b8adef1b05e2ca2a48db9fcf1a35ae9a1e Merge branch phy-broken-modes
- 308d3165d8b2b98d3dc3d97d6662062735daea67 dt: bindings: net: use boolean dt properties for eee broken modes
- 57f3986231bb2c69a55ccab1d2b30a00818027ac net: phy: use boolean dt properties for eee broken modes
- 3bb9ab63276696988d8224f52db20e87194deb4b net: phy: fix sign type error in genphy_config_eee_advert
- 50f4d9bda9f8510db1392b4e832fca95c56295a1 printk: fix typo in CONSOLE_LOGLEVEL_DEFAULT help text
- 1b011e2f13fcf37e1e577fed25b295808d6c83b9 ratelimit: fix WARN_ON_RATELIMIT return value
- 4983f0ab7ffaad1e534b21975367429736475205 kcov: make kcov work properly with KASLR enabled
- 7ede8665f27cde7da69e8b2fbeaa1ed0664879c5 arm64: setup: introduce kaslr_offset()
- 4dd72b4a47a5309333c8ddf9ec7df3380dede30d mm: fadvise: avoid expensive remote LRU cache draining after FADV_DONTNEED
- 98e1d55d033eed2a474924c94fc2051ab20de402 ima: platform-independent hash value
- d68a6fe9fccfd00589c61df672b449d66ba3183f ima: define a canonical binary_runtime_measurements list format
- c7d09367702e2f4faebc6176d24df72dd5066c3e ima: support restoring multiple template formats
- 3f23d624de73252e27603361aa357289d9459a2e ima: store the builtin/custom template definitions in a list
- 7b8589cc29e7c35dcfd2d5138979f17b48f90110 ima: on soft reboot, save the measurement list
- ab6b1d1fc4aae6b8bd6fb1422405568094c9b40f powerpc: ima: send the kexec buffer to the next kernel
- d158847ae89a25615f3d8757ad8c6f50fc816db5 ima: maintain memory size needed for serializing the measurement list
- dcfc56937b62bf720f99a4d9aabfd243194322be ima: permit duplicate measurement list entries
- 94c3aac567a9ddb9e868a7fae3c927c08b51b7c6 ima: on soft reboot, restore the measurement list
- 467d27824920e866af148132f555d40ca1fb199e powerpc: ima: get the kexec buffer passed by the previous kernel
- 0a28cfd51e17f4f0a056bcf66bfbe492c3b99f38 ipv4: Should use consistent conditional judgement for ip fragment in __ip_append_data and ip_finish_output
- d4166b8b33650d9dc89715c9540ba0f261490d4d ath10k: free host-mem with DMA_BIRECTIONAL flag
- 9899694a7f67714216665b87318eb367e2c5c901 samples/bpf: Move open_raw_sock to separate header
- 205c8ada314f78e6637342089e5b585a051d6cf5 samples/bpf: Remove perf_event_open() declaration
- 811b4f0d785d33eabfff5d0ea60596b6b8bdc825 samples/bpf: Be consistent with bpf_load_program bpf_insn parameter
- 5dc880de6e7c8566fbc8bc5dfc3a922d2d1c5ee3 tools lib bpf: Add bpf_prog_{attach,detach}
- 43371c83f382bd495a2294e91a32f30763cfdbef samples/bpf: Switch over to libbpf
- ed6c166cc7dc329736cace3affd2df984fb22ec8 perf diff: Do not overwrite valid build id
- edee44be59190bf22d5c6e521f3852b7ff16862f perf annotate: Dont throw error for zero length symbols
- 6ba0566cf2afcdb17bff882e3a95cbbcb22c4a83 drm/i915: skip the first 4k of stolen memory on everything >= gen8
- abb0deacb5a6713b918ac6395182cb27bb88be69 drm/i915: Fallback to single PAGE_SIZE segments for DMA remapping
- d8953c8326d87a337763ca547ad7db034a94ddb1 drm/i915: Fix use after free in logical_render_ring_init
- 1c4672ce4eeaeaadeea8adabaad21262b7172607 drm/i915: disable PSR by default on HSW/BDW
- b1b7ec985805e005055d1d471ca586a715ffc10a drm/i915: Fix setting of boost freq tunable
- 2c57b18adb93fc070039538f1ce375d3d3e99bbb drm/i915: tune down the fast link training vs boot fail
- 057f803ff10742addd19a7c2fb6fb83940059a6c drm/i915: Reorder phys backing storage release
- dccf82ad1775f2b9c36ec85e25e39d88c7e86818 drm/i915/gen9: Fix PCODE polling during SAGV disabling
- 2c7d0602c815277f7cb7c932b091288710d8aba7 drm/i915/gen9: Fix PCODE polling during CDCLK change notification
- 22ca0d4991169b76e753d767a45f1105c356bbb8 drm/i915/dsi: Fix chv_exec_gpio disabling the GPIOs it is setting
- 25e23bc57e737a0d81dc6b03c610789866858b35 drm/i915/dsi: Fix swapping of MIPI_SEQ_DEASSERT_RESET / MIPI_SEQ_ASSERT_RESET
- bb98e72adaf9d19719aba35f802d4836f5d5176c drm/i915/dsi: Do not clear DPOUNIT_CLOCK_GATE_DISABLE from vlv_init_display_clock_gating
- 35f6c2336b1a5007ec837623f771d2d56dfba5c2 drm/i915: drop the struct_mutex when wedged or trying to reset
- cabab3f9f5ca077535080b3252e6168935b914af s390/kbuild: enable modversions for symbols exported from asm
- 8f2b468aadc81ca0fc78e41696b648e30d91ba5c s390/vtime: correct system time accounting
- 2b66325d5ea7c2a39ac69ed83b6979afe480d81a brcmfmac: fix uninitialized field in scheduled scan ssid configuration
- cb853da3a368c40300a0e940f86be582037bb082 brcmfmac: fix memory leak in brcmf_cfg80211_attach()
- 9de3ffa1b714e6b8ebc1723f71bc9172a4470f7d perf bench futex: Fix lock-pi help string
- 2bd42f3aaa53ebe78b9be6f898b7945dd61f9773 perf trace: Check if MAP_32BIT is defined (again)
- 96c2fb69b92fcf6006dfb3017d6d887f8321407b samples/bpf: Make perf_event_read() static
- 264c3e8de4fbda1d1342213c78fb3788a43cfd41 spi: sh-msiof: Do not use C++ style comment
- 1cab2a84f470e15ecc8e5143bfe9398c6e888032 ASoC: wm_adsp: Dont overrun firmware file buffer when reading region data
- 15520111500c33a012aeec28ece8c5f2dcbf6b5e mmc: core: Further fix thread wake-up
- 84ec048ba133c2a570273e90622d8fac4930553e mmc: sdhci: Fix to handle MMC_POWER_UNDEFINED
- 5b311c1519c658bf06f7a08a2ddc2648e4c9cd5c mmc: sdhci-cadence: add Socionext UniPhier specific compatible string
- 9120cf4fd9ae77245ce9137869bcbd16575cc633 x86/platform/intel/quark: Add printf attribute to imr_self_test_result()
- 634b847b6d232f861abd5a03a1f75677f541b156 x86/platform/intel-mid: Switch MPU3050 driver to IIO
- 34bfab0eaf0fb5c6fb14c6b4013b06cdc7984466 x86/alternatives: Do not use sync_core() to serialize I$
- a268b5f1d6e4639fa6d78fc8bdddaebaa032ab24 x86/topology: Document cpu_llc_id
- 59107e2f48831daedc46973ce4988605ab066de3 x86/hyperv: Handle unknown NMIs on one CPU when unknown_nmi_panic
- 8ac2b42238f549241a4755de40fd161fba3de438 NFSv4: Retry the DELEGRETURN if the embedded GETATTR is rejected with EACCES
- f07d4a31ccd7dbe3ca49bedc8298245d6877a43e NFS: Retry the CLOSE if the embedded GETATTR is rejected with EACCES
- d8d849835eb2082ea17655538a83fa467633927f NFSv4: Place the GETATTR operation before the CLOSE
- 9413a1a1bf5d58db610e3d9ba500f4150afa55ad NFSv4: Also ask for attributes when downgrading to a READ-only state
- a5f925bccce7b0dc083f0c5a8652600881cc38ab NFS: Dont abuse NFS_INO_REVAL_FORCED in nfs_post_op_update_inode_locked()
- e71708d4df1d4b81427badb9ac4bc4a813338b17 pNFS: Return RW layouts on OPEN_DOWNGRADE
- b6808145ad2aa625b962fc55f30484091d5e8fe7 NFSv4: Add encode/decode of the layoutreturn op in OPEN_DOWNGRADE
- 86cfb0418537460baf0de0b5e9253784be27a6f9 NFS: Dont disconnect open-owner on NFS4ERR_BAD_SEQID
- 3f8f25489fa62437530f654041504936d377d204 NFSv4: ensure __nfs4_find_lock_state returns consistent result.
- cfd278c280f997cf2fe4662e0acab0fe465f637b NFSv4.1: nfs4_fl_prepare_ds must be careful about reporting success.
- 1c48cee83bc2631ab8533311d594aaafe81d8aa9 pNFS/flexfiles: delete deviceid, dont mark inactive
- 187e593d2779fb92ae1de06f873d6e192ba35d88 NFS: Clean up nfs_attribute_timeout()
- 3f642a13359468181f29db3d8926ba36530be85e NFS: Remove unused function nfs_revalidate_inode_rcu()
- 21c3ba7e5dcdba23094fb50f6d1198faed94dac4 NFS: Fix and clean up the access cache validity checking
- 9cdd1d3f1a8cea9cfe7953f45fae9ff51c37afa3 NFS: Only look at the change attribute cache state in nfs_weak_revalidate()
- 61540bf6bb40ddfa3e766de91cedca2e1afd24eb NFS: Clean up cache validity checking
- 58ff41842c7b8b8a79752e3d040188ebddb95194 NFS: Dont revalidate the file on close if we hold a delegation
- 0bc2c9b4dca9668a236fde48ebb15e5f0735cbff NFSv4: Dont discard the attributes returned by asynchronous DELEGRETURN
- e603a4c1b5c2b9d24139eeb1769c5ac600318c07 NFSv4: Update the attribute cache info in update_changeattr
- a1f49cc179ce6b7b7758ae3ff5cdb138d0ee0f56 drm/amdgpu: fix cursor setting of dce6/dce8
- 08fe007968b2b45e831daf74899f79a54d73f773 ARC: mm: arc700: Dont assume 2 colours for aliasing VIPT dcache
- f64915be2d8c629e7b55ad37f90bd8db2713426e ARC: mm: No need to save cache version in @cpuinfo
- 73ba39ab9307340dc98ec3622891314bbc09cc2e btrfs: return the actual error value from  from btrfs_uuid_tree_iterate
- e93b1cc8a8965da137ffea0b88e5f62fa1d2a9e6 Merge branch for_linus of git://git.kernel.org/pub/scm/linux/kernel/git/jack/linux-fs
- 45d36906e256fe9f8e976461b4c559722c3cbe2a Merge tag for-linus of git://git.kernel.org/pub/scm/virt/kvm/kvm
- 633395b67bb222f85bb8f825c7751a54b9ec84ee block: check partition alignment
- f1e9132444a97b52b20d07f352323926b2df7c32 Merge branch dmi-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/jdelvare/staging
- ac5a28b0d3d173ba0a581342416ed339f2c3be3d Merge tag mfd-for-linus-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/lee/mfd
- ad688cdbb076833ba17fc65591cd0fe01900a5cf stmmac: fix memory barriers
- 162809dfc2bfb31eb54dc67733bcdab0f2d1534d net: ethernet: cavium: octeon: octeon_mgmt: Handle return NULL error from devm_ioremap
- c965809c669da004b660e5923b8add8fac5a7dc8 nvme : Use correct scnprintf in cmb show
- 25cdb64510644f3e854d502d69c73f21c6df88a9 block: allow WRITE_SAME commands with the SG_IO ioctl
- ef85b67385436ddc1998f45f1d6a210f935b3388 kvm: nVMX: Allow L1 to intercept software exceptions (#BP and #OF)
- cc0d907c0907561f108b2f4d4da24e85f18d0ca5 kvm: take srcu lock around kvm_steal_time_set_preempted()
- 931f261b42f10c8c8c9ab53f5ceb47ce51af7cf5 kvm: fix schedule in atomic in kvm_steal_time_set_preempted()
- db4d22c07e3e652eeec82abcc1399e6305edd838 mailbox: mailbox-test: allow reserved areas in SRAM
- baef9a35d24626ebdc5a9074455e63eea6c7f6af mailbox: mailbox-test: add support for fasync/poll
- cf17581340d730175f1f3f4ce6e90ae434154e37 mailbox: bcm-pdc: Remove unnecessary void* casts
- 30d1ef623fd1e99bc1bab5211ba1da0d97d40e64 mailbox: bcm-pdc: Simplify interrupt handler logic
- 63bb50bdb997f4bede1b5f2d56645f393f7f39fb mailbox: bcm-pdc: Performance improvements
- 38ed49ed4a99942f1a340f4a82a5a8b492e3463b mailbox: bcm-pdc: Dont use iowrite32 to write DMA descriptors
- 8aef00f090bcbe5237c5a6628e7c000890267efe mailbox: bcm-pdc: Convert from threaded IRQ to tasklet
- 7493cde34efc28641c295ee0d52ab9d790853c62 mailbox: bcm-pdc: Try to improve branch prediction
- e004c7e7d3b873a671fecf04f197982806e380eb mailbox: bcm-pdc: streamline rx code
- ab8d1b2d564f6649547b97e65806556c42f93a26 mailbox: bcm-pdc: Convert from interrupts to poll for tx done
- 9310f1ded44067b2da61fa0471ca5b7768dd28ae mailbox: bcm-pdc: PDC driver leaves debugfs files after removal
- 9fb0f9ac54b393ddfe49be7da7751f02bb133db6 mailbox: bcm-pdc: Changes so mbox client can be removed / re-inserted
- 9b1b2b3adb310560a31ea248fa0defc8f09129ff mailbox: bcm-pdc: Use octal permissions rather than symbolic
- 2f50497d71e2982584d1a11d636d43eea0f992e6 mailbox: sti: Fix module autoload for OF registration
- f42cce3c2409960adebe8e970574b23cbbf34e7d mailbox: mailbox-test: Fix module autoload
- 405182c2459fe2de4a3994ef39e866993e0e61d1 HID: sony: Ignore DS4 dongle reports when no device is connected
- c70d5f70ccbbdf56bb86adb42127db90d0c90976 HID: sony: Use DS4 MAC address as unique identifier on USB
- 2b6579d4a71afb19c6583470783371b992944f67 HID: sony: Fix error handling bug when touchpad registration fails
- fff5d99225107f5f13fe4a9805adc2a1c4b5fb00 swiotlb: Add swiotlb=noforce debug option
- ae7871be189cb41184f1e05742b4a99e2c59774d swiotlb: Convert swiotlb_force from int to enum
- 6c206e4d99f2ed2a5a59875858e3beecc69b6474 x86, swiotlb: Simplify pci_swiotlb_detect_override()
- 4a8b3a682be9addff7dbd16371fa8c34103b5c31 ASoC: Intel: bytcr_rt5640: fallback mechanism if MCLK is not enabled
- 2700e6067c72a99d1b7037692da0145ac44623c4 quota: Fix bogus warning in dquot_disable()
- c198b121b1a1d7a7171770c634cd49191bac4477 x86/asm: Rewrite sync_core() to use IRET-to-self
- 484d0e5c7943644cc46e7308a8f9d83be598f2b9 x86/microcode/intel: Replace sync_core() with native_cpuid()
- 426d1aff3138cf38da14e912df3c75e312f96e9e Revert x86/boot: Fail the boot if !M486 and CPUID is missing
- 1c52d859cb2d417e7216d3e56bb7fea88444cec9 x86/asm/32: Make sync_core() handle missing CPUID on all 32-bit kernels
- 3df8d9208569ef0b2313e516566222d745f3b94b x86/cpu: Probe CPUID leaf 6 even when cpuid_level == 6
- 7ebb916782949621ff6819acf373a06902df7679 x86/tools: Fix gcc-7 warning in relocs.c
- 8b5e99f02264130782a10ba5c0c759797fb064ee x86/unwind: Dump stack data on warnings
- 8023e0e2a48d45e8d5363081fad9f7ed4402f953 x86/unwind: Adjust last frame check for aligned function stacks
- 22d3c0d63b1108af0b4ef1cfdad1f6ef0710da30 x86/init: Fix a couple of comment typos
- 32786fdc9506aeba98278c1844d4bfb766863832 x86/init: Remove i8042_detect() from platform ops
- d79e141c1c6ea7cb70c169971d522b88c8d5b419 Input: i8042 - Trust firmware a bit more when probing on X86
- 93ffa9a479ffb65d045e74e141346e7f107fcde1 x86/init: Add i8042 state to the platform data
- c8b1b3dd89ea7b3f77a73e59c4c4495e16338e15 HID: asus: Fix keyboard support
- c9435f35ae64ee162555a82b6a3586b160093957 clocksource/drivers/moxart: Plug memory and mapping leaks
- f357563f958df06cd9ea9e614cdba30578bb08b1 irqchip/st: Mark st_irq_syscfg_resume() __maybe_unused
- 2b4c91569a40c4512ea1b413e0c817d179ce9868 x86/microcode/AMD: Use native_cpuid() in load_ucode_amd_bsp()
- a15a753539eca8ba243d576f02e7ca9c4b7d7042 x86/microcode/AMD: Do not load when running on a hypervisor
- 200d3553163f6065a0f1f142f92d1cf716d586c2 x86/microcode/AMD: Sanitize apply_microcode_early_amd()
- 8feaa64a9a69652fdff87205f8a8cfe1bfd5b522 x86/microcode/AMD: Make find_proper_container() sane again
- d4af49f810db8b855b043615c3b4312e5ba8aedb firmware: dmi_scan: Always show system identification string
- 983eeba7d2a854b540bd25c9e2311778408d9730 ARC: enable SG chaining
- b0b3a37b908b5906524c11f3ca12cd7c9d4adc1c Merge tag rtc-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/abelloni/linux
- d3e5925902dc0f639efc3641e07fca2bd7af5441 rtc: mcp795: Fix whitespace and indentation.
- a2b42997513401903341cf96616839ad22f151b6 rtc: mcp795: Prefer using the BIT() macro.
- 43d0b10f60c54667108729adb525bc1090d4238f rtc: mcp795: fix month write resetting date to 1.
- 26eeefd5956449b03c87c49b996e012ffe3e59aa rtc: mcp795: fix time range difference between linux and RTC chip.
- e72765c648a172f052486cba9688ddc28f23140b rtc: mcp795: fix bitmask value for leap year (LP).
- bcf18d88ac16c1a86bac7e8f5f4b1de1f752865f rtc: mcp795: use bcd2bin/bin2bcd.
- 0b6a8f5c9bebe51b95ff23939db570e8d298a36f rtc: add support for EPSON TOYOCOM RTC-7301SF/DG
- 9c19b8930d2cf95f5dc5ec11610400a7c61845d1 rtc: ds1307: Add ACPI support
- 67626c9323027534496d21cf32793121662d03c0 Input: synaptics_i2c - change msleep to usleep_range for small msecs
- 41c567a5d7d1a986763e58c3394782813c3bcb03 Input: i8042 - add Pegatron touchpad to noloop table
- 65dadffddbe44a60f8be9e95f264949ba1e547e9 Input: joydev - remove unused linux/miscdevice.h include
- 3be134e5152f08e8bd3c2afdaac723f64d93c2bb Merge tag libnvdimm-for-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/nvdimm/nvdimm
- 8421c60446290c0fef1858a806261871a40ebf76 Merge tag platform-drivers-x86-v4.10-2 of git://git.infradead.org/users/dvhart/linux-platform-drivers-x86
- 83da6b59919a71a1a97ce9863aa0267eaf6d496c platform/x86: surface3-wmi: Balance locking on error path
- 957ae5098185e763b5c06be6c3b4b6e98c048712 platform/x86: Add Whiskey Cove PMIC TMU support
- f7dd3b1734ea335fea01f103d48b3de26ea0d335 Merge branch x86-timers-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 217e2bfab22e740227df09f22165e834cddd8a3b docs: sphinx-extensions: make rstFlatTable work with docutils 0.13
- 1bbb05f52055c8b2fc1cbb2ac272b011593172f9 Merge branch x86-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 451bb1a6b2d24df6d677fe790950bec0679b741d Merge branch timers-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 98da295b35cf23222b52a3dc1d768b7997c95a32 Merge branch smp-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- eb3a3c074624fdae82a09e77740c131f85299d67 Merge branch irq-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- e259934d4df7f99f2a5c2c4f074f6a55bd4b1722 IB/rxe: Fix a memory leak in rxe_qp_cleanup()
- b414fa01c31318383ae29d9d23cb9ca4184bbd86 iw_cxgb4: set correct FetchBurstMax for QPs
- 8c9b9d87b855226a823b41a77a05f42324497603 x86/tsc: Limit the adjust value further
- 16588f659257495212ac6b9beaf008d9b19e8165 x86/tsc: Annotate printouts as firmware bug
- 298360af3dab45659810fdc51aba0c9f4097e4f6 drivers/gpu/drm/ast: Fix infinite loop if read fails
- 297e765e390a2ac996000b5f7228cbd84d995174 uprobes: Fix uprobes on MIPS, allow for a cache flush after ixol breakpoint creation
- ffc7dc8d838c6403a550021e4f28a737334d80a7 x86/floppy: Use designated initializers
- 649ac63a9ae5e08b7123f2fa98c2bf42f033bdb9 i2c: mux: mlxcpld: fix i2c mux selection caching
- 52f40e9d657cc126b766304a5dd58ad73b02ff46 Merge git://git.kernel.org/pub/scm/linux/kernel/git/davem/net
- 231753ef780012eb6f3922c3dfc0a7186baa33c2 Merge uncontroversial parts of branch readlink of git://git.kernel.org/pub/scm/linux/kernel/git/mszeredi/vfs
- 3e3397e7b11ce1b9526975ddfbe8dd569fc1f316 net: mv643xx_eth: fix build failure
- a6b3c48312f6a2c3905653c0633344f811c1dde5 isdn: Constify some function parameters
- 9a60c9072295b30459284beca9aff52be8dfd64b mlxsw: spectrum: Mark split ports as such
- 0110c350c86d511be2130cb2a30dcbb76c4af750 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/viro/vfs
- 483c4933ea09b7aa625b9d64af286fc22ec7e419 cgroup: Fix CGROUP_BPF config
- 67a72a58913ab0f2f239e771547a58987c266960 Merge tag mac80211-for-davem-2016-12-16 of git://git.kernel.org/pub/scm/linux/kernel/git/jberg/mac80211
- 7729bad4fd95e48bcafcb2222c63a8a5cdc42f61 qed: fix old-style function definition
- c2ed1880fd61a998e3ce40254a99a2ad000f1a7d net: ipv6: check route protocol when deleting routes
- c762eaa777b789540e3fe33581d6d0e593dbb22e r6040: move spinlock in r6040_close as SOFTIRQ-unsafe lock order detected
- 3a7f0762a6b784ac9257287346e4f5f5f7f420b7 irda: w83977af_ir: cleanup an indent issue
- 7cafe8f82438ced6de4c6f17b872a02c10f7a63a net: sfc: use new api ethtool_{get|set}_link_ksettings
- 99bff5ee44f32c3ca5115922e487b067d9c3dd6b net: davicom: dm9000: use new api ethtool_{get|set}_link_ksettings
- 93dfe6c290123f1059828001678e6f8b1a102d9a net: cirrus: ep93xx: use new api ethtool_{get|set}_link_ksettings
- b7b44fd23e6d2a896c6efbe85b39862f14aae11a net: chelsio: cxgb3: use new api ethtool_{get|set}_link_ksettings
- 49cad93909b18acf942b70356e65eeeaa9ca9d23 net: chelsio: cxgb2: use new api ethtool_{get|set}_link_ksettings
- 6219d05506b66e3157efa48b1b39042b04280ce1 Merge branch bpf-fixes
- 6760bf2ddde8ad64f8205a651223a93de3a35494 bpf: fix mark_reg_unknown_value for spilled regs on map value marking
- 5ccb071e97fbd9ffe623a0d3977cc6d013bee93c bpf: fix overflow in prog accounting
- aafe6ae9cee32df85eb5e8bb6dd1d918e6807b09 bpf: dynamically allocate digest scratch buffer
- d9cb5bfcc3339f1a63df8fe0af8cece33c83c3af Merge git://git.kernel.org/pub/scm/linux/kernel/git/cmetcalf/linux-tile
- 0f484e42baaf5a38fc79e99b917caa5431651fb1 Merge tag kvmgt-vfio-mdev-for-v4.10-rc1 of git://github.com/01org/gvt-linux
- af79ce47efabba36d1db0902d46a80de7f251411 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/dtor/input
- c07dee7348e2451bcf2f178bf0e7830268e2c31a Merge tag for-linus-20161216 of git://git.infradead.org/linux-mtd
- 135c919758b019599c9ea7730f7ceb063f19c7b7 Merge branch misc of git://git.kernel.org/pub/scm/linux/kernel/git/mmarek/kbuild
- 37861ffa8c28e6c479cf04a70b7d6cc33d23c2a8 Merge branch kconfig of git://git.kernel.org/pub/scm/linux/kernel/git/mmarek/kbuild
- 41e0e24b450fadc079dfb659d81f3076afcfbd8a Merge branch kbuild of git://git.kernel.org/pub/scm/linux/kernel/git/mmarek/kbuild
- 0aaf2146ecf00f7932f472ec5aa30d999c89530c Merge tag docs-4.10-2 of git://git.lwn.net/linux
- c44ef859ceff45db1c72f9ccbfae96843c4b1501 Merge branch for-4.10/libnvdimm into libnvdimm-for-next
- d7fe1a67f658b50ec98ee1afb86df7b35c2b2593 dax: add region id, size, and align attributes
- e8465447d2f3366069115f7453153561ac9a1220 block: Remove unused member (busy) from struct blk_queue_tag
- b8c0d911ac5285e6be8967713271a51bdc5a936a bcache: partition support: add 16 minors per bcacheN device
- be628be09563f8f6e81929efbd7cf3f45c344416 bcache: Make gc wakeup sane, remove set_task_state()
- 8e598769c55dd6c442a1c6cbd21e7abda2a52215 i2c: designware: fix wrong Tx/Rx FIFO for ACPI
- 1635c5d04ea9343f0e3c74709c29995a23801ecd i2c: xgene: Fix missing code of DTB support
- 7f638c1cb0a1112dbe0b682a42db30521646686b i2c: mux: pca954x: fix i2c mux selection caching
- 493ff7e2cdda9182fb709d3681315180d9165bd8 i2c: octeon: thunderx: Limit register access retries
- 40e972ab652f3e9b84a8f24f517345b460962c29 Merge branch gtp-fixes
- d928be81b44dc3cad75d7a9f9fcbe99725dc7e56 gtp: Fix initialization of Flags octet in GTPv1 header
- 88edf10315c8d72db70d39f3851cf2c91abdb634 gtp: gtp_check_src_ms_ipv4() always return success
- e999cb43d51f3635afd6253c5c066798ad998255 net/x25: use designated initializers
- ebf12f1320c70c3eaeb5b7d108444fafd54d352c isdn: use designated initializers
- 9751362a4fe7ad37115d20344ce6d914a088268d bna: use designated initializers
- aabd7ad949247ef315fa5086d2caad7885567434 WAN: use designated initializers
- 9d1c0ca5e1d6697ce1e32bb708bfe24dff34f287 net: use designated initializers
- 99a5e178bde4b0fa1f25ca8d9caee0cb5e329e7c ATM: use designated initializers
- 4794195058b916cabcfaf9f4dfc699e6f48784f7 isdn/gigaset: use designated initializers
- cd333e377f803dbf8ec7588f598b70d4a1178f58 Merge branch virtio_net-XDP
- 72979a6c35907b6a7ab85e7bc60e0d52dba68f9d virtio_net: xdp, add slowpath case for non contiguous buffers
- 56434a01b12e99eb60908f5f2b27b90726d0a183 virtio_net: add XDP_TX support
- 672aafd5d88a951f394334802b938b502010d9eb virtio_net: add dedicated XDP transmit queues
- f600b690501550b94e83e07295d9c8b9c4c39f4e virtio_net: Add XDP support
- f23bc46c30ca5ef58b8549434899fcbac41b2cfc net: xdp: add invalid buffer warning
- 08abb79542c9e8c367d1d8e44fe1026868d3f0a7 sctp: sctp_transport_lookup_process should rcu_read_unlock when transport is null
- 5cb2cd68ddf9a13af36cec633006c0f2bdfb300a sctp: sctp_epaddr_lookup_transport should be protected by rcu_read_lock
- 10a3ecf49b681af49bf1b4f3fcf00115059a0ac6 Merge branch dpaa_eth-fixes
- 63f4b4b0348b494c0fcfa1c41e7da865108dcaab MAINTAINERS: net: add entry for Freescale QorIQ DPAA Ethernet driver
- 708f0f4f9cec143403f8575493bea62a692b4ca2 dpaa_eth: remove redundant dependency on FSL_SOC
- 7d6f8dc0b2180ed60aea65660b35d7618ff6e4ee dpaa_eth: use big endian accessors
- 616f6b40236fb9fdfc5267e2e945e16b7448b641 irda: irnet: add member name to the miscdevice declaration
- 33de4d1bb9e3d90e2238e85d7865ec664cf48e60 irda: irnet: Remove unused IRNET_MAJOR define
- 24c946cc5d35e32c5bb0c07ebdad32756e2bd20d irnet: ppp: move IRNET_MINOR to include/linux/miscdevice.h
- e292823559709b09cd9bf7bd112bd13c93daa146 irda: irnet: Move linux/miscdevice.h include
- 078497a4d9535026b137c08e3746e600d5669a05 irda: irproc.c: Remove unneeded linux/miscdevice.h include
- dcdc43d6642c828fa10d25130a92b712003d2ca4 bpf: cgroup: annotate pointers in struct cgroup_bpf with __rcu
- 28055c9710e7ab1479d018224be697f63eac2daa Merge branch inet_csk_get_port-and-soreusport-fixes
- 0643ee4fd1b79c1af3bd7bc8968dbf5fd047f490 inet: Fix get port to handle zero port number with soreuseport set
- 9af7e923fdd82dc25ad5ea75e24e92708947f961 inet: Dont go into port scan when looking for specific bind port
- 0eb6984f70005e792917d9e51142a57f79b32c91 bpf, test_verifier: fix a test case error result on unprivileged
- a08dd0da5307ba01295c8383923e51e7997c3576 bpf: fix regression on verifier pruning wrt map lookups
- eb63ecc1706b3e094d0f57438b6c2067cfc299f2 net: vrf: Drop conntrack data after pass through VRF device on Tx
- a0f37efa82253994b99623dbf41eea8dd0ba169b net: vrf: Fix NAT within a VRF
- 8a9f5fdf87bf383388fd21caf764b9d169c20a95 Merge branch cls_flower-mask
- f93bd17b916959fc20fbb7dc578e1f2657a8c343 net/sched: cls_flower: Use masked key when calling HW offloads
- 970bfcd09791282de7de6589bfe440eb11e2efd2 net/sched: cls_flower: Use mask for addr_type
- 83a77e9ec4150ee4acc635638f7dedd9da523a26 net: macb: Added PCI wrapper for Platform Driver.
- 94acf164dc8f1184e8d0737be7125134c2701dbe ibmveth: calculate gso_segs for large packets
- 026acd5f47340382844f0af73516cf7ae6cdc876 net: qcom/emac: dont try to claim clocks on ACPI systems
- cb02de96ec724b84373488dd349e53897ab432f5 x86/mpx: Move bd_addr to mm_context_t
- 9763f7a4a5f7b1a7c480fa06d01b2bad25163c0a Merge branch work.autofs into for-linus
- 5235d448c48e1f5a4a34bf90d412775cb75ffb32 reorganize do_make_slave()
- 066715d3fde4834cbbec88d12ca277c4185b9303 clone_private_mount() doesnt need to touch namespace_sem
- f4cc1c3810a0382ff76a4e119a21b90b84dbe195 remove a bogus claim about namespace_sem being held by callers of mnt_alloc_id()
- e297046875f2c5a43684f54f0fd098249b4f293a platform/x86: ideapad-laptop: Add Y700 15-ACZ to no_hw_rfkill DMI list
- 1a64b719d3ae0e4fb939d9a9e31abb60b4ce4eb1 platform/x86: Introduce button support for the Surface 3
- 3dda3b3798f96d2974b5f60811142d3e25547807 platform/x86: Add custom surface3 platform device for controlling LID
- afc4715901f0dce3206837a7051af05abf5a1e06 platform/x86: mlx-platform: Add mlxcpld-hotplug driver registration
- c3886c9d6076555697551da9b921cf6a6e9cc2b5 platform/x86: mlx-platform: Fix semicolon.cocci warnings
- 6613d18e90385db5cdbe32fe47567a3c11575b2d platform/x86: mlx-platform: Move module from arch/x86
- 3c55d6bcfe8163ff2b5636b4aabe3caa3f5d95f4 Merge remote-tracking branch djwong/ocfs2-vfs-reflink-6 into for-linus
- 4da00fd1b948b408f76488c4e506af748be5fce8 Merge branch work.write_end into for-linus
- 14e73e78ee982710292248536aa84cba41e974f4 tile: use __ro_after_init instead of tile-specific __write_once
- 18bfd3e6ab69cc4c8a11e4fc4acc121050db9b6e tile: migrate exception table users off module.h and onto extable.h
- 870ee4ff5647dbf024f99ba5e56d0f3c344f1511 tile: remove #pragma unroll from finv_buffer_remote()
- 8e36f722f73f2fc1766af1af0b2f56f2299ba687 tile-module: Rename jump labels in module_alloc()
- 8797fe75f164d4b2f183e776003612ece565c76e tile-module: Use kmalloc_array() in module_alloc()
- 65f62ce8492139bd5caea77dfce724c540efc4eb tile/pci_gx: fix spelling mistake: delievered -> delivered
- 59331c215daf600a650e281b6e8ef3e1ed1174c2 Merge tag ceph-for-4.10-rc1 of git://github.com/ceph/ceph-client
- ff0f962ca3c38239b299a70e7eea27abfbb979c3 Merge branch overlayfs-linus of git://git.kernel.org/pub/scm/linux/kernel/git/mszeredi/vfs
- 087a76d390cbb8c0d21ea0cb3672ab4a7bb76362 Merge branch for-linus-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/mason/linux-btrfs
- 759b2656b259d10935647a92dbfae7fafee6a790 Merge tag nfsd-4.10 of git://linux-nfs.org/~bfields/linux
- b822ee6c5e5ba1f695fc514a65849cdd87618bd3 encx24j600: Fix some checkstyle warnings
- ebe5236d06abcdb1beb93ffbab73557d5b496824 encx24j600: bugfix - always move ERXTAIL to next packet in encx24j600_rx_packets
- ea7a2b9ac853d8c3afd929952ad4b3cb65ba329c Merge branch hisilicon-netdev-dev
- 8cd1f70f205a1c684037f06906566ddb3066d659 net: ethernet: hip04: Call SET_NETDEV_DEV()
- 2087d421a5a1af4883e3cf0afb93823b7e12132a net: ethernet: hisi_femac: Call SET_NETDEV_DEV()
- 66e2809dd324f0ab5e1f9d997b40d4d31a2e42b1 net: dsa: mv88e6xxx: Fix opps when adding vlan bridge
- e28ceeb10cd1883a4b6528c17a2b1f2024e35cad net/3com/3c515: Fix timer handling, prevent leaks and crashes
- 9a19a6db37ee0b7a6db796b3dcd6bb6e7237d6ea Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/viro/vfs
- bd9999cd6a5eb899504ce14c1f70c5479143bbbc Merge tag media/v4.10-1 of git://git.kernel.org/pub/scm/linux/kernel/git/mchehab/linux-media
- 9dfe495c7b4896fb88aa745660254a9704ae5930 Merge tag edac/v4.10-1 of git://git.kernel.org/pub/scm/linux/kernel/git/mchehab/linux-edac
- 9936f44add987355a7d79d52e48cd12255651c0d Merge branch for-linus-4.10-rc1 of git://git.kernel.org/pub/scm/linux/kernel/git/rw/uml
- 70f56cbbdc4ffccbea77e6f51ce9afcbda5fc20f Merge tag nios2-v4.10-rc1 of git://git.kernel.org/pub/scm/linux/kernel/git/lftan/nios2
- f26e8817b235d8764363bffcc9cbfc61867371f2 Merge branch next into for-linus
- de399813b521ea7e38bbfb5e5b620b5e202e5783 Merge tag powerpc-4.10-1 of git://git.kernel.org/pub/scm/linux/kernel/git/powerpc/linux
- 57ca04ab440168e101da746ef9edd1ec583b7214 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/s390/linux
- 3f5ad8be3713572f3946b69eb376206153d0ea2d KVM: hyperv: fix locking of struct kvm_hv fields
- 868f036fee4b1f934117197fb93461d2c968ffec libnvdimm: fix mishandled nvdimm_clear_poison() return value
- 067161281f428aa7c6e153e06aab7b5fe1ed1e98 watchdog: it87_wdt: add IT8620E ID
- f01d74cc5a2aefa0ba16e2821086a1f2d0a2c899 watchdog: mpc8xxx: Remove unneeded linux/miscdevice.h include
- 724284a323c4cdea6c1bb1448247ffc858f2bd1d watchdog: octeon: Remove unneeded linux/miscdevice.h include
- 054ae19422859c394d5f26a8756ed57d332f6284 watchdog: bcm2835_wdt: set WDOG_HW_RUNNING bit when appropriate
- 1d8565ee4f5bd9fccb738e53d6b9fc7a559f7d2b watchdog: loongson1: Add Loongson1 SoC watchdog driver
- b6621df5c87603310c3f94903bb30adbfeb9aa69 watchdog: cpwd: remove memory allocate failure message
- 72106c1894aa4e26ab403282cc7617fcb07d3d4d watchdog: da9062/61: watchdog driver
- bb79036215e2ca9d7ef5bd1461981396989c40da intel-mid_wdt: Error code is just an integer
- 31ecad65b011d64dfc80cab7c968078171aa2642 intel-mid_wdt: make sure watchdog is not running at startup
- 9eff1140a82db8c5520f76e51c21827b4af670b3 watchdog: mei_wdt: request stop on reboot to prevent false positive event
- 4cfccbdaa234b6564326ed3bf18c38f73693fe14 watchdog: hpwdt: changed maintainer information
- 35ffa961df7ed13b3701bdb546f08849921e50dc watchdog: jz4740: Fix modular build
- f06f35c66fdbd5ac38901a3305ce763a0cd59375 watchdog: qcom: fix kernel panic due to external abort on non-linefetch
- 9b3865749589d67f612d71b447847223b2321408 watchdog: davinci: add support for deferred probing
- 807f0b2d22b0934fc1c67df8a4961044bd76b081 watchdog: meson: Remove unneeded platform MODULE_ALIAS
- 0f3871f8a535d7e79512fe56f4a5a161b3a03422 watchdog: Standardize leading tabs and spaces in Kconfig file
- f99524dced4c89af52a82a369cb61a111b9169b3 watchdog: max77620_wdt: fix module autoload
- 57d77c62536ea0f388c840c8ac7e94be54425308 watchdog: bcm7038_wdt: fix module autoload
- 42cd4ed888393b2bc8ddfd277aa2d0ec0c7e0259 spi: armada-3700: Set mode bits correctly
- 9e4d59ada4d602e78eee9fb5f898ce61fdddb446 ASoC: hdmi-codec: use unsigned type to structure members with bit-field
- 8759fec4af222f338d08f8f1a7ad6a77ca6cb301 crypto: marvell - Copy IVDIG before launching partial DMA ahash requests
- 83337e544323a8bd7492994d64af339175ac7107 iscsi-target: Return error if unable to add network portal
- a3960ced84b8049783de678abf8cd680ee14175f target: Fix spelling mistake and unwrap multi-line text
- a91918cd3ea11f91c68e08e1e8ce1b560447a80e target/iscsi: Fix double free in lio_target_tiqn_addtpg()
- c3c8699664800a68600f1988302173067eaeaffa ovl: fix reStructuredText syntax errors in documentation
- 313684c48cc0e450ab303e1f82130ee2d0b50274 ovl: fix return value of ovl_fill_super
- 32a3d848eb91a298334991f1891e12e0362f91db ovl: clean up kstat usage
- 9aba652190f8cdced66967c97d6159de0cc8478e ovl: fold ovl_copy_up_truncate() into ovl_copy_up()
- 97c684cc911060ba7f97c0925eaf842f159a39e8 ovl: create directories inside merged parent opaque
- 5cf5b477f0ca33f56a30c7ec00e61a6204da2efb ovl: opaque cleanup
- c5bef3a72b9d8a2040d5e9f4bde03db7c86bbfce ovl: show redirect_dir mount option
- 3ea22a71b65b6743a53e286ff4991a06b9d2597c ovl: allow setting max size of redirect
- 688ea0e5a0e2278e2fcd0014324ab1ba68e70ad7 ovl: allow redirect_dir to default to on
- d15951198eaccb92c6b49e62cb72f5ff62da2236 ovl: check for emptiness of redirect dir
- a6c6065511411c57167a6cdae0c33263fb662b51 ovl: redirect on rename-dir
- 02b69b284cd7815239fabfe895bfef9a9eb5a3ce ovl: lookup redirects
- e28edc46b8e29d2a4c10263cd7769e657582fff4 ovl: consolidate lookup for underlying layers
- 48fab5d7c750ff70aa77c36a44c01211020bbc98 ovl: fix nested overlayfs mount
- 6b2d5fe46fa8f4fc1c5262c73930b9a2a94db2e3 ovl: check namelen
- bbb1e54dd53cf83863e856dd5518ce5e58791115 ovl: split super.c
- 2b8c30e9ef1492c34099b97365115504f6cd6995 ovl: use d_is_dir()
- 8ee6059c58ea525f76b4efb98f8f66845f697efc ovl: simplify lookup
- 3ee23ff1025a18796607cf4110a8ffa8e2d163fd ovl: check lower existence of rename target
- 370e55ace59c2d3ed8f0ca933155030b9652e04f ovl: rename: simplify handling of lower/merged directory
- 38e813db61c3951ef76d071ca7d2f46c2e939b80 ovl: get rid of PURE type
- 2aff4534b6c48c465c2ba3bca310646652318e16 ovl: check lower existence when removing
- c412ce498396097cb96b3e24e062752312a962c9 ovl: add ovl_dentry_is_whiteout()
- 99f5d08e3640c8319f353e6c883da150c48067f6 ovl: dont check sticky
- 804032fabb3b5270a7bc355f478eed45b1a5b041 ovl: dont check rename to self
- ca4c8a3a800039c2681d609c5b7491c1bd17c0a7 ovl: treat special files like a regular fs
- 6c02cb59e6fe1dfbe4352dbf089e7a16ef6bfac6 ovl: rename ovl_rename2() to ovl_rename()
- 2ea98466491b7609ace297647b07c28d99ef3722 ovl: use vfs_clone_file_range() for copy up if possible
- 31c3a7069593b072bd57192b63b62f9a7e994e9a Revert ovl: get_write_access() in truncate
- 2d8f2908e60be605dac89145c3edb5e42631d061 ovl: update doc
- b335e9d9944d9c66cdaadc5e295cc845c31e40a0 vfs: fix vfs_clone_file_range() for overlayfs files
- 031a072a0b8ac2646def77aa310a95016c884bb0 vfs: call vfs_clone_file_range() under freeze protection
- 913b86e92e1f68ab9db00ccb0fecf594732511e5 vfs: allow vfs_clone_file_range() across mount points
- 3616119da484699e7045957c009c13d778563874 vfs: no mnt_want_write_file() in vfs_{copy,clone}_file_range()
- 8d3e2936375bacce6abacbce3917d667e4133409 Revert vfs: rename: check backing inode being equal
- beef5121f3a4d1566c8ab8cd99b4e001862048cf Revert af_unix: fix hard linked sockets on overlay
- 659643f7d81432189c2c87230e2feee4c75c14c1 drm/i915/gvt/kvmgt: add vfio/mdev support to KVMGT
- f440c8a572d7e0002d5c2c8dbd740130ad8ffa5b drm/i915/gvt/kvmgt: read/write GPA via KVM API
- c55b1de02d68e4343045391c0f4978c0bc5a9447 drm/i915/gvt/kvmgt: replace kmalloc() by kzalloc()
- ebfb0184ef560897fad35005989e82433419202c Merge branch synaptics-rmi4 into next
- f43d3ec3a889c7f6a196f3b6d6b13345ee46af8a Input: imx6ul_tsc - generalize the averaging property
- c6f6634721c871bfab4235e1cbcad208d3063798 Merge branch next of git://git.kernel.org/pub/scm/linux/kernel/git/scottwood/linux into next
- 9cf8bd529c6ba81402ebf6b7a56307b0787e4f93 libnvdimm: replace mutex_is_locked() warnings with lockdep_assert_held
- 73e2e0c9b13c97df1c8565f6e158caac3c481b44 Merge tag nfs-for-4.10-1 of git://git.linux-nfs.org/projects/trondmy/linux-nfs
- ed3c5a0be38c180ab0899a0f52719e81f36b87a1 Merge tag for_linus of git://git.kernel.org/pub/scm/linux/kernel/git/mst/vhost
- 47057abde515155a4fee53038e7772d6b387e0aa nfsd: add support for the umask attribute
- 66d466722c39f663b2bbeb44ba4f9419a548fa23 Merge branch for-linus of git://git.armlinux.org.uk/~rmk/linux-arm
- 991688bfc63550b8c7ab9fb1de2feb44e3071d29 Merge tag armsoc-drivers of git://git.kernel.org/pub/scm/linux/kernel/git/arm/arm-soc
- 482c3e8835e9e9b325aad295c21bd9e965a11006 Merge tag armsoc-dt64 of git://git.kernel.org/pub/scm/linux/kernel/git/arm/arm-soc
- 786a72d79140028537382fa63bea63d5640c27d6 Merge tag armsoc-dt of git://git.kernel.org/pub/scm/linux/kernel/git/arm/arm-soc
- 3bd776bbda9e8f2453e7361d340933dccd067fc3 Merge tag armsoc-arm64 of git://git.kernel.org/pub/scm/linux/kernel/git/arm/arm-soc
- 775fadd09e7beac2fc61cc0517629e9fa69bdb56 Merge tag armsoc-defconfig of git://git.kernel.org/pub/scm/linux/kernel/git/arm/arm-soc
- e79ab194d15e1baa25540cb9efaf2a459cf4bc32 Merge tag armsoc-soc of git://git.kernel.org/pub/scm/linux/kernel/git/arm/arm-soc
- 3ec5e8d82b1a4ee42c8956099d89b87917dd3ba5 Merge tag armsoc-fixes-nc of git://git.kernel.org/pub/scm/linux/kernel/git/arm/arm-soc
- 09dee2a608a4a7d42f021f83084ade7de2415d7e Merge tag linux-kselftest-4.10-rc1-update of git://git.kernel.org/pub/scm/linux/kernel/git/shuah/linux-kselftest
- d25b6af91ec600faaff3a7e863f19d3e16593e52 Merge tag arc-4.10-rc1-part1 of git://git.kernel.org/pub/scm/linux/kernel/git/vgupta/arc
- 6bdf1e0efb04a1716373646cb6f35b73addca492 Makefile: drop -D__CHECK_ENDIAN__ from cflags
- 378d5a40fa2c251b31d64e9a7e746f71c2e39b14 fs/logfs: drop __CHECK_ENDIAN__
- dc67a9f70c0b43b0d1f3aa04407e67ca4cf9b241 Documentation/sparse: drop __CHECK_ENDIAN__
- 9efeccacd3a486128d3add611dd4cefb5b60a58c linux: drop __bitwise__ everywhere
- 46d832f5e2102cce455672c5a0b8cbe97e27fe42 checkpatch: replace __bitwise__ with __bitwise
- 9536099a8ef185abc0497d5e995ce23bd587a96e Documentation/sparse: drop __bitwise__
- 376a5fb34b04524af501a0c5979c5920be940e05 tools: enable endian checks for all sparse builds
- 05de97003c773e7881e4df3f767b81a6508107f2 linux/types.h: enable endian checks for all sparse builds
- cecdbdc3771e5b8583a9b43b03335b4223a9a6c9 virtio_mmio: Set dev.release() to avoid warning
- 8d390464bf22a47252eb976efae2f462c5c884e5 vhost: remove unused feature bit
- 0c7eaf5930e145b9f1a0121bd5813a05b0fc77f2 virtio_ring: fix description of virtqueue_get_buf
- b9fd06d0dae38a88efa4b770dfa9db7dcbe3cda9 vhost/scsi: Remove unused but set variable
- ea9156fb3b71d9f7e383253eaff9dd7498b23276 tools/virtio: use {READ,WRITE}_ONCE() in uaccess.h
- 9d1b972f8a25bba01ecfc1d90d7a2fbf1923d052 vringh: kill off ACCESS_ONCE()
- 5da889c795b1fbefc9d8f058b54717ab8ab17891 tools/virtio: fix READ_ONCE()
- dbaf0624ffa57ae6e7d87a823185ccd9a7852d3c crypto: add virtio-crypto driver
- 809ecb9bca6a9424ccd392d67e368160f8b76c92 vhost: cache used event for better performance
- 6c083c2b8a0a110cad936bc0a2c089f0d8115175 vsock: lookup and setup guest_cid inside vhost_vsock_lock
- a3cbec69727c8c149ee2b3652e184818cc269fe6 virtio_pci: split vp_try_to_find_vqs into INTx and MSI-X variants
- 66f2f55542270c44d67f05533594f75404c1481a virtio_pci: merge vp_free_vectors into vp_del_vqs
- 9f8196cc05caa9aba19f38f29c5f9a12722986c4 virtio_pci: remove the call to vp_free_vectors in vp_request_msix_vectors
- fa3a3279354e5f7a13ec16f2c9f5e39124745332 virtio_pci: use pci_alloc_irq_vectors
- d41795978c47fa87b6514a0f2238958b7e8319a0 virtio: clean up handling of request_irq failure
- 179a7ba6806805bd4cd7a5e4574b83353c5615ad Merge tag trace-v4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/rostedt/linux-trace
- 5e176d6973bdac04d9f298ca384c39f08eb084cb Merge tag for-linus-4.10-ofs1 of git://git.kernel.org/pub/scm/linux/kernel/git/hubcap/linux
- 39d2c3b96e072c8756f3b980588fa516b7988cb1 Merge tag upstream-4.10-rc1 of git://git.infradead.org/linux-ubifs
- e18bf801f1501e15830db5fa927a6e2832d49d7b Merge tag platform-drivers-x86-v4.10-1 of git://git.infradead.org/users/dvhart/linux-platform-drivers-x86
- 8600b697cd4787ac3ce053d48ca7301836fd0c55 Merge branch i2c/for-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/wsa/linux
- 0ab7b12c49b6fbf2d4d0381374b82935f949be5f Merge tag pci-v4.10-changes of git://git.kernel.org/pub/scm/linux/kernel/git/helgaas/pci
- cb2bf25145e0d2abef20f47dd2ae55bff97fd9cb platform/x86: thinkpad_acpi: Initialize local in_tablet_mode and type
- a9a16a6d136593c9e6f72e481b2b86ae1d8d1fce Merge tag iommu-updates-v4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/joro/iommu
- d3ea547853852481dc5eba6d4cb13adab1564d0b rdma: fix buggy code that the compiler warns about
- 8a19e7fa085e22519f2b069406f82ae24d3f3c93 drm/amdgpu: refine set clock gating for tonga/polaris
- ca18b84986ccde80fe3ba6c2aed4408b25c0da8c drm/amdgpu: initialize cg flags for tonga/polaris10/polaris11.
- 398d82ccbd8b97e67d2503f09345de5d63a80c56 drm/amdgpu: add new gfx cg flags.
- ad1830d504d85233392215c9966e5876b99c481e drm/amdgpu: fix pg cant be disabled by PG mask.
- c4d17b81244d23e7727f0bf68f0f63905e871a73 drm/amdgpu: always initialize gfx pg for gfx_v8.0.
- 98fccc78bc29e35f7204f5f6cf7f0a923e335222 drm/amdgpu: enable AMD_PG_SUPPORT_CP in Carrizo/Stoney.
- 202e0b227b906cb80a2791f21216a55d9468d61b drm/amdgpu: fix init save/restore list in gfx_v8.0
- eb584241226958d45aa1f07f4f6a6ea9da98b29e drm/amdgpu: fix enable_cp_power_gating in gfx_v8.0.
- 54971406b7731efd5dbe0b1ccc42dfbd8af1f3b2 drm/amdgpu: disable uvd pg on Tonga.
- 4d5b57e05a67c3cfd8e2b2a64ca356245a15b1c6 Merge tag for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/dledford/rdma
- 6df8b74b1720db1133ace0861cb6721bfe57819a Merge tag devicetree-for-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/robh/linux
- 57d64e6f5fac7b47dd03487f5f2670a7f0c67335 Merge tag pwm/for-4.10-rc1 of git://git.kernel.org/pub/scm/linux/kernel/git/thierry.reding/linux-pwm
- 19c75bcbe0113cbbf05e4d89e0502a23358bfca9 Merge branch linus of git://git.kernel.org/pub/scm/linux/kernel/git/herbert/crypto-2.6
- d40fc181ebec6b1d560e2167208276baa4f3bbf0 samples/bpf: Make samples more libbpf-centric
- a5580c7f7a6d078696458d283df5d6547ad1c740 tools lib bpf: Add flags to bpf_create_map()
- 83d994d02bf4594d6bfa9b2b67befb6cff7f9380 tools lib bpf: use __u32 from linux/types.h
- 0cb34dc2a37290f4069c5b01735c9725dc0a1b5c tools lib bpf: Sync {tools,}/include/uapi/linux/bpf.h
- e216874cc1946d28084fa90e495e02725a29e25f perf annotate: Fix jump target outside of function address range
- 3ee2eb6da20db1edad31070da38996e8e0f8adfa perf annotate: Support jump instruction with target as second operand
- 23dc4f1586159470aac707caae526824dd077e25 perf record: Force ignore_missing_thread for uid option
- a359c17a7e1a9c99384499cf7b43d80867080789 perf evsel: Allow to ignore missing pid
- 38af91f01de0e160c17ae380acb5bab5d51066f4 perf thread_map: Add thread_map__remove function
- 83c2e4f3968d6871eed295f2f5675d3d70b01afa perf evsel: Use variable instead of repeating lengthy FD macro
- 631ac41b46d293fb3ee43a809776c1663de8d9c6 perf mem: Fix --all-user/--all-kernel options
- 7e6a79981b7a797b37b1dbeca3fd6ae1cb6d881f perf tools: Remove some needless __maybe_unused
- ba957ebb54893acaf3dc846031073a63f021cee1 perf sched timehist: Show callchains for idle stat
- 07235f84ece6b66f43334881806aad3467cf3d84 perf sched timehist: Add -I/--idle-hist option
- a4b2b6f56e0cfe729cf89318d44b6a875b31d95a perf sched timehist: Skip non-idle events when necessary
- 699b5b920db04a6ff5c03a519e4c182aeb350952 perf sched timehist: Save callchain when entering idle
- 3bc2fa9cb829ccf6527e7117d9af769d93ee6d39 perf sched timehist: Introduce struct idle_time_data
- 96039c7c52e03b7d6dd773664e74b79e3ae9856a perf sched timehist: Split is_idle_sample()
- aeafd623f866c429307e3a4a39998f5f06b4f00e perf tools: Move headers check into bash script
- ee84595a91c60d33cbf1d5b941b04a3ee6cf7ce0 afs, rxrpc: Update the MAINTAINERS file
- b9a0deb96b8b5a7e896da183974ba6feb727f14a redo: radix tree test suite: fix compilation
- 8fa9a697ab083af0f4a2807869752685ed8a7a6a printk: Remove no longer used second struct cont
- 30b507051dd1f79bbedce79cb37dc0ef31f5fb6c xtensa: update DMA-related Documentation/features entries
- 644b213ccced83495eb54dd48764f7e963bcc1c0 xtensa: configure shared DMA pool reservation in kc705 DTS
- 9d2ffe5c62554f2795859bb661eb138759eee980 xtensa: enable HAVE_DMA_CONTIGUOUS
- 512f09801b356c54baef62543e51169f03b2e642 cpu/hotplug: Clarify description of __cpuhp_setup_state() return value
- d0905ca757bc40bd1ebc261a448a521b064777d7 target/user: Fix use-after-free of tcmu_cmds if they are expired
- 83781d180b219bd079ae72b341ee3f21fb236e97 KVM: x86: Expose Intel AVX512IFMA/AVX512VBMI/SHA features to guest.
- 37b9a671f346a184c4e381b32ee465cf7d248ae8 kvm: nVMX: Correct a VMX instruction error code for VMPTRLD
- 5372e155a28f56122eb10db56d4130f481a89cd7 x86/mm: Drop unused argument removed from sync_global_pgds()
- c2b36129ce53a22b89dd2b88db33e7ffdefe0f41 ASoC: topology: kfree kcontrol->private_value before freeing kcontrol
- c0af52437254fda8b0cdbaae5a9b6d9327f1fcd5 genirq/affinity: Fix node generation from cpumask
- c1a9eeb938b5433947e5ea22f89baff3182e7075 tick/broadcast: Prevent NULL pointer dereference
- 9bf11ecce5a2758e5a097c2f3a13d08552d0d6f9 clocksource/dummy_timer: Move hotplug callback after the real timers
- 0ea617a298dcdc2251b4e10f83ac3f3e627b66e3 ASoC: rsnd: dont double free kctrl
- 4838a0def07f5611347860b1fc0129c3fe77cc02 EDAC: Document HW_EVENT_ERR_DEFERRED type
- 6b1fb6f7037221981fb2cf1822c31b5fba1b9c22 edac.rst: move concepts dictionary from edac.h
- e002075819d987dec3bf9fa3ca98ad19fa86ae0f edac: fix kenel-doc markups at edac.h
- 66c222a02fadfd7cc62c754c12379d6bb08eaf77 edac: fix kernel-doc tags at the drivers/edac_*.h
- b73bbad352a50fb2d8dd42241b534a3dace03b49 edac: adjust docs location at MAINTAINERS and 00-INDEX
- 6634fbb6b6356e6f5b428a349952b368b25d514d driver-api: create an edac.rst file with EDAC documentation
- e01aa14cf2e7ff6d39614f8087800d08ba1629b2 edac: move documentation from edac_mc.c to edac_core.h
- fdaf0b3505f330b8a56ddec4e904049be998d6d1 edac: move documentation from edac_pci*.c to edac_pci.h
- 5336f75499bbb293910b3502b3c4a4f9ab9ff078 edac: move documentation from edac_device to edac_core.h
- 78d88e8a3d738f1ce508cd24b525d2e6cdfda1c1 edac: rename edac_core.h to edac_mc.h
- 6d8ef2472410c8ab004729a71ec829a224699a08 edac: move EDAC device definitions to drivers/edac/edac_device.h
- 0b892c717714334890ea179a2dc1941a223e446f edac: move EDAC PCI definitions to drivers/edac/edac_pci.h
- fd77f6ba7b3ae5f02f8d4d706df6534ae9722dce docs-rst: admin-guide: add documentation for EDAC
- 9c058d24ccb36d91650a84d9cbc27409f769d9a9 edac.txt: Improve documentation, adding RAS introduction
- e4b5301674c0d2d866de767f02a44bc322af8d7f edac.txt: update information about newer Intel CPUs
- 96714bd7078fecc91631596c3ca4ddd0fd3ecde6 edac.txt: remove info that the Nehalem EDAC is experimental
- b27a2d04feb6969e74942378d5012d84877d3544 edac.txt: convert EDAC documentation to ReST
- 032d0ab743ff8ee340d5fc2a00c833dfe74c49e4 edac.txt: add a section explaining the dimmX and rankX directories
- 723061753724009a6e3cbec9deba7860dba2df99 edac: edac_core.h: remove prototype for edac_pci_reset_delay_period()
- a2c223b5ed64d7a0266cf1a3e0b2726647a98ed8 edac: edac_core.h: get rid of unused kobj_complete
- 5bae156241e05d25171b18ee43e49f103c3f8097 x86/tsc: Force TSC_ADJUST register to value >= zero
- 6a369583178d0b89c2c3919c4456ee22fee0f249 x86/tsc: Validate TSC_ADJUST after resume
- 65390ea01ce678379da32b01f39fcfac4903f256 Merge branch patchwork into v4l_for_linus
- aec03f89e905dca9ce4b061e03ee1da3a3eb3432 ACPI/NUMA: Do not map pxm to node when NUMA is turned off
- 4370a3ef39f3d07342a1ae9967701bd697c8d9df x86/acpi: Use proper macro for invalid node
- 427d77a32365d5f942d335248305a5c237baf63a x86/smpboot: Prevent false positive out of bounds cpumask access warning
- a17d93ff3a950fefaea40e4a4bf3669b9137c533 mac80211: fix legacy and invalid rx-rate report
- 374402a2a1dfbbee8ab1a5a32ec4887bf8c15d52 cifs_get_root shouldnt use path with tree name
- 395664439c4945e4827543e3ca80f7b74e1bf733 Fix default behaviour for empty domains and add domainauto option
- c6fc663e90e56fdcaa3ad62801cfa99f287b8bfc cifs: use %16phN for formatting md5 sum
- c4364f837caf618c2fdb51a2e132cf29dfd1fffa Merge branches work.namei, work.dcache and work.iov_iter into for-linus
- 5cc60aeedf315a7513f92e98314e86d515b986d1 Merge tag xfs-for-linus-4.10-rc1 of git://git.kernel.org/pub/scm/linux/kernel/git/dgc/linux-xfs
- 5c2992ee7fd8a29d04125dc0aa3522784c5fa5eb printk: remove console flushing special cases for partial buffered lines
- 5aa068ea4082b39eafc356c27c9ecd155b0895f6 printk: remove games with previous record flags
- f83f12d660d11718d3eed9d979ee03e83aa55544 vsock/virtio: fix src/dst cid format
- 819483d806f4324b42a25f8dd760735ae659141c vsock/virtio: mark an internal function static
- 6c7efafdd5c1639084dd08ace82567e19a4032be vsock/virtio: add a missing __le annotation
- 72952cc0614b61650b2b13f57752a6dd82cbeae5 vhost: add missing __user annotations
- 2f952c0105d14bd46bb6d6a3cc03ad789a381228 vhost: make interval tree static inline
- 3373755a415c9c8024d26cf32fd812a8cdb82541 drm/virtio: annotate virtio_gpu_queue_ctrl_buffer_locked
- f862e60f8d52dae33c9f72afc20fab691a89f0bd drm/virtio: fix lock context imbalance
- 8854a56f3e71703e0253697e4cc82b20acf732dc drm/virtio: fix endianness in primary_plane_update
- 7328fa64aa30405c2d6abd44bb6866e914dba35d virtio_console: drop unused config fields
- 196202be3cfc75762b0075e2d69f55cef949c610 Merge tag for-linus-4.10 of git://git.code.sf.net/p/openipmi/linux-ipmi
- 1d0fd57a50aa372dd2e84b16711023cbcd826cb8 logfs: remove from tree
- e3842cbfe0976b014288147b130551d8bf52b96c Merge tag dmaengine-4.10-rc1 of git://git.infradead.org/users/vkoul/slave-dma
- c60923cb9cb5e042790839d553ed77e68ef45adf virtio_ring: fix complaint by sparse
- 61bd405f4edcf7396cc7853e48212342feead06d virtio_pci_modern: fix complaint by sparse
- 4d98ead183a2be77bfea425d5243e32629eaaeb1 Merge tag modules-for-v4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/jeyu/linux
- a57cb1c1d7974c62a5c80f7869e35b492ace12cd Merge branch akpm (patches from Andrew)
- cf1b3341afab9d3ad02a76b3a619ea027dcf4e28 Merge branch for-linus of git://git.kernel.dk/linux-block
- 80eabba70260dcb55b05098f6c1fecbe5c0e518b Merge branch for-4.10/fs-unmap of git://git.kernel.dk/linux-block
- 852d21ae1fcdf0e4de6b5bfa730d29cb013c7ff3 docs: add back Documentation/Changes file (as symlink)
- e1e14ab8411df344a17687821f8f78f0a1e73cbb radix tree test suite: delete unused rcupdate.c
- 092bc0b225a9bdb6dca0959ddd6826afb6d40747 radix tree test suite: add new tag check
- e8de4340767dd002978c285e3adddaeda8ac652c radix-tree: ensure counts are initialised
- bbe9d71f2c545398987a6fea5090a6ca76f4a8dc radix tree test suite: cache recently freed objects
- de1af8f62a78ea8abcc2dddb6de622e4069a368e radix tree test suite: add some more functionality
- 424251a4a929a1b6dff2056d49135e3805132e32 idr: reduce the number of bits per level from 8 to 6
- 444306129a920015a2cc876d13fcbf52382f39bd rxrpc: abstract away knowledge of IDR internals
- 37f4915fef0572e41ab91b7d3f7feb237cddbd92 tpm: use idr_find(), not idr_find_slowpath()
- 99c494077e2d4282a17120a772eecc00ec3004cc idr: add ida_is_empty
- 3e3cdc68bede179a957fcd6be7b833a83df4e5de radix tree test suite: check multiorder iteration
- a90eb3a2a405cf7e96093ed531a285067dfdbc9d radix-tree: fix replacement for multiorder entries
- 2791653a6814d170fa893344618563a7b1da95c6 radix-tree: add radix_tree_split_preload()
- e157b555945fb16ddc6cce605a1eb6b4135ea5f1 radix-tree: add radix_tree_split
- 175542f575723e43f897ddb09d0011c13f7cf0ec radix-tree: add radix_tree_join
- 268f42de718128cd0301293177e79c08c38e39a6 radix-tree: delete radix_tree_range_tag_if_tagged()
- 478922e2b0f41567e4a530771bfb3f693f857d45 radix-tree: delete radix_tree_locate_item()
- 148deab223b23734069abcacb5c7118b0e7deadc radix-tree: improve multiorder iterators
- b35df27a39f40e39fabf1b1e9569c7b24e1add6a btrfs: fix race in btrfs_free_dummy_fs_info()
- 218ed7503aee07c7758dcbdd782e8c1a25c9f1e9 radix-tree: improve dump output
- bc412fca6edc25bbbe28b6449512e15ebb1573ae radix-tree: make radix_tree_find_next_bit more useful
- 9498d2bb34b0866829c313569df35e77a83f12eb radix-tree: create node_tag_set()
- 91d9c05ac6c788531136888d31ef18c6a0ec160f radix-tree: move rcu_head into a union with private_list
- 91b9677c4c1242a3d0afd76d0e91f43808243b92 radix-tree: fix typo
- 0629573e6bbd60f20ed2d7a91da1214a6274e751 radix tree test suite: use common find-bit code
- b328daf3b7130098b105c18bdae694ddaad5b6e3 tools: add more bitmap functions
- 101d9607fffefdfc9e3922f0ac9061a61edda1b0 radix tree test suite: record order in each item
- 3ad75f8a1d9b047989059c67afc38d57161270e9 radix tree test suite: handle exceptional entries
- af1c5cca9030f1bb935463ceb8274bfe82719128 radix tree test suite: use rcu_barrier
- cfa40bcfd6fed7010b1633bf127ed8571d3b607e radix tree test suite: benchmark for iterator
- ba20cd60c97945f0de9fe313f869b3a5855e1503 radix tree test suite: iteration test misuses RCU
- 061ef3936b16edc8f779d403d569392505665ed5 radix tree test suite: make runs more reproducible
- 6df5ee786786ddafdddc922344a0b789f5b25fa4 radix tree test suite: free preallocated nodes
- 847d357635ce4c63b8901ab81333586a0f115fa5 radix tree test suite: track preempt_count
- 31023cd66468359790beb046b6808fe0444672a2 radix tree test suite: allow GFP_ATOMIC allocations to fail
- ebb9a9aedb95f697673a96a26ff0322a13676381 tools: add WARN_ON_ONCE
- 4b4bb46d00b386e1c972890dc5785a7966eaa9c0 dax: clear dirty entry tags on cache flush
- 2f89dc12a25ddf995b9acd7b6543fe892e3473d6 dax: protect PTE modification on WP fault by radix tree entry lock
- a6abc2c0e77b16480f4d2c1eb7925e5287ae1526 dax: make cache flushing protected by entry lock
- cae1240257d9ba4b40eb240124c530de8ee349bc mm: export follow_pte()
- a19e25536ed3a20845f642ce531e10c27fb2add5 mm: change return values of finish_mkwrite_fault()
- 66a6197c118540d454913eef24d68d7491ab5d5f mm: provide helper for finishing mkwrite faults
- 997dd98dd68beb2aea74cac53e7fd440cc8dba68 mm: move part of wp_page_reuse() into the single call site
- a41b70d6dfc28b9e1a17c2a9f3181c2b614bfd54 mm: use vmf->page during WP faults
- 38b8cb7fbb892503fe9fcf748ebbed8c9fde7bf8 mm: pass vm_fault structure into do_page_mkwrite()
- 97ba0c2b4b0994044e404b7a96fc92a2e0424534 mm: factor out common parts of write fault handling
- b1aa812b21084285e9f6098639be9cd5bf9e05d7 mm: move handling of COW faults into DAX code
- 9118c0cbd44262d0015568266f314e645ed6b9ce mm: factor out functionality to finish page faults
- 3917048d4572b9cabf6f8f5ad395eb693717367c mm: allow full handling of COW faults in ->fault handlers
- 2994302bc8a17180788fac66a47102d338d5d0ec mm: add orig_pte field into vm_fault
- fe82221f57ea6840a4238a8e077e3f93f257a03f mm: use passed vm_fault structure for in wp_pfn_shared()
- 936ca80d3773bd9b6dda8a0dfd54425f9ec1be9d mm: trim __do_fault() arguments
- 667240e0f2e13e792a5af99b3c34dfab12ef125b mm: use passed vm_fault structure in __do_fault()
- 0721ec8bc156fafc9057ec1df95cdb3bbc3cbae8 mm: use pgoff in struct vm_fault instead of passing it separately
- 1a29d85eb0f19b7d8271923d8917d7b4f5540b3e mm: use vmf->address instead of of vmf->virtual_address
- 82b0f8c39a3869b6fd2a10e180a862248736ec6f mm: join struct fault_env and vm_fault
- 8b7457ef9a9eb46cd1675d40d8e1fd3c47a38395 mm: unexport __get_user_pages_unlocked()
- 5b56d49fc31dbb0487e14ead790fc81ca9fb2c99 mm: add locked parameter to get_user_pages_remote()
- 370b262c896e5565b271a3ea3abee4d0914ba443 ipc/sem: avoid idr tree lookup for interrupted semop
- b5fa01a22e4ba9e3ca6de7cb94c3d21e42da449c ipc/sem: simplify wait-wake loop
- f150f02cfbc7b6b980e260856555abd73235a6b0 ipc/sem: use proper list api for pending_list wakeups
- 4663d3e8f21652f33c698fcc2bf20f61499d9c3e ipc/sem: explicitly inline check_restart
- 4ce33ec2e42d4661bf05289e213bc088eecb9132 ipc/sem: optimize perform_atomic_semop()
- 9ae949fa382b080170f9d3c8bd9dea951cf52ee7 ipc/sem: rework task wakeups
- 248e7357cf8ec50bdaca68dce7c488ce843b6b93 ipc/sem: do not call wake_sem_queue_do() prematurely ... as this call should obviously be paired with its _prepare()
- 7a5c8b57cec93196b3e84e3cad2ff81ae0faed78 sparc: implement watchdog_nmi_enable and watchdog_nmi_disable
- 73ce0511c43686095efd2f65ef564aab952e07bc kernel/watchdog.c: move hardlockup detector to separate file
- 249e52e35580fcfe5dad53a7dcd7c1252788749c kernel/watchdog.c: move shared definitions to nmi.h
- 22722799de869912fb541c2c85b51cec4226c614 ktest.pl: fix english
- b5fc8c6c000aa083a671cd8f1736d04081bf65aa drivers/net/wireless/intel/iwlwifi/dvm/calib.c: simplfy min() expression
- b6f8a92c9ca835b4a079ecee8433d0d110398448 posix-timers: give lazy compilers some help optimizing code away
- 63980c80e1e99cb324942f3b5e59657025af47c0 ipc/shm.c: coding style fixes
- 999898355e08ae3b92dfd0a08db706e0c6703d30 ipc: msg, make msgrcv work with LONG_MIN
- db2aa7fd15e857891cefbada8348c8d938c7a2bc initramfs: allow again choice of the embedded initram compression algorithm
- 35e669e1a254e8b60d4a8983205b383666cc01ca initramfs: select builtin initram compression algorithm on KConfig instead of Makefile
- 34aaff40b42148b23dcde40152480e25c7d2d759 kdb: call vkdb_printf() from vprintk_default() only when wanted
- d5d8d3d0d4adcc3aec6e2e0fb656165014a712b7 kdb: properly synchronize vkdb_printf() calls with other CPUs
- d1bd8ead126668a2d6c42d97cc3664e95b3fa1dc kdb: remove unused kdb_event handling
- 2d13bb6494c807bcf3f78af0e96c0b8615a94385 kernel/debug/debug_core.c: more properly delay for secondary CPUs
- db862358a4a96f52d3b0c713c703828f90d97de9 kcov: add more missing includes
- 0462554707d62d53fc400ecb3cc19d7f9c786b95 Kconfig: lib/Kconfig.ubsan fix reference to ubsan documentation
- 700199b0c192c7243539757177782780f5a45afb Kconfig: lib/Kconfig.debug: fix references to Documenation
- 9a29d0fbc2d9ad99fb8a981ab72548cc360e9d4c relay: check array offset before using it
- bd4171a5d4c2827f4ae7a235389648d7c149a41b igb: update code to better handle incrementing page count
- 5be5955425c22df5e25ee0628b57f523437af6dc igb: update driver to make use of DMA_ATTR_SKIP_CPU_SYNC
- 44fdffd70504c15b617686753dfdf9eb0ddf3729 mm: add support for releasing multiple instances of a page
- 0495c3d367944e4af053983ff3cdf256b567b053 dma: add calls for dma_map_page_attrs and dma_unmap_page_attrs
- 4bfa135abec99f4b35b5636f56a6db75ce3c64d7 arch/xtensa: add option to skip DMA sync as a part of mapping
- 33c77e53d838dc27e9d2edec5b6ab6a11861fb32 arch/tile: add option to skip DMA sync as a part of map and unmap
- 68bbc28f616c18b695a13e59adefb9a1fc0c46a0 arch/sparc: add option to skip DMA sync as a part of map and unmap
- a08120017d7d659719d446fb036d500fa9b1e6f9 arch/sh: add option to skip DMA sync as a part of mapping
- 6f774809612d1f1fc800b452ee1ef447a277ec9d arch/powerpc: add option to skip DMA sync as a part of mapping
- f50a2bd298b47e1957f67f794aed90f2c3bd9a10 arch/parisc: add option to skip DMA sync as a part of map and unmap
- 043b42bcbbc6bc87c457b156041d74d51f6cebc2 arch/openrisc: add option to skip DMA sync as a part of mapping
- abdf4799dac6210e3d09d368c4ed19e984c45dce arch/nios2: add option to skip DMA sync as a part of map and unmap
- 9f318d470e37a470d65449f94a06165ea72dbce1 arch/mips: add option to skip DMA sync as a part of map and unmap
- 98ac2fc274e07a22bea43682cf8998f47ffea9d0 arch/microblaze: add option to skip DMA sync as a part of map and unmap
- 38bdbdc7e391f5326a9f27f0bc8be0c175a73567 arch/metag: add option to skip DMA sync as a part of map and unmap
- 5140d2344f1036dadffbb949a60af971b6dde0d3 arch/m68k: add option to skip DMA sync as a part of mapping
- b8a346dd472af45e1ee8cbc77101dad0b836210b arch/hexagon: Add option to skip DMA sync as a part of mapping
- 34f8be79a772094a96da83f52f247cff2bc13978 arch/frv: add option to skip sync on DMA map
- 64c596b59c726514f548e15f13a87010efbff40d arch/c6x: add option to skip sync on DMA map and unmap
- 8c16a2e209d563a1909451c769417a6f953e5b2c arch/blackfin: add option to skip sync on DMA map
- e8b4762c22589a514add9bf9dda7a3050e4fa54c arch/avr32: add option to skip sync on DMA map
- fc1b138de7917d8fda5995aeecdb10c8182d9f75 arch/arm: add option to skip sync on DMA map and unmap
- 8a3385d2d47cd912f28d23bd2225ee37de518d86 arch/arc: add option to skip sync on DMA mapping
- 7560ef39dc0bfebba8f43766d8bb4c1ec5eb66fc sysctl: add KERN_CONT to deprecated_sysctl_warning()
- 8e53c073a41795365eb0e47ae23441dc01c70511 kexec: add cond_resched into kimage_alloc_crash_control_pages
- 401721ecd1dcb0a428aa5d6832ee05ffbdbffbbe kexec: export the value of phys_base instead of symbol address
- 69f58384791ac6da4165ce8e6defd6f408f4afdf Revert kdump, vmcoreinfo: report memory sections virtual addresses
- 760c6a9139c37e16502362b22656d0cc4e840e8f coredump: clarify unsafe core_pattern warning
- c7be96af89d4b53211862d8599b2430e8900ed92 signals: avoid unnecessary taking of sighand->siglock
- 73e64c51afc56d4863ae225e947ba2f16ad04487 mm, compaction: allow compaction for GFP_NOFS requests
- 4d1f0fb096aedea7bb5489af93498a82e467c480 kernel/watchdog: use nmi registers snapshot in hardlockup handler
- 40f7828b36e3b9dd2fdc34d065e342cddf8d7bef btrfs: better handle btrfs_printk() defaults
- 053d20f5712529016eae10356e0dea9b360325bd netfilter: nft_payload: mangle ckecksum if NFT_PAYLOAD_L4CSUM_PSEUDOHDR is set
- 3e38df136e453aa69eb4472108ebce2fb00b1ba6 netfilter: nf_tables: fix oob access
- c2e756ff9e699865d294cdc112acfc36419cf5cc netfilter: nft_queue: use raw_smp_processor_id()
- 8010d7feb2f0367ae573ad601b2905e29db50cd3 netfilter: nft_quota: reset quota after dump
- 412ac77a9d3ec015524dacea905471d66480b7ac Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/ebiederm/user-namespace
- dcdaa2f9480c55c6dcf54ab480e82e93e5622318 Merge branch stable-4.10 of git://git.infradead.org/users/pcmoore/audit
- 683b96f4d1d132fcefa4a0bd11916649800d7361 Merge branch next of git://git.kernel.org/pub/scm/linux/kernel/git/jmorris/linux-security
- f88f0bdfc32f3d1e2fd03ec8a7f7b456df4db725 um: UBD Improvements
- 45ee2c1d66185e5bd27702c60cce3c43fa3370d2 libceph: remove now unused finish_request() wrapper
- c297eb42690b904fb5b78dd9ad001bafe25f49ec libceph: always signal completion when done
- 80e80fbb584dc0d0dc894c4965bc2a199c7cd3f2 ceph: avoid creating orphan object when checking pool permission
- 0f1d6dfe03ca4e36132221b918499c6f0b0f048d Merge branch linus of git://git.kernel.org/pub/scm/linux/kernel/git/herbert/crypto-2.6
- d1b1cea1e58477dad88ff769f54c0d2dfa56d923 blk-mq: Fix failed allocation path when mapping queues
- d2a145252c52792bc59e4767b486b26c430af4bb scsi: avoid a permanent stop of the scsi devices request queue
- d05c5f7ba164aed3db02fb188c26d0dd94f5455b vfs,mm: fix return value of read() at s_maxbytes
- 307d9075a02b696e817b775c565e45c4fa3c32f2 scsi: mpt3sas: Recognize and act on iopriority info
- 093df73771bac8a37d607c0e705d157a8cef4c5c scsi: qla2xxx: Fix Target mode handling with Multiqueue changes.
- 5601236b6f7948cd1783298f6d4cacce02e22fde scsi: qla2xxx: Add Block Multi Queue functionality.
- d74595278f4ab192af66d9e60a9087464638beee scsi: qla2xxx: Add multiple queue pair functionality.
- 4fa183455988adaa7f6565ca06bceecafb527820 scsi: qla2xxx: Utilize pci_alloc_irq_vectors/pci_free_irq_vectors calls.
- 77ddb94a4853204dc680121d59221b1be7c2297e scsi: qla2xxx: Only allow operational MBX to proceed during RESET.
- 7e8a9486786d5ede1d2405fab140c6a0d8b2c1fe scsi: hpsa: remove memory allocate failure message
- 2c9bce5b49713acba3e90ce994d60996adcd4b30 scsi: Update 3ware driver email addresses
- 6f2ce1c6af37191640ee3ff6e8fc39ea10352f4c scsi: zfcp: fix rport unblock race with LUN recovery
- 56d23ed7adf3974f10e91b643bd230e9c65b5f79 scsi: zfcp: do not trace pure benign residual HBA responses at default level
- dac37e15b7d511e026a9313c8c46794c144103cd scsi: zfcp: fix use-after-free in FC ingress path after TMF
- 165ae50e450bc7de6c741bf2c27ed0920a40a9af scsi: libcxgbi: return error if interface is not up
- 1fe1fdb04b92f54b58eb8b71d2f28cf73fd9801c scsi: cxgb4i: libcxgbi: add missing module_put()
- 44830d8fd28a729729d14bb160341a6170631eb7 scsi: cxgb4i: libcxgbi: cxgb4: add T6 iSCSI completion feature
- 586be7cb694fdbb3a35cc35c03387ce0fc534572 scsi: cxgb4i: libcxgbi: add active open cmd for T6 adapters
- e0eed8ab7379faba26f9d85a5904b8292dc4d8b9 scsi: cxgb4i: use cxgb4_tp_smt_idx() to get smt_idx
- ace7f46ba5fde7273207c7122b0650ceb72510e0 scsi: qedi: Add QLogic FastLinQ offload iSCSI driver framework.
- 6f94ba20799b98c8badf047b184fb4cd7bc45e44 Merge branch vmw_pvrdma into merge-test
- 29c8d9eba550c6d73d17cc1618a9f5f2a7345aa1 IB: Add vmw_pvrdma driver
- 9032ad78bb58f2567fc95125ee69cde7b74c0a21 Merge branches misc, qedr, reject-helpers, rxe and srp into merge-test
- 86ef0beaa0bdbec70d4261977b8b4a100fe54bfe Merge branch mlx into merge-test
- 253f8b22e0ad643edafd75e831e5c765732877f5 Merge branch hfi1 into merge-test
- 884fa4f3048c4c43facfa6ba3b710169f7ee162c Merge branches chelsio, debug-cleanup, hns and i40iw into merge-test
- 46d0703fac3ffa12ec36f22f386d96d0f474c9c2 IB/mlx4: fix improper return value
- 5b4c9cd7e4790f37b595aeb4bf6fcbf7e3ba9e2c IB/ocrdma: fix bad initialization
- 6a3a1056d66e6a64446930b0d9de2430d835d38f infiniband: nes: return value of skb_linearize should be handled
- 3b9d9650096921f27086d8e0a66eba277f7badba MAINTAINERS: Update Intel RDMA RNIC driver maintainers
- f93146c82a589e9e7a3053cede927b00a0212a54 MAINTAINERS: Remove Mitesh Ahuja from emulex maintainers
- 7ae123edd37a47e178eb9a6631fe4a7108262c10 Merge tag acpi-urgent-4.10-rc1 of git://git.kernel.org/pub/scm/linux/kernel/git/rafael/linux-pm
- 17069d32a3408e69d257a3fe26f08de0336d958d IB/core: fix unmap_sg argument
- bbcd9c53c743cfee9feb0ee3b25070691d76c5ee Merge tag for-v4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/sre/linux-power-supply
- 22b1ae6169e3cb9e33ba549a0c07a0cc469143d7 qede: fix general protection fault may occur on probe
- ce38207f161513ee3d2bd3860489f07ebe65bc78 Merge tag sound-4.10-rc1 of git://git.kernel.org/pub/scm/linux/kernel/git/tiwai/sound
- a9042defa29a01cc538b742eab047848e9b5ae14 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/jikos/trivial
- 6960d58240190a885c09e784b8dcc1345951a7c8 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/jikos/livepatching
- f39fdf2ab846ecc636d6272b47f28a05a2052a14 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/jikos/hid
- 775a2e29c3bbcf853432f47d3caa9ff8808807ad Merge tag dm-4.10-changes of git://git.kernel.org/pub/scm/linux/kernel/git/device-mapper/linux-dm
- 7ceb740c540dde362b3055ad92c6a38009eb7a83 IB/mthca: Replace pci_pool_alloc by pci_pool_zalloc
- 2a4c32edd39b7de166e723b1991abcde4db3a701 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/shli/md
- b9f98bd4034a3196ff068eb0fa376c5f41077480 Merge tag mmc-v4.10-2 of git://git.kernel.org/pub/scm/linux/kernel/git/ulfh/mmc
- a829a8445f09036404060f4d6489cb13433f4304 Merge tag scsi-misc of git://git.kernel.org/pub/scm/linux/kernel/git/jejb/scsi
- 1974ab9d9d5b6eeafa629f793fdf59958646cb9d mlx5, calc_sq_size(): Make a debug message more informative
- 3d6bdf1625857ba50f433bd140dada387432f051 mlx5: Remove a set-but-not-used variable
- 626bc02d4d33510b6ecb6f37c577f844cc6cfc57 mlx5: Use { } instead of { 0 } to init struct
- 4fa354c9dbfef9226a690d8ee319b046f3067a6a IB/srp: Make writing the add_target sysfs attr interruptible
- 290081b45342ef902ed756f929fa9e4feb9f7dab IB/srp: Make mapping failures easier to debug
- 3787d9908c4e05af0322613fe7f8c617c1ddb1d5 IB/srp: Make login failures easier to debug
- 042dd765bdf401c0ccdeb16717b0c2a0b1405f18 IB/srp: Introduce a local variable in srp_add_one()
- 1a1faf7a8a251d134d375b7783a614ee79e932f2 IB/srp: Fix CONFIG_DYNAMIC_DEBUG=n build
- 84b6079134420f4635f23c2088a3892057b23bb0 Merge tag configfs-for-4.10 of git://git.infradead.org/users/hch/configfs
- d3a2418ee36a59bc02e9d454723f3175dcf4bfd9 IB/multicast: Check ib_find_pkey() return value
- 11b642b84e8c43e8597de031678d15c08dd057bc IPoIB: Avoid reading an uninitialized member variable
- 2fe2f378dd45847d2643638c07a7658822087836 IB/mad: Fix an array index check
- 533c7b69c764ad5febb3e716899f43a75564fcab audit: use proper refcount locking on audit_sock
- fba143c66abb81307a450679f38ab953fe96a413 netns: avoid disabling irq for netns id
- a09cfa470817ac086cf68418da13a2b91c2744ef audit: dont ever sleep on a command record/message
- 6c54e7899693dee3db67ea996e9be0e10f67920f audit: handle a clean auditd shutdown with grace
- e1d166212894d9d959a601c4802882b877bb420a audit: wake up kauditd_thread after auditd registers
- 3197542482df22c2a131d4a813280bd7c54cedf5 audit: rework audit_log_start()
- c6480207fdf7b61de216ee23e93eac0a6878fa74 audit: rework the audit queue handling
- af8b824f283de5acc9b9ae8dbb60e4adacff721b audit: rename the queues and kauditd related functions
- 4aa83872d346806d9b54768aa0d1329050542bad audit: queue netlink multicast sends just like we do for unicast sends
- 6c9255645350ce2aecb7c3cd032d0e93d4a7a71a audit: fixup audit_init()
- 55a6f170a413cd8dc7a3a52e5a326e1a87579b4f audit: move kaudit thread start from auditd registration to kaudit init (#2)
- b42dde478bcaa8113b0d1cd82ad0048372c5599d IB/mlx4: Rework special QP creation error path
- 0d38c240f97602d9a4553252bb710521f49bb264 IB/srpt: Report login failures only once
- 5f4c7e4eb5f36974ed46a485290f5d01ace5fdba IB/usnic: simplify IS_ERR_OR_NULL to IS_ERR
- 9315bc9a133011fdb084f2626b86db3ebb64661f IB/core: Issue DREQ when receiving REQ/REP for stale QP
- 24dc08c3c9891a79f2754f99b7bffe65745af0f3 IB/nes: use new api ethtool_{get|set}_link_ksettings
- def4a6ffc9d178d6bb14178f56873c4831fb05a7 IB/isert: do not ignore errors in dma_map_single()
- f6f0083cca66e673cca6fa26b52b107b5570081d spi: armada-3700: fix unsigned compare than zero on irq
- 4286db8456f4fa0c6af2b6b9abc5991a7e7da69c spi: sh-msiof: Add R-Car Gen 2 and 3 fallback bindings
- 107177b14d8179f864315fc4daed9da777ed30c2 ARCv2: intc: default all interrupts to priority 1
- 78833e79d516901413d6e9278cbebf6116d62c78 ARCv2: entry: document intr disable in hard isr
- 5084fdf081739b7455c7aeecda6d7b83ec59c85f Merge tag ext4_for_linus of git://git.kernel.org/pub/scm/linux/kernel/git/tytso/ext4
- 22dccc5454a39427de7b87a080d026b6bf66a7b9 IB/rdmavt: Only put mmap_info ref if it exists
- f5eabf5e5129e8ab5b3e7f50b24444aca1680e64 IB/rdmavt: Handle the kthread worker using the new API
- 6efaf10f163d9a60d1d4b2a049b194a53537ba1b IB/rdmavt: Avoid queuing work into a destroyed cq kthread worker
- e98172462f0b75ed60f3a73aa280fb29cafd450f IB/mlx4: avoid a -Wmaybe-uninitialize warning
- 14ab8896f5d993c5f427504276e3c42ccb3cc354 IB/mlx5: avoid bogus -Wmaybe-uninitialized warning
- 09cb6464fe5e7fcd5177911429badd139c4481b7 Merge tag for-f2fs-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/jaegeuk/f2fs
- 35493294df1a1b06268a4e7b77b7a323772779f3 rdma UAPI: Use __kernel_sockaddr_storage
- ba75d570b60c05cda21c0b43c5fbdc4e344f892d ubifs: Initialize fstr_real_len
- 512fb1b32bac02ebec50e5060f94dc1ad23ed28f nvmet_rdma: log the connection reject message
- 1e38a366ee86ac2b7a8110775cb3353649b18b70 ib_isert: log the connection reject message
- 39384f04d03e10986c783cd527555225ec592821 rds_rdma: log the connection reject message
- 97540bb90acfab268b256a58c3e51cd06b2d1654 ib_iser: log the connection reject message
- 7f03953c2f28cdb9c31f3f1410ba5be1f385a693 nvme-rdma: use rdma connection reject helper functions
- 5f24410408fd093734ce758f2fe3a66fe543de22 rdma_cm: add rdma_consumer_reject_data helper function
- 5042a73d3e9de7bcc2a31adea08ee95bbce998dc rdma_cm: add rdma_is_consumer_reject() helper function
- 77a5db13153906a7e00740b10b2730e53385c5a8 rdma_cm: add rdma_reject_msg() helper function
- 19d37ce2a7159ee30bd59d14fe5fe13c932bd5b7 Merge tag dlm-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/teigland/linux-dlm
- 3e5cecf26842ecfde8ea487c02cb12709cd90ef5 Merge tag jfs-4.10 of git://github.com/kleikamp/linux-shaggy
- aecb66b2b01a87b4b723267b9193c8f00d661c1f qedr: remove pointless NULL check in qedr_post_send()
- aafec388a1b7fc533a81c03b4a81c6e5f3e5688f qedr: Use list_move_tail instead of list_del/list_add_tail
- 181d80151f9c6ff3c765c1bd2e4e200ada23c2f3 qedr: Fix possible memory leak in qedr_create_qp()
- ea7ef2accdeaf825165cccd60b848765677bf1f2 qedr: return -EINVAL if pd is null and avoid null ptr dereference
- 9fa240bbfc4200b080c8fad12579659c2c2f36b5 IB/mad: Eliminate redundant SM class version defines for OPA
- 0b7589ecca2b6f962cf3314a3a5a675deeefb624 s390/pci: query fmb length
- d03502684b65492339d70f11aa8ed6df3961a3bf s390/zcrypt: add missing memory clobber to ap_qci inline assembly
- f1c7ea26178176ca783cc2ac54f211630344290c s390/extmem: add missing memory clobber to dcss_set_subcodes
- 86fa7087d348b6c8a159c77ea20e530ee1230c34 s390/nmi: fix inline assembly constraints
- 7a71fd1c59dfd20fac4d14486d63d3d5ab70498a s390/lib: add missing memory barriers to string inline assemblies
- 259acc5c255a4260b3db0461afd5d93fabfe8524 s390/cpumf: fix qsi inline assembly
- 6d7b2ee9d56af3d17d88b0f43b7dc14ee38161b7 s390/setup: reword printk messages
- 50cff5adcf8eb8bcdd79087a91878f298fb58dcf s390/dasd: fix typos in DASD error messages
- 75a357341e7c9d3893405ea6f9d722036012dd1f s390: fix compile error with memmove_early() inline assembly
- 13b251bdc8b97c45cc8b1d57193ab05ec0fe97e8 s390/zcrypt: tracepoint definitions for zcrypt device driver.
- cccd85bfb7bf6787302435c669ceec23b5a5301c s390/zcrypt: Rework debug feature invocations.
- bf9f31190aa176c43c15cf58b60818d325e0f851 s390/zcrypt: Improved invalid domain response handling.
- c1c1368de497648cf532e7f37a407361c70aa638 s390/zcrypt: Fix ap_max_domain_id for older machine types
- 148784246ef2d85f000713cf56e1c90b405228e8 s390/zcrypt: Correct function bits for CEX2x and CEX3x cards.
- e47de21dd35bad6d1e71482a66699cd04e83ea40 s390/zcrypt: Fixed attrition of AP adapters and domains
- b886a9d1560d6c7d5d58344b16f53ab2cba5b666 s390/zcrypt: Introduce new zcrypt device status API
- e28d2af43614eb86f59812e7221735fc221bbc10 s390/zcrypt: add multi domain support
- 34a15167739412750846d4f1a5540d9e592fd815 s390/zcrypt: Introduce workload balancing
- 9af3e04ee41e6841b2accb9dc96562bcf4e59916 s390/zcrypt: get rid of ap_poll_requests
- 0db78559f965a2e652dbe8acf35333f2081bf872 s390/zcrypt: header for the AP inline assmblies
- 236fb2ab95e9832880501d465d64eb2f2935b852 s390/zcrypt: simplify message type handling
- fc1d3f02544a6fd5f417921b57c663388586a17a s390/zcrypt: Move the ap bus into kernel
- b3e8652bcbfa04807e44708d4d0c8cdad39c9215 s390/zcrypt: Introduce CEX6 toleration
- 36e1f3d107867b25c616c2fd294f5a1c9d4e5d09 blk-mq: Avoid memory reclaim when remapping queues
- 6fce983f9b3ef51d47e647b2cff15049ef803781 ASoC: dwc: Fix PIO mode initialization
- dadab2d4e3cf708ceba22ecddd94aedfecb39199 spi: SPI_FSL_DSPI should depend on HAS_DMA
- ed141f2890cdb738fc7131367f5fb15632bc3e60 Merge branch syscalls into for-linus
- 41884629fe579bde263dfc3d1284d0f5c7af7d1a Merge branches clkdev, fixes, misc and sa1100-base into for-linus
- 18e615ad87bce9125ef3990377a4a946ec0f21f3 crypto: skcipher - fix crash in virtual walk
- efcae7c931b473285e38c778bdaa9f36de9f78d6 sign-file: Fix inplace signing when src and dst names are both specified
- fbb726302a9ae06b373e04a54ad30eafa288dd10 crypto: asymmetric_keys - set error code on failure
- 74dcba3589fc184c7118905eda22b3a4aaef95ff NTB: correct ntb_spad_count comment typo
- ecbf12882f90d95decbc0e4cf100ef6935e96445 misc: ibmasm: fix typo in error message
- 846221cfb8f64c613b7635c94e0c02549a666c14 Remove references to dead make variable LINUX_INCLUDE
- d06505b2a95efba25dc635b64a481e3197e9369a Remove last traces of ikconfig.h
- 9165dabb2500b3dcb98fc648d27589a5a806227e treewide: Fix printk() message errors
- 95f21c5c6d8345f8253057b24a98adfbceb2aca1 Documentation/device-mapper: s/getsize/getsz/
- 96e132ebc0a162c643e0e6e6f1f85c3be3355715 Merge branches for-4.10/asus, for-4.10/cp2112, for-4.10/i2c-hid-nopower, for-4.10/intel-ish, for-4.10/mayflash, for-4.10/microsoft-surface-3, for-4.10/multitouch, for-4.10/sony, for-4.10/udraw-ps3, for-4.10/upstream and for-4.10/wacom/generic into for-linus
- 31dcfec11f827e9a5d8720fe4728f1305894884f x86/boot/64: Push correct start_cpu() return address
- ec2d86a9b646d93f1948569f368e2c6f5449e6c7 x86/boot/64: Use push instead of call in start_cpu()
- 06deeec77a5a689cc94b21a8a91a76e42176685d cifs: Fix smbencrypt() to stop pointing a scatterlist at the stack
- 18591add41ec9558ce0e32ef88626c18cc70c686 thermal: rockchip: handle set_trips without the trip points
- cadf29dc2a8bcaae83e6e4c3229965de747c8601 thermal: rockchip: optimize the conversion table
- d3530497f5c33530c50acb435b7d54e0a82d8032 thermal: rockchip: fixes invalid temperature case
- cdd8b3f7b779e39bda1a8057f287da065216720b thermal: rockchip: dont pass table structs by value
- e6ed1b4ad30331e6d878579dd95764d0a224cacd thermal: rockchip: improve conversion error messages
- 7a62a52333f8b5b82753d9529c11b3404bc5c183 block_dev: dont update file access position for sync direct IO
- d2a61918401ea8db8a6f922e98e86a66b4930cec nvme/pci: Log PCI_STATUS when the controller dies
- bcc7f5b4bee8e327689a4d994022765855c807ff block_dev: dont test bdev->bd_contains when it is not stable
- cdb98c2698b4af287925abcba4d77d92af82a0c3 Revert nvme: add support for the Write Zeroes command
- 4625d2a513d60ca9c3e8cae42c8f3d9efc1b4211 Merge branch topic/st_fdma into for-linus
- 57fb7ee10c27b315600445b2bad72236a11951ad Merge branch topic/s3c64xx into for-linus
- 90644ad7f2c0292b1a2a98d733bd17f449bb9885 Merge branch topic/qcom into for-linus
- 83cb0dcaf11fa045cecad4cc6310f3bfbf0cf87e Merge branch topic/pxa into for-linus
- db82df3e81b4c89e39b82bf6aa290612cfb2c12c Merge branch topic/omap into for-linus
- 3f809e844c6ba46fe5e16b20ad70ac4027341b36 Merge branch topic/ioat into for-linus
- 7fc3b3f946341a035f05e13756f7b2c441492c55 Merge branch topic/doc into for-linus
- cc31e9b718dafd8a1bdc593234ddbbf4faa2511c Merge branch acpi-cppc
- f4000cd99750065d5177555c0a805c97174d1b9f Merge tag arm64-upstream of git://git.kernel.org/pub/scm/linux/kernel/git/arm64/linux
- 2ec4584eb89b8933d1ee307f2fc9c42e745847d7 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/s390/linux
- aa3ecf388adc90bde90776bba71a7f2d278fc4e3 Merge tag for-linus-4.10-rc0-tag of git://git.kernel.org/pub/scm/linux/kernel/git/xen/tip
- b5cab0da75c292ffa0fbd68dd2c820066b2842de Merge branch stable/for-linus-4.9 of git://git.kernel.org/pub/scm/linux/kernel/git/konrad/swiotlb
- 93173b5bf2841da7e3a9b0cb1312ef5c87251524 Merge tag for-linus of git://git.kernel.org/pub/scm/virt/kvm/kvm
- 1c59e1edb13d60b97b7b03b332ceed5d967d4227 Merge tag hwmon-for-linus-v4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/groeck/linux-staging
- bb3dd056ed1af9b186f0d9fe849eab78c51d14ce Merge tag spi-v4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/broonie/spi
- 3fa71d0f58a9b9df84e8e79196f961bcfbf01b2e crypto: doc - optimize compilation
- 3f692d5f97cb834a42bcfb3cc10f5e390a9d7867 crypto: doc - clarify AEAD memory structure
- 71f3f027f8f8532d397ff2da7bdcd99bf0aa3867 crypto: doc - remove crypto_alloc_ablkcipher
- 8d23da22ac33be784451fb005cde300c09cdb19d crypto: doc - add KPP documentation
- c30c98d174e5ecbb5d70c7c92846d4d884f8b38a crypto: doc - fix separation of cipher / req API
- 0184cfe72d2f139c4feed7f3820ba2269f5de322 crypto: doc - fix source comments for Sphinx
- c441a4781ff1c5b78db1410f708aa96dceec5fa2 crypto: doc - remove crypto API DocBook
- 3b72c814a8e8cd638e1ba0da4dfce501e9dff5af crypto: doc - convert crypto API documentation to Sphinx
- 334bb773876403eae3457d81be0b8ea70f8e4ccc x86/kbuild: enable modversions for symbols exported from asm
- 7b882cb800095f216c9da6b6735d10d26df8168b Merge branch for-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/tj/libata
- 9f56eca3aeeab699a7dbfb397661d2eca4430e94 ata: avoid probing NCQ Prio Support if not explicitly requested
- b92e09bb5bf4db65aeb8ca0094fdd5142ed54451 Merge branch for-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/tj/libata
- f5f3bde4f676ea4b23ac1d7293c69a069e687351 ARC: ARCompact entry: elide re-reading ECR in ProtV handler
- c11a6cfb0103d5d831e20bd9b75d10d13519fec5 Merge branch for-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/tj/wq
- 20737738d397dfadbca1ea50dcc00d7259f500cf Merge branch md-next into md-linus
- e6efef7260ac2bb170059980a78440499f2cc0db Merge branch for-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/tj/percpu
- b78b499a67c3f77aeb6cd0b54724bc38b141255d Merge tag char-misc-4.10-rc1 of git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/char-misc
- ef548c551e72dbbdcc6d9ed7c7b3b01083fea8e2 dm flakey: introduce error_writes feature
- 3e1ed981b7a903ba81199d4d25b80c6bba705160 netlink: revert broken, broken 2-clause nla_ok()
- 098c30557a9a19827240aaadc137e4668157dc6b Merge tag driver-core-4.10-rc1 of git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/driver-core
- 72cca7baf4fba777b8ab770b902cf2e08941773f Merge tag staging-4.10-rc1 of git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/staging
- 5266e70335dac35c35b5ca9cea4251c1389d4a68 Merge tag tty-4.10-rc1 of git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/tty
- 03f8d4cca352fd41f26b5c88dec1e4d3f507f5de Merge tag usb-4.10-rc1 of git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/usb
- a67485d4bf97918225dfb5246e531643755a7ee1 Merge tag acpi-4.10-rc1 of git://git.kernel.org/pub/scm/linux/kernel/git/rafael/linux-pm
- 2939e1a86f758b55cdba73e29397dd3d94df13bc btrfs: limit async_work allocation and worker func duration
- ec9160dacdb08eaeb40a878db97dfed6c2212d91 ubifs: Use fscrypt ioctl() helpers
- 7b9dc3f75fc8be046e76387a22a21f421ce55b53 Merge tag pm-4.10-rc1 of git://git.kernel.org/pub/scm/linux/kernel/git/rafael/linux-pm
- 7d29f349a4b9dcf5bc9dcc05630d6a7f6b6b3ccd IB/mlx5: Properly adjust rate limit on QP state transitions
- 189aba99e70030cfb56bd8f199bc5b077a1bc6ff IB/uverbs: Extend modify_qp and support packet pacing
- 528e5a1bd3f0e9b760cb3a1062fce7513712a15d IB/core: Support rate limit for packet pacing
- d949167d68b304c0a00331cf33ef49a29b65d85f IB/mlx5: Report mlx5 packet pacing capabilities when querying device
- ca5b91d63192ceaa41a6145f8c923debb64c71fa IB/mlx5: Support RAW Ethernet when RoCE is disabled
- 45f95acd63222dd1dc752fa904536327b10f1082 IB/mlx5: Rename RoCE related helpers to reflect being Eth ones
- d012f5d6f8597f936f44c79e46345fda86dcff4d IB/mlx5: Refactor registration to netdev notifier
- b216af408c985092a79472ad10e6f216cb2973fc IB/mlx5: Use u64 for UMR length
- afd02cd3a9b6c04b41d946b5d7f6e17b3fc30c6b IB/mlx5: Avoid system crash when enabling many VFs
- c73b7911de97fad3ab9032a110af48d6ab2da48f IB/mlx5: Assign SRQ type earlier
- c482af646d0809a8d5e1b7f4398cce3592589b98 IB/mlx4: Fix out-of-range array index in destroy qp flow
- 41c450fd8da549c5f7cced6650354095b0d4312a IB/mlx5: Make create/destroy_ah available to userspace
- 5097e71f3edafad3e7d8d4f9c4a137d9aad0fae2 IB/mlx5: Use kernel driver to help userspace create ah
- 477864c8fcd953e5a988073ca5be18bb7fd93410 IB/core: Let create_ah return extended response to user
- 6ad279c5a2e55bf2bd100b4222090d4717de88d5 IB/mlx5: Report that device has udata response in create_ah
- c90ea9d8e51196d9c528e57d9ab09ee7d41f0ba0 IB/core: Change ib_resolve_eth_dmac to use it in create AH
- 2d1e697e9b716b8a692bc9c197e5f4ffd10d7307 IB/mlx5: Add support to match inner packet fields
- fbf46860b19ddb485f00bef1ad1a43aabc9f71ad IB/core: Introduce inner flow steering
- ffb30d8f107b27820a069ae6772ab48e58cc0b2f IB/mlx5: Support Vxlan tunneling specification
- a0cb4c759af12943806564294fa53ab08cb7cf93 IB/uverbs: Add support for Vxlan protocol
- 76bd23b34204cad78f48aec4cef38869a66aa594 IB/core: Align structure ib_flow_spec_type
- 0dbf3332b7b683db33a385a3ce9baab157e3ff9a IB/core: Add flow spec tunneling support
- 1cbe6fc86ccfe05a910be4883da7c7bd28c190fe IB/mlx5: Add support for CQE compressing
- 7e43a2a5bae39fedaa7cce21d637e0c8d96d8e54 IB/mlx5: Report mlx5 CQE compression caps during query
- 191ded4a4d991acf17207e0b4370fef070bce3e9 IB/mlx5: Report mlx5 multi packet WQE caps during query
- c226dc22ec4904340e3e14a536983cda3dbe7914 net/mlx5: Report multi packet WQE capabilities
- d680ebed91e0b45c43ae03a880a0b43211096161 IB/rxe: Increase max number of completions to 32k
- bf08e884bfd5be068fd2ccf2bc450f085d8dd853 IB/mlx4: Check if GRH is available before using it
- 1f22e454df2eb99ba6b7ace3f594f6805cdf5cbc IB/mlx4: When no DMFS for IPoIB, dont allow NET_IF QPs
- 36869cb93d36269f34800b3384ba7991060a69cf Merge branch for-4.10/block of git://git.kernel.dk/linux-block
- 9439b3710df688d853eb6cb4851256f2c92b1797 Merge tag drm-for-v4.10 of git://people.freedesktop.org/~airlied/linux
- 1d161d4cd719ac498545c94805803af8af9b642f platform/x86: dell-laptop: Use brightness_set_blocking for kbd_led_level_set
- bb55a2ee76c2426686d320354f9ff7d9eadeb34b platform/x86: thinkpad_acpi: Fix old style declaration GCC warning
- a3c42a467a254a17236ab817d5c7c6bc054e4f84 platform/x86: thinkpad_acpi: Adding new hotkey ID for Lenovo thinkpad
- b03f4d49469f3bde9600192af15b8f17f8673679 platform/x86: thinkpad_acpi: Add support for X1 Yoga (2016) Tablet Mode
- b31800283868746fc59686486a11fb24b103955b platform/x86: thinkpad_acpi: Move tablet detection into separate function
- e74e259939275a5dd4e0d02845c694f421e249ad platform/x86: asus-nb-wmi.c: Add X45U quirk
- 085370eb19d3b502d56b318abd269bef77524590 platform/x86: asus-nb-wmi: Make use of dmi->ident
- 8023eff10e7b0327898f17f0b553d2e45c71cef3 platform/x86: asus-wmi: Set specified XUSB2PR value for X550LB
- b4aca383f9afb5f84b05de272656e6d4a919d995 platform/x86: intel_mid_thermal: Fix suspend handlers unused warning
- bb9ad484845d7cc48f0c8db199a91c3a669d908f platform/x86: intel-vbtn: Switch to use devm_input_allocate_device
- 3526ecadc86cc1d485153255498cde7d0275dd37 platform/x86: Use ACPI_FAILURE at appropriate places
- 5dc444b804eae57abaf6f05663d9cb9f030bb9d2 platform/x86: dell-wmi: Add events created by Dell Rugged 2-in-1s
- 915ac0574c85e4202a4ede961d9e1230b1cca06f platform/x86: dell-wmi: Adjust wifi catcher to emit KEY_WLAN
- daf5d1433d6697ec8786604c30f69b2f9d4c7978 platform/x86: intel_pmc_core: Add KBL CPUID support
- 9c2ee19987ef02fe3dbe507d81ff5c7dd5bb4f21 platform/x86: intel_pmc_core: Add LTR IGNORE debug feature
- fe748227570107abaa4767c39be3eff934bdaf5c platform/x86: intel_pmc_core: Add MPHY PLL clock gating status
- 173943b3dae570d705e3f5237110a64a28c0bf74 platform/x86: intel_pmc_core: ModPhy core lanes pg status
- 0bdfaf429d1da662742708153bf8cc945bf4904b platform/x86: intel_pmc_core: Add PCH IP Power Gating Status
- 8434709ba71473f75572245c247d3c1e92509cf3 platform/x86: intel_pmc_core: Fix PWRMBASE mask and mmio reg len
- 5241b1938a4d33eee3d3b43f23067c8e5b96db45 platform/x86: acer-wmi: Only supports AMW0_GUID1 on acer family
- 7079efc9d3e7f1f7cdd34082ec58209026315057 Merge tag fbdev-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/tomba/linux
- edc5f445a681a6f2522c36a4860f10ad457ab00e Merge tag vfio-v4.10-rc1 of git://github.com/awilliam/linux-vfio
- 22d8262c33e52b10a4c442b04a2388b4bc589ee4 Merge tag gcc-plugins-v4.10-rc1 of git://git.kernel.org/pub/scm/linux/kernel/git/kees/linux
- 52281b38bc28e188a8aad17c3bf200e670a37aba Merge tag pstore-v4.10-rc1 of git://git.kernel.org/pub/scm/linux/kernel/git/kees/linux
- 5f52a2c512a55500349aa261e469d099ede0f256 Merge branch for-chris-4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/fdmanana/linux into for-linus-4.10
- daf34710a9e8849e04867d206692dc42d6d22263 Merge tag edac_for_4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/bp/bp
- 9346116d148595a28fe3521f81ac8e14d93239c3 Merge branch next of git://git.kernel.org/pub/scm/linux/kernel/git/rzhang/linux
- b8d2798f32785398fcd1c48ea80c0c6c5ab88537 Merge tag clk-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/clk/linux
- 961288108e26e5024801c75d0e7c8e9a2de2b02b Merge tag rpmsg-v4.10 of git://github.com/andersson/remoteproc
- edc57ea92cb838e1d04529cb9002097ad6da8a4b Merge tag rproc-v4.10 of git://github.com/andersson/remoteproc
- 5233c331cfb41433bc167fc7c70ea67c1133ffec Merge tag mmc-v4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/ulfh/mmc
- 58f253d26254b7ec0faa0a67d70912facd6687e4 Merge tag regulator-v4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/broonie/regulator
- 96955c9682051e70f06103f0d96e26d2f35f4910 Merge tag regmap-v4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/broonie/regmap
- 3dbb16b87b57bb1088044ad2a0432e4769075002 selftests: ftrace: Shift down default message verbosity
- 1f0a53f623b675e856554f2bb1d6b630ea78125d Merge tag leds_for_4.10 of git://git.kernel.org/pub/scm/linux/kernel/git/j.anaszewski/linux-leds
- 20d5ba4928ceb79b919092c939ae4ef4d88807bd Merge tag pinctrl-v4.10-1 of git://git.kernel.org/pub/scm/linux/kernel/git/linusw/linux-pinctrl
- 061ad5038ca5ac75419204b216bddc2806008ead Merge tag gpio-v4.10-1 of git://git.kernel.org/pub/scm/linux/kernel/git/linusw/linux-gpio
- a220871be66f99d8957c693cf22ec67ecbd9c23a virtio-net: correctly enable multiqueue
- 385886686609dbdcd2e8f55c358647faa8d4f89e ubifs: Use FS_CFLG_OWN_PAGES
- d8da0b5d64d58f7775a94bcf12dda50f13a76f22 mac80211: Ensure enough headroom when forwarding mesh pkt
- ec4efc4a10c3b9a3ab4cf37dc3719fd3c4632cd0 mac80211: dont call drv_set_default_unicast_key() for VLANs
- 22f6592b23ef8a0c09283bcb13087340721e1154 selftest/gpio: add gpio test case
- 981c3db62e2d2dfb0c5725dd55d8c3cf8ed4edd8 selftest: sync: improve assert() failure message
- 5716863e0f8251d3360d4cbfc0e44e08007075df fsnotify: Fix possible use-after-free in inode iteration on umount

* Wed Dec 14 2016 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.9.0-4
- 968c61815916312b756653b1b57351a1e44d7176 Merge tag v4.9 into hostos-devel
- 1385457f02cf5cebb366a319bfb4ee81099c2771 KVM: PPC: Book3S HV: Fix H_PROD to actually wake the target vcpu
- d1cfbb63f9906da02159969920dbcaaf859dd022 KVM: PPC: Book3S: Move prototypes for KVM functions into kvm_ppc.h
- 69973b830859bc6529a7a0468ba0d80ee5117826 Linux 4.9
- 2e4333c14de06a333783d6812cf3c4998f78b0c8 Merge branch upstream of git://git.linux-mips.org/pub/scm/ralf/upstream-linus
- ba735155b9647b6167fd50276ca0fbfbce4e836c MIPS: Lantiq: Fix mask of GPE frequency
- edb6fa1a6452edf736c04d02e3f6de59043df69e MIPS: Return -ENODEV from weak implementation of rtc_mips_set_time
- 045169816b31b10faed984b01c390db1b32ee4c1 Merge branch linus of git://git.kernel.org/pub/scm/linux/kernel/git/herbert/crypto-2.6
- cd6628953e4216b65e7d91ab70ff8e5b65c9fde9 Merge git://git.kernel.org/pub/scm/linux/kernel/git/davem/net
- d33695fbfab73a4a6550fa5c2d0bacc68d7c5901 net: mlx5: Fix Kconfig help text
- ab4e4c07aca7b33f8d00c5d6b083a564660ca8a5 net: smsc911x: back out silently on probe deferrals
- 7b5967389f5a8dfb9d32843830f5e2717e20995d ibmveth: set correct gso_size and gso_type
- 810ac7b7558d7830e72d8dbf34b851fce39e08b0 Merge branch libnvdimm-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/nvdimm/nvdimm
- 861d75d098e2d0a2d7692c9d6a30b6fd2c81387c Merge branch for-4.9-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/tj/libata
- af9468db44989f995ec98c5cc63c99b16b78ee66 Merge tag ceph-for-4.9-rc9 of git://github.com/ceph/ceph-client
- 1f6c926c0aa9180d42fcda53578881fc57f83a9a Merge tag armsoc-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/arm/arm-soc
- 751471201eb92b95a29cf3dd2b296ee6f6d93d23 Merge tag m68k-for-v4.9-tag2 of git://git.kernel.org/pub/scm/linux/kernel/git/geert/linux-m68k
- 1ca17e97966aa4b651e56861f83695e3645bf954 Merge branch drm-fixes of git://people.freedesktop.org/~airlied/linux
- 2b41226b39b654a5e20bce5a7332f307fdb9156b Revert radix tree test suite: fix compilation
- 1472d599a8d30429bf322fdc53bae3bec382308d Merge branch ethernet-missing-netdev-parent
- 5579f28cc8ba8a3b489cb042fcb30d331236c3bb net: ethernet: cpmac: Call SET_NETDEV_DEV()
- 9cecb138e54c54989375bceeb448affcdf03497f net: ethernet: lantiq_etop: Call SET_NETDEV_DEV()
- c4587631c7bad47c045e081d1553cd73a23be59a vhost-vsock: fix orphan connection reset
- a37102dcd7ec71f6f6a00b1ad770c3bde3af3c18 Merge branch parisc-4.9-5 of git://git.kernel.org/pub/scm/linux/kernel/git/deller/parisc-linux
- 1e97426d29fec42e559d12cdb069c83962be762e Merge tag linux-can-fixes-for-4.9-20161208 of git://git.kernel.org/pub/scm/linux/kernel/git/mkl/linux-can
- d2a007ab191646d41553ffb6624cef1957e899ae cxgb4/cxgb4vf: Assign netdev->dev_port with port ID
- 24d0492b7d5d321a9c5846c8c974eba9823ffaa0 parisc: Fix TLB related boot crash on SMP machines
- b4aafe77ec65ab2846a5780bb1ba4eff7ccf82d1 Merge tag scsi-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/jejb/scsi
- 1a31cc86ef3ce9d873a713f422c34b47a188caec driver: ipvlan: Unlink the upper dev when ipvlan_link_new failed
- 93a97c50cbf1c007caf12db5cc23e0d5b9c8473c ser_gigaset: return -ENOMEM on error instead of success
- 038ccb3e8cee52e07dc118ff99f47eaebc1d0746 ARM: dts: orion5x: fix number of sata port for linkstation ls-gl
- 7b8076ce8a00d553ae9d3b7eb5f0cc3e63cb16f1 NET: usb: cdc_mbim: add quirk for supporting Telit LE922A
- b67d0dd7d0dc9e456825447bbeb935d8ef43ea7c can: peak: fix bad memory access and free sequence
- c3f4688a08fd86f1bf8e055724c84b7a40a09733 ceph: dont set req->r_locked_dir in ceph_d_revalidate
- 678b5c6b22fed89a13d5b2267f423069a9b11c80 crypto: algif_aead - fix uninitialized variable warning
- 318c8932ddec5c1c26a4af0f3c053784841c598e Merge branch akpm (patches from Andrew)
- 166ad0e1e2132ff0cda08b94af8301655fcabbcd kcov: add missing #include <linux/sched.h>
- 53855d10f4567a0577360b6448d52a863929775b radix tree test suite: fix compilation
- 5c7e9ccd91b90d87029261f8856294ee51934cab zram: restrict add/remove attributes to root only
- 4e4f3e984954143fb0b8e5035df7ff22dd07bb6a Merge branch drm-fixes-4.9 of git://people.freedesktop.org/~agd5f/linux into drm-fixes
- e185934ff94466b4a449165e5f1c164a44d005f2 libata-scsi: disable SCT Write Same for the moment
- 4b707fa00a80b19b80bc8df6f1cbf4bdd9c91402 ARM: dts: imx7d: fix LCDIF clock assignment
- 4367c1d846552163f65aec11dcbe2659c8cf7128 dts: sun8i-h3: correct UART3 pin definitions
- ea5a9eff96fed8252f3a8c94a84959f981a93cae Merge branch x86-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 68f5503bdc8fc309b62a4f555a048ee50d0495a5 Merge branch sched-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- bf7f1c7e2fdfe8b5050e8b3eebf111bf2ed1e8c9 Merge branch perf-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 5b43f97f3f21c42ba738df2797930e32e05d5a25 Merge branch locking-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 407cf05d46fe59e2becfad3a55387d172f6fd0d0 Merge branch core-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- ec988ad78ed6d184a7f4ca6b8e962b0e8f1de461 phy: Dont increment MDIO bus refcount unless its a different owner
- a50af86dd49ee1851d1ccf06dd0019c05b95e297 netvsc: reduce maximum GSO size
- 74685b08fbb26ff5b8448fabe0941a53269dd33e drivers: net: cpsw-phy-sel: Clear RGMII_IDMODE on rgmii links
- 233900d8857dc426557751e30b2150778974417c Merge tag linux-can-fixes-for-4.9-20161207 of git://git.kernel.org/pub/scm/linux/kernel/git/mkl/linux-can
- ce779d6b5bbe6a32452a882605d09518cc79e4ba Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/mszeredi/fuse
- f27c2f69cc8edc03ea8086f974811b9b45b2f3a5 Revert default exported asm symbols to zero
- a0ac402cfcdc904f9772e1762b3fda112dcc56a0 Dont feed anything but regular iovecs to blk_rq_map_user_iov
- faefba95c9e8ca3a523831c2ec2150f5ea054dae drm/amdgpu: just suspend the hw on pci shutdown
- 48a992727d82cb7db076fa15d372178743b1f4cd crypto: mcryptd - Check mcryptd algorithm compatibility
- 0c1e16cd1ec41987cc6671a2bff46ac958c41eb5 crypto: algif_aead - fix AEAD tag memory handling
- 39eaf759466f4e3fbeaa39075512f4f345dffdc8 crypto: caam - fix pointer size for AArch64 boot loader, AArch32 kernel
- 9e5f7a149e00d211177f6de8be427ebc72a1c363 crypto: marvell - Dont corrupt state of an STD req for re-stepped ahash
- 68c7f8c1c4e9b06e6b153fa3e9e0cda2ef5aaed8 crypto: marvell - Dont copy hash operation twice into the SRAM
- 332b05ca7a438f857c61a3c21a88489a21532364 can: raw: raw_setsockopt: limit number of can_filter that can be set
- febe42964fe182281859b3d43d844bb25ca49367 parisc: Remove unnecessary TLB purges from flush_dcache_page_asm and flush_icache_page_asm
- c78e710c1c9fbeff43dddc0aa3d0ff458e70b0cc parisc: Purge TLB before setting PTE
- 325896ffdf90f7cbd59fb873b7ba20d60d1ddf3c device-dax: fix private mapping restriction, permit read-only
- a7de92dac9f0dbf01deb56fe1d661d7baac097e1 tools/testing/nvdimm: unit test acpi_nfit_ctl()
- d6eb270c57fef35798525004ddf2ac5dcdadd43b acpi, nfit: fix bus vs dimm confusion in xlat_status
- 82aa37cf09867c5e2c0326649d570e5b25c1189a acpi, nfit: validate ars_status output buffer size
- efda1b5d87cbc3d8816f94a3815b413f1868e10d acpi, nfit, libnvdimm: fix / harden ars_status output length handling
- 9a901f5495e26e691c7d0ea7b6057a2f3e6330ed acpi, nfit: fix extended status translations for ACPI DSMs
- bc3913a5378cd0ddefd1dfec6917cc12eb23a946 Merge git://git.kernel.org/pub/scm/linux/kernel/git/davem/sparc
- 163117e8d4fd7a235ec48479e31bbda0c74eff56 dbri: move dereference after check for NULL
- da1b466fa47a9c1107e3709395778845dc3bbad7 Merge git://git.kernel.org/pub/scm/linux/kernel/git/davem/net
- 10d20bd25e06b220b1d816228b036e367215dc60 shmem: fix shm fallocate() list corruption
- 32f16e142d7acabad68ef27c123d0caf1548aac3 Merge branch mlx5-fixes
- c0f1147d14e4b09018a495c5095094e5707a4f44 net/mlx5e: Change the SQ/RQ operational state to positive logic
- 3c8591d593a3da9ae8e8342acb1f6ab9ab478e92 net/mlx5e: Dont flush SQ on error
- b8335d91b472289939e26428dfa88c54aee3b739 net/mlx5e: Dont notify HW when filling the edge of ICO SQ
- f9c14e46748be9a2adafdb7d216f6cdeb435aadc net/mlx5: Fix query ISSI flow
- 9e5b2fc1d39b3122e2028849d0edc5df1d1a4761 net/mlx5: Remove duplicate pci dev name print
- f663ad98623926b8d7bdef4b4648d10c0229aebe net/mlx5: Verify module parameters
- f85de6666347c974cdf97b1026180995d912d7d0 net: fec: fix compile with CONFIG_M5272
- d14584d91976c42c7178164665c4959495740939 be2net: Add DEVSEC privilege to SET_HSW_CONFIG command.
- e37e2ff350a321ad9c36b588e76f34fbba305be6 virtio-net: Fix DMA-from-the-stack in virtnet_set_mac_address()
- dcb17d22e1c2cd72e72190c736349a675362b3bc tcp: warn on bogus MSS and try to amend it
- efc45154828ae4e49c6b46f59882bfef32697d44 uapi glibc compat: fix outer guard of net device flags enum
- 6b3374cb1c0bd4699ace03d7e0dc14b532e4f52e net: stmmac: clear reset value of snps, wr_osr_lmt/snps, rd_osr_lmt before writing
- c01638f5d919728f565bf8b5e0a6a159642df0d9 fuse: fix clearing suid, sgid for chown()
- f943fe0faf27991d256e10b5a85f175385c64cdc lockdep: Fix report formatting
- 8fc31ce8896fc3cea1d79688c8ff950ad4e73afe perf/core: Remove invalid warning from list_update_cgroup_even()t
- 7f612a7f0bc13a2361a152862435b7941156b6af perf/x86: Fix full width counter, counter overflow
- 1dba23b12f49d7cf3d4504171c62541122b55141 perf/x86/intel: Enable C-state residency events for Knights Mill
- 69042bf2001b44e81cd86ab11a4637b9d9a14c5a objtool: Fix bytes check of leas rex_prefix
- ed5d7788a934a4b6d6d025e948ed4da496b4f12e netlink: Do not schedule work from sk_destruct
- ffe3bb85c19e1dbf96cc13aad823ae0a8855d066 uapi: export nf_log.h
- ad558858295726cb876b78d1c39d471372f1901a uapi: export tc_skbmod.h
- c823abac17926767fb50175e098f087a6ac684c3 net: ep93xx_eth: Do not crash unloading module
- 34e0f2c2d82d7d939bfa249672311050b3b537f1 Merge branch bnx2x-fixes
- 360d9df2acd9f0b89aabaf16fca08954f113bd4e bnx2x: Prevent tunnel config for 577xx
- 65870fa77fd7f83d7be4ed924d47ed9e3831f434 bnx2x: Correct ringparam estimate when DOWN
- 9a53682b340b97642793271ba095cc9531a7b649 isdn: hisax: set error code on failure
- 005f7e68e74df94c2a676b5a3e98c6fb65aae606 net: bnx2x: fix improper return value
- 0ff18d2d36efad65572990fa7febeb3ebe19da89 net: ethernet: qlogic: set error code on failure
- 7cf6156633b71743c09a8e56b1f0dedfc4ce6e66 atm: fix improper return value
- 8ad3ba934587c8ecbfee13331d859a7849afdfbb net: irda: set error code on failures
- c79e167c3cba066892542f3dfb5e73b7207e01df net: caif: remove ineffective check
- 0eab121ef8750a5c8637d51534d5e9143fb0633f net: ping: check minimum size on ICMP header length
- d9d04527c79f0f7d9186272866526e871ef4ac6f Merge tag powerpc-4.9-7 of git://git.kernel.org/pub/scm/linux/kernel/git/powerpc/linux
- 4606c9e8c541f97034e53e644129376a6170b8c7 atm: lanai: set error code when ioremap fails
- 51920830d9d0eb617af18dc60443fcd4fb50a533 net: usb: set error code when usb_alloc_urb fails
- b59589635ff01cc25270360709eeeb5c45c6abb9 net: bridge: set error code on failure
- 14dd3e1b970feb125e4f453bc3b0569db5b2069b net: af_mpls.c add space before open parenthesis
- 89aa8445cd4e8c2556c40d42dd0ceb2cbb96ba78 netdev: broadcom: propagate error code
- 2279b752ac5c2d3592fe6fe5610c123c2ee8b37c Merge branch fib-suffix-length-fixes
- a52ca62c4a6771028da9c1de934cdbcd93d54bb4 ipv4: Drop suffix update from resize code
- 1a239173cccff726b60ac6a9c79ae4a1e26cfa49 ipv4: Drop leaf from suffix pull/push functions
- ef3263e35e26eb1061260131c4d6d579eea21f85 Merge branch linus of git://git.kernel.org/pub/scm/linux/kernel/git/herbert/crypto-2.6
- 3e5de27e940d00d8d504dfb96625fb654f641509 Linux 4.9-rc8
- c66ebf2db555c6ed705044eabd2b37dcd546f68b net: dcb: set error code on failures
- 0cb65c83304a341b9d09678448d7c8b550689531 Merge tag drm-fixes-for-v4.9-rc8 of git://people.freedesktop.org/~airlied/linux
- a38b61009425b3882704270e792a6e743f5d9426 Merge tag batadv-net-for-davem-20161202 of git://git.open-mesh.org/linux-merge
- ab7cd8d83e5dba13027de66f1b008b08b30b71a4 Merge tag drm-intel-fixes-2016-12-01 of git://anongit.freedesktop.org/git/drm-intel into drm-fixes
- 3c49de52d5647cda8b42c4255cf8a29d1e22eff5 Merge branch akpm (patches from Andrew)
- bd041733c9f612b66c519e5a8b1a98b05b94ed24 mm, vmscan: add cond_resched() into shrink_node_memcg()
- 20ab67a563f5299c09a234164c372aba5a59add8 mm: workingset: fix NULL ptr in count_shadow_nodes
- 865563924022d8a307ee6dbc6a9ab4fb4d461cce kbuild: fix building bzImage with CONFIG_TRIM_UNUSED_KSYMS enabled
- 8dc0f265d39a3933f4c1f846c7c694f12a2ab88a Merge tag fixes-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/arm/arm-soc
- 8bca927f13bc1cebe23a3709af6ce3016400f7ac Merge git://git.kernel.org/pub/scm/linux/kernel/git/davem/net
- b98b0bc8c431e3ceb4b26b0dfc8db509518fb290 net: avoid signed overflows for SO_{SND|RCV}BUFFORCE
- 5b01014759991887b1e450c9def01e58c02ab81b geneve: avoid use-after-free of skb->data
- 3de81b758853f0b29c61e246679d20b513c4cfec tipc: check minimum bearer MTU
- f0d21e894713b43a75bdf2d1b31e587bd5db5341 Merge tag linux-can-fixes-for-4.9-20161201 of git://git.kernel.org/pub/scm/linux/kernel/git/mkl/linux-can
- 50d5aa4cf822887f88841e4d8f8502434af679a9 net: renesas: ravb: unintialized return value
- 33d446dbba4d4d6a77e1e900d434fa99e0f02c86 sh_eth: remove unchecked interrupts for RZ/A1
- 8c4799ac799665065f9bf1364fd71bf4f7dc6a4a net: bcmgenet: Utilize correct struct device for all DMA operations
- ed8d747fd2b9d9204762ca6ab8c843c72c42cc41 Fix up a couple of field names in the CREDITS file
- 9bd813da24cd49d749911d7fdc0e9ae9a673d746 NET: usb: qmi_wwan: add support for Telit LE922A PID 0x1040
- d5c83d0d1d83b3798c71e0c8b7c3624d39c91d88 cdc_ether: Fix handling connection notification
- 6b6ebb6b01c873d0cfe3449e8a1219ee6e5fc022 ip6_offload: check segs for NULL in ipv6_gso_segment.
- 721c7443dcb26bf8c0b4ad317a36c7dfa140f1e4 RDS: TCP: unregister_netdevice_notifier() in error path of rds_tcp_init_net
- 80d1106aeaf689ab5fdf33020c5fecd269b31c88 Revert: ip6_tunnel: Update skb->protocol to ETH_P_IPV6 in ip6_tnl_xmit()
- b4e479a96fc398ccf83bb1cffb4ffef8631beaf1 ipv6: Set skb->protocol properly for local output
- f4180439109aa720774baafdd798b3234ab1a0d2 ipv4: Set skb->protocol properly for local output
- 84ac7260236a49c79eede91617700174c2c19b0c packet: fix race condition in packet_set_ring
- 4aa675aaf22790188d6b9c47d3d44570720c0e34 Merge tag for-linus of git://git.kernel.org/pub/scm/virt/kvm/kvm
- 3e52d063d809df58da9be59c67d755c0d1ffa7c8 Merge branch i2c/for-current of git://git.kernel.org/pub/scm/linux/kernel/git/wsa/linux
- 2219d5ed77e8bdc2ef1f0b79f34d2cc0be802b25 net: ethernet: altera: TSE: do not use tx queue lock in tx completion handler
- 151a14db228181fb49abaf83e13f3be58ec102c4 net: ethernet: altera: TSE: Remove unneeded dma sync for tx buffers
- 8ab2ae655bfe384335c5b6b0d6041e0ddce26b00 default exported asm symbols to zero
- 909e481e2467f202b97d42beef246e8829416a85 arm64: dts: juno: fix cluster sleep state entry latency on all SoC versions
- d262fd12cd03afca40ced117d837fa576a667eab Merge branch stmmac-probe-error-handling-and-phydev-leaks
- d2ed0a7755fe14c790f398ae55088d00492ef168 net: ethernet: stmmac: fix of-node and fixed-link-phydev leaks
- 661f049be17a3894cb438d46ba5af8e3643aac28 net: ethernet: stmmac: platform: fix outdated function header
- 5cc70bbcacf6728b598b529a061930d8271adbb5 net: ethernet: stmmac: dwmac-meson8b: fix probe error path
- 939b20022765bc338b0f72cbf1eed60a907398d7 net: ethernet: stmmac: dwmac-generic: fix probe error path
- 2d222656db08b8eef3b53b56cf1ce4a90fe8cd78 net: ethernet: stmmac: dwmac-rk: fix probe error path
- 0a9e22715ee384cf2a714c28f24ce8881b9fd815 net: ethernet: stmmac: dwmac-sti: fix probe error path
- 50ac64cfc39dad2ba0d8ad553d2d87dfc738cbba net: ethernet: stmmac: dwmac-socfpga: fix use-after-free on probe errors
- 6919756caaeaa76dc56287252fb656e3c2d9b4e1 net/rtnetlink: fix attribute name in nlmsg_size() comments
- 1be5d4fa0af34fb7bafa205aeb59f5c7cc7a089d locking/rtmutex: Use READ_ONCE() in rt_mutex_owner()
- dbb26055defd03d59f678cb5f2c992abe05b064a locking/rtmutex: Prevent dequeue vs. unlock race
- c2d0f48a13e53b4747704c9e692f5e765e52041a batman-adv: Check for alloc errors when preparing TT local data
- 4db5e636ddca41f4292359fdb3ac7cc4346a359a Merge tag pci-v4.9-fixes-4 of git://git.kernel.org/pub/scm/linux/kernel/git/helgaas/pci
- c54cdc316dbd35695cd54dd425327463c72809e4 ixgbe/ixgbevf: Dont use lco_csum to compute IPv4 checksum
- 516165a1e2f22e512a976f8dafd76a22310ccfd9 igb/igbvf: Dont use lco_csum to compute IPv4 checksum
- fadf3a28054404f075c05d9ca8ebd4b4ce9ebc0f net: asix: Fix AX88772_suspend() USB vendor commands failure issues
- 2caceb3294a78c389b462e7e236a4e744a53a474 Merge branch overlayfs-linus of git://git.kernel.org/pub/scm/linux/kernel/git/mszeredi/vfs
- 92cf44e284d0c2e456d43c0951107a4ec046ef1c Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/dtor/input
- d3fc425e819be7c251a9c208cd4c0a6373c19bfe kbuild: make sure autoksyms.h exists early
- 7bbf91ce27dd83cae1452995b15d358db92a8235 Merge branch master of git://git.kernel.org/pub/scm/linux/kernel/git/klassert/ipsec
- 3d2dd617fb3c6430e438038070d2d2fb423725f9 Merge git://git.kernel.org/pub/scm/linux/kernel/git/pablo/nf
- a0f1d21c1ccb1da66629627a74059dd7f5ac9c61 KVM: use after free in kvm_ioctl_create_device()
- 0f4828a1da3342be81e812b28fbcf29261146d25 Merge tag kvm-arm-for-4.9-rc7 of git://git.kernel.org/pub/scm/linux/kernel/git/kvmarm/kvmarm
- f00b534ded60bd0a23c2fa8dec4ece52aa7d235f can: peak: Add support for PCAN-USB X6 USB interface
- fe5b40642f1a2dddfeb84be007b2c975c28d4c6c can: peak: Fix bittiming fields size in bits
- dadc4a1bb9f0095343ed9dd4f1d9f3825d7b3e45 powerpc/64: Fix placement of .text to be immediately following .head.text
- 409bf7f8a02ef88db5a0f2cdcf9489914f4b8508 powerpc/eeh: Fix deadlock when PE frozen state cant be cleared
- 43c4f67c966deb1478dc9acbf66ab547287d530f Merge branch akpm (patches from Andrew)
- 5cbc198ae08d84bd416b672ad8bd1222acd0855c mm: fix false-positive WARN_ON() in truncate/invalidate for hugetlb
- 828347f8f9a558cf1af2faa46387a26564f2ac3e kasan: support use-after-scope detection
- 045d599a286bc01daa3510d59272440a17b23c2e kasan: update kasan_global for gcc 7
- f8ff04e2be0815b34d11a72d08473a383a3c9eb5 lib/debugobjects: export for use in modules
- 529e71e16403830ae0d737a66c55c5f360f3576b zram: fix unbalanced idr management at hot removal
- 655548bf6271b212cd1e4c259da9dbe616348d38 thp: fix corner case of munlock() of PTE-mapped THPs
- e1465d125d2189e667029b9fa8a6f455180fbcf2 mm, thp: propagation of conditional compilation in khugepaged.c
- 83fb8b055544a25ceeac34a666a2149331ea94bf Merge tag drm-misc-fixes-2016-11-30 of git://anongit.freedesktop.org/git/drm-misc into drm-fixes
- f513581c35525bccfb0aadb55189478df1cfddba Merge tag clk-fixes-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/clk/linux
- 4c9456df8849204435c4de1849120b916975d75d arm64: dts: juno: Correct PCI IO window
- aa196eed3d80d4b003b04a270712b978a012a939 macvtap: handle ubuf refcount correctly when meet errors
- af1cc7a2b86ddb8668ac38097866bedd7b849a76 tun: handle ubuf refcount correctly when meet errors
- 4ccfd6383a1a4838ed034120f00d02dbdc681d6f net: ethernet: ti: cpsw: fix ASSERT_RTNL() warning during resume
- e2b588ab60c797d327551d9aaca914f962d5194b Merge tag pwm/for-4.9 of git://git.kernel.org/pub/scm/linux/kernel/git/thierry.reding/linux-pwm
- e2d2afe15ed452f91797a80dbc0a17838ba03ed4 bpf: fix states equal logic for varlen access
- 17a49cd549d9dc8707dc9262210166455c612dde netfilter: arp_tables: fix invoking 32bit iptable -P INPUT ACCEPT failed in 64bit kernel
- 0fcba2894c6b370ebf4b49099d20ff6333a430f7 Merge tag wireless-drivers-for-davem-2016-11-29 of git://git.kernel.org/pub/scm/linux/kernel/git/kvalo/wireless-drivers
- 7752f72748db3ce9312e2171f80cbbb42bf4dde6 Merge branch l2tp-fixes
- 31e2f21fb35bfaa5bdbe1a4860dc99e6b10d8dcd l2tp: fix address test in __l2tp_ip6_bind_lookup()
- df90e6886146dd744eb3929782e6df9749cd4a69 l2tp: fix lookup for sockets not bound to a device in l2tp_ip
- d5e3a190937a1e386671266202c62565741f0f1a l2tp: fix racy socket lookup in l2tp_ip and l2tp_ip6 bind()
- a3c18422a4b4e108bcf6a2328f48867e1003fd95 l2tp: hold socket before dropping lock in l2tp_ip{, 6}_recv()
- 0382a25af3c771a8e4d5e417d1834cbe28c2aaac l2tp: lock socket before checking flags in connect()
- bb83d62fa83405d7c325873a317c9374f98eedef cxgb4: Add PCI device ID for new adapter
- a107bf8b3905b61bf8b5c181268bca8c05af7f69 isofs: add KERN_CONT to printing of ER records
- 80cca775cdc4f8555612d2943a2872076b33e0ff net: fec: cache statistics while device is down
- 17b463654f41f0aa334efd5a6efeab8a6e9496f7 vxlan: fix a potential issue when create a new vxlan fdb entry.
- 2425f1808123bf69a8f66d4ec90e0d0e302c2613 Input: change KEY_DATA from 0x275 to 0x277
- f92a80a9972175a6a1d36c6c44be47fb0efd020d openvswitch: Fix skb leak in IPv6 reassembly.
- 57891633eeef60e732e045731cf20e50ee80acb4 crypto: rsa - Add Makefile dependencies to fix parallel builds
- 66bf093772040ae8b864d2cf953f2c73005f7815 crypto: chcr - Fix memory corruption
- 5102981212454998d549273ff9847f19e97a1794 crypto: drbg - prevent invalid SG mappings
- 0f8d0cf517868beba21f8b5cdb709f275ac9c7d0 Merge tag v4.9-rc7 into hostos-devel

* Wed Nov 30 2016 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.9.0-3
- 0f8d0cf517868beba21f8b5cdb709f275ac9c7d0 Merge tag v4.9-rc7 into hostos-devel
- 769f8858dd3c35c8a0866da51f890a117f9a0549 Merge branch kvm-ppc-next into hostos-devel
- 6ccad8cea5bcb0660f56677a5fdc52265f8ddf76 KVM: Add halt polling documentation
- 908a09359ef4ed9e9ca1147b9d35f829d7e42a74 KVM: PPC: Book3S HV: Comment style and print format fixups
- f4944613ad1ab6760589d5791488be1236c07fcc KVM: PPC: Decrease the powerpc default halt poll max value
- e03f3921e597cbcc6880033e5c52fa1db524f88b KVM: PPC: Book3S HV: Add check for module parameter halt_poll_ns
- 307d93e476a340116cbddd1d3d7edf9b3cdd7506 KVM: PPC: Book3S HV: Use generic kvm module parameters
- ec76d819d27040e418801d1a57bd3bdfde51019e KVM: Export kvm module parameter variables
- e5517c2a5a49ed5e99047008629f1cd60246ea0e Linux 4.9-rc7
- 105ecadc6d9c1effd23dd46fcc340f62d467cd6c Merge git://git.infradead.org/intel-iommu
- ff17bf8a0d2d60a343db304b835c0e83efa660d9 Merge branch upstream of git://git.linux-mips.org/pub/scm/ralf/upstream-linus
- d8e435f3ab6fea2ea324dce72b51dd7761747523 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/viro/vfs
- 8e54cadab447dae779f80f79c87cbeaea9594f60 fix default_file_splice_read()
- e348031214d5dce67be93271433b27a93cba5b3f Merge branch i2c/for-current of git://git.kernel.org/pub/scm/linux/kernel/git/wsa/linux
- a56f3eb2cd72d4d678a63cf8cacf9d39aa8020f3 Merge branch fixes of git://git.armlinux.org.uk/~rmk/linux-arm
- a0d60e62ea5c88a9823410e9d0929a513e29dea2 Merge git://git.kernel.org/pub/scm/linux/kernel/git/davem/net
- 30e2b7cfc54c1efa0aa4c75eb8aa19318e3932e3 Merge branch libnvdimm-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/nvdimm/nvdimm
- fc13ca191ee2ae5f379e2933cdff523c3b4fffc9 Merge tag for-linus of git://git.kernel.org/pub/scm/virt/kvm/kvm
- 39c1573748166b348117d6bf161ceffce90e734f Merge tag powerpc-4.9-6 of git://git.kernel.org/pub/scm/linux/kernel/git/powerpc/linux
- 6998cc6ec23740347670da13186d2979c5401903 tipc: resolve connection flow control compatibility problem
- e8f967c3d88489fc1562a31d4e44d905ac1d3aff mvpp2: use correct size for memset
- 5e7dfeb758663391ec721e6a4519d3df874f9b1f net/mlx5: drop duplicate header delay.h
- 8f8a8b13b447842b147539ae2cab6699897539b9 net: ieee802154: drop duplicate header delay.h
- 4ee12efa2dbf949d72ef2f7ef2e044af5a67b515 ibmvnic: drop duplicate header seq_file.h
- 1f1e70efe53c01844ce76d77c3383c2bcb6beb49 fsl/fman: fix a leak in tgec_free()
- 8006f6bf5e39f11c697f48df20382b81d2f2f8b8 net: ethtool: dont require CAP_NET_ADMIN for ETHTOOL_GLINKSETTINGS
- d876a4d2afecacf4b4d8b11479e9f1ed0080bb2e tipc: improve sanity check for received domain records
- f79675563a6bbfc2ff85684bbbaea9ef092664d2 tipc: fix compatibility bug in link monitoring
- 97db8afa2ab919fc400fe982f5054060868bdf07 net: ethernet: mvneta: Remove IFF_UNICAST_FLT which is not implemented
- 3ad0e83cf86bcaeb6ca3c37060a3ce866b25fb42 Merge branch parisc-4.9-4 of git://git.kernel.org/pub/scm/linux/kernel/git/deller/parisc-linux
- 86b01b5419fd303a3699b2ce6f4b9bfbdaa4ed37 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/jmorris/linux-security
- cd3caefb4663e3811d37cc2afad3cce642d60061 Fix subtle CONFIG_MODVERSIONS problems
- beb53e4b2328b0947622dd1bf407295bf1d9b436 Merge tag acpi-4.9-rc7 of git://git.kernel.org/pub/scm/linux/kernel/git/rafael/linux-pm
- 686564434e88b67ea8dbbf9150286d04c83bd193 MAINTAINERS: Add bug tracking system location entry type
- 89119f08354b628548118cacd686a7700372ad19 Revert i2c: designware: do not disable adapter after transfer
- 7e5c07af8693e72b23aefb70da88b31b30c35b22 Merge branches acpi-sleep-fixes and acpi-wdat-fixes
- fb09c8c524dae2b893aacc9348e876a87b45b697 Merge tag linux-can-fixes-for-4.9-20161123 of git://git.kernel.org/pub/scm/linux/kernel/git/mkl/linux-can
- f7db0ec9572f66b36c0d4d6bc4b564da53c8b35d dwc_eth_qos: drop duplicate headers
- f2051f8f9d30f5bae693863dca3416a1ef69064c Merge tag mfd-fixes-4.9.1 of git://git.kernel.org/pub/scm/linux/kernel/git/lee/mfd
- ea9ea6c6f595ec774e957834d5485949c469ed0e Merge tag media/v4.9-4 of git://git.kernel.org/pub/scm/linux/kernel/git/mchehab/linux-media
- 6006d6e719a02337132c96bf2114a703a0514856 Merge tag drm-fixes-for-v4.9-rc7 of git://people.freedesktop.org/~airlied/linux
- 5035b230e7b67ac12691ed3b5495bbb617027b68 parisc: Also flush data TLB in flush_icache_page_asm
- c0452fb9fb8f49c7d68ab9fa0ad092016be7b45f parisc: Fix race in pci-dma.c
- 43b1f6abd59063a088416a0df042b36450f91f75 parisc: Switch to generic sched_clock implementation
- 741dc7bf1c7c7d93b853bb55efe77baa27e1b0a9 parisc: Fix races in parisc_setup_cache_timing()
- 1a41741fd60b0a2d1102c3d1ff9d58cb324a8d29 mfd: wm8994-core: Dont use managed regulator bulk get API
- 3cfc43df7af0533b39b97bb03980e02e9716fc52 mfd: wm8994-core: Disable regulators before removing them
- 2a872a5dcec7052e9fd948ee77a62187791735ff MIPS: mm: Fix output of __do_page_fault
- d29ccdb3f0e5dccb170200c9f3d573eaa5af261b mfd: syscon: Support native-endian regmaps
- 9704668e4b7105ede483f38da7f29d71b5bc0165 Merge branch mediatek-drm-fixes-2016-11-24 of https://github.com/ckhu-mediatek/linux.git-tags into drm-fixes
- 984d7a1ec67ce3a46324fa4bcb4c745bbc266cf2 powerpc/mm: Fixup kernel read only mapping
- f5527fffff3f002b0a6b376163613b82f69de073 mpi: Fix NULL ptr dereference in mpi_powm() [ver #3]
- 2b95fda2c4fcb6d6625963f889247538f247fce0 X.509: Fix double free in x509_cert_parse() [ver #3]
- d74200024009c8d974c7484446c9eb1622408a17 gpu/drm/exynos/exynos_hdmi - Unmap region obtained by of_iomap
- f9e154a0e6730218c222d95af22784b0a53e3f58 Merge branch for-upstream of git://git.kernel.org/pub/scm/linux/kernel/git/bluetooth/bluetooth
- 19a8bb28d1c66670a2aebf9c78ec21c0b942f4b8 net sched filters: fix filter handle ID in tfilter_notify_chain()
- 76da8706d90d8641eeb9b8e579942ed80b6c0880 net: dsa: bcm_sf2: Ensure we re-negotiate EEE during after link change
- 867d1212bf3c53dc057f7bca72155048cc51d18c bnxt: do not busy-poll when link is down
- 30c7be26fd3587abcb69587f781098e3ca2d565b udplite: call proper backlog handlers
- 16ae16c6e5616c084168740990fc508bda6655d4 Merge tag mmc-v4.9-rc5 of git://git.kernel.org/pub/scm/linux/kernel/git/ulfh/mmc
- bae73e80d48ace1faa33da846dd124fbef661b7f Merge tag usb-4.9-rc7 of git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/usb
- e2b6535d47ce223e327de053b804d2e572a98bbc Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/jikos/hid
- df492896e6dfb44fd1154f5402428d8e52705081 KVM: x86: check for pic and ioapic presence before use
- 81cdb259fb6d8c1c4ecfeea389ff5a73c07f5755 KVM: x86: fix out-of-bounds accesses of rtc_eoi map
- 2117d5398c81554fbf803f5fd1dc55eb78216c0c KVM: x86: drop error recovery in em_jmp_far and em_ret_far
- 444fdad88f35de9fd1c130b2c4e4550671758fd2 KVM: x86: fix out-of-bounds access in lapic
- 18594e9bc4a27e72d7961a7afe4250a502d1538d init: use pr_cont() when displaying rotator during ramdisk loading.
- 764d3be6e415b40056834bfd29b994dc3f837606 ipv6: bump genid when the IFA_F_TENTATIVE flag is clear
- 1031398035a25e5c90c66befb6ff41fa4746df98 MIPS: Mask out limit field when calculating wired entry count
- 4d6d5f1d08d2138dc43b28966eb6200e3db2e623 i2c: designware: fix rx fifo depth tracking
- 2bf413d56b7de72ab800a6edb009177e5669b929 i2c: designware: report short transfers
- 5ad45307d990020b25a8f7486178b6e033790f70 drm/mediatek: fix null pointer dereference
- f6c872397028837c80685ee96c4011c62abe9a73 drm/mediatek: fixed the calc method of data rate per lane
- 1ee6f347f81925fa8f3816e69ca1b49021f37850 drm/mediatek: fix a typo of DISP_OD_CFG to OD_RELAYMODE
- a1ff57416af9a7971a801d553cd53edd8afb28d6 powerpc/boot: Fix the early OPAL console wrappers
- a8acaece5d88db234d0b82b8692dea15d602f622 KVM: PPC: Correctly report KVM_CAP_PPC_ALLOC_HTAB
- a91d5df2b44a0c9b171ac47a48e02e762c8224e9 KVM: PPC: Move KVM_PPC_PVINFO_FLAGS_EV_IDLE definition next to its structure
- e2702871b4b70a39e08c46744a8fa16e281120aa KVM: PPC: Book3S HV: Fix compilation with unusual configurations
- b6e01232e25629907df9db19f25da7d4e8f5b589 net/mlx4_en: Free netdev resources under state lock
- a4cd0271ead09439fa03ce38fa79654dd1e5484b net: revert net: l2tp: Treat NET_XMIT_CN as success in l2tp_eth_dev_xmit
- 93af205656bed3d8d3f4b85b2a3749c7ed7d996a rtnetlink: fix the wrong minimal dump size getting from rtnl_calcit()
- 57aac71b3e9ed890cf2219dd980c36f859b43d6a bnxt_en: Fix a VXLAN vs GENEVE issue
- 920c1cd36642ac21a7b2fdc47ab44b9634d570f9 netdevice.h: fix kernel-doc warning
- c3891fa2543cbab26093f5e425b8a50cd6837f16 driver: macvlan: Check if need rollback multicast setting in macvlan_open
- ffa54a238c69184414a8f3dc35a18aed875290e7 net: phy: micrel: fix KSZ8041FTL supported value
- 855f6529c7c974a566eb56d5e3351a628305e16e Merge branch for-upstream/hdlcd of git://linux-arm.org/linux-ld into drm-fixes
- 7ad54c99be62ff2f96deb002cff8221dd6f57087 Merge branch drm-fixes-4.9 of git://people.freedesktop.org/~agd5f/linux into drm-fixes
- 22a1e7783e173ab3d86018eb590107d68df46c11 xc2028: Fix use-after-free bug properly
- 10b9dd56860e93f11cd352e8c75a33357b80b70b Merge tag nfs-for-4.9-4 of git://git.linux-nfs.org/projects/anna/linux-nfs
- 2ee13be34b135957733b84ef5f7bd30c80ec3c42 KVM: PPC: Book3S HV: Update kvmppc_set_arch_compat() for ISA v3.00
- 45c940ba490df28cb87b993981a5f63df6bbb8db KVM: PPC: Book3S HV: Treat POWER9 CPU threads as independent subcores
- 84f7139c064ed740d183ae535bda2f6d7ffc0d57 KVM: PPC: Book3S HV: Enable hypervisor virtualization interrupts while in guest
- bf53c88e42ac5dfdef649888d01b3bc96375647b KVM: PPC: Book3S HV: Use stop instruction rather than nap on POWER9
- f725758b899f11cac6b375e332e092dc855b9210 KVM: PPC: Book3S HV: Use OPAL XICS emulation on POWER9
- 1704a81ccebc69b5223220df97cde8a645271828 KVM: PPC: Book3S HV: Use msgsnd for IPIs to other cores on POWER9
- 7c5b06cadf274f2867523c1130c11387545f808e KVM: PPC: Book3S HV: Adapt TLB invalidations to work on POWER9
- e9cf1e085647b433ccd98582681b17121ecfdc21 KVM: PPC: Book3S HV: Add new POWER9 guest-accessible SPRs
- 83677f551e0a6ad43061053e7d6208abcd2707f0 KVM: PPC: Book3S HV: Adjust host/guest context switch for POWER9
- 7a84084c60545bc47f3339344f1af5f94599c966 KVM: PPC: Book3S HV: Set partition table rather than SDR1 on POWER9
- abb7c7ddbacd30b9a879491998966771504760bd KVM: PPC: Book3S HV: Adapt to new HPTE format on POWER9
- bc33b1fc83c0ecfcfcbb3c36fbaf7aec8bba6518 Merge remote-tracking branch remotes/powerpc/topic/ppc-kvm into kvm-ppc-next
- 4d92c8d036a7f1c9671eb672e7623925f5274737 Merge branch stable of git://git.kernel.org/pub/scm/linux/kernel/git/cmetcalf/linux-tile
- e658a6f14d7c0243205f035979d0ecf6c12a036f tile: avoid using clocksource_cyc2ns with absolute cycle count
- d3ac31f3b4bf9fade93d69770cb9c34912e017be drm/radeon: fix power state when port pm is unavailable (v2)
- 1db4496f167bcc7c6541d449355ade2e7d339d52 drm/amdgpu: fix power state when port pm is unavailable
- d443a0aa3a291e5f78072f2fa464e03bc83fafad HID: hid-sensor-hub: clear memory to avoid random data
- 6dab07df555b652d8d989348b2ce04498d7f9a70 HID: rmi: make transfer buffers DMA capable
- b7a87ad6775f3ed69e6573b91ed3c2f1338884ad HID: magicmouse: make transfer buffers DMA capable
- 061232f0d47fa10103f3efa3e890f002a930d902 HID: lg: make transfer buffers DMA capable
- 1ffb3c40ffb5c51bc39736409b11816c4260218e HID: cp2112: make transfer buffers DMA capable
- ded9b5dd205ef04aa095c3b731c635b201191a59 Merge branch perf-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 5499a6b22e5508b921c447757685b0a5e40a07ed can: bcm: fix support for CAN FD frames
- 8478132a8784605fe07ede555f7277d989368d73 Revert arm: move exports to definitions
- 23aabe73d53c29ee8da71397f87f190bdcde5b68 Merge branch linus of git://git.kernel.org/pub/scm/linux/kernel/git/herbert/crypto-2.6
- 02ed21aeda0e02d84af493f92b1b6b6b13ddd6e8 powerpc/powernv: Define and set POWER9 HFSCR doorbell bit
- 1f0f2e72270c089c291aac794800cc326c4c05dd powerpc/reg: Add definition for LPCR_PECE_HVEE
- 9dd17e8517f5ccd594a01374b0b41ec1a1c266af powerpc/64: Define new ISA v3.00 logical PVR value and PCR register value
- ffe6d810fe95208b9f132fb7687930185129305a powerpc/powernv: Define real-mode versions of OPAL XICS accessors
- 9d66195807ac6cb8a14231fd055ff755977c5fca powerpc/64: Provide functions for accessing POWER9 partition table
- 23400ac997062647f2b63c82030d189671b1effe Merge branch for-rc of git://git.kernel.org/pub/scm/linux/kernel/git/rzhang/linux
- 39385cb5f3274735b03ed1f8e7ff517b02a0beed Bluetooth: Fix using the correct source address type
- b66c08ba28aa1f81eb06a1127aa3936ff77e5e2c Merge tag scsi-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/jejb/scsi
- 57527ed10b3bc2abf50844f6995371fa9ac503df Merge tag clk-fixes-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/clk/linux
- d55b352b01bc78fbc3d1bb650140668b87e58bf9 NFSv4.x: hide array-bounds warning
- 000b8949e903fc8bf78b99ac8568347251986ebf Merge branch sched-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 7cfc4317ea56615aaa006f37fc89ed248fcc0fc0 Merge branch x86-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- c9b8af1330198ae241cd545e1f040019010d44d9 flow_dissect: call init_default_flow_dissectors() earlier
- 4345a64ac931a8dc499f1fc69880952412f36c3e parisc: Fix printk continuations in system detection
- 7a79279e7186c4ac8b753cbd335ecc4ba81b5970 drm/arm: hdlcd: fix plane base address update
- 033ac60c7f21f9996a0fab2fd04f334afbf77b33 perf/x86/intel/uncore: Allow only a single PMU/box within an events group
- b8000586c90b4804902058a38d3a59ce5708e695 perf/x86/intel: Cure bogus unwind from PEBS entries
- ae31fe51a3cceaa0cabdb3058f69669ecb47f12e perf/x86: Restore TASK_SIZE check on frame pointer
- 8e5bfa8c1f8471aa4a2d30be631ef2b50e10abaf sched/autogroup: Do not use autogroup->tg in zombie threads
- 18f649ef344127ef6de23a5a4272dbe2fdb73dde sched/autogroup: Fix autogroup_move_group() to never skip sched_move_task()
- 9e5f68842276672a05737c23e407250f776cbf35 powerpc: Fix missing CRCs, add more asm-prototypes.h declarations
- c8467f7a3620698bf3c22f0e199b550fb611a8ae crypto: scatterwalk - Remove unnecessary aliasing check in map_and_copy
- 8acf7a106326eb94e143552de81f34308149121c crypto: algif_hash - Fix result clobbering in recvmsg
- 7a43906f5cbfb74712af168988455e350707e310 powerpc: Set missing wakeup bit in LPCR on POWER9
- 3b404a519815b9820f73f1ecf404e5546c9270ba Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/jmorris/linux-security
- 7fd317f8c330a8d3ed6468d5670e5c09c25846e2 powerpc/64: Add some more SPRs and SPR bits for POWER9
- 8d1a2408efa6a5e75f4c968351a240425c3fa0e5 Merge git://git.kernel.org/pub/scm/linux/kernel/git/davem/sparc
- effb46b40f8053fd19698daf9e6b5833cabeba29 watchdog: wdat_wdt: Select WATCHDOG_CORE
- 27e7ab99db51569886f52f9d025473e9f453a67b Merge git://git.kernel.org/pub/scm/linux/kernel/git/davem/net
- 7082c5c3f2407c52022507ffaf644dbbab97a883 tcp: zero ca_priv area when switching cc algorithms
- 7c6ae610a1f0a9d3cebf790e0245b4e0f76aa86e net: l2tp: Treat NET_XMIT_CN as success in l2tp_eth_dev_xmit
- d75a6a0e3933acbba44e4ad8d8f3c4d4f76b6e03 NFSv4.1: Keep a reference on lock states while checking
- 6bc5445c0180a0c7cc61a95d131c7eac66459692 ethernet: stmmac: make DWMAC_STM32 depend on its associated SoC
- 9713adc2a1a5488f4889c657a0c0ce0c16056d3c Revert ACPI: Execute _PTS before system reboot
- ec638db8cb9ddd5ca08b23f2835b6c9c15eb616d thermal/powerclamp: add back module device table
- e96271f3ed7e702fa36dd0605c0c5b5f065af816 perf/core: Fix address filter parser
- 647f80a1f233bb66fc58fb25664d029e0f12f3ae mmc: dw_mmc: fix the error handling for dma operation
- e5dce2868818ca8706924f7bdc7939d481eefab0 x86/platform/intel-mid: Rename platform_wdt to platform_mrfld_wdt
- a980ce352fcd408d30b044455e5f6e959d6258b6 x86/build: Build compressed x86 kernels as PIE when !CONFIG_RELOCATABLE as well
- 8c5c86fb6abec7d76ec4d51a46714161bceab315 x86/platform/intel-mid: Register watchdog device after SCU
- b22cbe404a9cc3c7949e380fa1861e31934c8978 x86/fpu: Fix invalid FPU ptrace state after execve()
- ed68d7e9b9cfb64f3045ffbcb108df03c09a0f98 x86/boot: Fail the boot if !M486 and CPUID is missing
- fc0e81b2bea0ebceb71889b61d2240856141c9ee x86/traps: Ignore high word of regs->cs in early_fixup_exception()
- 3d40658c977769ce2138f286cf131537bf68bdfe apparmor: fix change_hat not finding hat after policy replacement
- 68b8b72bb221f6d3d14b7fcc9c6991121b6a06ba KVM: PPC: Book3S HV: Drop duplicate header asm/iommu.h
- f064a0de1579fabded8990bed93971e30deb9ecb KVM: PPC: Book3S HV: Dont lose hardware R/C bit updates in H_PROTECT
- 0d808df06a44200f52262b6eb72bcb6042f5a7c5 KVM: PPC: Book3S HV: Save/restore XER in checkpointed register state
- a56ee9f8f01c5a11ced541f00c67646336f402b6 KVM: PPC: Book3S HV: Add a per vcpu cache for recently page faulted MMIO entries
- f05859827d28bde311a92e0bb5c1b6a92c305442 KVM: PPC: Book3S HV: Clear the key field of HPTE when the page is paged out
- 28d057c8970d394fe048f0b2b9f203889110f165 KVM: PPC: Book3S HV: Use list_move_tail instead of list_del/list_add_tail
- ebe4535fbe7a190e13c0e175e7e7a02898dbac33 KVM: PPC: Book3S HV: sparse: prototypes for functions called from assembler
- 025c95113866415c17b47b2a80ad6341214b1fe9 KVM: PPC: Book3S HV: Fix sparse static warning
- 9c763584b7c8911106bb77af7e648bef09af9d80 Linux 4.9-rc6
- 697ed8d03909140d95484d46d277a4e46d89b0e5 Merge branch fixes of git://git.armlinux.org.uk/~rmk/linux-arm
- 51b9a31c42edcd089f5b229633477ab5128faf03 tipc: eliminate obsolete socket locking policy description
- 3f0ae05d6fea0ed5b19efdbc9c9f8e02685a3af3 rtnl: fix the loop index update error in rtnl_dump_ifinfo()
- 32c231164b762dddefa13af5a0101032c70b50ef l2tp: fix racy SOCK_ZAPPED flag check in l2tp_ip{,6}_bind()
- 77079b133f242d3e3710c9b89ed54458307e54ff Merge tag armsoc-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/arm/arm-soc
- d117b9acaeada0b243f31e0fe83e111fcc9a6644 Merge tag ext4_for_stable of git://git.kernel.org/pub/scm/linux/kernel/git/tytso/ext4
- 8cdf3372fe8368f56315e66bea9f35053c418093 ext4: sanity check the block and cluster size at mount time
- 0f0909e242f73c1154272cf04f07fc9afe13e5b8 fscrypto: dont use on-stack buffer for key derivation
- 3c7018ebf8dbf14e7cd4f5dc648c51fc979f45bb fscrypto: dont use on-stack buffer for filename encryption
- 50d438fb9e4229cb37ec89a22c066b626e30885c Merge branch i2c/for-current of git://git.kernel.org/pub/scm/linux/kernel/git/wsa/linux
- dce9ce3615ca03bd7adb09a182b5ee192684f17f Merge tag for-linus of git://git.kernel.org/pub/scm/virt/kvm/kvm
- ad092de60f865c1ad94221bd06d381ecea446cc8 i2c: i2c-mux-pca954x: fix deselect enabling for device-tree
- f6918382c7d8a13eb1c71d375bdd88f3ae6a5833 Merge tag powerpc-4.9-5 of git://git.kernel.org/pub/scm/linux/kernel/git/powerpc/linux
- 384b0dc4c84eb0ffe04589694a31a06226d61f7a Merge branch linus of git://git.kernel.org/pub/scm/linux/kernel/git/herbert/crypto-2.6
- 6741897602aabae6542631cafbd2616943acc735 Merge tag leds_4.9-rc6 of git://git.kernel.org/pub/scm/linux/kernel/git/j.anaszewski/linux-leds
- eab8d4bc0aa79d0d401bde62bf33b4adaab08db9 Merge tag dmaengine-fix-4.9-rc6 of git://git.infradead.org/users/vkoul/slave-dma
- a2b07739ff5ded8ca7e9c7ff0749ed6f0d36aee2 kvm: x86: merge kvm_arch_set_irq and kvm_arch_set_irq_inatomic
- 7301d6abaea926d685832f7e1f0c37dd206b01f4 KVM: x86: fix missed SRCU usage in kvm_lapic_set_vapic_addr
- 22583f0d9c85e60c9860bc8a0ebff59fe08be6d7 KVM: async_pf: avoid recursive flushing of work items
- e3fd9a93a12a1020067a676e826877623cee8e2b kvm: kvmclock: let KVM_GET_CLOCK return whether the master clock is in use
- 1650b4ebc99da4c137bfbfc531be4a2405f951dd KVM: Disable irq while unregistering user notifier
- 910170442944e1f8674fd5ddbeeb8ccd1877ea98 iommu/vt-d: Fix PASID table allocation
- 8b9534406456313beb7bf9051150b50c63049ab7 KVM: x86: do not go through vcpu in __get_kvmclock_ns
- e5dbc4bf0b8c9ab50cc5699214240e84515be6eb Merge tag kvm-arm-for-4.9-rc6 of git://git.kernel.org/pub/scm/linux/kernel/git/kvmarm/kvmarm
- adda306744ec64c7bcd6c230a6bc060fb77bd7c3 Merge tag batadv-net-for-davem-20161119 of git://git.open-mesh.org/linux-merge
- 9dd35d6882a10629b95f2bc41a541740ef24c226 sparc: drop duplicate header scatterlist.h
- 178c7ae944444c198a1d9646477ab10d2d51f03e net: macb: add check for dma mapping error in start_xmit()
- 20afa6e2f9c129e13031cc4a21834a03641cb8a4 Merge tag acpi-4.9-rc6 of git://git.kernel.org/pub/scm/linux/kernel/git/rafael/linux-pm
- 04e36857d6747e4525e68c4292c081b795b48366 Merge branch rc-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/mmarek/kbuild
- aad931a30fd88c5319868c6891396d04ad6bfb3e Merge tag nfsd-4.9-2 of git://linux-nfs.org/~bfields/linux
- dbfa048db97c15ee3fff2ee17b19e61f3ab12d53 MAINTAINERS: Add LED subsystem co-maintainer
- aab0b243b9a2fab7dcee0ce6e13789d3ab0394bf Merge branches acpica-fixes, acpi-cppc-fixes and acpi-tools-fixes
- 79c3dcbabb8fc9df45e283e288938a45ef1a7a16 Merge branch sparc-lockdep-small
- e245d99e6cc4a0b904b87b46b4f60d46fb405987 lockdep: Limit static allocations if PROVE_LOCKING_SMALL is defined
- e6b5f1be7afe1657c40c08082c562b1a036a54c1 config: Adding the new config parameter CONFIG_PROVE_LOCKING_SMALL for sparc
- d41cbfc9a64d11835a5b5b90caa7d6f3a88eb1df NFSv4.1: Handle NFS4ERR_OLD_STATEID in nfs4_reclaim_open_state
- 1a9bbccaf8182da368dae454b57dc1c55074d266 sunbmac: Fix compiler warning
- 266439c94df9e6aee3390c6e1cfdb645e566f704 sunqe: Fix compiler warnings
- 5cc7861eb5b425c7a30ff7676a4b9d0ca62d5c76 NFSv4: Dont call close if the open stateid has already been cleared
- 49cc0c43d0d60ba8ca1cd754921bb50119d42940 Merge branch sun4v-64bit-DMA
- d30a6b84df00128e03588564925dc828a53e6865 sparc64: Enable 64-bit DMA
- f08978b0fdbf37d3c91efb60a20bdee3ba8f59c6 sparc64: Enable sun4v dma ops to use IOMMU v2 APIs
- 5116ab4eabed575b7cca61a6e89b7d6fb7440970 sparc64: Bind PCIe devices to use IOMMU v2 service
- 31f077dc7dffd4a444932a9fe7fe84d9c7b90b73 sparc64: Initialize iommu_map_table and iommu_pool
- f0248c1524fae654e9746e6843b9657fb3917387 sparc64: Add ATU (new IOMMU) support
- c88c545bf3202ca2cdb45df93eb40e3bcdbb3742 sparc64: Add FORCE_MAX_ZONEORDER and default to 13
- f82ef3e10a870acc19fa04f80ef5877eaa26f41e rtnetlink: fix FDB size computation
- 0f5258cd91e9d78a1ee30696314bec3c33321a93 netns: fix get_net_ns_by_fd(int pid) typo
- 87305c4cd261664a12cff16740d0c40065bbd07f Merge tag mac80211-for-davem-2016-11-18 of git://git.kernel.org/pub/scm/linux/kernel/git/jberg/mac80211
- 06a77b07e3b44aea2b3c0e64de420ea2cfdcbaa9 af_unix: conditionally use freezable blocking calls in read
- 0e2d1af399a3674351a5d0b8da5ba5764e0973a4 Merge branch cpsw-fixes
- 23a09873221c02106cf767a86743a55873f0d05b net: ethernet: ti: cpsw: fix fixed-link phy probe deferral
- 3420ea88509f9d585b39f36e737022faf0286d9a net: ethernet: ti: cpsw: add missing sanity check
- a7fe9d466f6a33558a38c7ca9d58bcc83512d577 net: ethernet: ti: cpsw: fix secondary-emac probe error path
- 8cbcc466fd4abd38a14b9d9b76c63a2cb7006554 net: ethernet: ti: cpsw: fix of_node and phydev leaks
- a4e32b0d0a26ba2f2ba1c65bd403d06ccc1df29c net: ethernet: ti: cpsw: fix deferred probe
- 86e1d5adcef961eb383ce4eacbe0ef22f06e2045 net: ethernet: ti: cpsw: fix mdio device reference leak
- c46ab7e08c79be7400f6d59edbc6f26a91941c5a net: ethernet: ti: cpsw: fix bad register access in probe error path
- 06ba3b2133dc203e1e9bc36cee7f0839b79a9e8b net: sky2: Fix shutdown crash
- 3e7dfb1659c2888fc0152ec2b02a5e932397bb0a NFSv4: Fix CLOSE races with OPEN
- 23ea44c2150d14b97518435a65cc74111804fbeb NFSv4.1: Fix a regression in DELEGRETURN
- c1717701be2f0639e5f817385a524131dbd3ff38 Merge tag sound-4.9-rc6 of git://git.kernel.org/pub/scm/linux/kernel/git/tiwai/sound
- bd2bc2b8e63f872f8aa0f3536a40ffce6e1840bb Merge tag gpio-v4.9-4 of git://git.kernel.org/pub/scm/linux/kernel/git/linusw/linux-gpio
- 12b70ec0d3a6eb2696f3c091af6ecac31d2f8e66 Merge tag drm-fixes-for-v4.9-rc6-brown-paper-bag of git://people.freedesktop.org/~airlied/linux
- c0da038d7afed2892346fdb9601e4fefee13a800 Merge tag usb-serial-4.9-rc6 of git://git.kernel.org/pub/scm/linux/kernel/git/johan/usb-serial into usb-linus
- a8348bca2944d397a528772f5c0ccb47a8b58af4 crypto: algif_hash - Fix NULL hash crash with shash
- b0921d5c9ed6ffa8a4d6afc5ee5f136b87445f14 mmc: sdhci-of-esdhc: fixup PRESENT_STATE read
- 268200bcafe4741db27667a42e5165a02800fb02 Merge tag fixes-for-v4.9-rc6 of git://git.kernel.org/pub/scm/linux/kernel/git/balbi/usb into usb-linus
- cac4a185405d4415eca269cae976438b44a37ae0 powerpc/mm: Fix missing update of HID register on secondary CPUs
- 05e78c6933d613a7da0d0473f4c19c865af04c2c usb: gadget: f_fs: fix wrong parenthesis in ffs_func_req_match()
- b112c84a6ff035271d41d548c10215f18443d6a6 KVM: arm64: Fix the issues when guest PMCCFILTR is configured
- 9e3f7a29694049edd728e2400ab57ad7553e5aa9 arm64: KVM: pmu: Fix AArch32 cycle counter access
- e40ed1542dd779e5037a22c6b534e57127472365 perf/x86: Add perf support for AMD family-17h processors
- 91e08ab0c8515450258d7ad9033bfe69bebad25a x86/dumpstack: Prevent KASAN false positive warnings
- c2d75e03d6307bda0e14b616818a6f7b09fd623a x86/unwind: Prevent KASAN false positive warnings in guess unwinder
- 9853a55ef1bb66d7411136046060bbfb69c714fa cfg80211: limit scan results cache size
- 96ed1fe511a8b4948e53f3bad431d8737e8f231f powerpc/mm/radix: Invalidate ERAT on tlbiel for POWER9 DD1
- 68d85d0e03eab60c238ebe673c7cea1cf70275d4 i2c: digicolor: use clk_disable_unprepare instead of clk_unprepare
- 9883ed4433b358528e1a41e56ae01a4b02a1dde3 Merge tag sunxi-fixes-for-4.9 of https://git.kernel.org/pub/scm/linux/kernel/git/mripard/linux into fixes
- c28aedec503d42a2b9f86102e3ae9d03bb54079e Merge tag sti-dt-for-v4.9-rc of git://git.kernel.org/pub/scm/linux/kernel/git/pchotard/sti into fixes
- d2e3cb98402421d29c296c9ec4257804c9705fad Merge tag imx-fixes-4.9-2 of git://git.kernel.org/pub/scm/linux/kernel/git/shawnguo/linux into fixes
- 52cad4b54da3448c819d240c5a7ce08ec9398680 Merge tag omap-for-v4.9/fixes-for-rc-cycle of git://git.kernel.org/pub/scm/linux/kernel/git/tmlind/linux-omap into fixes
- fbcdf6877eacc0dc6b69b5aac5b43fb6b182aee4 Merge tag mvebu-fixes-4.9-1 of git://git.infradead.org/linux-mvebu into fixes
- c2ee69d83b2b14d68ad7ee1773fc1d40e97f201d Merge tag drm-intel-fixes-2016-11-17 of ssh://git.freedesktop.org/git/drm-intel into drm-fixes
- 1c8018f7a7a60a649260fdd7e8645a356299e920 ipmi/bt-bmc: change compatible node to aspeed, ast2400-ibt-bmc
- 7d40c2cf080950eab63a0747482027f5f1dae0d3 Revert drm/mediatek: set vblank_disable_allowed to true
- e9f01049d1ea4679a3258b8423fe54bae424ee0e Revert drm/mediatek: fix a typo of OD_CFG to OD_RELAYMODE
- 623898671c8eb05639e746e6d84cffa281616438 Merge branch for-linus of git://git.kernel.dk/linux-block
- 57400d305201e1025ea0c20c851173146271bd1b Merge tag for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/dledford/rdma
- bec1b089ab287d5df160205f5949114e5a3d3162 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/viro/vfs
- d46bc34da9bcdab815c4972ad0d433af8eb98c8a Merge tag for-linus-4.9-rc5-ofs-1 of git://git.kernel.org/pub/scm/linux/kernel/git/hubcap/linux
- 30a391a13ab9215d7569da4e1773c5bb4deed96d net sched filters: pass netlink message flags in event notification
- 5d1904204c99596b50a700f092fe49d78edba400 mremap: fix race between mremap() and page cleanning
- b5c2d49544e5930c96e2632a7eece3f4325a1888 ip6_tunnel: disable caching when the traffic class is inherited
- 30563f933a27eb9f9391a0e531dffde5182e422a Merge branch phy-dev-leaks
- 13c9d934a5a1d04f055c20c2253090e9afd9a5d1 net: phy: fixed_phy: fix of_node leak in fixed_phy_unregister
- 3ae30f4ce65e9d4de274b1472169ab3c27f5c666 of_mdio: fix device reference leak in of_phy_find_device
- 48c1699d5335bc045b50989a06b1c526b17a25ff of_mdio: fix node leak in of_phy_register_fixed_link error path
- cfc44a4d147ea605d66ccb917cc24467d15ff867 net: check dead netns for peernet2id_alloc()
- f7c4a46352b58c04e4d2111df7fe0358ce84546d phy: twl4030-usb: Fix for musb session bit based PM
- 247529170d72ee16bbdfc94c3a696c79ea645c3a usb: musb: Drop pointless PM runtime code for dsps glue
- 536d599d4a5104a8f1f771d3a8db97138b0c9ebb usb: musb: Add missing pm_runtime_disable and drop 2430 PM timeout
- 2bff3916fda9145587c0312b6f5c43d82504980c usb: musb: Fix PM for hub disconnect
- ea2f35c01d5ea72b43b9b4fb4c5b9417a9eb2fb8 usb: musb: Fix sleeping function called from invalid context for hdrc glue
- c723bd6ec2b50e7c8b3424d9cb8febd8ffa3da1f usb: musb: Fix broken use of static variable for multiple instances
- a5a40d4624cd2328c69768f6eb41716fc249d7be crypto: caam - fix type mismatch warning
- d5afc1b68a6ddc27746d31f775025afe75ec8122 dmaengine: cppi41: More PM runtime fixes
- 553bbc11aa6c1f9e0f529a06aeeca15fbe4a3985 x86/boot: Avoid warning for zero-filling .bss
- 680bb946a1ae04fe0ff369a4965f76b48c07dc54 fix iov_iter_advance() for ITER_PIPE
- 4a59015372840a6fc35d7fd40638a9d5dc3ec958 xattr: Fix setting security xattrs on sockfs
- e5f6f564fd191d365fcd775c06a732a488205588 bnxt: add a missing rcu synchronization
- e47112d9d6009bf6b7438cedc0270316d6b0370d net: dsa: b53: Fix VLAN usage and how we treat CPU port
- 961b708e95181041f403251f660bc70be3ff6ba3 Merge tag drm-fixes-for-v4.9-rc6 of git://people.freedesktop.org/~airlied/linux
- 5c6b2aaf9316fd0983c0c999d920306ddc65bd2d iw_cxgb4: invalidate the mr when posting a read_w_inv wr
- 4ff522ea47944ffd3d4d27023ace8bc6a722c834 iw_cxgb4: set *bad_wr for post_send/post_recv errors
- 6fa1f2f0aa6191193704b9ff10e5a2cafe540738 Merge branches hfi1 and mlx into k.o/for-4.9-rc
- 6d931308f55faaef3f30bd0346c47f99528b229d IB/rxe: Update qp state for user query
- aa75b07b478a774b1432e2df1be5cd8ae834de0f IB/rxe: Clear queue buffer when modifying QP to reset
- 002e062e13db10973adb8302f231e48b477c7ccf IB/rxe: Fix handling of erroneous WR
- 1454ca3a97e147bb91e98b087446c39cf6692a48 IB/rxe: Fix kernel panic in UDP tunnel with GRO and RX checksum
- 593ff73bcfdc79f79a8a0df55504f75ad3e5d1a9 IB/mlx4: Fix create CQ error flow
- 37995116fecfce2b61ee3da6e73b3e394c6818f9 IB/mlx4: Check gid_index return value
- a1ab8402d15d2305d2315d96ec3294bfdf16587e IB/mlx5: Fix NULL pointer dereference on debug print
- dbaaff2a2caa03d472b5cc53a3fbfd415c97dc26 IB/mlx5: Fix fatal error dispatching
- 6bc1a656ab9f57f0112823b4a36930c9a29d1f89 IB/mlx5: Resolve soft lock on massive reg MRs
- 16b0e0695a73b68d8ca40288c8f9614ef208917b IB/mlx5: Use cache line size to select CQE stride
- efd7f40082a0dfd112eb87ff2124467a5739216f IB/mlx5: Validate requested RQT size
- 90be7c8ab72853ff9fc407f01518a898df1f3045 IB/mlx5: Fix memory leak in query device
- 3c7ba5760ab8eedec01159b267bb9bfcffe522ac IB/core: Avoid unsigned int overflow in sg_alloc_table
- 61c3702863be9e9f1ef12ed5a5b17bae6cdfac0b IB/core: Add missing check for addr_resolve callback return value
- aeb76df46d1158d5f7f3d30f993a1bb6ee9c67a0 IB/core: Set routable RoCE gid type for ipv4/ipv6 networks
- 9db0ff53cb9b43ed75bacd42a89c1a0ab048b2b0 IB/cm: Mark stale CM ids whenever the mad agent was unregistered
- 5b810a242c28e1d8d64d718cebe75b79d86a0b2d IB/uverbs: Fix leak of XRC target QPs
- 5fd0f1cae3cced7d3518d22afb4fc7192a0b8fa1 Merge tag xtensa-20161116 of git://github.com/jcmvbkbc/linux-xtensa
- 2a3811068fbc6bf09bb09d166b65394b091c1085 ARM: Fix XIP kernels
- 29ed197333bdb1ccda1790bd2418f3a835de86fd Merge branch drm-fixes-4.9 of git://people.freedesktop.org/~agd5f/linux into drm-fixes
- 51a4c38a5511c0027c54d330f7dd2239f6c95b82 Merge branch mediatek-drm-fixes-2016-11-11 of https://github.com/ckhu-mediatek/linux.git-tags into drm-fixes
- 955e16026d08a601d02b961d13b6db9d6c13c8c9 net/phy/vitesse: Configure RGMII skew on VSC8601, if needed
- 5f00a8d8a2c2fd99528ab1a3632f0e77f4d25202 cxgb4: do not call napi_hash_del()
- ea339343d64a14594d882ccb52e8619d42defe5e be2net: do not call napi_hash_del()
- d5a4b1a540b8a9a44888b383472a80b84765aaa0 tools/power/acpi: Remove direct kernel source include reference
- 813ae37e6aed72cc457094b6066aa38efd66c9e9 Merge branch x86/cpufeature of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip into kvm/next
- 963abe5c8a0273a1cf5913556da1b1189de0e57a virtio-net: add a missing synchronize_net()
- f9c22ec6c1c511285dc539b83aabdabdb6baf245 gpio: Remove GPIO_DEVRES option
- d48756228ee9161ac8836b346589a43fabdc9f3c nvme/pci: Dont free queues on error
- da7800a88c5a3b798f763d6f9f343e9a49860c4f drm/amd/powerplay: avoid out of bounds access on array ps.
- c8616671af913ed2c5fb5b45f09c28599458ba1a Merge tag sunxi-clk-fixes-for-4.9 of https://git.kernel.org/pub/scm/linux/kernel/git/mripard/linux into clk-fixes
- bdfdabfedc30c9574dde6198a1739d2be03bf934 clk: efm32gg: Pass correct type to hw provider registration
- 3ca0b51decf780ce6277b088a9f28cd6fb71e372 clk: berlin: Pass correct type to hw provider registration
- a7741713dd361f081e5b48c04f59d0bbb1f32ed3 Merge branch thunderx-fixes
- c94acf805d93e7beb5898ac97ff327ae0b6f04dd net: thunderx: Fix memory leak and other issues upon interface toggle
- 964cb69bdc9db255f7c3a80f6e1bed8a25e4c60e net: thunderx: Fix VF drivers interface statistics
- cadcf95a4f70362c96a8fe39ff5d5df830d4db7f net: thunderx: Fix configuration of L3/L4 length checking
- 712c3185344050c591d78584542bd945e4f6f778 net: thunderx: Program LMAC credits based on MTU
- 612e94bd99912f3b2ac616c00c3dc7f166a98005 net: thunderx: Introduce BGX_ID_MASK macro to extract bgx_id
- b71de936c38e80d1f059fd54d8704e9d86d6bd10 Merge branch fib-tables-fixes
- 3114cdfe66c156345b0ae34e2990472f277e0c1b ipv4: Fix memory leak in exception case for splitting tries
- 3b7093346b326e5d3590c7d49f6aefe6fa5b2c9a ipv4: Restore fib_trie_flush_external function and fix call ordering
- f23cc643f9baec7f71f2b74692da3cf03abbbfda bpf: fix range arithmetic for bpf map access
- 984573abf8d09bace3cf8cda224bacb75b4c61d2 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/mszeredi/fuse
- 116fc01f2ed7578e70ea85c67f6507ae50a5932e Merge tag mfd-fixes-4.9 of git://git.kernel.org/pub/scm/linux/kernel/git/lee/mfd
- 4cb19355ea19995941ccaad115dbfac6b75215ca device-dax: fail all private mapping attempts
- 19ff7fcc76e6911a955742b40f85ba1030ccba5e orangefs: add .owner to debugfs file_operations
- 2ab13292d7a314fa45de0acc808e41aaad31989c USB: serial: cp210x: add ID for the Zone DPMX
- 47bdf3378d62a627cfb8a54e1180c08d67078b61 x86/cpuid: Provide get_scattered_cpuid_leaf()
- 47f10a36003eaf493125a5e6687dd1ff775bfd8c x86/cpuid: Cleanup cpuid_regs definitions
- 722f191080de641f023feaa7d5648caf377844f5 mfd: core: Fix device reference leak in mfd_clone_cell
- f40584200bc4af7aa4399635b9ac213c62a13ae7 mfd: stmpe: Fix RESET regression on STMPE2401
- 9600702082b29fd3f8a6d744df74ad4c48d4a432 mfd: intel_soc_pmic_bxtwc: Fix usbc interrupt
- 274e43edcda6f709aa67e436b3123e45a6270923 mfd: intel-lpss: Do not put device in reset state on suspend
- 2c8c34167c987e463d62a55384fcec7fa8d03a54 mfd: lpss: Fix Intel Kaby Lake PCH-H properties
- c499336cea8bbe15554c6fcea2138658c5395bfe perf/x86/uncore: Fix crash by removing bogus event_list[] handling for SNB client uncore IMC
- f96acec8c8020807429d21324547f4b904c37177 x86/sysfb: Fix lfb_size calculation
- 9164b4ceb7b492a77c7fe770a4b9d1375c9cd45a x86/sysfb: Add support for 64bit EFI lfb_base
- bc9db5ad3253c8e17969bd802c47b73e63f125ab drm/i915: Assume non-DP++ port if dvo_port is HDMI and theres no AUX ch specified in the VBT
- 59349a3822819d26dca4e1ebe16cbca458a56b0b KVM: PPC: Book3S HV: Dont lose hardware R/C bit updates in H_PROTECT

* Wed Nov 16 2016 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.9.0-2
- 59349a3822819d26dca4e1ebe16cbca458a56b0b KVM: PPC: Book3S HV: Dont lose hardware R/C bit updates in H_PROTECT
- aa9fc673d5e9b38e56cdae367ab33e8a66c3ac69 KVM: PPC: Book3S HV: Add a per vcpu cache for recently page faulted MMIO entries
- 115cc85ef3afa564092632d4ecb6b005983ead26 KVM: PPC: Book3S HV: Clear the key field of HPTE when the page is paged out
- d7b3e48fb768126732b3eb5fa3a170ab3a3d401c KVM: PPC: XICS: Dont lock twice when doing check resend
- 8643b30f7291fa314628834a99859933e0bc6605 KVM: PPC: XICS: Implement ICS P/Q states
- ac4893d9904755c24ef49047bededbbcadcb9922 KVM: PPC: XICS: Fix potential resend twice issue
- 636faefeff2ba7c7bbe5082bdae3a14409db4cff KVM: PPC: XICS: correct the real mode ICP rejecting counter
- 781556f4ad17e147aff41bcfc00a5c33f99e880a KVM: PPC: XICS cleanup: remove XICS_RM_REJECT
- ce1fd2ce4490b17d8d34db47ca8e125e139b93d3 Merge branch hostos-base into hostos-devel

* Wed Nov 09 2016 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 4.9.0-1
- ce1fd2c Merge branch hostos-base into hostos-devel
- 88afbd1 Merge tag v4.9-rc4 into hostos-base
- 652917a Merge branch hostos-stable into hostos-devel
- 528e382 KVM: PPC: Book3S HV: Save/restore XER in checkpointed register state
- bc33b0c Linux 4.9-rc4
- bd060ac Merge branch i2c/for-current of git://git.kernel.org/pub/scm/linux/kernel/git/wsa/linux
- ffbcbfc Merge branches sched-urgent-for-linus and core-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 6c286e8 Merge tag md/4.9-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/shli/md
- e12d8d5 Merge tag scsi-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/jejb/scsi
- f29b909 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/dtor/input
- 03daa36 Merge tag firewire-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/ieee1394/linux1394
- d8d1721 Merge tag media/v4.9-3 of git://git.kernel.org/pub/scm/linux/kernel/git/mchehab/linux-media
- 41e6410 Merge tag pci-v4.9-fixes-2 of git://git.kernel.org/pub/scm/linux/kernel/git/helgaas/pci
- 785bcb4 Merge tag for-linus-20161104 of git://git.infradead.org/linux-mtd
- d299704 Merge tag mmc-v4.9-rc2 of git://git.kernel.org/pub/scm/linux/kernel/git/ulfh/mmc
- 594aef6 Merge tag gpio-v4.9-3 of git://git.kernel.org/pub/scm/linux/kernel/git/linusw/linux-gpio
- fb415f2 Merge tag nfsd-4.9-1 of git://linux-nfs.org/~bfields/linux
- 46d7cbb Merge branch for-4.9-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/kdave/linux
- bd30fac Merge branch overlayfs-linus of git://git.kernel.org/pub/scm/linux/kernel/git/mszeredi/vfs
- d4c5f43 Merge tag drm-fixes-for-v4.9-rc4 of git://people.freedesktop.org/~airlied/linux
- 416379f PCI: designware: Check for iATU unroll support after initializing host
- 66cecb6 Merge tag for-linus of git://git.kernel.org/pub/scm/virt/kvm/kvm
- 34c510b Merge branch upstream of git://git.linux-mips.org/pub/scm/ralf/upstream-linus
- f7df76e Merge branch parisc-4.9-3 of git://git.kernel.org/pub/scm/linux/kernel/git/deller/parisc-linux
- 147b36d i2c: core: fix NULL pointer dereference under race condition
- 16a767e MIPS: Fix max_low_pfn with disabled highmem
- f92722d MIPS: Correct MIPS I FP sigcontext layout
- 758ef0a MIPS: Fix ISA I/II FP signal context offsets
- 6daaa32 MIPS: Remove FIR from ISA I FP signal context
- 35938a0 MIPS: Fix ISA I FP sigcontext access violation handling
- 5a1aca4 MIPS: Fix FCSR Cause bit handling for correct SIGFPE issue
- c9e5603 MIPS: ptrace: Also initialize the FP context on individual FCSR writes
- 8a98495 MIPS: dump_tlb: Fix printk continuations
- 752f549 MIPS: Fix __show_regs() output
- 41000c5 MIPS: traps: Fix output of show_code
- fe4e09e MIPS: traps: Fix output of show_stacktrace
- bcf084d MIPS: traps: Fix output of show_backtrace
- 818f38c MIPS: Fix build of compressed image
- 9a59061 MIPS: generic: Fix KASLR for generic kernel.
- 4736697 MIPS: KASLR: Fix handling of NULL FDT
- 93032e3 MIPS: Malta: Fixup reboot
- 682c1e5 MIPS: CPC: Provide default mips_cpc_default_phys_base to ignore CPC
- e9300a4 firewire: net: fix fragmented datagram_size off-by-one
- 667121a firewire: net: guard against rx buffer overflows
- 8243d55 sched/core: Remove pointless printout in sched_show_task()
- 3820050 sched/core: Fix oops in sched_show_task()
- 74b2d9f powerpc/64: Use optimized checksum routines on little-endian
- 59bf3bb powerpc/64: Fix checksum folding in csum_tcpudp_nofold and ip_fast_csum_nofold
- 7ec30fc Merge tag drm-intel-fixes-2016-11-01 of git://anongit.freedesktop.org/drm-intel into drm-fixes
- e676717 Merge tag imx-drm-fixes-20161021 of git://git.pengutronix.de/pza/linux into drm-fixes
- eed6f0e virtio-gpu: fix vblank events
- 18088db parisc: Ignore the pkey system calls for now
- 6a6e2a1 parisc: Use LINUX_GATEWAY_ADDR define instead of hardcoded value
- 6ed5183 parisc: Ensure consistent state when switching to kernel stack at syscall entry
- f4125cf parisc: Avoid trashing sr2 and sr3 in LWS code
- 6f63d0f parisc: use KERN_CONT when printing device inventory
- d9092f5 kvm: x86: Check memopp before dereference (CVE-2016-8630)
- 355f4fb kvm: nVMX: VMCLEAR an active shadow VMCS after last use
- ea26e4e KVM: x86: drop TSC offsetting kvm_x86_ops to fix KVM_GET/SET_CLOCK
- 577f12c Merge tag gcc-plugins-v4.9-rc4 of git://git.kernel.org/pub/scm/linux/kernel/git/kees/linux
- 04659fe Merge tag for_linus of git://git.kernel.org/pub/scm/linux/kernel/git/mst/vhost
- a75e003 Merge tag vfio-v4.9-rc4 of git://github.com/awilliam/linux-vfio
- f46c445 nfsd: Fix general protection fault in release_lock_stateid()
- 8d42629 svcrdma: backchannel cannot share a page for send and rcv buffers
- 812d478 gpio/mvebu: Use irq_domain_add_linear
- 405c075 fork: Add task stack refcounting sanity check and prevent premature task stack freeing
- b0a6af8 drm/nouveau/acpi: fix check for power resources support
- 5f7f8f6 Merge branch drm-fixes-staging of ssh://people.freedesktop.org/~/linux into drm-fixes
- c7e9d39 gpio: of: fix GPIO drivers with multiple gpio_chip for a single node
- 953b956 gpio: GPIO_GET_LINE{HANDLE,EVENT}_IOCTL: Fix file descriptor leak
- 0c183d9 Merge tag spi-fix-v4.9-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/broonie/spi
- 58bea41 latent_entropy: Fix wrong gcc code generation with 64 bit variables
- da7389a gcc-plugins: Export symbols needed by gcc
- 3f7b55b Merge tag regulator-fix-v4.9-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/broonie/regulator
- 80a306d Merge tag regmap-fix-v4.9-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/broonie/regmap
- 6eb3c60 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/jmorris/linux-security
- befd996 tpm: remove invalid min length check from tpm_do_selftest()
- 41ec793 Merge branch fixes of git://git.armlinux.org.uk/~rmk/linux-arm
- 04ed7d9 Merge git://git.kernel.org/pub/scm/linux/kernel/git/davem/sparc
- 641089c ovl: fsync after copy-up
- b93d4a0 ovl: fix get_acl() on tmpfs
- fd3220d ovl: update S_ISGID when setting posix ACLs
- 75bfa81 virtio_ring: mark vring_dma_dev inline
- 678ff27 virtio/vhost: add Jason to list of maintainers
- 2ff9844 virtio_blk: Delete an unnecessary initialisation in init_vq()
- 668866b virtio_blk: Use kmalloc_array() in init_vq()
- 3dae2c6 virtio: remove config.c
- 3456376 virtio: console: Unlock vqs while freeing buffers
- 948a8ac ringtest: poll for new buffers once before updating event index
- d3c3589 ringtest: commonize implementation of poll_avail/poll_used
- 44d65ea ringtest: use link-time optimization
- 8424af5 virtio: update balloon size in balloon probe
- 0ea1e4a virtio_ring: Make interrupt suppression spec compliant
- a0be1db virtio_pci: Limit DMA mask to 44 bits for legacy virtio devices
- 2a26d99 Merge git://git.kernel.org/pub/scm/linux/kernel/git/davem/net
- fceb9c3 geneve: avoid using stale geneve socket.
- c6fcc4f vxlan: avoid using stale vxlan socket.
- 087892d qede: Fix out-of-bound fastpath memory access
- 3034783 net: phy: dp83848: add dp83822 PHY support
- 9fe1c98 enic: fix rq disable
- 06bd2b1 tipc: fix broadcast link synchronization problem
- 8bf371e ibmvnic: Fix missing brackets in init_sub_crq_irqs
- 9888d7b ibmvnic: Fix releasing of sub-CRQ IRQs in interrupt context
- dbc34e7 Revert ibmvnic: Fix releasing of sub-CRQ IRQs in interrupt context
- 4c96f5b Merge branch 40GbE of git://git.kernel.org/pub/scm/linux/kernel/git/jkirsher/net-queue
- f9d4286 arch/powerpc: Update parameters for csum_tcpudp_magic & csum_tcpudp_nofold
- a909d3e Linux 4.9-rc3
- 42fd2b5 Merge branch x86-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- e59cc76 Merge branch mlx4-fixes
- eb4b678 net/mlx4_en: Save slave ethtool stats command
- d2582a0 net/mlx4_en: Fix potential deadlock in port statistics flow
- 6f2e0d2 net/mlx4: Fix firmware command timeout during interrupt test
- 81d1841 net/mlx4_core: Do not access comm channel if it has not yet been initialized
- 9d2afba net/mlx4_en: Fix panic during reboot
- 8d59de8 net/mlx4_en: Process all completions in RX rings after port goes up
- 4850cf4 net/mlx4_en: Resolve dividing by zero in 32-bit system
- 72da2e9 net/mlx4_core: Change the default value of enable_qos
- 33a1f8b net/mlx4_core: Avoid setting ports to auto when only one port type is supported
- aa0c08f net/mlx4_core: Fix the resource-type enum in res tracker to conform to FW spec
- efa5637 Merge tag upstream-4.9-rc3 of git://git.infradead.org/linux-ubifs
- ff57087 rds: debug messages are enabled by default
- 880b583 Merge tag mac80211-for-davem-2016-10-27 of git://git.kernel.org/pub/scm/linux/kernel/git/jberg/mac80211
- 8d7533e ibmvnic: Fix releasing of sub-CRQ IRQs in interrupt context
- fd33b24 net: mv643xx_eth: Fetch the phy connection type from DT
- 2674235 Merge tag armsoc-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/arm/arm-soc
- ad60133 Merge tag batadv-net-for-davem-20161026 of git://git.open-mesh.org/linux-merge
- e934f68 Revert hv_netvsc: report vmbus name in ethtool
- 104ba78 packet: on direct_xmit, limit tso and csum to supported devices
- 4700e9c net_sched actions: use nla_parse_nested()
- 166e604 cxgb4: Fix error handling in alloc_uld_rxqs().
- a4256bc IB/mlx4: avoid a -Wmaybe-uninitialize warning
- 2fbef66 Merge remote-tracking branches spi/fix/dt, spi/fix/fsl-dspi and spi/fix/fsl-espi into spi-linus
- 5ee67b5 spi: dspi: clear SPI_SR before enable interrupt
- ae148b0 ip6_tunnel: Update skb->protocol to ETH_P_IPV6 in ip6_tnl_xmit()
- 96a8eb1 bpf: fix samples to add fake KBUILD_MODNAME
- 2a29003 Merge tag char-misc-4.9-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/char-misc
- 74e3368 Merge remote-tracking branches regmap/fix/header and regmap/fix/macro into regmap-linus
- b70e8be Merge tag v4.9-rockchip-dts64-fixes1 of git://git.kernel.org/pub/scm/linux/kernel/git/mmind/linux-rockchip into fixes
- bb70e53 Merge tag arm-soc/for-4.9/devicetree-arm64-fixes of http://github.com/Broadcom/stblinux into fixes
- fbaff05 Merge tag imx-fixes-4.9 of git://git.kernel.org/pub/scm/linux/kernel/git/shawnguo/linux into fixes
- 10e15a6 Merge tag uniphier-fixes-v4.9 of git://git.kernel.org/pub/scm/linux/kernel/git/masahiroy/linux-uniphier into fixes
- c636e17 Merge tag driver-core-4.9-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/driver-core
- db4a57e Merge tag staging-4.9-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/staging
- 37cc6bb Merge tag tty-4.9-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/tty
- 9af6f26 Merge tag usb-4.9-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/usb
- e4cabca inet: Fix missing return value in inet6_hash
- 58a86c4 Merge branch mlx5-fixes
- 6b27619 net/mlx5: Avoid passing dma address 0 to firmware
- 04c0c1a net/mlx5: PCI error recovery health care simulation
- 05ac2c0 net/mlx5: Fix race between PCI error handlers and health work
- 2241007 net/mlx5: Clear health sick bit when starting health poll
- 247f139 net/mlx5: Change the acl enable prototype to return status
- 5e1e93c net/mlx5e: Unregister netdev before detaching it
- 2b02955 net/mlx5e: Choose best nearest LRO timeout
- e83d695 net/mlx5: Correctly initialize last use of flow counters
- 32dba76 net/mlx5: Fix autogroups groups num not decreasing
- eccec8d net/mlx5: Keep autogroups list ordered
- bba1574 net/mlx5: Always Query HCA caps after setting them
- b47bd6e {net, ib}/mlx5: Make cache line size determination at runtime.
- bf911e9 sctp: validate chunk len before actually using it
- 1e90a13 x86/smpboot: Init apic mapping before usage
- 1217e1d md: be careful not lot leak internal curr_resync value into metadata. -- (all)
- 7449f69 raid1: handle read error also in readonly mode
- 9a8b27f raid5-cache: correct condition for empty metadata write
- 0e2ce9d Merge tag nand/fixes-for-4.9-rc3 of github.com:linux-nand/linux
- c067aff Merge tag acpi-4.9-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/rafael/linux-pm
- b546e0c Merge tag pm-4.9-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/rafael/linux-pm
- 1308fd7 Merge tag arc-4.9-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/vgupta/arc
- 21e2d9d Merge branches acpica-fixes, acpi-pci-fixes and acpi-apei-fixes
- 8633db6 ACPICA: Dispatcher: Fix interpreter locking around acpi_ev_initialize_region()
- 8121aa2 ACPICA: Dispatcher: Fix an unbalanced lock exit path in acpi_ds_auto_serialize_method()
- 25ccd24 ACPICA: Dispatcher: Fix order issue of method termination
- 6fcc8ce Merge tag powerpc-4.9-4 of git://git.kernel.org/pub/scm/linux/kernel/git/powerpc/linux
- 8b2ada2 Merge branches pm-cpufreq-fixes and pm-sleep-fixes
- b49c317 Merge branch perf-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- 18e601d sunrpc: fix some missing rq_rbuffer assignments
- ed99d36 Merge branch libnvdimm-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/nvdimm/nvdimm
- b92d964 Merge tag arm64-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/arm64/linux
- c38c04c Merge branch x86-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- a8006bd Merge branch timers-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- c2e169b Merge branch mlxsw-fixes
- 8b99bec mlxsw: spectrum_router: Compare only trees which are in use during tree get
- 2083d36 mlxsw: spectrum_router: Save requested prefix bitlist when creating tree
- ba14fa1 regulator: core: silence warning: VDD1: ramp_delay not set
- 72193a9 regmap: Rename ret variable in regmap_read_poll_timeout
- 965c4b7 Merge branches core-urgent-for-linus, irq-urgent-for-linus and sched-urgent-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/tip/tip
- b75dcd9 ARC: module: print pretty section names
- d65283f ARC: module: elide loop to save reference to .eh_frame
- f644e36 ARC: mm: retire ARC_DBG_TLB_MISS_COUNT...
- c300547 ARC: build: retire old toggles
- d975cbc ARC: boot log: refactor cpu name/release printing
- d7c4611 ARC: boot log: remove awkward space comma from MMU line
- a024fd9 ARC: boot log: dont assume SWAPE instruction support
- 73e284d ARC: boot log: refactor printing abt features not captured in BCRs
- f616751 Merge branch for-linus-4.9 of git://git.kernel.org/pub/scm/linux/kernel/git/mason/linux-btrfs
- 711c1f2 ARCv2: boot log: print IOC exists as well as enabled status
- 2cd0b50 Merge tag sound-4.9-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/tiwai/sound
- bdb5208 Merge tag drm-x86-pat-regression-fix of git://people.freedesktop.org/~airlied/linux
- e0f3e6a Merge tag dm-4.9-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/device-mapper/linux-dm
- 4393700 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/jmorris/linux-security
- a00052a ubifs: Fix regression in ubifs_readdir()
- 40b6e61 ubi: fastmap: Fix add_vol() return value test in ubi_attach_fastmap()
- a7d5afe MAINTAINERS: Add entry for genwqe driver
- eb94cd6 VMCI: Doorbell create and destroy fixes
- a7a7aee GenWQE: Fix bad page access during abort of resource allocation
- 6ad3756 vme: vme_get_size potentially returning incorrect value on failure
- c89d545 drm/i915: Fix SKL+ 90/270 degree rotated plane coordinate computation
- 7e9b3f9 drm/i915: Remove two invalid warns
- 6d9deb9 drm/i915: Rotated view does not need a fence
- e3b9e6e drm/i915/fbc: fix CFB size calculation for gen8+
- 1fb3672 drm: i915: Wait for fences on new fb, not old
- 0ce140d drm/i915: Clean up DDI DDC/AUX CH sanitation
- 198c5ee drm/i915: Respect alternate_aux_channel for all DDI ports
- 5e33791 drm/i915/gen9: fix watermarks when using the pipe scaler
- fd58753 drm/i915: Fix mismatched INIT power domain disabling during suspend
- be4dd65 drm/i915: fix a read size argument
- 47ed324 drm/i915: Use fence_write() from rpm resume
- 01c72d6 drm/i915/gen9: fix DDB partitioning for multi-screen cases
- 7a0e17b drm/i915: workaround sparse warning on variable length arrays
- 9cccc76 drm/i915: keep declarations in i915_drv.h
- d0f4bce tty: serial_core: fix NULL struct tty pointer access in uart_write_wakeup
- 4dda864 tty: serial_core: Fix serial console crash on port shutdown
- 9bcffe7 tty/serial: at91: fix hardware handshake on Atmel platforms
- bd768e1 KVM: x86: fix wbinvd_dirty_mask use-after-free
- f92b760 perf/x86/intel: Honour the CPUID for number of fixed counters in hypervisors
- 5aab90c perf/powerpc: Dont call perf_event_disable() from atomic context
- 0933840 perf/core: Protect PMU device removal with a pmu_bus_running check, to fix CONFIG_DEBUG_TEST_DRIVER_REMOVE=y kernel panic
- 1c27f64 x86/microcode/AMD: Fix more fallout from CONFIG_RANDOMIZE_MEMORY=y
- 8ff0513 mtd: mtk: avoid warning in mtk_ecc_encode
- 73f907f mtd: nand: Fix data interface configuration logic
- ce93bed mtd: nand: gpmi: disable the clocks on errors
- 14970f2 Merge branch akpm (patches from Andrew)
- 1cfa126 Merge branch drm-fixes-4.9 of git://people.freedesktop.org/~agd5f/linux into drm-fixes
- aa72c26 Merge tag drm-misc-fixes-2016-10-27 of git://anongit.freedesktop.org/git/drm-misc into drm-fixes
- 8e81910 drivers/misc/sgi-gru/grumain.c: remove bogus 0x prefix from printk
- 17a8893 cris/arch-v32: cryptocop: print a hex number after a 0x prefix
- 9105585 ipack: print a hex number after a 0x prefix
- ee52c44 block: DAC960: print a hex number after a 0x prefix
- 14f947c fs: exofs: print a hex number after a 0x prefix
- 62e931f lib/genalloc.c: start search from start of chunk
- 89a2848 mm: memcontrol: do not recurse in direct reclaim
- 8f72cb4 CREDITS: update credit information for Martin Kepplinger
- 06b2849 proc: fix NULL dereference when reading /proc/<pid>/auxv
- 37df49f mm: kmemleak: ensure that the task stack is not freed during scanning
- 02754e0 lib/stackdepot.c: bump stackdepot capacity from 16MB to 128MB
- 0e07f66 latent_entropy: raise CONFIG_FRAME_WARN by default
- c0a0aba kconfig.h: remove config_enabled() macro
- 8c8d4d4 ipc: account for kmem usage on mqueue and msg
- 07a63c4 mm/slab: improve performance of gathering slabinfo stats
- 1f84a18 mm: page_alloc: use KERN_CONT where appropriate
- 1bc11d7 mm/list_lru.c: avoid error-path NULL pointer deref
- 2175358 h8300: fix syscall restarting
- b274c0b kcov: properly check if we are in an interrupt
- 86d9f48 mm/slab: fix kmemcg cache creation delayed issue
- 52e73eb device-dax: fix percpu_ref_exit ordering
- 67463e5 Allow KASAN and HOTPLUG_MEMORY to co-exist when doing build testing
- 867dfe3 nvdimm: make CONFIG_NVDIMM_DAX bool
- 9db4f36 mm: remove unused variable in memory hotplug
- 4e68af0 Merge branch i2c/for-current of git://git.kernel.org/pub/scm/linux/kernel/git/wsa/linux
- 7f2145b Merge branch next of git://git.kernel.org/pub/scm/linux/kernel/git/rzhang/linux
- 55bea71 Merge branch for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/s390/linux
- 599b076 i40e: fix call of ndo_dflt_bridge_getlink()
- 9ee7837 net sched filters: fix notification of filter delete with proper handle
- 7618c6a Merge tag modules-next-for-linus of git://git.kernel.org/pub/scm/linux/kernel/git/rusty/linux
- 4c95aa5 i40e: disable MSI-X interrupts if we cannot reserve enough vectors
- ea6acb7 i40e: Fix configure TCs after initial DCB disable
- a3b8cb1 ixgbe: fix panic when using macvlan with l2-fwd-offload enabled
- c121f72 net: bgmac: fix spelling mistake: connecton -> connection
- bc72f3d flow_dissector: fix vlan tag handling
- d5d32e4 net: ipv6: Do not consider link state for nexthop validation
- 830218c net: ipv6: Fix processing of RAs in presence of VRF
- e30520c kalmia: avoid potential uninitialized variable use
- 3065616 MAINTAINERS: add more people to the MTD maintainer team
- e0f841f macsec: Fix header length if SCI is added if explicitly disabled
- e279654 MAINTAINERS: add a maintainer for the SPI NOR subsystem
- f62265b at803x: double check SGMII side autoneg
- 4fc6d23 Revert at803x: fix suspend/resume for SGMII link
- e3300ff Merge tag for-linus-4.9-rc2-ofs-1 of git://git.kernel.org/pub/scm/linux/kernel/git/hubcap/linux
- e890038 Merge tag xfs-fixes-for-linus-4.9-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/dgc/linux-xfs
- 796f468 kvm/x86: Show WRMSR data is in hex
- a2941d0 drm/amd/powerplay: fix bug get wrong evv voltage of Polaris.
- 71451bd drm/amdgpu/si_dpm: workaround for SI kickers
- 570dd45 btrfs: fix races on root_log_ctx lists
- 18c2152 Merge tag scsi-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/jejb/scsi
- 4a3c390 Merge branch for-4.9-fixes of git://git.kernel.org/pub/scm/linux/kernel/git/tj/libata
- 9c953d6 Merge branch for-linus of git://git.kernel.dk/linux-block
- 9dcb8b6 mm: remove per-zone hashtable of bitlock waitqueues
- a74ad5e sparc64: Handle extremely large kernel TLB range flushes more gracefully.
- 7fe3113 blk-mq: update hardware and software queues for sleeping alloc
- 248ff02 driver core: Make Kconfig text for DEBUG_TEST_DRIVER_REMOVE stronger
- 2a9becd kernfs: Add noop_fsync to supported kernfs_file_fops
- 49ce5b5 Merge remote-tracking branch mkp-scsi/4.9/scsi-fixes into fixes
- 009e39a vt: clear selection before resizing
- 03842c1 sc16is7xx: always write state when configuring GPIO as an output
- c03e1b8 sh-sci: document R8A7743/5 support
- ecb988a tty: serial: 8250: 8250_core: NXP SC16C2552 workaround
- 32b2921 tty: limit terminal size to 4M chars
- d704b2d tty: serial: fsl_lpuart: Fix Tx DMA edge case
- f00a7c5 serial: 8250_lpss: enable MSI for sure
- be2c92b serial: core: fix console problems on uart_close
- 09065c5 serial: 8250_uniphier: fix clearing divisor latch access bit
- 0ead21a serial: 8250_uniphier: fix more unterminated string
- beadba5 serial: pch_uart: add terminate entry for dmi_system_id tables
- 78c2244 devicetree: bindings: uart: Add new compatible string for ZynqMP
- 0267a4f serial: xuartps: Add new compatible string for ZynqMP
- bc2a024 serial: SERIAL_STM32 should depend on HAS_DMA
- b20fb13 serial: stm32: Fix comparisons with undefined register
- 42acfc6 tty: vt, fix bogus division in csi_J
- b5149a5 Merge tag kvm-s390-master-4.9-2 of git://git.kernel.org/pub/scm/linux/kernel/git/kvms390/linux into HEAD
- fb479e4 powerpc/64s: relocation, register save fixes for system reset interrupt
- bd77c44 powerpc/mm/radix: Use tlbiel only if we ever ran on the current cpu
- 39715bf powerpc/process: Fix CONFIG_ALIVEC typo in restore_tm_state()
- 85c856b kvm: nVMX: Fix kernel panics induced by illegal INVEPT/INVVPID types
- bdc3478 ALSA: usb-audio: Add quirk for Syntek STK1160
- 58e3948 KVM: document lock orders
- d1f63f0 mmc: sdhci-msm: Fix error return code in sdhci_msm_probe()
- f5d6d2d sched/fair: Remove unused but set variable rq
- 56fb2d6 objtool: Fix rare switch jump table pattern detection
- 31e6ec4 security/keys: make BIG_KEYS dependent on stdrng.
- 7df3e59 KEYS: Sort out big_key initialisation
- 03dab86 KEYS: Fix short sprintf buffer in /proc/keys show function
- 67f0160 MAINTAINERS: Update qlogic networking drivers
- e52fed7 netvsc: fix incorrect receive checksum offloading
- 2bf7dc8 scsi: arcmsr: Send SYNCHRONIZE_CACHE command to firmware
- 4d2b496 scsi: scsi_debug: Fix memory leak if LBP enabled and module is unloaded
- 10df8e6 udp: fix IP_CHECKSUM handling
- ecc515d sctp: fix the panic caused by route update
- 293de7d doc: update docbook annotations for socket and skb
- 92d230d rocker: fix error return code in rocker_world_check_init()
- 2876a34 sunrpc: dont pass on-stack memory to sg_set_buf
- 05692d7 vfio/pci: Fix integer overflows, bitmask check
- ad11044 PCI: qcom: Fix pp->dev usage before assignment
- 7dc86ef drm/radeon/si_dpm: workaround for SI kickers
- 49a5d73 drm/amdgpu: fix s3 resume back, uvd dpm randomly cant disable.
- 3fa72fe arm64: mm: fix __page_to_voff definition
- 3f7a09f arm64/numa: fix incorrect log for memory-less node
- 26984c3 arm64/numa: fix pcpu_cpu_distance() to get correct CPU proximity
- a236441 sparc64: Fix illegal relative branches in hypervisor patched TLB cross-call code.
- 830cda3 sparc64: Fix instruction count in comment for __hypervisor_flush_tlb_pending.
- 4da5caa drm/dp/mst: Check peer device type before attempting EDID read
- 36e3fa6 drm/dp/mst: Clear port->pdt when tearing down the i2c adapter
- a288960 drm/fb-helper: Keep references for the current set of used connectors
- 38d868e drm: Dont force all planes to be added to the state due to zpos
- 94d7dea block: flush: fix IO hang in case of flood fua req
- 7dfcb36 drm/fb-helper: Fix connector ref leak on error
- 36343f6 KVM: fix OOPS on flush_work
- 45c7ee4 KVM: s390: Fix STHYI buffer alignment for diag224
- e1e575f KVM: MIPS: Precalculate MMIO load resume PC
- ede5f3e KVM: MIPS: Make ERET handle ERL before EXL
- 9078210 KVM: MIPS: Fix lazy user ASID regenerate for SMP
- 5de0a8c x86: Fix export for mcount and __fentry__
- 5c0ba57 spi: fsl-espi: avoid processing uninitalized data on error
- 62c6151 doc: Add missing parameter for msi_setup
- cfcc145 Merge tag extcon-fixes-for-4.9-rc3 of git://git.kernel.org/pub/scm/linux/kernel/git/chanwoo/extcon into char-misc-linus
- 87d3b65 drm/fb-helper: Dont call dirty callback for untouched clips
- cac5fce drm: Release reference from blob lookup after replacing property
- 2925d36 extcon: qcom-spmi-misc: Sync the extcon state on interrupt
- c1aa677 Merge tag usb-ci-v4.9-rc2 of git://git.kernel.org/pub/scm/linux/kernel/git/peter.chen/usb into usb-linus
- 7cf321d drm/drivers: add support for using the arch wc mapping API.
- b4f7f4a mac80211: fix some sphinx warnings
- e1957db cfg80211: process events caused by suspend before suspending
- 8ef4227 x86/io: add interface to reserve io memtype for a resource range. (v1.1)
- 849c498 sparc64: Handle extremely large kernel TSB range flushes sanely.
- 9d9fa23 sparc: Handle negative offsets in arch_jump_label_transform
- a467a67 MAINTAINERS: Begin module maintainer transition
- b429ae4 sparc64: Fix illegal relative branches in hypervisor patched TLB code.
- 537b4b4 drm/radeon: drop register readback in cayman_cp_int_cntl_setup
- ef6239e drm/amdgpu/vce3: only enable 3 rings on new enough firmware (v2)
- 0ce57f8 ahci: fix the single MSI-X case in ahci_init_one
- 6bad6bc timers: Prevent base clock corruption when forwarding
- 041ad7b timers: Prevent base clock rewind when forwarding clock
- 4da9152 timers: Lock base for same bucket optimization
- b831275 timers: Plug locking race vs. timer migration
- 9b50898 ALSA: seq: Fix time account regression
- 533169d i2c: imx: defer probe if bus recovery GPIOs are not ready
- 171e23e i2c: designware: Avoid aborted transfers with fast reacting I2C slaves
- ba9ad2a i2c: i801: Fix I2C Block Read on 8-Series/C220 and later
- 6036160 i2c: xgene: Avoid dma_buffer overrun
- 60a951a i2c: digicolor: Fix module autoload
- 2cb496d i2c: xlr: Fix module autoload for OF registration
- 06e7b10 i2c: xlp9xx: Fix module autoload
- 3855ada i2c: jz4780: Fix module autoload
- 1779165 i2c: allow configuration of imx driver for ColdFire architecture
- 6a676fb i2c: mark device nodes only in case of successful instantiation
- d320b9a x86/quirks: Hide maybe-uninitialized warning
- a2209b7 x86/build: Fix build with older GCC versions
- 7fbe6ac x86/unwind: Fix empty stack dereference in guess unwinder
- 399c168 i2c: rk3x: Give the tuning value 0 during rk3x_i2c_v0_calc_timings
- ae824f0 i2c: hix5hd2: allow build with ARCH_HISI
- 45c7a49 mmc: dw_mmc-pltfm: fix the potential NULL pointer dereference
- 991d5ad usb: chipidea: host: fix NULL ptr dereference during shutdown
- 1a3f099 ALSA: hda - Fix surround output pins for ASRock B150M mobo
- 407a3ae hv: do not lose pending heartbeat vmbus packets
- 888abf4 Merge branch hostos-base into hostos-devel

* Mon Oct 31 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 4.8.4-2
- Remove unused macros and simplify package numbering

* Wed Oct 26 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 4.8.4-1
- 888abf4 Merge branch hostos-base into hostos-devel
200b22d powerpc/mm/iommu, vfio/spapr: Put pages on VFIO container shutdown
f27109c vfio/spapr: Reference mm in tce_container
e96f99c powerpc/iommu: Stop using @current in mm_iommu_xxx
5fa3141 powerpc/iommu: Pass mm_struct to init/cleanup helpers
4948c53 Revert powerpc/iommu: Stop using @current in mm_iommu_xxx
d0850cd Revert powerpc/mm/iommu: Put pages on process exit
1e28a11 Merge tag v4.8.4 into hostos-devel
a2b4234 Linux 4.8.4
9362516 cfq: fix starvation of asynchronous writes
afac708 acpi, nfit: check for the correct event code in notifications
3245ff5 drm: virtio: reinstate drm_virtio_set_busid()
336f2e1 cachefiles: Fix attempt to read i_blocks after deleting file [ver #2]
7bf9989 vfs: move permission checking into notify_change() for utimes(NULL)
6b74694 dlm: free workqueues after the connections
3fae786 crypto: vmx - Fix memory corruption caused by p8_ghash
e15e0b8 crypto: ghash-generic - move common definitions to a new header file
fb13b62 ext4: unmap metadata when zeroing blocks
ff50a72 ext4: release bh in make_indexed_dir
99fa4c5 ext4: allow DAX writeback for hole punch
5373f6c ext4: fix memory leak when symlink decryption fails
7a68938 ext4: fix memory leak in ext4_insert_range()
30ac674 ext4: bugfix for mmaped pages in mpage_release_unused_pages()
eac6c9e ext4: reinforce check of i_dtime when clearing high fields of uid and gid
ddcd996 ext4: enforce online defrag restriction for encrypted files
4cd2546 jbd2: fix lockdep annotation in add_transaction_credits()
3d549dc vfs,mm: fix a dead loop in truncate_inode_pages_range()
d9cf9c3 mm/hugetlb: fix memory offline with hugepage size > memory block size
a9d465b ipc/sem.c: fix complex_count vs. simple op race
f653028 scsi: ibmvfc: Fix I/O hang when port is not mapped
0f24761 scsi: arcmsr: Simplify user_len checking
cf4dc8d scsi: arcmsr: Buffer overflow in arcmsr_iop_message_xfer()
2f9aa71 autofs: Fix automounts by using current_real_cred()->uid
dfca701 async_pq_val: fix DMA memory leak
5c55afa reiserfs: Unlock superblock before calling reiserfs_quota_on_mount()
dad1754 ASoC: Intel: Atom: add a missing star in a memcpy call
9b3aaaa ASoC: nau8825: fix bug in FLL parameter
9119232 brcmfmac: use correct skb freeing helper when deleting flowring
5de3cae brcmfmac: fix memory leak in brcmf_fill_bss_param
4a50f92 brcmfmac: fix pmksa->bssid usage
7d5d3b1 mm: filemap: dont plant shadow entries without radix tree node
bbf4e0b xfs: change mailing list address
c5b4bb7 i40e: avoid NULL pointer dereference and recursive errors on early PCI error
65fc3ba mm: filemap: fix mapping->nrpages double accounting in fuse
0e2993e fuse: fix killing s[ug]id in setattr
f72bae3 fuse: invalidate dir dentry after chmod
66b8e7f fuse: listxattr: verify xattr list
a4be745 clk: mvebu: dynamically allocate resources in Armada CP110 system controller
a6cf0bc clk: mvebu: fix setting unwanted flags in CP110 gate clock
51b2e35 IB/hfi1: Fix defered ack race with qp destroy
9ae3f9e drivers: base: dma-mapping: page align the size when unmap_kernel_range
3ec2e37 mei: amthif: fix deadlock in initialization during a reset
f22a8a5 btrfs: assign error values to the correct bio structs
1092e30 Btrfs: catch invalid free space trees
6691ebe Btrfs: fix mount -o clear_cache,space_cache=v2
1ff6341 Btrfs: fix free space tree bitmaps on big-endian systems
ba77f1d carl9170: fix debugfs crashes
c5054f7 b43legacy: fix debugfs crash
d7b4155 b43: fix debugfs crash
7c64663 debugfs: introduce a public file_operations accessor
ead1b01 ARCv2: fix local_save_flags
fa85ff8 ARCv2: intc: Use kflag if STATUS32.IE must be reset
ddd8060 serial: 8250_port: fix runtime PM use in __do_stop_tx_rs485()
80ece27 serial: 8250_dw: Check the data->pclk when get apb_pclk
307475d BUG: atmel_serial: Interrupts not disabled on close
40995fa serial: imx: Fix DCD reading
f516f49 Merge tag v4.8.3 into hostos-devel
1888926 Linux 4.8.3
89eeba1 mm: remove gup_flags FOLL_WRITE games from __get_user_pages()
0312017 Make __xfs_xattr_put_listen preperly report errors.
8523011 scsi: configure runtime pm before calling device_add in scsi_add_host_with_dma
ccb3dd2 v4l: rcar-fcp: Dont force users to check for disabled FCP support
cb5d016 Linux 4.8.2
87d6616 tpm_crb: fix crb_req_canceled behavior
17b6c49 tpm: fix a race condition in tpm2_unseal_trusted()
a8284cf ima: use file_dentry()
8af6ecc Bluetooth: Add a new 04ca:3011 QCA_ROME device
ec07719 ARM: cpuidle: Fix error return code
88277ac ARM: dts: MSM8660 remove flags from SPMI/MPP IRQs
150b065 ARM: dts: MSM8064 remove flags from SPMI/MPP IRQs
c018058 ARM: dts: mvebu: armada-390: add missing compatibility string and bracket
47d2e11 ARM: fix delays
7393344 x86/dumpstack: Fix x86_32 kernel_stack_pointer() previous stack access
36fc875 x86/mm/pkeys: Do not skip PKRU register if debug registers are not used
0480b22 arch/x86: Handle non enumerated CPU after physical hotplug
720aa4d x86/apic: Get rid of apic_version[] array
4c31498 x86/platform/intel-mid: Keep SRAM powered on at boot
768235b x86/platform/intel-mid: Add Intel Penwell to ID table
70c6cb0 x86/cpu: Rename Merrifield2 to Moorefield
6a667db x86/pkeys: Make protection keys an eager feature
b36aa57 x86/irq: Prevent force migration of irqs which are not in the vector domain
ebf5f66 x86/boot: Fix kdump, cleanup aborted E820_PRAM max_pfn manipulation
0efaa26 arm64: fix dump_backtrace/unwind_frame with NULL tsk
c9eb7cf KVM: PPC: BookE: Fix a sanity check
ebc12d6 KVM: arm/arm64: vgic: Dont flush/sync without a working vgic
4684879 KVM: arm64: Require in-kernel irqchip for PMU support
92b2384 KVM: MIPS: Drop other CPU ASIDs on guest MMU changes
759896f KVM: PPC: Book3s PR: Allow access to unprivileged MMCR2 register
88540ad xen/x86: Update topology map for PV VCPUs
c64c760 mfd: wm8350-i2c: Make sure the i2c regmap functions are compiled
ceeddee mfd: 88pm80x: Double shifting bug in suspend/resume
0187dcd mfd: atmel-hlcdc: Do not sleep in atomic context
6c4c6ae mfd: rtsx_usb: Avoid setting ucr->current_sg.status
14ca6ce ALSA: usb-line6: use the same declaration as definition in header for MIDI manufacturer ID
e09db64 ALSA: usb-audio: Extend DragonFly dB scale quirk to cover other variants
80e84e0 ALSA: ali5451: Fix out-of-bound position reporting
72c6187 phy: sun4i-usb: Use spinlock to guard phyctl register access
ac8aa11 usb: dwc3: fix Clear Stall EP command failure
4e584cf timekeeping: Fix __ktime_get_fast_ns() regression
c8661aa usb: storage: fix runtime pm issue in usb_stor_probe2
945f419 powerpc/64: Fix race condition in setting lock bit in idle/wakeup code
490b36e powerpc/64: Re-fix race condition between going idle and entering guest
a3a03f3 Merge tag v4.8.1 into hostos-devel

* Fri Oct 14 2016 Murilo Opsfelder Araújo <muriloo@linux.vnet.ibm.com> - 4.8.1-3
- Remove unused macros and simplify package numbering
- Bump specrelease

* Thu Oct 13 2016 Murilo Opsfelder Araújo <muriloo@linux.vnet.ibm.com> - 4.8.1-2
- Fix kernel version to 4.8.1

* Wed Oct 05 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com>- 4.8.0-1.3200.0.3
- Rebase on top of Linux 4.8

* Tue Sep 20 2016 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 4.7.0-2.el7.centos.3200.0.2
- rebuilt with kernel live patching enabled

* Tue Aug 30 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 4.7.0-1.pkvm3_1_1.3100.0.1
- Build August, 24th, 2016

* Wed Jun 15 2016 <baseuser@ibm.com>
  Log from git:
- 3daef95fd14797b1d11dbdef73bc52f1d5be6fae PCI: Ignore enforced alignment when kernel uses existing firmware setup
- 8b9484f5791a1ce4c7d914e0d7d1f607863c7b0d KVM: PPC: Book3S HV: Fix build error in book3s_hv.c
- 9fa11225e9b46d4ff9fd2c15762309a4d35faa1d PCI: Ignore enforced bridge window alignment
- 6513022774c8fad0da695ac5785f21a5ffa5e731 PCI: Ignore enforced alignment to VF BARs
- 834bc4171ce5809c584864362edde3ee4a76b632 vfio-pci: Allow to mmap sub-page MMIO BARs if the mmio page is exclusive
- 2b9d202754c4013bcaec4e29b262475ba6060485 PCI: Add support for enforcing all MMIO BARs to be page aligned
- 03f31147ec1c74bcbc9502b142f8b9ec815dbe08 PCI: Add a new option for resource_alignment to reassign alignment
- 30a02ba20e1bc3c4911244f33169a4ad6fc1d465 PCI: Do not Use IORESOURCE_STARTALIGN to identify bridge resources
- 65d5496d77d4cddcdf059e07e2ecc12d2a084cb3 PCI: Ignore resource_alignment if PCI_PROBE_ONLY was set
- 2edb74537d44c377a3845d5ddb9935c6f5bdc7ef vfio-pci: Allow to mmap MSI-X table if interrupt remapping is supported
- 48d41314503f170a2cdd88255b448deecf27c9de pci-ioda: Set PCI_BUS_FLAGS_MSI_REMAP for IODA host bridge
- ababfd906cbf3b0699b0a6057f5001efdc2c1b0e PCI: Add a new PCI_BUS_FLAGS_MSI_REMAP flag
- 778481f2477f8cbd87e986fe7e5d0b95869fd724 vfio/pci: Include sparse mmap capability for MSI-X table regions
- b540dad8a4ea74f497d81838a580cf1e1d18b4f6 vfio: Define sparse mmap capability for regions
- 3df5ed1226cffae70a6a4206876d024f9a27e1cc vfio: Add capability chain helpers
- 2c107ada6725cf3fb2b4ab2d6ffc8aa4a7d9b6b2 vfio: Define capability chains
- 2be3dfce35e187cd026abdec1abb65ba197c20ac powerpc/livepatch: Add live patching support on ppc64le
- 84441d15214a6934cb3979bad7bf8bc25db99c3a powerpc/livepatch: Add livepatch stack to struct thread_info
- cf1fb11267f5d801a5dc911fc8924bb86507560d powerpc/livepatch: Add livepatch header
- e77a525f59fefd4dff5c9779db229564bb88950a livepatch: Allow architectures to specify an alternate ftrace location
- 783ec857c7ca6b7df8de09dab7f3bfd5fe4d75ea ftrace: Make ftrace_location_range() global
- eaaf29c8ec3d0fe45282caa202b0646c67a00868 powerpc/ftrace: Add Kconfig & Make glue for mprofile-kernel
- 49739b9859369cf88f435e963413e4c53f298edf powerpc/ftrace: Add support for -mprofile-kernel ftrace ABI
- bda3508fde2326678e19374c7ead69492d680a3e powerpc/ftrace: Use $(CC_FLAGS_FTRACE) when disabling ftrace
- 09c9d468e8f3285a6fd53d5ed255a93c097af597 powerpc/ftrace: Use generic ftrace_modify_all_code()
- de633469a533bc2dabadfa7402b6d9e184d2beee powerpc/module: Create a special stub for ftrace_caller()
- b880c1f65eb63405f6134b9ec09e2a151c67a3bd powerpc/module: Mark module stubs with a magic value
- 6e7a4c897ac011900798680f6196ecbcc5e6bc20 powerpc/module: Only try to generate the ftrace_caller() stub once
- c81624eb676acd1b2b3917199eb7ac0ba576c50c powerpc: Create a helper for getting the kernel toc value
- 405ff074906b7b5bdb5447c46bc3d6d0ee76dd99 Merge tag 'v4.4.11' into powerkvm-v3.1.1
- 63c5c743d44943ba15eb9fa08fd33dbec018d621 powerpc/eeh: Drop unnecessary label in eeh_pe_change_owner()
- e1c14771e52651c81c81dcb869000644aa32c233 powerpc/eeh: Ignore handlers in eeh_pe_reset_and_recover()
- eed63c2932b65c3a3d3ed9affce88788b8ffb68d powerpc/eeh: Restore initial state in eeh_pe_reset_and_recover()
- 9fb223f024b8109153dfe51b278e2231b7fb160a powerpc/eeh: Don't report error in eeh_pe_reset_and_recover()
- 6aa4dfeacaa4159a1f9162e736f0d3cadfd621a0 KVM: PPC: Book3S HV: Implement halt polling in the kvm_hv kernel module
- 1a60004feeeb49972df0e2ce1d562b5406eb27b0 KVM: PPC: Book3S HV: Change vcore element runnable_threads from linked-list to array
- 1c7ef2c779f59b44022b8384cc5b3fd469a56dae xfs: detect and trim torn writes during log recovery
- d0db03762836b5fe2d936b3be6f2feb244f08229 xfs: refactor log record start detection into a new helper
- 278e465ac94e36935b06f949936c8f3af94f8869 xfs: support a crc verification only log record pass
- 6d735e50e31c92b370620a06eab09808ea025664 xfs: return start block of first bad log record during recovery
- d62f388a5169f7583a80a802a6c1fbc0e2177615 xfs: refactor and open code log record crc check
- 45d6ec1c2623449244625757e746a2f4c3c047b4 xfs: refactor log record unpack and data processing
- 2042010057f6dcfe2ce63e350cc32904218a2f81 xfs: detect and handle invalid iclog size set by mkfs
- 544ec5b08d007f184ab97abdbed87e613c8c0b83 Linux 4.4.11
- 6ff8315a4df67bfad96cffc406f91ceb6df70cde nf_conntrack: avoid kernel pointer value leak in slab name
- 62b68367b74b2456ee68deafab047067a6acae67 drm/radeon: fix DP link training issue with second 4K monitor
- bafa4fbc2b4ac51045fe7fb3de94bcd5560a56c7 drm/i915/bdw: Add missing delay during L3 SQC credit programming
- bf12e894e6b4ae0181af83ce5f6bb5e05c744660 drm/i915: Bail out of pipe config compute loop on LPT
- 472f52f5639238f569696082e0effbfb2171ad1a drm/radeon: fix PLL sharing on DCE6.1 (v2)
- 9df2dc6cf4adb711545f48001b34f35fd3bb79ef Revert "[media] videobuf2-v4l2: Verify planes array in buffer dequeueing"
