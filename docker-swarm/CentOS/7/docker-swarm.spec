#
# spec file for package docker-swarm
#
# Copyright (c) 2015 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

%global commit          a0fd82b90932741bda54245e990df433a9ee06a7
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

Name:           docker-swarm
Version:        1.1.0
Release:        1.git%{shortcommit}
Summary:        Docker-native clustering system
License:        Apache-2.0
Group:          System/Management
Url:            https://github.com/docker/swarm
Source:         %{name}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  go >= 1.5

%description
Docker Swarm is native clustering for Docker. It turns a pool of Docker hosts
into a single, virtual host.

%prep
%setup -q -n %{name}

%build
export GOPATH=$PWD/Godeps/_workspace
mkdir -p $GOPATH/src/github.com/docker
ln -s $PWD $GOPATH/src/github.com/docker/swarm
go build -x -o swarm

%install
%{__mkdir_p} %{buildroot}%{_bindir}
%{__install} -m755 swarm %{buildroot}%{_bindir}/swarm

%files
%defattr(-,root,root,-)
%{_bindir}/swarm
%doc LICENSE.docs README.md

%changelog
