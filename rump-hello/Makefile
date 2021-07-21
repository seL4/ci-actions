# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

default: build

IMG=sel4/rump-hello:latest

build:
	docker build -t $(IMG) -f Dockerfile ..

push: build
	docker push $(IMG)

run: build
	docker run -e GITHUB_REPOSITORY -e GITHUB_REF \
	  -e GITHUB_WORKSPACE -e INPUT_ARCH -e INPUT_MARCH -e INPUT_MODE \
		-e INPUT_COMPILER -e INPUT_DEBUG -e INPUT_MATRIX -e INPUT_NAME \
		-e INPUT_REQ $(IMG)

test: build
	docker run -ti --entrypoint bash -e GITHUB_REPOSITORY -e GITHUB_REF \
	  -e GITHUB_WORKSPACE -e INPUT_ARCH -e INPUT_MARCH -e INPUT_MODE \
		-e INPUT_COMPILER -e INPUT_DEBUG -e INPUT_MATRIX -e INPUT_NAME \
		-e INPUT_REQ \
		-v $(shell pwd):/mnt:z $(IMG)
