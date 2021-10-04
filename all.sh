#!/bin/bash
set -x
set -e
set -o pipefail
export TERRAFORM_NO_COLOR=-no-color
echo version 4
tfswitch
echo '>>>' testing

if [ x$TRAVIS = xtrue ]; then
  env
  pwd
  ls
  apk add python3
  python3 --version
  apk add py3-pip
  pip3 --version
  pip3 install pytest
  pytest --version
  pip3 install -r test/requirements.txt
fi
success=true
./000-prerequisites.sh
if ./010-create.sh; then
  if ! ./800-test.sh; then
    echo '>>>' 800-testt.sh failed
    success=false
  fi
fi
if ! ./900-cleanup.sh; then
  echo '>>>' 900-cleanup.sh failed
  success=false
fi
if [ x$success != xtrue ]; then
  exit 1
fi
