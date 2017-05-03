# Version data and metadata for host-os projects #

This repository contains metadata to build the projects at the open-power-host-os
namespace.
It also contains additional data necessary to create the software packages.

As new features are introduced in the projects at open-power-host-os new tags will
be added here to establish a valid and tested set of software versions to build.

## Supported GNU/Linux distributions ##

* CentOS 7.3 PPC64LE

## Installation ##
The Builds project, at https://github.com/open-power-host-os/builds uses this
repository automatically by cloning it and doing a git checkout in the tag
refered in its config.yaml.

## Supported Packages and versions ##

<table>
  <thead>
    <th>Software</th>
    <th>Version</th>
  </thead>
  <tbody>
    <tr>
      <td>SLOF</td>
      <td>20170303</td>
    </tr>
    <tr>
      <td>crash</td>
      <td>7.1.6</td>
    </tr>
    <tr>
      <td>docker-swarm</td>
      <td>1.1.0</td>
    </tr>
    <tr>
      <td>docker</td>
      <td>1.12.2</td>
    </tr>
    <tr>
      <td>flannel</td>
      <td>0.5.5</td>
    </tr>
    <tr>
      <td>gcc</td>
      <td>4.8.5</td>
    </tr>
    <tr>
      <td>ginger-base</td>
      <td>2.2.1</td>
    </tr>
    <tr>
      <td>ginger</td>
      <td>2.3.0</td>
    </tr>
    <tr>
      <td>golang-github-russross-blackfriday</td>
      <td>1.2</td>
    </tr>
    <tr>
      <td>golang-github-shurcooL-sanitized_anchor_name</td>
      <td>0</td>
    </tr>
    <tr>
      <td>golang</td>
      <td>1.7.1</td>
    </tr>
    <tr>
      <td>hwdata</td>
      <td>0.288</td>
    </tr>
    <tr>
      <td>kernel</td>
      <td>4.11.0</td>
    </tr>
    <tr>
      <td>kimchi</td>
      <td>2.3.0</td>
    </tr>
    <tr>
      <td>kubernetes</td>
      <td>1.2.0</td>
    </tr>
    <tr>
      <td>libnl3</td>
      <td>3.2.28</td>
    </tr>
    <tr>
      <td>librtas</td>
      <td>1.4.1</td>
    </tr>
    <tr>
      <td>libservicelog</td>
      <td>1.1.16</td>
    </tr>
    <tr>
      <td>libvirt</td>
      <td>3.2.0</td>
    </tr>
    <tr>
      <td>libvpd</td>
      <td>2.2.5</td>
    </tr>
    <tr>
      <td>lshw</td>
      <td>B.02.18</td>
    </tr>
    <tr>
      <td>lsvpd</td>
      <td>1.7.7</td>
    </tr>
    <tr>
      <td>novnc</td>
      <td>0.5.1</td>
    </tr>
    <tr>
      <td>ppc64-diag</td>
      <td>2.7.2</td>
    </tr>
    <tr>
      <td>qemu</td>
      <td>2.9.0</td>
    </tr>
    <tr>
      <td>servicelog</td>
      <td>1.1.14</td>
    </tr>
    <tr>
      <td>sos</td>
      <td>3.3</td>
    </tr>
    <tr>
      <td>systemtap</td>
      <td>3.1</td>
    </tr>
    <tr>
      <td>wok</td>
      <td>2.3.0</td>
    </tr>
  </tbody>
</table>

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
