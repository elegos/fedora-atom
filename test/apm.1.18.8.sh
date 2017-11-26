#!/usr/bin/env bash

# Tests directory
cd `dirname "${BASH_SOURCE[0]}"`
# Root directory
cd ..

RPM_FILE="apm-1.18.8-1.fc27.x86_64.rpm"
RPM_PATH="`pwd`/build/RPMS/x86_64/${RPM_FILE}"

if ! [ -f "${RPM_PATH}" ]; then
  echo "You need to compile the package before"
  exit 1
fi

# Fedora 27
docker run --rm -ti \
  --user 0 \
  --volume "`pwd`/build/RPMS/x86_64:/rpms" \
  fedora:27 \
  bash -c "cd /rpms && dnf install -y ${RPM_FILE}"