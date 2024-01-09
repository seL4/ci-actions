# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

ARG WORKSPACE=/workspace
ARG SCRIPTS=/ci-scripts
ARG ACTION=camkes-vm

FROM sel4/camkes-vm:latest

ARG ACTION
ARG SCRIPTS

COPY steps.sh ${SCRIPTS}/
RUN chmod a+rx ${SCRIPTS}/*

COPY builds.yml \
     build.py \
     seL4-platforms/platforms.yml \
     seL4-platforms/platforms.py \
     seL4-platforms/builds.py \
     /builds/

ARG WORKSPACE
RUN mkdir -p ${WORKSPACE}
WORKDIR ${WORKSPACE}

ENTRYPOINT /ci-scripts/steps.sh
