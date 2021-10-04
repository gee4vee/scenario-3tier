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

# same all as in 010-create, reverse it
all="vpc_tf"
tf=$(echo "$all" | awk '{ for (i=NF; i>1; i--) printf("%s ",$i); print $1; }')

# destroy the buckets in reverse order
for dir in $tf; do
  (
    cd $dir
    echo '>>>' "destroy resources with terraform in the $dir/ directory"
    if [ -e terraform.tfstate ]; then
      terraform destroy -auto-approve
    fi
  )
done

success=true
