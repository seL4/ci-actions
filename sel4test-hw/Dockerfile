# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

ARG WORKSPACE=/workspace
ARG SCRIPTS=/ci-scripts
ARG ACTION=sel4test-hw

FROM sel4/sel4test-hw:latest

ARG SCRIPTS
ARG ACTION

COPY steps.sh ${SCRIPTS}/
RUN chmod a+rx ${SCRIPTS}/*

COPY builds.yml \
     build.py \
     seL4-platforms/platforms.yml \
     seL4-platforms/platforms.py \
     seL4-platforms/builds.py \
     /builds

ARG WORKSPACE
WORKDIR ${WORKSPACE}

ENTRYPOINT /ci-scripts/steps.sh
