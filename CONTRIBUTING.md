<!--
     Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)

     SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Contributions Welcome!

Contributions to this repository are welcome!

There are plenty of additional actions that could be added, and there is
probably a lot that could be optimised and done more nicely.

See [open issues][issues] for things than need work. There is also a list of
[good first issues][first-issues] if you are new to all this and want to get
involved.

If you have any enhancements, fixes, or additions, do feel encouraged to
raise a pull request or file a new issue.

[issues]: https://github.com/seL4/ci-actions/issues?q=is%3Aopen+is%3Aissue+no%3Aassignee
[first-issues]: https://github.com/seL4/ci-actions/issues?q=is%3Aopen+is%3Aissue+no%3Aassignee+label%3A%22good+first+issue%22


## Build/Test

To try out any of the GitHub actions in this repo, you can usually follow the
example in the corresponding `README.md` file, add the action to a workflow
file in your own repository, and perform the action that triggers it, e.g. a
pull request or push to a branch in your repository.

New CI actions can be a bit hard to test. As much as possible and makes sense,
any new actions should be added to the CI suite of this repository and/or tested
with a pull request to one of the repositories they are targeted for.

For example, to test a new pull request action, e.g. `link-check`, on a
feature branch `link`, you would add a separate commit with a change to 
`.github/workflows/pr.yml` that looks somewhat like this:

```yaml
  shell:
    name: 'Link Check'
    runs-on: ubuntu-latest
    steps:
    - uses: seL4/ci-actions/link-check@link
```

and raise a pull request. If the action performs as intended on that PR, the
branch `@link` can be changed to `@master` or whatever else is appropriate.


## Developer Certificate of Origin (DCO)

This repository uses the same sign-off process as the Linux kernel. For every
commit, use

    git commit -s

to add a sign-off line to your commit message, which will come out as:

    Signed-off-by: name <email>

By adding this line, you make the declaration that you have the right to make
this contribution under the open source license the files use that you changed
or contributed.

The full text of the declaration is at <https://developercertificate.org>.


## Contact

The seL4 repositories are managed by the [Technical Steering Committee][TSC]
of the [seL4 Foundation][seL4F], helped by people in [additional
roles][roles] for the Foundation in the [seL4 GitHub org][seL4org].

<https://sel4.systems/contact/> has information on mailing lists, forum, and
chat to get in touch with developers and users.

The main author of the CI actions in this repository is [Gerwin Klein][GK], [@lsf37][lsf37] on GitHub.

[TSC]: https://sel4.systems/Foundation/TSC/
[seL4F]: https://sel4.systems/Foundation/
[roles]: https://docs.sel4.systems/processes/roles.html
[seL4org]: https://github.com/orgs/seL4/teams
[GK]: https://doclsf.de/
[lsf37]: https://github.com/lsf37
