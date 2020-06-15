# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

# The context for this Dockerfile is the repo root

FROM sel4/liche:f57a5d1c5

RUN apk add git
COPY scripts/checkout.sh link-check/steps.sh /usr/bin/

ENTRYPOINT steps.sh
