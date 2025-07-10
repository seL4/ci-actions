# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

default: build

IMG=sel4/link-check:latest

build:
	docker build -t $(IMG) -f Dockerfile ..

push: build
	docker push $(IMG)

test: build
	docker run -ti --entrypoint bash -e GITHUB_REPOSITORY -e GITHUB_REF \
	  -e INPUT_DIR -e INPUT_EXCLUDE -e INPUT_EXCLUDE_URLS -e INPUT_TIMEOUT \
		-e INPUT_DOC_ROOT -e INPUT_NUM_REQUESTS -e INPUT_TOKEN -e INPUT_VERBOSE \
		-e GITHUB_TOKEN $(IMG)
