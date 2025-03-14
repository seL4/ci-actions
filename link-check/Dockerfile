# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

# The context for this Dockerfile is the repo root

FROM lycheeverse/lychee:sha-85263df

RUN apt-get update
RUN apt-get install -y git curl
RUN curl -OL https://github.com/mikefarah/yq/releases/download/v4.45.1/yq_linux_386.tar.gz
RUN tar -xvf yq_linux_386.tar.gz ./yq_linux_386 && mv yq_linux_386 /usr/bin/yq && rm yq_linux_386.tar.gz
COPY scripts/checkout.sh link-check/steps.sh /usr/bin/

ENTRYPOINT steps.sh
