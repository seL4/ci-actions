# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

default: build

IMG=sel4/cparser-run:latest

build:
	docker build -t $(IMG) -f Dockerfile ..

push: build
	docker push $(IMG)

run: build
	docker run -e GITHUB_REPOSITORY -e GITHUB_REF -e GITHUB_WORKSPACE $(IMG)

test: build
	docker run -ti --entrypoint bash -e GITHUB_REPOSITORY -e GITHUB_REF \
	  -e GITHUB_WORKSPACE $(IMG)
