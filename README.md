# Version data and metadata for host-os projects #

This repository contains metadata to build the projects at the open-power-host-os
namespace.
It also contains additional data necessary to create the software packages.

As new features are introduced in the projects at open-power-host-os new tags will
be added here to establish a valid and tested set of software versions to build.

The list of the latest packages and their versions is present at:
https://open-power-host-os.github.io/latest

## Supported GNU/Linux distributions ##

* CentOS 7.3 PPC64LE

## Installation ##
The Builds project, at https://github.com/open-power-host-os/builds uses this
repository automatically by cloning it and doing a git checkout in the tag
refered in its configuration file.

## Release package

The release package (`open-power-host-os-release`) takes care
of system-wide configurations. It places a file at
`/etc/open-power-host-os-release` indicating the current
OpenPOWER Host OS version. It also prepares the POWER system
for KVM virtualization, by disabling simultaneous multi-threading
and creating necessary preset files.

## Packages groups

We have "metapackages" that require the installation of certain sets of
related packages. All of those also install the
[`open-power-host-os-release`](#release-package) package.

The packages installed by each metapackage are as follows:

- open-power-host-os-all
  - open-power-host-os-base
  - open-power-host-os-container
  - open-power-host-os-ras
  - open-power-host-os-virt
  - open-power-host-os-virt-management
  - gcc
  - golang-github-russross-blackfriday
  - golang-github-shurcooL-sanitized_anchor_name
  - golang

- open-power-host-os-base
  - open-power-host-os-release
  - kernel

- open-power-host-os-container
  - open-power-host-os-base
  - docker
  - docker-swarm
  - flannel
  - kubernetes

- open-power-host-os-ras
  - open-power-host-os-base
  - crash
  - hwdata
  - libnl3
  - librtas
  - libservicelog
  - libvpd
  - lshw
  - lsvpd
  - ppc64-diag
  - servicelog
  - sos
  - systemtap

- open-power-host-os-virt
  - open-power-host-os-base
  - SLOF
  - libvirt
  - qemu

- open-power-host-os-virt-management
  - open-power-host-os-base
  - open-power-host-os-virt
  - novnc
  - ginger
  - ginger-base
  - kimchi
  - wok
