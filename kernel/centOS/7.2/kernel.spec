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
Release: 4%{?dist}
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
