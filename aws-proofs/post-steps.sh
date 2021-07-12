#!/bin/bash
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

# Always terminate AWS instance at end of action

echo "::group::Terminating AWS instance"

ID=$(cat instance.txt | jq -r '.Instances[0].InstanceId')
echo "Instance ID: ${ID}"
aws ec2 terminate-instances --instance-ids ${ID}

echo "::endgroup::"
