# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

# The context of this Dockerfiles is the repo root (../)

ARG WORKSPACE=/workspace

FROM trustworthysystems/sel4-riscv

COPY --from=sel4/cparser-builder /c-parser /c-parser

COPY cparser-run/steps.sh \
     scripts/checkout-manifest.sh \
     scripts/fetch-branch.sh \
     /usr/bin/

WORKDIR /usr/bin
RUN chmod a+rx checkout-manifest.sh fetch-branch.sh steps.sh

RUN mkdir /builds
COPY cparser-run/builds.yml \
     cparser-run/build.py \
     seL4-platforms/platforms.yml \
     seL4-platforms/platforms.py \
     /builds/

ARG WORKSPACE
RUN mkdir -p ${WORKSPACE}
WORKDIR ${WORKSPACE}

ENTRYPOINT steps.sh
