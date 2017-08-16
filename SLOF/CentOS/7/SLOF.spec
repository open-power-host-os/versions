%global commit          %{?git_commit_id}
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitcommittag    .git%{shortcommit}

Name:           SLOF
Version:        20170724
Release:        1%{?extraver}%{gitcommittag}%{?dist}
Summary:        Slimline Open Firmware

License:        BSD
URL:            http://www.openfirmware.info/SLOF
BuildArch:      noarch

Source0:        %{name}.tar.gz

# LTC: building native; no need for xcompiler
BuildRequires:  perl(Data::Dumper)


%description
Slimline Open Firmware (SLOF) is initialization and boot source code
based on the IEEE-1275 (Open Firmware) standard, developed by
engineers of the IBM Corporation.

The SLOF source code provides illustrates what's needed to initialize
and boot Linux or a hypervisor on the industry Open Firmware boot
standard.

Note that you normally wouldn't need to install this package
separately.  It is a dependency of qemu-system-ppc64.


%prep
%setup -q -n %{name}

if test -r "gitlog" ; then
    echo "This is the first 50 lines of a gitlog taken at archive creation time:"
    head -50 gitlog
    echo "End of first 50 lines of gitlog."
fi

%build
export CROSS=""
make qemu %{?_smp_mflags} V=2


%install
mkdir -p $RPM_BUILD_ROOT%{_datadir}/qemu
cp -a boot_rom.bin $RPM_BUILD_ROOT%{_datadir}/qemu/slof.bin


%files
%doc FlashingSLOF.pdf
%doc LICENSE
%doc README
%dir %{_datadir}/qemu
%{_datadir}/qemu/slof.bin


%changelog
* Wed Aug 16 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 20170724-1.git
- Version update
- Updating to 685af54 virtio-net: rework the driver to support multiple open

* Mon Aug 14 2017 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 20170303-5.git
- Bump release

* Mon Aug 07 2017 Fabiano Rosas <farosas@linux.vnet.ibm.com> - 20170303-4.git
- Add extraver macro to Release field

* Tue Jul 18 2017 Murilo Opsfelder Araújo <muriloo@linux.vnet.ibm.com> - 20170303-3.gitc39657a
- c39657a5f7d502c132a4ae7f407f8281a2ce68e4 board_qemu: move code out of fdt-fix-node-phandle
- 4c345ef71ecab658a17020c7780dd5a7d01029bf board_qemu: drop unused values early in fdt-fix-node-phandle
- ed256fbdc56948f2e8c9fcfda734b0169cec7066 pci: Improve the pci-var-out debug function
- 089fc18a9b8c38ff83d678f4ea05b270a172848c libhvcall: drop unused KVMPPC_H_REPORT_MC_ERR and KVMPPC_H_NMI_MCE defines
- 834113a1c67d6fb53dea153c3313d182238f2d36 libnet: Move parse_tftp_args to tftp.c
- 64215f41aafd182e51947dc5d544e5ebaab744ca libnet: Make the code compilable with -Wformat-security
- 14df554937c80997c610c6aef9fb89f3449f5ff4 libnet: Move the external declaration of send_ip to ethernet.h
- bc0dc192899f4462986220172a78a8cf59d22fcc libc: Declare size_t as unsigned long
- 5d34a1b6c57d5f029e7df1b0d972e7801d315344 libnet/netload: Three more minor clean-ups
- c633b135c0dd0dc2c59f229c0d74974a5127c187 libnet/tftp: Allow loading to address 0
- d2d31be1b59ad65c72920428d4624d0fc18fae8e libnet: Refactor some code of netload() into a separate function
- 140c3f39db4ce4c0c5de352da80307fc72fc8430 libnet: Rework error message printing
- 2f5f2529958894bcdf2db13a69d3b00765cf0278 libnet: Remove remainders of netsave code
- db35f1b8a2d3e44f4a12ca926359cc2575e98064 lib/Makefile: Pass FLAG to make in SUBDIRS target
- 895dbdd0dbd74887c9734b0b1dcc7f2f33a5a669 virtio-net: Fix ugly error message
- 62674aabe20612a9786fa03e87cf6916ba97a99a pci-phb: Set correct pci-bus-number while walking PCI bridges
- d5997edcbc1f3a7a75a2c144affeb8cbe8549f02 libnet: Cosmetical clean-up
- e8f7543db0d83e06b227e12f33492109aea1403c paflof: Print stack warning to stderr, not stdout
- 8c41240bc4e9f4e3a0b331af18d7305caae024b7 libnet: Allocate ICMPv6 packet space on the heap, not on the stack
- fa94a3bb20734cb8e0280b232d16b6d466ec3d53 A new SLOF boot menu
- 1f0600f25d64ced53d69347871c209bde8bb2a3c libc: The arguments of puts() can be marked as "const"
- 9d5d3b8bd256ac701b0ac0c4059a2b77b6f15912 Increase MAX-ALIAS to 10
- d258260ee4fd48948bb0c61d22ee96b97c934c5e Use TYPE for the standard output instead of io_putchar()
- 11ff4ba277ca9a9dc51136bab64772c9ac1541f6 pci: Remove unused next-pci-[mem|mmio|io] functions
- fcd31d3e672a013d0a02005c053955100c426ff6 pci: Reserve free space at the end of bridge windows instead of at the beginning
- 38c7e29976d315b354a4d1eaf7e56d942e5422dd pci: Generate a 64-bit range property if necessary
- 75a42176b7bca4551664be3db47bd23de1425b74 pci: Fix assigned-addresses for 64bit nonprefetchable BAR
- d90e32c661608d3ba9cbf77d66c6b8efb6219bdc pci-phb: Set pci-max-mem64 to the correct value
- 06e1e07e5f329dcb2441bc778e13af7825603c62 Rework the printing of the banner during boot
- 15572e4d646758ad75d69526d096c380fe3aaf2b bootmsg: Fix message for detected kernel
- 2f1e6a73f2090bcd87eb4185763c744a290c13ad logo: Update the logo
- 975b31f80aff26addee5d70c34de9cd1b0a204ca pci: Put non-prefetchable 64bit BARs into 32bit MMIO window
- 0ba3b03ba3fee180bbd76e43434fae42b2759f6f Fix "Unsupported PQ" problems in the scsi-disk open function

* Wed Mar 15 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 20170303-2.git1903174
- 1903174472f8800caf50c959b304501b4c01153c pci: force minimum mem bar alignment
  of 64K for board-qemu

* Wed Mar 08 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 20170303-1.git66d250e
- Version update
- 66d250ef0fd06bb88b7399b9563b5008201f2d63 version: update to 20170303
- ef5286f020d850f47fe196297f673769f6d63198 qemu-bootlist: Take the -boot strict=off setting properly into account
- 007a175410f919a4368499bd8ef11c32bbf3e01e virtio-scsi: initialize vring avail queue buffers
- f8ad6d0ae9c2861e2106580d7a2b8f72e95fb29f virtio: Remove global variables in block and 9p driver

* Wed Feb 15 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 20161019-4.gitba46a3f
- ba46a3f133c8532a517779cc3763e8ac2409d626 Remove superfluous checkpoints in tree.fs
- a0b96fe66fcd991b407c1d67ca842921e477a6fd Provide write function in the disk-label package
- 264553932ba3cee4b7472838daaecfaaa61c91da virtio: Implement block write support
- eee0d12dc541dd345d7931976e352ea5a6494155 scsi: Add SCSI block write support
- abd21203aa27435e9e5248350dcaf14940de0947 deblocker: Add a write function
- 9290756ae1195b331373dbcfd3b37d978b3b71f4 virtio-scsi: Fix descriptor order for SCSI WRITE commands
- 9b8945ecbde65b06ea2ab9e28a6178024b0420fb board-qemu: Add a possibility to use hvterm input instead of USB keyboard
- 38bf852e73ce6f0ac801dfe8ef1545c4cd0b5ddb Do not try to use virtio-gpu in VGA mode
- b294381e48ed9c3300e7aea4c4ba7f17729ffd9f virtio: Fix stack comment of virtio-blk-read
- 7412f9e058132a9218827c23369b8cba33d756af envvar: Do not read default values for /options from the NVRAM anymore
- 32568e8e1119e3308b3c97d4a290fd5e8a273e11 envvar: Set properties in /options during (set-defaults)

* Wed Feb  8 2017 Nikunj A. Dadhania <nikunj@linux.vnet.ibm.com> - 20161019
- Pull upstream SLOF present in qemu 2.8

* Thu Nov 3 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 20160525-3
- Spec cleanup

* Tue Aug 30 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 20160525-2.1
- Build August, 24th, 2016

* Tue Sep 10 2013 baseuser@ibm.com
- Base-8.x spec file
