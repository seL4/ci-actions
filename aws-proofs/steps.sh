#!/bin/bash
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

# The GitHub action mostly starts up an AWS instance and hands over to there.
# For now we keep an active ssh session during the test so that we get live
# logs.

if [ "${GITHUB_EVENT_NAME}" = "pull_request_target" ] ||
   [ "${GITHUB_EVENT_NAME}" = "pull_request" ]
then
  echo "::group::PR info"
  pip3 install -U PyGithub
  export INPUT_EXTRA_PRS="$(get-prs)"
  echo "::endgroup::"
fi

echo "::group::AWS"
# fail on any error
set -e

aws configure set default.region us-east-2
aws configure set default.output json

echo "Starting AWS instance..."
aws ec2 run-instances --launch-template "LaunchTemplateName=l4v-runner" --count 1 > instance.txt

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

# Prime GH runner with VM ssh host key. This does not gain any actual security,
# because we have nothing to verify the key against. It only makes ssh/scp less chatty.
mkdir -p ~/.ssh
ssh-keyscan -t ecdsa ${IP} 2> /dev/null >> ~/.ssh/known_hosts

if [ "${GITHUB_EVENT_NAME}" = "pull_request_target" ]
then
  GITHUB_REF=${GH_HEAD_SHA}
fi

echo "::endgroup::"

export INPUT_CI_BRANCH=master

ssh -o SendEnv=INPUT_CI_BRANCH \
    -o SendEnv=INPUT_L4V_ARCH \
    -o SendEnv=INPUT_MANIFEST \
    -o SendEnv=INPUT_ISA_BRANCH \
    -o SendEnv=INPUT_SESSION \
    -o SendEnv=INPUT_CACHE_BUCKET \
    -o SendEnv=INPUT_CACHE_NAME \
    -o SendEnv=INPUT_CACHE_READ \
    -o SendEnv=INPUT_CACHE_WRITE \
    -o SendEnv=INPUT_SKIP_DUPS \
    -o SendEnv=INPUT_TOKEN \
    -o SendEnv=INPUT_XML \
    -o SendEnv=INPUT_EXTRA_PRS \
    -o SendEnv=GITHUB_REPOSITORY \
    -o SendEnv=GITHUB_REF \
    -o SendEnv=GITHUB_BASE_REF \
    -o SetEnv=GITHUB_WORKSPACE=/home/test-runner \
    test-runner@${IP} ./run

# leave logs on GitHub runner for later artifact upload
scp test-runner@${IP}:logs.tar.xz .

# instance termination is in post-steps.sh
