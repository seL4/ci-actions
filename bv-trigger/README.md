<!--
  Copyright 2023 Kry10 Limited
  SPDX-License-Identifier: BSD-2-Clause
-->

# Trigger binary verification

Can be called from an l4v proof workflow run to trigger binary verification.

This works by issuing a repository-dispatch event on the graph-refine
repository, but only if there is kernel-build artifact available. The event
starts a graph-refine binary-decompilation workflow run, which retrieves kernel
build artifacts from the l4v proof workflow and runs the decompiler.

The final stage of binary verification, graph refinement, is not directly
triggered here, but may triggered by the completion of the graph-refine
binary-decompilation workflow. Graph refinement is performed by a custom back
end. It is expensive, so policy settings in the back end may be used to limit
which decompilation runs actually proceed to graph refinement. The `tag` input
be used in that policy decision.

## Example usage

The following example includes a per-architecture matrix job that:
- Runs `aws-proofs`, which saves kernel builds to `artifacts/kernel-builds`, but
  only if proofs performed SimplExportAndRefine, which is needed by binary
  verification.
- Uses `actions/upload-artifact` to create a `kernel-builds` artifact in the
  current workflow. We use `if-no-files-found: ignore` because the kernel builds
  will only be present if the proofs included SimplExportAndRefine.

Note that all jobs in the matrix upload to the same `kernel-builds` artifact,
but this does not cause a conflict, because uploads are prefixed with a path
that depends on the architecture name.

Once all proof jobs in the matrix are finished, we can use the `bv-trigger`
action in a dependent job. `bv-trigger` will look for the `kernel-builds`
artifact. If the artifact is present, `bv-trigger` will issue a
`repository-dispatch` event on the `graph-refine` repository, starting a
decompilation workflow.

```yaml
jobs:
  proofs:
    name: Proofs
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        arch: [ARM, ARM_HYP, AARCH64, RISCV64, X64]
    steps:
      - name: Proofs
        uses: seL4/ci-actions/aws-proofs@master
        with:
          L4V_ARCH: ${{ matrix.arch }}
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_SSH: ${{ secrets.AWS_SSH }}
      - name: Upload kernel builds
        uses: actions/upload-artifact@v3
        with:
          name: kernel-builds
          path: artifacts/kernel-builds
          if-no-files-found: ignore

  binary-verification:
    name: Trigger binary verification
    needs: proofs
    steps:
      - name: Trigger binary verification
        uses: seL4/ci-actions/bv-trigger@master
        with:
          token: ${{ secrets.PRIV_REPO_TOKEN }}
          tag: l4v/example-tag
```
