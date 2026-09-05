#!/bin/bash
#
# Copyright 2026, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

# Run an AWS command, retry with backoff+jitter when throttled.
#
# Usage: aws-retry.sh <command line>

set -u

# Number of attempts before giving up.
ATTEMPTS=${AWS_RETRY_ATTEMPTS:-10}
# Delay in seconds before retry with exponential backoff up to AWS_RETRY_MAX_DELAY.
DELAY=${AWS_RETRY_DELAY:-15}
MAX_DELAY=${AWS_RETRY_MAX_DELAY:-120}

# AWS errors on which to retry.
RETRY='RequestLimitExceeded|Throttling|InsufficientInstanceCapacity|ServiceUnavailable|SlowDown'

ERR=$(mktemp)
trap 'rm -f "${ERR}"' EXIT

attempt=1
while true; do
  "$@" 2> "${ERR}"
  status=$?
  cat "${ERR}" >&2

  if [ ${status} -eq 0 ]; then
    exit 0
  fi

  if ! grep -Eq "${RETRY}" "${ERR}"; then
    exit ${status}
  fi

  if [ ${attempt} -ge "${ATTEMPTS}" ]; then
    echo "aws-retry: giving up after ${attempt} attempts" >&2
    exit ${status}
  fi

  # add jitter to restart in [DELAY/2, DELAY]
  half=$(( DELAY / 2 ))
  wait=$(( half + RANDOM % (half + 1) ))
  echo "aws-retry: attempt ${attempt} of ${ATTEMPTS} throttled, retrying in ${wait}s" >&2
  sleep ${wait}

  attempt=$(( attempt + 1 ))
  DELAY=$(( DELAY * 2 ))
  if [ ${DELAY} -gt "${MAX_DELAY}" ]; then
    DELAY=${MAX_DELAY}
  fi
done
