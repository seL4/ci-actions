#!/bin/bash
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

# The GitHub action mostly starts up an AWS and hands over to there. For now we
# keep an active ssh session during the test so that we get live logs.

echo "::group::AWS"
# fail on any error
set -e

aws configure set default.region us-east-2
aws configure set default.output json

echo "Starting AWS instance..."
aws ec2 run-instances --image-id ami-02109a93a0bf86295 --count 1 \
                      --instance-type c5.4xlarge \
                      --iam-instance-profile "Name=test-runner-role" \
                      --security-group-ids sg-0491b450a86520294 \
                      --instance-market-options "MarketType=spot" \
                      --instance-initiated-shutdown-behavior terminate > instance.txt

ID=$(cat instance.txt | jq -r '.Instances[0].InstanceId')

echo "Instance ID: ${ID}"
echo "Pending, waiting for instance to be up..."

aws ec2 wait instance-running --instance-ids ${ID}

echo "Instance is running."

IP=$(aws ec2 describe-instances --instance-ids ${ID} | \
     jq -r '.Reservations[0].Instances[0].PublicIpAddress')

echo "IP address ${IP}"
if [ -z ${IP} ]; then exit 1; fi

echo "Waiting for sshd to come up"
until nc -w5 -z ${IP} 22; do echo "."; sleep 3; done

eval $(ssh-agent)
ssh-add -q - <<< "${AWS_SSH}"

if [ "${GITHUB_EVENT_NAME}" = "pull_request_target" ]
then
  GH_REF=${GH_HEAD_SHA}
else
  GH_REF=${GITHUB_REF}
fi

echo "::endgroup::"

CI_BRANCH=master

ssh -o StrictHostKeyChecking=no test-runner@${IP} \
    "bash -c \"export INPUT_L4V_ARCH=${INPUT_L4V_ARCH}; \
               export INPUT_MANIFEST=${INPUT_MANIFEST}; \
               export INPUT_ISA_BRANCH=${INPUT_ISA_BRANCH}; \
               export INPUT_SESSION=${INPUT_SESSION}; \
               export INPUT_CACHE_NAME=${INPUT_CACHE_NAME}; \
               export INPUT_CACHE_READ=${INPUT_CACHE_READ}; \
               export INPUT_CACHE_WRITE=${INPUT_CACHE_WRITE}; \
               export INPUT_SKIP_DUPS=${INPUT_SKIP_DUPS}; \
               export GITHUB_REPOSITORY=${GITHUB_REPOSITORY}; \
               export GITHUB_REF=${GH_REF}; \
               export GITHUB_BASE_REF=${GITHUH_BASE_REF}; \
               export GITHUB_WORKSPACE=/home/test-runner; \
               ./run ${CI_BRANCH}\""

# leave logs on GitHub runner for later artifact upload
scp test-runner@${IP}:logs.tar.xz .

# instance termination is in post-steps.sh
