# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

# The context for this Dockerfile is the repo root

FROM trustworthysystems/camkes:latest

COPY scripts/*.sh camkes-unit/steps.sh /usr/bin/

RUN mkdir /workspace
WORKDIR /workspace

ENTRYPOINT steps.sh
