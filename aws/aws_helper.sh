#!/bin/bash
#
# This is a simple helper that uses the 'aws' CLI to create and destroy EC2
# instances. I use this if I need a scratch instance quickly. It also includes
# a facility to delete all the auto-generated instances.
#
# TO USE THIS, YOU WILL HAVE TO CHANGE THE VALUES BELOW. You'll also have to
# set up the 'aws' CLI and create at least 1 security group, 1 subnet, and 1
# ssh key in EC2.

# ##### OPTIONS #####
# Project/user specific:
# Profile to use (this is probably 'default', if you do not have multiple
# profiles).
profile=admin
# Name of ssh key to add to new instances
key=remote-key
# Security group for instances
sg=sg-cc5241a9
# Subnet for instances
subnet=subnet-565bc86c

# Preferences:
# Amazon linux
ami=ami-b70554c8
# We don't use this, we just print a reminder.
ami_default_user=ec2-user
# 1 GB RAM, 1 VCPU
instance_type=t2.micro

# You shouldn't have to change this part.
# We set <tag_key>=true in the instance metadata, so we can find our own
# instances again.
tag_key=created_by_aws_helper
# ##### END OPTIONS #####

cmd=$1
if [[ $cmd != "start" && $cmd != "stop" && $cmd != "list" ]]; then
  echo "Invalid command '$cmd'. Usage:"
  echo "$0 start|stop|list"
  exit 2
fi

function do_start() {
  aws ec2 run-instances \
    --profile $profile \
    --image-id $ami \
    --count 1 \
    --instance-type $instance_type \
    --key-name $key \
    --security-group-ids $sg \
    --subnet-id $subnet \
    --tag-specifications "ResourceType=instance,Tags=[{Key=$tag_key,Value=true}]"
}

function do_list() {
  echo "Auto-launched instances. Default user: $ami_default_user"
  echo
  aws ec2 describe-instances \
    --profile $profile \
    --filter Name=tag:$tag_key,Values=true \
    --query 'Reservations[].Instances[].[InstanceId,State.Name,PublicIpAddress]' \
    --output text
}

function do_stop() {
  ids_json="$(aws ec2 describe-instances \
    --profile $profile \
    --filter Name=tag:$tag_key,Values=true \
    --query 'Reservations[].Instances[].InstanceId')"
  json=$(cat <<_END_
{
    "InstanceIds": $ids_json,
    "DryRun": false
}
_END_
)

	aws ec2 terminate-instances \
    --profile $profile \
    --cli-input-json "$json"
}

if [[ $cmd == "start" ]]; then
  do_start
  rc=$?
  if [[ $rc != 0 ]]; then
    echo 'aws ec2 launch-instances existed with an error.'
    exit $rc
  fi

  echo "Waiting 5 seconds for instance launch..."
  sleep 5

  do_list
elif [[ $cmd == "stop" ]]; then
  do_stop
elif [[ $cmd == "list" ]]; then
  do_list
fi
