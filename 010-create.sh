#!/bin/bash
set -e

success=false
trap check_finish EXIT
check_finish() {
  if [ $success = true ]; then
    echo '>>>' success
  else
    echo "FAILED"
  fi
}

all="vpc_tf"

# no parameters run all tf directories.  one parameter start at the provided dir.
case $# in
  0) tf="$all";;
  1) tf=$(expr " $all " : '.*\( '"$1"' .*\)');;
  *) echo starting_point; exit 0;;
esac

echo directories: $tf

for dir in $tf; do
  (
    cd $dir
    echo '>>>' "creating resources with terraform in the $dir/ directory"
    terraform init
    terraform apply -auto-approve
  )
done

success=true
