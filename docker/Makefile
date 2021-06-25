# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

default: build

IMG=sel4/cparser-builder:latest

build:
	docker build -t $(IMG) -f cparser-builder.dockerfile ..

push: build
	docker push $(IMG)

test: build
	docker run -ti --entrypoint bash $(IMG)
