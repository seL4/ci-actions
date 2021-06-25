# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

# ---[ sel4/cparser-builder ]---
#
# Builder container for the l4v standalone C parser
# see the preprocess action for an example how to use

# The context of this Dockerfiles is the repo root (../)

ARG WORKSPACE=/workspace

FROM trustworthysystems/sel4

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       mlton \
    && apt-get clean autoclean \
    && apt-get autoremove --yes \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/

COPY scripts/checkout-manifest.sh /usr/bin/
RUN chmod a+rx /usr/bin/checkout-manifest.sh

ARG WORKSPACE
RUN mkdir -p ${WORKSPACE}
WORKDIR ${WORKSPACE}

RUN checkout-manifest.sh

ARG CPARSER_DIR=${WORKSPACE}/l4v/tools/c-parser
WORKDIR ${CPARSER_DIR}
RUN make standalone-cparser

ARG CP_DEST=/c-parser/standalone-parser
RUN mkdir -p ${CP_DEST}
WORKDIR ${CP_DEST}
ARG CP_SRC=${CPARSER_DIR}/standalone-parser
RUN cp ${CP_SRC}/c-parser .
RUN cp -r ${CP_SRC}/ARM ${CP_SRC}/ARM_HYP ${CP_SRC}/RISCV64 ${CP_SRC}/X64 .
