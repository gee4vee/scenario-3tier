#!/bin/bash

set -ex

BASENAME=travis-3tier

success=false
trap check_finish EXIT
check_finish() {
  if [ $success = true ]; then
    echo '>>>' success
  else
    echo "FAILED"
  fi
}


if [ x$TF_VAR_resource_group_name = x ]; then
  echo TF_VAR_resource_group_name is not set, source local.env?
  exit 1
fi

this_dir=$(dirname "$0")
# source $this_dir/shared.sh

# It would be good to do the travis clean up in travis on failure... but for now lets do it from my desktop.
# can't use terraform - that state is all gone

instance_keys_rm(){
  local instance=$1
  keys_json=$(ibmcloud resource service-keys --instance-id $instance --output json)
  key_ids=$(jq -r '.[]|.guid' <<< "$keys_json")
  for key in $key_ids; do
    c="ibmcloud resource service-key-delete --force $key"
    echo $c
    $c
  done
}

vpc_names=$(ibmcloud is vpcs --output json | jq -r '.[]|select(.name|test("'$BASENAME'"))|.name')
for vpc_name in $vpc_names; do
  xvpc-cleanup.sh $vpc_name
done

instances=$(ibmcloud resource service-instances --output json | jq -r '.[]|select(.name|test("'$BASENAME'"))')
# instance_crns=$(ibmcloud resource service-instances --output json | jq -r '.[]|select(.name|test("'$BASENAME'"))|.id')
instance_crns=$(jq -r .'id' <<< "$instances")
instance_guids=$(jq -r .'guid' <<< "$instances")
for instance_guid in $instance_guids; do
  instance_keys_rm $instance_guid
done

for instance_crn in $instance_crns; do
  c="ibmcloud resource service-instance-delete -f $instance_crn"
  echo $c
  $c
done

success=true
