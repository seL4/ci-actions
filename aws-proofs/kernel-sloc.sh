#!/bin/bash

# Copyright CSIRO
# SPDX-License-Identifier: BSD-2-Clause

# Estimate lines of code in preprocessed kernel.

KERNEL=l4v/spec/cspec/c/build/${L4V_ARCH}/kernel_all.c_pp

drop_multiline_comments() {
    sed -e '/^ *\/\*\([^*]\|\*[^/]\)*$/,/*\/ *$/ d' "$@"
}

drop_oneline_comments() {
    grep -v '^ */\*.*\*/ *$' "$@"
}

drop_cplusplus_comments() {
    grep -v '^ *//' "$@"
}

drop_PP_directives() {
    grep -v '^ *#' "$@"
}

drop_blank_lines() {
    grep -v '^ *\(;\)\?$' "$@"
}

trim_C_source() {
    drop_multiline_comments | \
    drop_oneline_comments | \
    drop_cplusplus_comments | \
    drop_PP_directives | \
    drop_blank_lines
}

if [ -e "$KERNEL" ]; then
    SLOC=$(trim_C_source < "$KERNEL" | wc -l)
else
    SLOC=N/A
fi

echo "SLOC measure for $KERNEL: $SLOC"
