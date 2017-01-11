%global provider        github
%global provider_tld    com
%global project         projectatomic
%global repo            oci-systemd-hook
# https://github.com/projectatomic/oci-systemd-hook
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     %{provider_prefix}
%global commit          41491a3c73193527487fb502026d41d3f0aad1aa
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

Name:           oci-systemd-hook
Epoch:          1
Version:        0.1.4
Release:        4.git%{shortcommit}%{?dist}
Summary:        OCI systemd hook for docker
Group:          Applications/Text
License:        GPLv3+
URL:            https://%{import_path}
Source0:        %{repo}.tar.gz

BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  pkgconfig(yajl)
BuildRequires:  pkgconfig(libselinux)
BuildRequires:  pkgconfig(mount)
BuildRequires:  go-md2man

%description
OCI systemd hooks enable running systemd in a OCI runc/docker container.

%prep
%setup -q -n %{repo}

%build
aclocal
autoreconf -i
%configure --libexecdir=%{_libexecdir}/oci/hooks.d/
make %{?_smp_mflags}

%install
%make_install

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%files
%doc README.md
%license LICENSE
%{_mandir}/man1/oci-systemd-hook.1*
%dir %{_libexecdir}/oci
%dir %{_libexecdir}/oci/hooks.d
%{_libexecdir}/oci/hooks.d/oci-systemd-hook

%changelog
* Thu Jun 30 2016 Lokesh Mandvekar <lsm5@redhat.com> - 1:0.1.4-4.git41491a3
- Bump Epoch to 1 so that it can obsolete subpackage from docker

* Tue Jun 28 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0.1.4-3.git41491a3
- re-add provider_prefix since gofed needs it

* Thu Jun 23 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0.1.4-2.git41491a3
- built commit 41491a3
- spec file cleanup
- remove provider_prefix and only use import_path

* Thu Feb 18 2016 Dan Walsh <dwalsh@redhat.com> - 0.1.4-1.gitde345df
- Fix up to prepare for review

* Mon Nov 23 2015 Mrunal Patel <mrunalp@gmail.com> - 0.1.3
- Fix bug in man page installation

* Mon Nov 23 2015 Mrunal Patel <mrunalp@gmail.com> - 0.1.2
- Add man pages

* Mon Nov 23 2015 Mrunal Patel <mrunalp@gmail.com> - 0.1.1
- Initial RPM release
