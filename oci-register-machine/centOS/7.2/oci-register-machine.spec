%if 0%{?fedora}
%global with_devel 0
%global with_bundled 0
%global with_debug 1
%global with_check 1
%global with_unit_test 0
%else
%global with_devel 0
%global with_bundled 1
%global with_debug 1
# no test files so far
%global with_check 0
# no test files so far
%global with_unit_test 0
%endif

%if 0%{?with_debug}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%global provider github
%global provider_tld com
%global project projectatomic
%global repo oci-register-machine
# https://github.com/projectatomic/oci-register-machine
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path %{provider_prefix}
%global commit af6c129ea47222e63c85b7872104adf2e9057297
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name: %{repo}
Epoch: 1
Version: 0
Release: 1.8.git%{shortcommit}%{?dist}
Summary: Golang binary to register OCI containers with systemd-machined
License: ASL 2.0
URL: https://%{import_path}
Source0: %{name}.tar.gz

# e.g. el6 has ppc64 arch without gcc-go, so EA tag is required
ExclusiveArch:  %{ix86} x86_64 %{arm} ppc64le
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang} >= 1.6.2

%if ! 0%{?with_bundled}
BuildRequires: golang(github.com/godbus/dbus)
BuildRequires: golang(gopkg.in/yaml.v1)
%endif
BuildRequires:   go-md2man
%if 0%{?fedora}
Requires: systemd-container
%else
Requires: systemd
%endif

%description
%{summary}

%if 0%{?with_devel}
%package devel
Summary: %{summary}
BuildArch: noarch
Provides: golang(%{import_path}) = %{version}-%{release}

%if 0%{?with_check} && ! 0%{?with_bundled}
%endif

%description devel
%{summary}

This package contains the source files for
building other packages which use import path with
%{import_path} prefix.
%endif

%if 0%{?with_unit_test} && 0%{?with_devel}
%package unit-test-devel
Summary: Unit tests for %{name} package
%if 0%{?with_check}
#Here comes all BuildRequires: PACKAGE the unit tests
#in %%check section need for running
%endif

# test subpackage tests code from devel subpackage
Requires: %{name}-devel = %{version}-%{release}

%description unit-test-devel
%{summary}

This package contains unit tests for project
providing packages with %{import_path} prefix.
%endif

%prep
%setup -q -n %{name}
sed -i 's/false/true/' %{name}.conf

%build
mkdir -p src/%{provider}.%{provider_tld}/%{project}
ln -s ../../../ src/%{import_path}

%if ! 0%{?with_bundled}
export GOPATH=$(pwd):%{gopath}
%else
export GOPATH=$(pwd):$(pwd)/Godeps/_workspace:%{gopath}
%endif

make %{?_smp_mflags} build docs

%install
install -d -p %{buildroot}%{_bindir}
make DESTDIR=%{buildroot} install

# source code for building projects
%if 0%{?with_devel}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
echo "%%dir %%{gopath}/src/%%{import_path}/." >> devel.file-list
# find all *.go but no *_test.go files and generate devel.file-list
for file in $(find . -iname "*.go" \! -iname "*_test.go") ; do
    echo "%%dir %%{gopath}/src/%%{import_path}/$(dirname $file)" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> devel.file-list
done
%endif

# testing files for this project
%if 0%{?with_unit_test} && 0%{?with_devel}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
# find all *_test.go files and generate unit-test.file-list
for file in $(find . -iname "*_test.go"); do
    echo "%%dir %%{gopath}/src/%%{import_path}/$(dirname $file)" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> unit-test-devel.file-list
done
%endif

%if 0%{?with_devel}
sort -u -o devel.file-list devel.file-list
%endif

%check
%if 0%{?with_check} && 0%{?with_unit_test} && 0%{?with_devel}
%if ! 0%{?with_bundled}
export GOPATH=%{buildroot}%{gopath}:%{gopath}
%else
export GOPATH=%{buildroot}%{gopath}:$(pwd)/Godeps/_workspace:%{gopath}
%endif

%endif

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%files
%license LICENSE
%doc %{name}.1.md README.md
%config(noreplace) %{_sysconfdir}/%{name}.conf
%dir %{_libexecdir}/oci
%dir %{_libexecdir}/oci/hooks.d
%{_libexecdir}/oci/hooks.d/%{name}
%{_mandir}/man1/%{name}.1*

%if 0%{?with_devel}
%files devel -f devel.file-list
%license LICENSE
%doc %{name}.1.md README.md
%dir %{gopath}/src/%{provider}.%{provider_tld}/%{project}
%endif

%if 0%{?with_unit_test} && 0%{?with_devel}
%files unit-test-devel -f unit-test-devel.file-list
%license LICENSE
%doc %{name}.1.md README.md
%endif

%changelog
* Thu Aug 25 2016 Lokesh Mandvekar <lsm5@redhat.com> - 1:0-1.8.gitaf6c129
- Resolves: #1370289 - ship config file to enable/disable
oci-register-machine
- built commit af6c129

* Tue Jul 12 2016 Lokesh Mandvekar <lsm5@redhat.com> - 1:0-1.7.git31bbcd2
- remove obsoletes

* Tue Jul 12 2016 Lokesh Mandvekar <lsm5@redhat.com> - 1:0-1.6.git31bbcd2
- build with golang >= 1.6.2

* Tue Jul 05 2016 Lokesh Mandvekar <lsm5@redhat.com> - 1:0-1.5.git31bbcd2
- Obsoletes the subpackage earlier provided by docker

* Thu Jun 30 2016 Lokesh Mandvekar <lsm5@redhat.com> - 1:0-1.4.git31bbcd2
- Bump Epoch to 1 so that it can obsolete same subpackage from docker

* Tue Jun 28 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0-1.3.git31bbcd2
- use latest commit (builds successfully for RHEL)

* Thu Jun 23 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0-1.2.git7d4ce65
- spec cleanup

* Wed Apr 20 2016 Daniel Walsh <dwalsh@redhat.com> - 0-1-1.git7d4ce65
- Add requires for systemd-machined systemd unit file

* Sat Mar 26 2016 Daniel Walsh <dwalsh@redhat.com> - 1-0.2.git7d4ce65
-  Fix logging format patch from Andy Goldstein

* Mon Feb 22 2016 Daniel Walsh <dwalsh@redhat.com> - 1-0.1
- Initial Release

* Thu Nov 19 2015 Sally O'Malley <somalley@redhat.com> - 0-0.1.git6863
- First package for Fedora
