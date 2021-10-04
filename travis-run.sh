#!/bin/bash
export TRAVIS_JOB_ID=57286535

  docker run -i --volume $PWD:/root/mnt/home --workdir /root/mnt/home \
    --env TRAVIS=true \
    --env TF_VAR_ibmcloud_api_key \
    --env TF_VAR_basename=travis-3tier-$TRAVIS_JOB_ID \
    --env TF_VAR_region=us-south \
    --env TF_VAR_resource_group_name=3tier \
    --env TF_VAR_ssh_key_name="pfq" \
    l2fprod/ibmcloud-ci all.sh
