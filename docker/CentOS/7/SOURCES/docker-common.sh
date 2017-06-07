#!/bin/sh
. /etc/sysconfig/docker
[ -e "${DOCKERBINARY}" ] || DOCKERBINARY=/usr/bin/docker-current
if [ ! -f /usr/bin/docker-current ]; then
    DOCKERBINARY=/usr/bin/docker-latest
fi
if [[ ${DOCKERBINARY} != "/usr/bin/docker-current" && ${DOCKERBINARY} != /usr/bin/docker-latest ]]; then
    echo "DOCKERBINARY has been set to an invalid value:" $DOCKERBINARY
    echo ""
    echo "Please set DOCKERBINARY to /usr/bin/docker-current or /usr/bin/docker-latest
by editing /etc/sysconfig/docker"
else
    exec ${DOCKERBINARY} "$@"
fi
