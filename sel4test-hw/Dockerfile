# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

# The context of this Dockerfiles is the repo root (../)

ARG WORKSPACE=/workspace

FROM trustworthysystems/sel4-riscv

RUN pip3 install junitparser strip-ansi

COPY sel4test-hw/steps.sh \
     scripts/checkout-manifest.sh \
     scripts/fetch-branch.sh \
     scripts/repo-util \
     /usr/bin/

WORKDIR /usr/bin
RUN chmod a+rx checkout-manifest.sh fetch-branch.sh repo-util steps.sh

RUN mkdir /builds
COPY sel4test-hw/builds.yml \
     sel4test-hw/build.py \
     seL4-platforms/platforms.yml \
     seL4-platforms/platforms.py \
     seL4-platforms/builds.py \
     /builds/

ARG WORKSPACE
RUN mkdir -p ${WORKSPACE}
WORKDIR ${WORKSPACE}

ENTRYPOINT steps.sh
