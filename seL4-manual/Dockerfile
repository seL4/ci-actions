# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

# The context of this Dockerfiles is the repo root (../)

ARG WORKSPACE=/workspace

FROM trustworthysystems/sel4:latest

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       doxygen \
       texlive \
       texlive-fonts-extra \
       texlive-latex-extra \
    && apt-get clean autoclean \
    && apt-get autoremove --yes \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/

COPY seL4-manual/steps.sh \
     scripts/checkout.sh \
     /usr/bin/

WORKDIR /usr/bin
RUN chmod a+rx checkout.sh steps.sh

ARG WORKSPACE
RUN mkdir -p ${WORKSPACE}
WORKDIR ${WORKSPACE}

ENTRYPOINT steps.sh
