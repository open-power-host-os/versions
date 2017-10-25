# OpenPOWER Host OS packages metadata

This repository contains metadata to build the projects at the open-power-host-os
namespace.
It also contains additional data necessary to create the software packages.

The [builds](https://github.com/open-power-host-os/builds) project
uses this repository automatically by cloning it and doing a git
checkout in the tag referred in its configuration file.

As new features are introduced in the projects at open-power-host-os new tags will
be added here to establish a valid and tested set of software versions to build.

The list of the latest packages and their versions is present at:
https://open-power-host-os.github.io/latest

## Supported GNU/Linux distributions

* CentOS 7.4 PPC64LE

## Additional information

For convenience, this repository also provides a release package and
packages groups:

### Release package

The release package (`open-power-host-os-release`) takes care
of system-wide configurations. It places a file at
`/etc/open-power-host-os-release` indicating the current
OpenPOWER Host OS version. It also prepares the POWER system
for KVM virtualization, by disabling simultaneous multi-threading
and creating necessary systemd preset files.

### Package groups

A set of related packages is grouped into a "metapackage". They should be installed 
like normal packages (not using the prefix `@` in yum). The list of 
metapackages is the following:

* open-power-host-os-all

* open-power-host-os-base

* open-power-host-os-container

* open-power-host-os-ras

* open-power-host-os-virt

To see a complete list of which packages are installed by each group, refer to 
[open-power-host-os/CentOS/7/open-power-host-os.spec](open-power-host-os/CentOS/7/open-power-host-os.spec)
file in this repository.
