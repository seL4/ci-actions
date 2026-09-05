#!/bin/bash
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

# Always terminate AWS instance at end of action

echo "::group::Terminating AWS instance"

ACTION_DIR="${SCRIPTS}/../${INPUT_ACTION_NAME}"
AWS_RETRY="${ACTION_DIR}/aws-retry.sh"

ID=$(cat instance.txt | jq -r '.Instances[0].InstanceId')
echo "Instance ID: ${ID}"

# terminate-instances is rate limited on AWS, so needs to be under retry.
"${AWS_RETRY}" aws ec2 terminate-instances --instance-ids ${ID}
status=$?

if [ ${status} -ne 0 ]; then
  echo "::error::Could not terminate AWS instance ${ID}, it may still be running"
fi

echo "::endgroup::"

exit ${status}
