Version data and metadata for host-os projects
***************************************************
This repository contains metadata to build the projects at the open-power-host-os
namespace.
It also contains additional data necessary to create the software packages.

As new features are introduced in the projects at open-power-host-os new tags will
be added here to establish a valid and tested set of software versions to build.

Supported GNU/Linux distributions
---------------------------------

* CentOS 7.2 PPC64LE

Installation
------------
The Builds project, at https://github.com/open-power-host-os/builds uses this
repository automatically by cloning it and doing a git checkout in the tag
refered in its config.yaml.

Supported Packages and versions
-------------------------------

======================                        ========
Software                                      Version
======================                        ========
SLOF                                          20160525
crash                                         7.1.6
docker                                        1.1.2
docker-swarm                                  1.1.0
flannel                                       0.5.5
gcc                                           4.8.5
ginger                                        2.3.0
ginger-base                                   2.2.1
golang                                        1.7.1
golang-github-shurcooL-sanitized_anchor_name  0-0.1
golang-github-russross-blackfriday            1.2-5
hwdata                                        0.288
iprutils                                      2.4.13
kernel                                        4.8.4
kimchi                                        2.3.0
librtas                                       1.4.1
libseccomp                                    2.3.1
libservicelog                                 1.1.16
libvirt                                       2.2.0
libvpd                                        2.2.5
linux-firmware                                20150904
lsvpd                                         1.7.7
novnc                                         0.5.1
oci-register-machine                          0-1.8
oci-systemd-hook                              0-1.8
powerpc-utils                                 1.3.2
ppc64-diag                                    2.7.1
qemu                                          2.7.0
servicelog                                    1.1.14
sos                                           3.3
systemtap                                     3.0.4
wok                                           2.3.0
======================                        ========
