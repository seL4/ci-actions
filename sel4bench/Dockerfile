# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

# The context of this Dockerfiles is the repo root (../)

ARG WORKSPACE=/workspace
ARG SCRIPTS=/ci-scripts
ARG ACTION=sel4bench

FROM trustworthysystems/sel4:latest

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libffi-dev \
    && apt-get clean autoclean \
    && apt-get autoremove --yes \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/
RUN pip3 install junitparser PyGithub

ARG SCRIPTS
ARG ACTION
RUN mkdir ${SCRIPTS}
COPY ${ACTION}/steps.sh scripts/* ${SCRIPTS}/
RUN chmod a+rx ${SCRIPTS}/*
ENV  PATH "${SCRIPTS}:${PATH}"

RUN mkdir /builds
COPY ${ACTION}/builds.yml \
     ${ACTION}/build.py \
     seL4-platforms/platforms.yml \
     seL4-platforms/platforms.py \
     seL4-platforms/builds.py \
     /builds/

ARG WORKSPACE
RUN mkdir -p ${WORKSPACE}
WORKDIR ${WORKSPACE}

ENTRYPOINT steps.sh
