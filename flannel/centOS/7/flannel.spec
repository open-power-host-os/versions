%global with_devel 0
%global with_bundled 1
%global with_debug 1
%global with_check 0

%if 0%{?with_debug}
# https://bugzilla.redhat.com/show_bug.cgi?id=995136#c12
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif
%global provider        github
%global provider_tld    com
%global project         coreos
%global repo            flannel
%global import_path     %{provider}.%{provider_tld}/%{project}/%{repo}
%global commit          cb8284fb60737793596dd2fc98d9608d3d0d66f0
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

%global devel_main      flannel-devel

Name:           flannel
Version:        0.5.5
Release:        1%{?dist}
Summary:        Etcd address management agent for overlay networks
License:        ASL 2.0
URL:            https://%{import_path}
Source0:        %{name}.tar.gz
Source1:        flanneld.sysconf
Source2:        flanneld.service
Source3:        flannel-docker.conf
Source4:        flannel-tmpfiles.conf

Patch0:         change-4001-to-2379-in-help-and-README.patch
Patch1:         change-coreos.com-network-to-atomic.io-network-in-he.patch
Patch3:         internal-to-inteernal.patch

ExclusiveArch:  %{ix86} x86_64 %{arm} ppc64le

BuildRequires:      golang >= 1.2.7
%if ! 0%{?with_bundled}
BuildRequires:      golang(code.google.com/p/goauth2/compute/serviceaccount)
BuildRequires:      golang(code.google.com/p/google-api-go-client/compute/v1)
BuildRequires:      golang(code.google.com/p/google-api-go-client/googleapi)
BuildRequires:      golang(github.com/coreos/etcd/client)
BuildRequires:      golang(github.com/coreos/etcd/pkg/transport)
BuildRequires:      golang(github.com/coreos/go-iptables/iptables)
BuildRequires:      golang(github.com/coreos/go-systemd/activation)
BuildRequires:      golang(github.com/coreos/go-systemd/daemon) >= 2-2
BuildRequires:      golang(github.com/coreos/pkg/flagutil)
BuildRequires:      golang(github.com/golang/glog)
BuildRequires:      golang(github.com/gorilla/mux)
BuildRequires:      golang(github.com/mitchellh/goamz/aws)
BuildRequires:      golang(github.com/mitchellh/goamz/ec2)
BuildRequires:      golang(github.com/vishvananda/netlink)
BuildRequires:      golang(github.com/vishvananda/netlink/nl)
BuildRequires:      golang(golang.org/x/net/context)
%endif
BuildRequires:      pkgconfig(systemd)
Requires:           systemd
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd

%description
Flannel is an etcd driven address management agent. Most commonly it is used to
manage the ip addresses of overlay networks between systems running containers
that need to communicate with one another.

%if 0%{?with_devel}
%package devel
Summary:  %{summary}
BuildRequires: golang >= 1.2.7

BuildRequires: golang(code.google.com/p/goauth2/compute/serviceaccount)
BuildRequires: golang(code.google.com/p/google-api-go-client/compute/v1)
BuildRequires: golang(code.google.com/p/google-api-go-client/googleapi)
BuildRequires: golang(github.com/coreos/etcd/client)
BuildRequires: golang(github.com/coreos/etcd/pkg/transport)
BuildRequires: golang(github.com/coreos/go-iptables/iptables)
BuildRequires: golang(github.com/coreos/go-systemd/activation)
BuildRequires: golang(github.com/golang/glog)
BuildRequires: golang(github.com/gorilla/mux)
BuildRequires: golang(github.com/mitchellh/goamz/aws)
BuildRequires: golang(github.com/mitchellh/goamz/ec2)
BuildRequires: golang(github.com/vishvananda/netlink)
BuildRequires: golang(github.com/vishvananda/netlink/nl)
BuildRequires: golang(golang.org/x/net/context)

Requires: golang(code.google.com/p/goauth2/compute/serviceaccount)
Requires: golang(code.google.com/p/google-api-go-client/compute/v1)
Requires: golang(code.google.com/p/google-api-go-client/googleapi)
Requires: golang(github.com/coreos/etcd/client)
Requires: golang(github.com/coreos/etcd/pkg/transport)
Requires: golang(github.com/coreos/go-iptables/iptables)
Requires: golang(github.com/coreos/go-systemd/activation)
Requires: golang(github.com/golang/glog)
Requires: golang(github.com/gorilla/mux)
Requires: golang(github.com/mitchellh/goamz/aws)
Requires: golang(github.com/mitchellh/goamz/ec2)
Requires: golang(github.com/vishvananda/netlink)
Requires: golang(github.com/vishvananda/netlink/nl)
Requires: golang(golang.org/x/net/context)

Provides: golang(%{import_path}/backend) = %{version}-%{release}
Provides: golang(%{import_path}/backend/alloc) = %{version}-%{release}
Provides: golang(%{import_path}/backend/awsvpc) = %{version}-%{release}
Provides: golang(%{import_path}/backend/gce) = %{version}-%{release}
Provides: golang(%{import_path}/backend/hostgw) = %{version}-%{release}
Provides: golang(%{import_path}/backend/udp) = %{version}-%{release}
Provides: golang(%{import_path}/backend/vxlan) = %{version}-%{release}
Provides: golang(%{import_path}/network) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/ip) = %{version}-%{release}
Provides: golang(%{import_path}/remote) = %{version}-%{release}
Provides: golang(%{import_path}/subnet) = %{version}-%{release}

%description devel
Flannel is an etcd driven address management agent. Most commonly it is used to
manage the ip addresses of overlay networks between systems running containers
that need to communicate with one another.

This package contains library source intended for
building other packages which use %{project}/%{repo}.
%endif

%prep
%setup -q -n %{name}
%patch0 -p1
%patch1 -p1
%patch3 -p1

%if ! 0%{?with_bundled}
find . -name "*.go" \
       -print |\
              xargs sed -i 's/github.com\/coreos\/flannel\/Godeps\/_workspace\/src\///g'
%endif

%build
mkdir -p src/github.com/coreos
ln -s ../../../ src/github.com/coreos/flannel

%if ! 0%{?with_bundled}
export GOPATH=$(pwd):%{gopath}
%else
export GOPATH=$(pwd):%{buildroot}/%{gopath}:$(pwd)/Godeps/_workspace
%endif

function gobuild { go build -a -ldflags "-B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \n')" -v -x "$@"; }

gobuild -o bin/flanneld .

%install
# package with binary
install -D -p -m 755 bin/flanneld %{buildroot}%{_bindir}/flanneld
install -D -p -m 644 %{SOURCE1} %{buildroot}/etc/sysconfig/flanneld
install -D -p -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/flanneld.service
install -D -p -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/docker.service.d/flannel.conf
install -D -p -m 755 dist/mk-docker-opts.sh %{buildroot}%{_libexecdir}/flannel/mk-docker-opts.sh
install -D -p -m 0755 %{SOURCE4} %{buildroot}%{_tmpfilesdir}/%{name}.conf

mkdir -p %{buildroot}/run
install -d -m 0755 %{buildroot}/run/%{name}/

%if 0%{?with_devel}
# devel package
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
cp -pav {backend,pkg,subnet} %{buildroot}/%{gopath}/src/%{import_path}/
%endif

%check
%if 0%{?with_check}
export GOPATH=${PWD}/_build:%{gopath}
go test %{import_path}/pkg/ip
#go test %{import_path}/remote
go test %{import_path}/subnet
%endif

%post
%systemd_post flanneld.service

%preun
# clean tempdir and workdir on removal or upgrade
%systemd_preun flanneld.service

%postun
%systemd_postun_with_restart flanneld.service

%files
%doc CONTRIBUTING.md  LICENSE MAINTAINERS README.md  DCO NOTICE
%{_bindir}/flanneld
%{_unitdir}/flanneld.service
%{_unitdir}/docker.service.d/flannel.conf
%{_libexecdir}/flannel/mk-docker-opts.sh
%dir %{_libexecdir}/flannel
%config(noreplace) %{_sysconfdir}/sysconfig/flanneld
%dir /run/%{name}/
%{_tmpfilesdir}/%{name}.conf

%if 0%{?with_devel}
%files devel
%doc CONTRIBUTING.md  LICENSE MAINTAINERS README.md  DCO NOTICE
%dir %{gopath}/src/%{provider}.%{provider_tld}/%{project}
%dir %{gopath}/src/%{import_path}/
%{gopath}/src/%{import_path}/
%endif

%changelog
* Wed Sep 07 2016 jchaloup <jchaloup@redhat.com> - 0.5.5-1
- Update to flannel v5.5.0
  resolves: #1373915

* Wed Jun 29 2016 jchaloup <jchaloup@redhat.com> - 0.5.3-10
- Own /usr/libexec/flannel directory
- make envs in service and config file canonical
  resolves: #1341223

* Thu Jan 14 2016 jchaloup <jchaloup@redhat.com> - 0.5.3-9
- Build with debug-info support
  resolves: #1298728

* Fri Oct 30 2015 jchaloup <jchaloup@redhat.com> - 0.5.3-8
- Add After=network-online.target and Wants=network-online.target
  to actively wait for network to get on
  resolves: #1275837

* Fri Oct 30 2015 jchaloup <jchaloup@redhat.com> - 0.5.3-7
- Add Restart=on-failure to flanned.service file

* Thu Oct 08 2015 jchaloup <jchaloup@redhat.com> - 0.5.3-6
- Make flannel start after the network is ready
  resolves: #1269291

* Wed Sep 23 2015 jchaloup <jchaloup@redhat.com> - 0.5.3-5
- Flannel now owns /run/flannel directory

* Wed Sep 23 2015 jchaloup <jchaloup@redhat.com> - 0.5.3-4
- Send systemd notification when -listen is used
- Create /run/flannel directory for mk-docker-opts.sh

* Thu Sep 17 2015 jchaloup <jchaloup@redhat.com> - 0.5.3-3
- Change coreos.com/network to atomic.io/network in help and docs
  related: #1261756

* Thu Sep 10 2015 jchaloup <jchaloup@redhat.com> - 0.5.3-2
- Change 4001 port in flannel --help and README.md as well
  resolves: #1261756

* Mon Aug 31 2015 jchaloup <jchaloup@redhat.com> - 0.5.3-1
- Update to 0.5.3
  resolves: #1258876

* Tue Jul 21 2015 jchaloup <jchaloup@redhat.com> - 0.5.1-3
- Change etcd port from 4001 to 2379
- Polish spec file

* Fri Jul 10 2015 jchaloup <jchaloup@redhat.com> - 0.5.1-2
- Change flannel prefix from /coreos.com/network to /atomic.io/network

* Fri Jul 10 2015 jchaloup <jchaloup@redhat.com> - 0.5.1-1
- Update to 0.5.1

* Fri Jul 10 2015 jchaloup <jchaloup@redhat.com> - 0.5.0-3
- Add After=etcd.service to flanneld.service

* Fri Jun 26 2015 jchaloup <jchaloup@redhat.com> - 0.5.0-2
- Add missing Requires: golang(github.com/gorilla/mux) to devel subpackage

* Fri Jun 26 2015 jchaloup <jchaloup@redhat.com> - 0.5.0-1
- Update to 0.5.0

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri May 22 2015 jchaloup <jchaloup@redhat.com> - 0.4.1-2
- Bump to upstream 9180d9a37e2ae6d7fceabea51c6416767c6b50f6
  related: #1223445

* Wed May 20 2015 jchaloup <jchaloup@redhat.com> - 0.4.1-1
- Bump to upstream 4ab27ddd3e87eb2daf152513c0b1dc22879393a8
  resolves: #1223445

* Fri Apr 10 2015 Eric Paris <eparis@redhat.com> - 0.3.1-1
- Bump to version 0.3.1

* Tue Apr 7 2015 Eric Paris <eparis@redhat.com> - 0.3.0-1
- Bump to version 0.3.0

* Mon Mar 30 2015 jchaloup <jchaloup@redhat.com> - 0.2.0-7
- Add debug info
  related: #1165688

* Fri Feb 20 2015 jchaloup <jchaloup@redhat.com> - 0.2.0-6
- Update [Build]Requires for go-etcd package

* Wed Jan 21 2015 Eric Paris <eparis@redhat.com> - 0.2.0-5
- Add generator more like upstream wants to use, use ExecStartPost
  (https://github.com/coreos/flannel/pull/85)

* Tue Jan 20 2015 Eric Paris <eparis@redhat.com> - 0.2.0-4
- Add generator to turn flannel env vars into docker flags

* Tue Jan 20 2015 Peter Lemenkov <lemenkov@gmail.com> - 0.2.0-3
- Change (Build)Requires accordning to the recent changes
  (http://pkgs.fedoraproject.org/cgit/golang-github-coreos-go-systemd.git/commit/?id=204f61c)

* Fri Jan 16 2015 Peter Lemenkov <lemenkov@gmail.com> - 0.2.0-2
- Change flannel service type to notify. See
  https://github.com/coreos/flannel/blob/v0.2.0/main.go#L213

* Tue Dec 23 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0.2.0-1
- update to upstream v0.2.0
- append FLANNEL_OPTIONS variable to unitfile command
- systemd-units merged into systemd for fedora18+

* Tue Dec  2 2014 John W. Linville <linville@redhat.com> - 0.1.0-8.gita7b435a
- Remove patches related to out-of-tree slice backend
- Update to latest upstream

* Thu Nov 20 2014 jchaloup <jchaloup@redhat.com> - 0.1.0-7.git071d778
- Removing deps on Godeps and adding deps on golang-github packages
- Removing wait-online service and changing Type of flannel.service from simple to notify
- Adding README and other doc files
- Adding spec file header with commit, import_path, ...
- Adding devel subpackage
- spec polished based on Lokesh' notes (3 lines below)
- modify summary in specfile as in bug description (capitalize if needed)
- might need to enforce NVR for coreos/go-systemd in deps
- pkgconfig(systemd) is preferable to systemd in BR (I think)
  resolves: #1165688

* Fri Nov 07 2014 - Neil Horman <nhoramn@tuxdriver.com>
- Updating to latest upstream

* Fri Nov 07 2014 - Neil Horman <nhoramn@tuxdriver.com>
- Added wait-online service to sync with docker

* Thu Nov 06 2014 - Neil Horman <nhoramn@tuxdriver.com>
- Fixed flanneld.service file
- Added linvilles slice type patch

* Tue Nov 04 2014 - Neil Horman <nhorman@tuxdriver.com> - 0.1.0-20141104gitdc530ce
- Initial Build
