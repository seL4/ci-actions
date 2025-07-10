# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

# ---[ sel4/cparser-builder ]---
#
# Builder container for the l4v standalone C parser
# see the preprocess action for an example how to use

# The context of this Dockerfiles is the repo root (../)

ARG WORKSPACE=/workspace
ARG CP_DEST=/c-parser/standalone-parser

FROM trustworthysystems/sel4:latest AS builder

COPY scripts/checkout-manifest.sh /usr/bin/
RUN chmod a+rx /usr/bin/checkout-manifest.sh

ARG SCRATCH=/scrach
ARG MLTON=mlton-20241230-1.amd64-linux.ubuntu-24.04_static
WORKDIR ${SCRATCH}
RUN apt update && apt install -y libgmp-dev
RUN wget https://github.com/MLton/mlton/releases/download/on-20241230-release/${MLTON}.tgz
RUN tar xvfz ${MLTON}.tgz
ENV PATH=${SCRATCH}/${MLTON}/bin:$PATH

ARG WORKSPACE
RUN mkdir -p ${WORKSPACE}
WORKDIR ${WORKSPACE}

RUN checkout-manifest.sh

ARG CPARSER_DIR=${WORKSPACE}/l4v/tools/c-parser
WORKDIR ${CPARSER_DIR}
RUN L4V_ARCH=ARM make cparser_tools

ARG CP_DEST
RUN mkdir -p ${CP_DEST}
WORKDIR ${CP_DEST}
ARG CP_SRC=${CPARSER_DIR}/standalone-parser
RUN cp ${CP_SRC}/c-parser .
RUN cp -r ${CP_SRC}/ARM ${CP_SRC}/ARM_HYP ${CP_SRC}/AARCH64 ${CP_SRC}/RISCV64 ${CP_SRC}/X64 .

FROM scratch
ARG CP_DEST
COPY --from=builder ${CP_DEST} ${CP_DEST}
