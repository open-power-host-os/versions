%global commit          %{?git_commit_id}
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gitcommittag    .git%{shortcommit}

Name:       kimchi
Version:    2.3.0
Release:    18%{?extraver}%{gitcommittag}%{?dist}
Summary:    Kimchi server application
BuildRoot:  %{_topdir}/BUILD/%{name}-%{version}-%{release}
BuildArch:  noarch
Group:      System Environment/Base
License:    LGPL/ASL2
Source0:    %{name}.tar.gz
Requires:   wok >= 2.1.0
Requires:   ginger-base
Requires:   qemu-kvm
Requires:   gettext
Requires:   libvirt
Requires:   libvirt-python
Requires:   libvirt-daemon-config-network
Requires:   python-websockify
Requires:   python-configobj
Requires:   novnc
Requires:   python-pillow
Requires:   pyparted
Requires:   python-psutil >= 0.6.0
Requires:   python-jsonschema >= 1.3.0
Requires:   python-ethtool
Requires:   sos
Requires:   python-ipaddr
Requires:   python-lxml
Requires:   nfs-utils
Requires:   iscsi-initiator-utils
Requires:   python-libguestfs
Requires:   libguestfs-tools
Requires:   python-magic
Requires:   python-paramiko
BuildRequires:  gettext-devel
BuildRequires:  libxslt
BuildRequires:  python-lxml
BuildRequires:  autoconf
BuildRequires:  automake

%if 0%{?rhel} >= 6 || 0%{?fedora} >= 19
Requires:   spice-html5
%endif

%if 0%{?fedora} >= 15 || 0%{?rhel} >= 7
%global with_systemd 1
%endif

%if 0%{?rhel} == 6
Requires:   python-ordereddict
Requires:   python-imaging
BuildRequires:    python-unittest2
%endif

%description
Web application to manage KVM/Qemu virtual machines


%prep
%setup -q -n %{name}
./autogen.sh --system


%build
%if 0%{?rhel} >= 6 || 0%{?fedora} >= 19
%configure
%else
%configure --with-spice-html5
%endif
make


%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install


%clean
rm -rf $RPM_BUILD_ROOT

%files
%attr(-, root, root)
%{python_sitelib}/wok/plugins/kimchi/
%{_datadir}/kimchi/doc/
%{_prefix}/share/locale/*/LC_MESSAGES/kimchi.mo
%{_datadir}/wok/plugins/kimchi/
%{_sysconfdir}/wok/plugins.d/kimchi.conf
%{_sysconfdir}/kimchi/
%{_sharedstatedir}/kimchi/
%{_sysconfdir}/systemd/system/wokd.service.d/kimchi.conf


%changelog
* Mon Aug 07 2017 Fabiano Rosas <farosas@linux.vnet.ibm.com> - 2.3.0-18.git
- Add extraver macro to Release field

* Wed Mar 08 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.3.0-17.git3830c25
- 3830c259b7628028dddac3a55aeb33ea964bae2b Merge remote-tracking branch upstream/master into hostos-devel
- 3195f7b1e49bf536cf6f4b9c0545c06c2fdd550d Fix typo

* Wed Mar 01 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.3.0-16.giteb28bd3
- eb28bd36b28c724a10f330da4e7594aa0f834104 Merge remote-tracking branch upstream/master into hostos-devel
- 5c80d731eec41c65f6d241a7898c832f1629b263 fix wrong tab enumeration
- b80f40d0a5eb3138a4ae8360911d3a9aa79f5ba0 Fix storage volume test to run without nginx
- 668e6661734811753419479452f4062b94c51e47 Fix tests to run without proxy

* Wed Feb 22 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.3.0-15.git3fe09a9
- 3fe09a9d232d236b14d11d8e025563cee8b63780 Merge remote-tracking branch upstream/master into hostos-devel
- 7e91dd255326a8e6a2fd2e1c2d7622b1cf8d66b4 Fix patch_auth() call according to Wok changes

* Wed Feb 15 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.3.0-14.git801facd
- 801facd867d55033f33ad3f2e6aea3dbce767c3f Merge remote-tracking branch upstream/master into hostos-devel
- 2c98a2bca9ce465b5df64929e601be7a17e2b4cd Improve logic to identify if a network is in use or not
- 6e21e0e90f79f49477bbaadc5b07b7743ee1ef02 Fix memory hotplug test case
- fe6c4b2efcce89913aa8ef9883407a6ef1c31623 Fix snapshots test case
- d077c8eae1a16f5f67b213fa4f38ddfad0fd9830 Bug fix: Set default host value while generating the virt-viewer config file
- 26b14dd93d77fafed55e0695402b3784f0172bd7 Update run_server() calls to do not pass model instance
- 759cceaf3fb0ebe2d857bd054c7c53710fbb85b0 Specify objectstore location when running on test mode
- aabfe36155b85018205148b51a136717f3cd9033 Bug Fix #979 - Change boot order UI

* Wed Feb 08 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.3.0-13.gitec17672
- ec17672b98a4723aa42c6fc114b3d428b66dcab4 Merge remote-tracking branch upstream/master into hostos-devel
- f55b821fc634fc05667541f75c606591d5e14f9d Update copyright date for root.py file
- df1b0afed6d1b699066c616bd541d2d3c9ec0f29 Bug fix #1089: osinfo.py tablet_bus=usb for x86 modern
- 0182d004d00571b42ef36151a32eb8cb96667367 Adding self.depends option in root.py
- e3890b31cd7e01aca54fce69b2d5d65b2a4fbd81 Fix for the kimchi #1102

* Thu Feb 02 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.3.0-12
- 4ea4cef057617b43381e7e3b913b4a34104cac40 Merge remote-tracking branch upstream/master into hostos-devel
- 000754a45b0dffb805cf4db2dc652117846cb1f6 Fixed truncation for Guest Interface GUI OVS network/interface scroll bar
- 9894bf5251c45b1b4bad8f54298b7417fa1e97c1 Fixed Truncation appeared on Virtualization->add network of Japanese language
- b557edf02c52434287aaa4b717dda4a89da107fb Fixed for Truncation occurs in edit a guest panel console row
- 4692db0d0b98bb0342aa41537beb0faa72fde7e3 Bug fix #1096 - Prevent mass detach based on source PCI address
- cce0ec7377a07ae8321bcc3f7702723580888c87 Remove role_key parameter
- bf479e55f8aa33fb8ad22d1bf0c74c3187eb74d7 Remove whitespaces

* Wed Jan 25 2017 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.3.0-11
- e6939383c4803297bd4587c2602a0e9da152e7c0 Merge remote-tracking branch upstream/master into hostos-devel
- a20630073f45e275a92f883f964f0ce8401a42af Add test to live snapshot
- 930a41177de27b4a4f0fa8bf19ebb3977cdaf976 Bug fix #1029: Unable to create a snapshot on a running guest
- 3358b6e65c797b04e7ed340195f1d874699a8a8b Live migration RDMA support: mockmodel changes
- e449623f0f491d51911a76095985780b6d75a17e Live migration RDMA support: test changes
- fff5e82647fafb585686c0e2abbdfad7d4315b53 Live migration RDMA support: ui changes
- ecee41ed4f63fe7e286517dd48abbc7164b2773f Live migration RDMA support: model changes
- 25d900fd35daea10c9fa2841e889ab45277d1f41 Live migration RDMA support: doc changes
- 823c1b2d375b7eab08ddb62d2e36c7553e53b960 Bug fix #1016: Display current storage volume size on resize dialog
- ed8b4eb5b1cd26afe0b8088c6c664e0a519eba98 Merge remote-tracking branch upstream/master into hostos-devel
- 9c39955d003b2efcaf63baf0bcea91a59e4835e8 VEPA interface not listed with VM running
- 1aa94415d91c452bb54d9e8d0065774a8ee0d051 Merge remote-tracking branch upstream/master into hostos-devel
- b507ce0d8e053a01532ea5421d2255b63770a10d Fix issue #1069: Allow user specifies the Template name when creating it
- 12ab67a2f6a0a03e08c0c4b42e9ddaf8c546111c Update copyright date
- a45663bffaf1497db59d67705511ad1ba30ca1e6 Bug fix #1073: Re-attach device to host when detaching it from guest
- 1d6bc597462f8bdd01f094b25886b1abce428dfe Merge remote-tracking branch upstream/master into hostos-devel
- bb3e57ca12cb9189bdbced83e58d36515776eec1 mockmodel.py: unsubscribing from exit channel on cleanup

* Wed Dec 28 2016 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.3.0-10
- 1d6bc597462f8bdd01f094b25886b1abce428dfe Merge remote-tracking branch upstream/master into hostos-devel
- bb3e57ca12cb9189bdbced83e58d36515776eec1 mockmodel.py: unsubscribing from exit channel on cleanup
- acb4d141c45694a94ec02068309dd4e6f97fea2c Merge remote-tracking branch upstream/master into hostos-devel

* Wed Dec 21 2016 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.3.0-9
- acb4d141c45694a94ec02068309dd4e6f97fea2c Merge remote-tracking branch upstream/master into hostos-devel
- 5b973bde305aefe61f091a0f30d4baa872a58060 Multi-culture UI issues for kimchi plugin Guest module
- 8c49fc6c5fba997f247088042138a41031b46e26 Multi-culture UI issues for kimchi plugin Storage module
- def86526bd09acb4a68cfe68db6be2a21ab92089 Corrected position of close icon for create a network pop up alert
- 7ab1a308f0167b5f0844e87aa3fdd6682195bc3e Multi-culture UI issues for kimchi plugin template module
- fb8a1f344a736699e11f6b63acfeca09ae8a30d0 Bug fix #1064: In Migrate guest window, text boxes are not taking input properly from keyboard.
- 94a5499d7440a5f313e88f724a3b757df6381ce2 Update README file to point to http://kimchi-project.github.io/kimchi/downloads/
- 5dcfc2bdf7039a32da4ef857fdd2f2268958372a Use libvirtd service in Ubuntu
- 426740b727103b6f5a13974753a388bc61dde6f5 Bug fix #1026: CentOS: Unable to get and update memory values for a powered off guest
- 69a81f6a101d586ce435b48f8d7ee060d65d5ad3 Bug fix #1057: Failed to import kimchi
- 9dd98ccffd8386aeb48134dda48566c7b59dfb0b Add more details to error message when probing image
- 61d3bbe25b0e7a7b686082633d6f793fc4ad6040 Add missing dependency to documentation
- 386c7d4e0bfec39a3a5cee348cd2360ffd74d5ee Bug fix #1066: Do not stora guest storage volume information on objectstore
- 9b68c246bdc0ef61886debd67783e9cc4ce7473e Bug fix #1015: Rename Guest Name ID header to Guest Name
- b49cbc6e88c64d79d8f0fbaa400da061573614a6 Fix checking for libvirt daemon on Ubuntu
- e02939371596831f7e7dc1228d7dcbfd284733b0 Fixed resize volume click input number in virtualization->storag
- 3b2ca799f2d534984c052b770b7f6546029be10d Merge remote-tracking branch upstream/master into hostos-devel

* Thu Dec 08 2016 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.3.0-8
- 3b2ca799f2d534984c052b770b7f6546029be10d Merge remote-tracking branch upstream/master into hostos-devel
- 7bc8b7d89c9a206e63250e3bc4d97fe6f16fcc8b Recognize openSUSE 42.2 ISO
- 9e98b5f63ffcc4b76d53aa3fd5536ceb969d9111 Merge remote-tracking branch upstream/master into hostos-devel

* Wed Nov 30 2016 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.3.0-7
- 9e98b5f63ffcc4b76d53aa3fd5536ceb969d9111 Merge remote-tracking branch upstream/master into hostos-devel
- 69db14d6039af2d28d022f6e1ce1452b03f0aefa CPU Hot plug/unplug: test_rest.py changes
- 4694423bf2e5ed4963843b9783f6134aa55b2cf5 CPU Hot plug/unplug: ui changes
- 1aefa588159d238de2c0d2cffdd7277b1db2341d CPU Hot plug/unplug: test changes
- 13374df1f7eef110c373d7b6a8492211a0975c39 CPU Hot plug/unplug: model changes
- 9dfa977ed81a2980e308e61d8607cdd80bcde9e3 CPU Hot plug/unplug: i18n changes
- ea2520874e55ca1919ca0469ce1c5b3488500030 Changing threads to be a free number field
- e23f8144a2619e8533788e5fede416ca077d3336 Edit Guest dialog: fixing Save button on Processor tab
- 4ff16929936b9bf9215cfb723747c3ac58a8e9f4 Adding CPU setup help text in Edit Guest/Template
- 6de1a7f82156e0d7c6894c4936bf656c95cf3f57 CPU configuration UI: several improvements
- ea43e85379ab77e12130b8ccd078852c86e72cba Adding Processor tab in Edit Guest dialog
- e031c59364be2ad8409aa4071828d00398125c10 template_edit_main.js: initProcessor now a global function
- 22c3767c724fb19d617a1428a6776ba890e5390b Adding sockets field in the topology of Templates
- 750d0c14decc46e564829b0e374a46c65330a1cc Bug fix #1072 - changing vpus verification
- 429e8ec8c5a290197408d59c965e3bf2b6c488bb Merge remote-tracking branch upstream/master into hostos-devel

* Sat Nov 26 2016 OpenPOWER Host OS Builds Bot <open-power-host-os-builds-bot@users.noreply.github.com> - 2.3.0-6
- 429e8ec8c5a290197408d59c965e3bf2b6c488bb Merge remote-tracking branch upstream/master into hostos-devel
- f3fd6c943e99d34d5def59a8404aa8409cbde6b4 Fix pep8 issue
- 38a06b616e3525fdfa9268d58b37954ac1c929b0 Fixed issue #1076 s390x : n/w shows twice same interface while adding for template
- f367ac242d91f198760b66c335b11b0051953f6b Fixed issue #1075 s390x : Edit Template storage tab Storage dropdown shows default text
- f621ecdc21c5705c606b98eada53511998b41c0b Fixed issue #1062 Disk path not taking input properly
- f11af4bc644f38546c95dd046bed0c16ec782b61 Update Kimchi code due chnages on Wok configuration parameters
- d75b2ae0a6ed5738e2e55ea9eeaa75b8373c284c po/ja_JP.po: fix trailing whitespace
- b436a6e8987027cd12fb348160e4e794e13232c3 rpmlint fixes on Fedora and Suse specs
- 3d81b206f732a15eb05f4aa6172845b1dd590a50 Issue #1050: Rename template with existing template name
- a4c77ec2ff06adacc0937a77dbcffc3b4176972f s390x specific changes to support storage path and storage pool as disk.
- 5f7a29f8db472767f95093808f36f8c8d4e9830b Edit template storage path should start with /
- 6381c26a083891324d6b0a95bd443b2a8603d0b7 Fixed issue #1074 IP address for the guest under Interfaces tab is blank
- f4934ca08d45760a16b4e39ebb2ee3704f64b445 Merge remote-tracking branch upstream/master into hostos-devel

* Wed Nov 09 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 2.3.0-5
- Kimchi rebase

* Thu Nov 3 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 2.3.0-4
- spec cleanup

* Wed Nov 02 2016 user - 2.3.0-3
- 71787ff Merge remote-tracking branch upstream/master into hostos-devel
0e180c4 Remove URI configuration from kimchi.conf file
d5b9a19 Issue #1061: For s390x, in edit template add storage path, even after changing value in path textbox its border still remains red.
4a9b757 Issue #1060: Edit template/Guest for s390x, console drop down shows empty box along with virtio and sclp.
8ac4fcb Issue #1059: Not able to save corrected img path after editing img based template which has incorrect img path due to the img is not available.
27deb5d Wok issue #173: Set tab color on tab-ext.xml and update SCSS files
c3123ca Wok issue #174: Let Wok create the whole navigation bar
70d3d2c Issue: #1008 Issues while editing a VEPA network
e765833 PCI hotplug: Check USB controller, define in template, add test in Power
1d9f65a Issue #651: Windows guests - default mouse type causing problems
af947ef Improve multifunction attach/detach operations
81a2872 Improve Fedora 24 identification
56ab027 Adding libvirt remote connection verification
9329a25 Github #1007: Fixing non-root ssh key generation
45c44c0 Github #1007: use provided user for password-less setup
138d1db For s390x virtualization edit template display Storage as header
25d9eb9 Added UI validation for s390x Virtualization Template Edit Add Storage module
2c5cd0b Added UI validation for s390x Virtualization Guest Edit Add Storage module
925fc3f Remove PowerKVM checks from memory alignment code
b1b0e8c Use tablet_bus for tablet input instead of kbd_bus
45b3174 Issue #733: CSS updates to handle relative path support.
f32880d Issue #733: Fix UI to handle relative paths.
79c6a80 Issue #1006: Invalid subnet value when editing a network raise an error
9747324 fix for issue #1049
a6d777e Issue #1048 : disable DASD disks without partitions on s390x
7a8eb3c Issue #962: Suggestion to check spec guidelines
9a17aa7 For s390x hide Netboot template for Virtualization Add Template
2315961 Issue #1047: In xmlutils/interface.py --> get_iface_xml returns none for type Ethernet
b67c319 Merge branch next
d49b302 Modified unit test cases to include new s390x specific features
c18ecbd For s390x hide VNC, PCI, Snapshot, Graphics and clone options
7b9d4e6 Issue #999 : Attach storage to guest on s390x without libvirt
2e4b180 Issue #1045 : boot order fix for guest edit
7289515 Introducing s390x UI Interfaces module for Edit Template under virtualization
2f830f0 Introducing Console for edit Guest module under virtualization
91c76d8 Introducing Console for edit template module under virtualization
7342092 added console parameter to vms api for s390x
588b2f2 added console parameter to templates api for s390x
7d28fe9 Introducing s390x UI Storage module for Edit Guest under virtualization
faa18b0 Introducing s390x UI Storage module for Edit Template under virtualization
89b541c Fix for Issue #1000 : Make Check fails on s390x environment
4a62c5e Issue #992 : Create template on s390x without libvirt storage.
d58c089 Introducing s390x UI Interfaces module for Edit Guest under virtualization
43944df Merge remote-tracking branch upstream/stable-2.3.x into hostos-devel
7186c53 Remove URI configuration from kimchi.conf file
a090447 Issue #1059: Not able to save corrected img path after editing img based template which has incorrect img path due to the img is not available.
439b4af Wok issue #173: Set tab color on tab-ext.xml and update SCSS files
7ffe39a Wok issue #174: Let Wok create the whole navigation bar
de50d9f Issue: #1008 Issues while editing a VEPA network
b29e675 PCI hotplug: Check USB controller, define in template, add test in Power
bd44fc1 Issue #651: Windows guests - default mouse type causing problems
2c80f01 Improve multifunction attach/detach operations
17fb7d3 Improve Fedora 24 identification
2937bcd Adding libvirt remote connection verification
67c5c8d Github #1007: Fixing non-root ssh key generation
ade2c49 Github #1007: use provided user for password-less setup
852503c Remove PowerKVM checks from memory alignment code
475678f Use tablet_bus for tablet input instead of kbd_bus
2cb417f Issue #1006: Invalid subnet value when editing a network raise an error
a7f6dbc Update ChangeLog, VERSION and po files to 2.3 release
65911fd Improve storage volume creation of XML
7761ae4 Fixed noTemplate message display
21fdd7a Fix make-rpm target
2933d64 Issue #1018 - Disable volume resize option on logical pool.
cf788ac Fix max number of memory slots for Ubuntu on Power
b8d9171 Issue #1017: Fix upload file to logical storage pool.
02d2d4f Fix issue #1019: Hide storage volume actions menu for iSCSI/SCSI pools
1c75947 Bug fix #521: Extend logical pool
6c044f9 Fix issue #1022: Remove Clone option for running guests
16b14bb Bug fix: Recognize Fedora 24 ISO
b8cdedd Fix issue #1005: Proper display paused guests on Gallery View
4a2e554 Bug fix: Disable Search More ISOs button on create Template dialog when the operation is in progress
9e863d8 Fix issue #1020: Fix alert icon position to do not overlay img/iso icon
2d1a0e7 Fix issue #1020: Verify libvirt access on real file path instead of symlink
52e44d1 Remove legacy check_files on Makefile
0ec9ead Issue #1012: Boot order gets reset to only one entry after editing a VM
063ef8b Issue #585: make clean does not revert its changes from make rpm
f0016f4 Fix issue #1010: Convert disk size to bytes while attaching new disk to guest
77ddaa6 remote iso listing for s390x
2be8daa Storagebuttons not behaving properly
3bc4697 Create test to verify graphics type change
90299ac Issue #836: Allow user change guest graphics type
1090f3a Issue #994: SPICE graphics does not need <channel> tag
6bdb060 For s390x architecture, serial type is not validated in vm xml as as not supported on s390x.
4a36120 Issue# 973 Emphasize resource name in dlg
60e0ca6 Updated API.md for addition paramters support for VM ifaces API on s390x/s390 architecture.
e7a6f95 Updated code to support VM ifaces on s390x/s390 architecture.
dff38a1 Updated API.md for addition interfaces paramter in template API.
b09bbaf Updated code to support interfaces parameter to template API only on s390x/s390 architecture.
963a294 /plugins/kimchi/ovsbridges API
190e612 Issue #606: Change icon to distinguish image generated template and iso generated template
1c48656 Issue #939: [UI] Guest tab is not rendered correctly if guests are not in running or shutoff state
c054786 Issue #921: Peers button disappears
cc0f163 Enhancement to /plugins/kimchi/interfaces
554be6c Enhancement to /plugins/kimchi/interfaces
2e111ef Issue #626: Snapshot revert does not release storage volume
298dff0 Update tests
7624370 Do not remove storagepools linked to guests
66bf654 mockmodel.py: fixing virtviewerfile_tmp path
92e903a Only on s390x add default networks to template if template.conf has default network configuration uncommented.
6ef5dc3 Update usage of add_task() method.
26d74de Check if VM is off before detaching multifn PCI
5f91b00 Github #986: create /data/virtviewerfiles dir automatically
bac1972 Revert Fix frontend vcpu hotplug
0bcc46e Fix differences from upstream code
b3f05e5 Revert Implement CPU HotPlug/HotUnplug
0c5755c Issue: #1008 Issues while editing a VEPA network

* Wed Oct 26 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 2.3.0-2
- 0c5755c Issue: #1008 Issues while editing a VEPA network
3bb1581 PCI hotplug: Check USB controller, define in template, add test in Power
fa8a9ce Issue #651: Windows guests - default mouse type causing problems
19b3621 Improve multifunction attach/detach operations

* Wed Oct 05 2016 user - 2.2.0-7
- bfe8c18 [HostOS] Revert Enable CPU HotPlug in UI
3661131 [HostOS] Revert Fix frontend vcpu hotplug
586b25a Use vfio for live assignment of devices too
70efd44 Update ChangeLog, VERSION and po files to 2.3 release
833ada3 Improve storage volume creation of XML
e33a592 Fixed noTemplate message display
d885f94 Fix make-rpm target

* Thu Sep 29 2016 Olav Philipp Henschel <olavph@linux.vnet.ibm.com> - 2.2.0-6
- d885f94 Fix make-rpm target
bdb879f Issue #1018 - Disable volume resize option on logical pool.
25d02dd Fix max number of memory slots for Ubuntu on Power
4a5690d Issue #1017: Fix upload file to logical storage pool.
639198b Fix issue #1019: Hide storage volume actions menu for iSCSI/SCSI pools
8f47e2a Bug fix #521: Extend logical pool
912bc93 Fix issue #1022: Remove Clone option for running guests
3091f31 Bug fix: Recognize Fedora 24 ISO
fc9bfbd Fix issue #1005: Proper display paused guests on Gallery View
7fb3e2c Bug fix: Disable Search More ISOs button on create Template dialog when the operation is in progress
8ae95fa Fix issue #1020: Fix alert icon position to do not overlay img/iso icon
b6fbaa2 Fix issue #1020: Verify libvirt access on real file path instead of symlink
48314ab Remove legacy check_files on Makefile
98a28cd Issue #1012: Boot order gets reset to only one entry after editing a VM
e9aa8f1 Issue #585: make clean does not revert its changes from make rpm
76f0d52 Fix issue #1010: Convert disk size to bytes while attaching new disk to guest
81d2bee Fallback multifunction attach/detach to single function

* Thu Sep 22 2016 user - 2.2.0-5
- 81d2bee Fallback multifunction attach/detach to single function
b9daefe remote iso listing for s390x
484cab8 Storagebuttons not behaving properly

* Wed Sep 07 2016 user - 2.2.0-3.pkvm3_1_1
- 484cab8 Storagebuttons not behaving properly
6c2249e Create test to verify graphics type change
dfb11f2 Issue #836: Allow user change guest graphics type
8ce6506 Issue #994: SPICE graphics does not need <channel> tag
2f5e538 For s390x architecture, serial type is not validated in vm xml as as not supported on s390x.
0889977 Issue# 973 Emphasize resource name in dlg
2bcb669 Updated API.md for addition paramters support for VM ifaces API on s390x/s390 architecture.
b2371dc Updated code to support VM ifaces on s390x/s390 architecture.
bdd88ad Updated API.md for addition interfaces paramter in template API.
fd39978 Updated code to support interfaces parameter to template API only on s390x/s390 architecture.
189f53b /plugins/kimchi/ovsbridges API
2285616 Issue #606: Change icon to distinguish image generated template and iso generated template
c7e9307 Issue #939: [UI] Guest tab is not rendered correctly if guests are not in running or shutoff state
8ad9319 Issue #921: Peers button disappears
30ce46d Enhancement to /plugins/kimchi/interfaces
b6eb399 Enhancement to /plugins/kimchi/interfaces
5a6b9a0 Issue #626: Snapshot revert does not release storage volume
12fe984 Attach all functions of multi-fn PCI PT at once

* Thu Sep 01 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 2.2.0-2.pkvm3_1_1
- Build August, 31st, 2016

* Wed Aug 24 2016 <baseuser@ibm.com>
  Log from git:
- 5d50e5308e1cf68c2c9530ea09e52856ef184aa3 Merge remote-tracking branch 'upstream/master' into powerkvm-v3.1.1
- 564caeff6a038f67fa2ae4d337c94d7fbc777b8c Fix when calling error message in storagepool
- 3a4eab04d079c2fad08b98b4a95e44899dd09fa6 Issue #933: Invalid image path not marking template as "invalid" (back-end)
- a05de4991cbb71d32133f8d4631750a3e89e2c28 test/test_model.py pep8 1.5.7 fix
- 12d85d330f6cb4e5de0cb17f9035afe5fef20a12 Issue #982 - Fix broken testcases.
- b73e7aea2d019f49e6d83caab07314b1e72ca9e0 Update docs
- 6490cb2d6ccf8e9917059cc22930ba2f856235f7 Update tests
- 6a37e55c893df381f6a4686bdf1f8ecb72b85de5 Issue #857: Support VM description
- 4231b292acef87ef06a3ff947dfa1c5bc43eb5bd Merge remote-tracking branch 'upstream/master' into openpower-v3.1.1
- 351917d8e642b7eadc94a6eeda20dc337ffb774f Issue #317 Inconsistent button status when adding or creating new resources
- 2c84b510e44df88f9ae2c512ca99e2a9ff28e86e Prevents pci passthrough double click
- 7cc96b592191b521effac1a6bb98a2b4dbf29474 Fix frontend vcpu hotplug
- 430a08b47dabef185bc94e41b0fdce31ed875846 Issue #585: 'make clean' does not revert its changes from 'make rpm'
- de355ab4b26f54994ea9b7c91aedb9fff00fcc2a model.py: use the new 'get_all_model_instances' utils function
- 7d7c2add2b457b89ce88424e20e60fa20d4360e2 Modified code, to return distro and version as unknown, if guestfs import failed.
- 56bf15c1b670186f44ec48f41b20c3dfdf657044 Added s390x architecture support in osinfo params.
- 1d235836a8f4dfbf8cd9d4517fa1ace9ac247672 Added on_poweroff, on_reboot, on_crash tag to also support s390x architecture.
- b0675bc8473a9cfc47a11f2eb1d22b8a0a97df39 Added method for implementation of s390x boot detection.
- 13073796fdb2eac2c05a1f75ed1a5f002db073b0 Added check for s390x architecture to not add graphics in params as not supported.
- 83d92f8c40e80384102b9c3b79d94d366b853ce2 Issue #604: Windows XP: Kimchi should set the right NIC Type in Templates
- 38aeade3d04fc62c7a3852b8480d96be8289e36c Revert "Use verbs in the past"
- 4cb6484ea412dac08ab995ae47e8c37380e6037f Updated serial console to support s390x architecture.
- 6719ebb3d274c6236486ec7bb714cc09cc632424 New memory Hot-UNplug implementation
- c90d95dfc04cee88268cec1835f0dc057a071f78 Merge remote-tracking branch 'upstream/master' into openpower-v3.1.1
- b45afea94cb11628c1a41c8714df4eca938a247d Validate passthrough inside the task
- 12bb8addb91dd6acab39acb83d8f701b8e2a73b0 Replace device companion check before the passthrough
- 2c0ce1d5012a47be92dd719ad4626d6ba91e998a Improve PCI passthrough performance
- d62079bc06b9df6a93e4b93e022664e8d5d504bb Add test to verify bootmenu and update old tests
- 616c6a9b29616577d2a5850d1ae45b4307636d82 Allow guest to enable bootmenu on startup
- 6eeaa837854671add9356ee3490f6f18fcce579a Disable vm statistics/screenshots in edit guest
- 765a954dcf6e25ee17c802a2c193794cfbaa744c Issue #968: Kimchi is searching for 'undefined' VM
- 42717b3fd98e4d40f75be4cc515fbec9d05a74c7 Add test to check bootorder
- 255e6d90c7bf756798054940bdf71924971f16aa Add function to retrieve bootorder on vm lookup
- 7d6be682ab01fadd2590a9af7ea199749a85a086 Update REST API
- 394422f11cc99b9cc9dbad4e4ea1920020dcaa4b Update documentation about bootorder on vm update
- a5b9e1fd8f34d6886bc3874b9f4f1dd45ddac613 Create method to change bootorder of a guest
- e05c7a378ba4302047ebc12142ed850e1215ad7c Add function get_bootorder_node
- 24cc635d8d0180bc77a6473a511dc14fed6d3fdb Virt-Viewer launcher: mockmodel changes
- d57f2b555190f57a3925eec357c9f9c81514512a Virt-Viewer launcher: changes after adding libvirt event listening
- 5d58c673aa76c0644cbec28bc975f9b4b54555d1 Virt-Viewer launcher: libvirt events to control firewall
- b822c44aa56b0a5b3e74237b633f48c628886dfa Virt-Viewer launcher: test changes for firewall manager
- dc70e6bc6541d59ee43beb037221a415a7e98df1 Virt-Viewer launcher: adding FirewallManager class
- 80c170d86d338e489238cecf3b537305a801ef6d Virt-Viewer launcher: test changes
- f5a47afc4448b625010b8427ac84cef5d82151c9 Virt-Viewer launcher: virtviewerfile module
- f8b51e1ce33ef3a1fb25cdfad5423a6a29fa5893 Virt-Viewer launcher: control/vms.py and model/vms.py changes
- 9148d3f0cce3ff8b46b76e443e8f6087f4790182 Virt-Viewer launcher: Makefile and config changes
- abb511449c12c151e01f643dbb0dcfad6b700928 Virt-Viewer launcher: docs and i18n changes
- 66144ab95e71b9905cc3f4fbae4799ef7c24d2ff Merge remote-tracking branch 'upstream/master' into openpower-v3.1.1
- e0faa466f6c25bddb6dfe299c02aa755bf6af394 Kimchi kills Wokd due to sys.exit() calls in files networks.py and storagepools.py
- 66567fe2181c8fe613e7e7282c3416840dcd8d49 Issue #969: Error message showing up in parent panel rather than modal window in Add Storage

* Thu Jun 18 2015 Lucio Correia <luciojhc@linux.vnet.ibm.com> 2.0
- Run kimchi as a plugin

* Thu Feb 26 2015 Frédéric Bonnard <frediz@linux.vnet.ibm.com> 1.4.0
- Add man page for kimchid

* Tue Feb 11 2014 Crístian Viana <vianac@linux.vnet.ibm.com> 1.1.0
- Add help pages and XSLT dependency

* Tue Jul 16 2013 Adam Litke <agl@us.ibm.com> 0.1.0-1
- Adapted for autotools build

* Thu Apr 04 2013 Aline Manera <alinefm@br.ibm.com> 0.0-1
- First build
