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

Name: kernel%{?variant}
Group: System Environment/Kernel
License: GPLv2
URL: http://www.kernel.org/
Version: 4.9.0
Release: 1%{?dist}
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

Source0: linux-source.tar.gz

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
mv linux-source kernel-%{KVRA}
#setup -q -n kernel-%{rheltarball} -c


#mv linux-%{rheltarball} linux-%{KVRA}
cd kernel-%{KVRA}

# Drop some necessary files from the source dir into the buildroot
#cp $RPM_SOURCE_DIR/kernel-%{version}-*.config .
%define make make %{?cross_opts}
cp %{SOURCE1001} .
cp %{SOURCE1001} .config

#/usr/bin/patch -p1 < $RPM_SOURCE_DIR/fix.script.location.patch

# Any further pre-build tree manipulations happen here.
make oldconfig

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
%defattr(-,root,root)
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
 mkdir -p $RPM_BUILD_ROOT/usr/src/kernels/%{KVRA}%{?2:.%{2}}/arch/powerpc/scripts
 install -m 0755  arch/powerpc/scripts/gcc-check-mprofile-kernel.sh $RPM_BUILD_ROOT/usr/src/kernels/%{KVRA}%{?2:.%{2}}/arch/powerpc/scripts/gcc-check-mprofile-kernel.sh
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
%defattr(-,root,root)
/usr/include/*
%endif

%if %{with_bootwrapper}
%files bootwrapper
%defattr(-,root,root)
/usr/sbin/*
%{_libdir}/kernel-wrapper
%endif

# only some architecture builds need kernel-doc
%if %{with_doc}
%files doc
%defattr(-,root,root)
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
%defattr(-,root,root,-)
/lib/modules/kabi-*
%endif
%endif

%if %{with_perf}
%files -n perf
%defattr(-,root,root)
%{_bindir}/perf
%dir %{_libexecdir}/perf-core
%{_libexecdir}/perf-core/*
/usr/share/perf-core/strace/groups/file
%{_libdir}/traceevent
%if %{with_doc}
%{_mandir}/man[1-8]/perf*
%endif
%{_sysconfdir}/bash_completion.d/perf

%if ! 0%{?cross_build}
%files -n python-perf
%defattr(-,root,root)
%{python_sitearch}
%endif

%if %{with_debuginfo}
%files -f perf-debuginfo.list -n perf-debuginfo
%defattr(-,root,root)

%if ! 0%{?cross_build}
%files -f python-perf-debuginfo.list -n python-perf-debuginfo
%defattr(-,root,root)
%endif # ! cross_build
%endif # with_debuginfo
%endif # with_perf

%if %{with_tools}
%files -n kernel-tools -f cpupower.lang
%defattr(-,root,root)

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
%defattr(-,root,root)
%endif

%ifarch %{cpupowerarchs}
%files -n kernel-tools-libs
%defattr(-,root,root)
%{_libdir}/libcpupower.so.0
%{_libdir}/libcpupower.so.0.0.1

%files -n kernel-tools-libs-devel
%defattr(-,root,root)
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
%defattr(-,root,root)\
/%{image_install_path}/%{?-k:%{-k*}}%{!?-k:vmlinuz}-%{KVRA}%{?2:.%{2}}\
%if %{with_uimage} \
/%{image_install_path}/%{?-k:%{-k*}}%{!?-k:*Image*}-%{KVRA}%{?2:.%{2}}\
%endif \
%if %{with_dtb} \
/%{image_install_path}/dtb-%{KVRA}%{?2:+%{2}} \
%endif\
/%{image_install_path}/.vmlinuz-%{KVRA}%{?2:.%{2}}.hmac \
%attr(600,root,root) /boot/System.map-%{KVRA}%{?2:.%{2}}\
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
%defattr(-,root,root)\
%if %{with_modules}\
/usr/src/kernels/%{KVRA}%{?2:.%{2}}\
%endif\
%if %{with_debuginfo}\
%ifnarch noarch\
%{expand:%%files -f debuginfo%{?2}.list %{?2:%{2}-}debuginfo}\
%defattr(-,root,root)\
%endif\
%endif\
%endif\
%{nil}

%kernel_variant_files %{with_default}
%kernel_variant_files %{with_debug} debug
%kernel_variant_files %{with_kdump} kdump


%changelog
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

* Wed Oct 31 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 4.8.4-2
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
