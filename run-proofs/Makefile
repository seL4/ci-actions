# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

default: build

IMG=sel4/run-proofs:latest

build:
	docker build -t $(IMG) -f Dockerfile ..

push: build
	docker push $(IMG)

test: build
	docker run -ti --entrypoint bash -e GITHUB_REPOSITORY -e GITHUB_REF \
	  -e GITHUB_SHA -e INPUT_SESSION -e INPUT_ISA_BRANCH  -e INPUT_MANIFEST \
		-e GITHUB_WORKSPACE -e INPUT_L4V_ARCH -e GITHUB_BASE_REF $(IMG)
