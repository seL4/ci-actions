# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

# The context for this Dockerfile is the repo root

FROM trustworthysystems/l4v-riscv

COPY scripts/*.sh run-proofs/steps.sh /usr/bin/

# For local testing, will be overriden by github runner
RUN mkdir /workspace
WORKDIR /workspace

ENTRYPOINT steps.sh
