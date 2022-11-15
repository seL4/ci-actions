# Copyright 2022, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

# The context of this Dockerfiles is the repo root (../)

ARG WORKSPACE=/workspace
ARG SCRIPTS=/ci-scripts
ARG ACTION=webserver

FROM trustworthysystems/camkes:latest

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       rubygems ruby-dev bundler doxygen \
    && apt-get clean autoclean \
    && apt-get autoremove --yes \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/
RUN gem install bundler:2.1.2
RUN pip3 install junitparser PyGithub

ARG ACTION
ARG SCRIPTS
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
