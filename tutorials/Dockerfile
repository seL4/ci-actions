# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

# The context of this Dockerfiles is the repo root (../)

ARG WORKSPACE=/workspace

FROM trustworthysystems/camkes:latest

RUN pip3 install junitparser

COPY tutorials/steps.sh \
     scripts/checkout-manifest.sh \
     scripts/fetch-branch.sh \
     scripts/repo-util \
     /usr/bin/

WORKDIR /usr/bin
RUN chmod a+rx checkout-manifest.sh fetch-branch.sh repo-util steps.sh

RUN mkdir /builds
COPY tutorials/builds.yml \
     tutorials/build.py \
     seL4-platforms/platforms.yml \
     seL4-platforms/platforms.py \
     seL4-platforms/builds.py \
     /builds/

RUN mkdir -p /github/home

ARG WORKSPACE
RUN mkdir -p ${WORKSPACE}
WORKDIR ${WORKSPACE}

ENTRYPOINT steps.sh
