# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

# The context of this Dockerfiles is the repo root (../)

ARG WORKSPACE=/workspace
ARG SCRIPTS=/ci-scripts
ARG ACTION=preprocess

FROM trustworthysystems/sel4:latest

COPY --from=sel4/cparser-builder /c-parser /c-parser

ARG ACTION
ARG SCRIPTS
RUN mkdir ${SCRIPTS}
COPY ${ACTION}/steps.sh ${ACTION}/make_munge.sh ${ACTION}/test_munge.sh \
     scripts/* ${SCRIPTS}/
RUN chmod a+rx ${SCRIPTS}/*
ENV  PATH "${SCRIPTS}:${PATH}"

ARG WORKSPACE
RUN mkdir -p ${WORKSPACE}
WORKDIR ${WORKSPACE}

ENTRYPOINT steps.sh
