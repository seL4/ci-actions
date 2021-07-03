# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

# The context of this Dockerfiles is the repo root (../)

ARG WORKSPACE=/workspace

FROM trustworthysystems/sel4-riscv

COPY --from=sel4/cparser-builder /c-parser /c-parser

COPY preprocess/make_munge.sh \
     preprocess/test_munge.sh \
     preprocess/steps.sh \
     scripts/checkout-manifest.sh \
     scripts/fetch-pr.sh \
     scripts/repo-util \
     /usr/bin/

WORKDIR /usr/bin
RUN chmod a+rx make_munge.sh test_munge.sh checkout-manifest.sh repo-util steps.sh

ARG WORKSPACE
RUN mkdir -p ${WORKSPACE}
WORKDIR ${WORKSPACE}

ENTRYPOINT steps.sh
