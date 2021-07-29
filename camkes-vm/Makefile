# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

default: build

IMG=sel4/camkes-vm:latest

build:
	docker build -t $(IMG) -f Dockerfile ..

push: build
	docker push $(IMG)

run: build
	docker run --rm -e GITHUB_REPOSITORY -e GITHUB_REF \
	  -e GITHUB_WORKSPACE -e INPUT_ARCH -e INPUT_MARCH -e INPUT_MODE \
		-e INPUT_COMPILER -e INPUT_DEBUG -e INPUT_MATRIX -e INPUT_NAME \
		-e INPUT_REQ -e INPUT_PLATFORM $(IMG)

# pass in a dummy HOME directory to simulate GitHub changing HOME
test: build
	docker run --rm -ti --entrypoint bash -e GITHUB_REPOSITORY -e GITHUB_REF \
	  -e GITHUB_WORKSPACE -e INPUT_ARCH -e INPUT_MARCH -e INPUT_MODE \
		-e INPUT_COMPILER -e INPUT_DEBUG -e INPUT_MATRIX -e INPUT_NAME \
		-e INPUT_REQ -e INPUT_PLATFORM -e HOME=/tmp \
		-v $(shell pwd):/mnt:z $(IMG)
