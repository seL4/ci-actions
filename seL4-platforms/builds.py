# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse and represent build definitions.

The Build class represents build definitions.

Use `load_builds` to load a build list from a yaml file, `run_builds` to run
them, `run_build_script` for a standard test driver frame, and
`default_junit_results` for a standard place to leave a jUnit summary file.
"""

from platforms import ValidationException, Platform, platforms, load_yaml, mcs_unsupported

from typing import Optional
from io import StringIO
from junitparser import JUnitXml
from strip_ansi import strip_ansi

import copy
import os
import shutil
import subprocess
import sys

# exported names:
__all__ = [
    "Build", "load_builds", "run_builds", "run_build_script", "default_junit_results"
]

# where to expect jUnit results by default
default_junit_results = 'results.xml'


class Build:
    """Represents a build definition.

    Currently, this is mainly a name and a platform, with mode if not determined
    by platform, and optional build settings.

    See cparser-run/builds.yml for examples.
    """

    def __init__(self, entries: dict, default={}):
        """Construct a Build from yaml dictionary. Accept optional default build attributes."""
        self.mode = None
        self.settings = {}
        [self.name] = entries.keys()
        attribs = copy.deepcopy(default)
        # this potentially overwrites the default settings dict, we restore it later
        attribs.update(entries[self.name])
        self.__dict__.update(**attribs)

        if 'settings' in default:
            for k, v in default['settings'].items():
                if not k in self.settings:
                    self.settings[k] = v

        p = self.get_platform()
        m = self.get_mode()
        if p.arch != "x86":
            self.settings[p.cmake_toolchain_setting(m)] = "TRUE"
        self.settings["PLATFORM"] = p.get_platform(m)
        # somewhat misnamed now; sets test output to parsable xml:
        self.settings["BAMBOO"] = "TRUE"
        self.files = p.image_names(m, "sel4test-driver")

    def get_platform(self) -> Platform:
        """Return the Platform object for this build definition."""
        return platforms[self.platform]

    def get_mode(self) -> Optional[int]:
        """Return the mode (32/64) for this build; taken from platform if not defined"""
        if not self.mode and self.get_platform().get_mode():
            return self.get_platform().get_mode()
        else:
            return self.mode

    def settings_args(self):
        """Return the build settings as an argument list [-Dkey=val]"""
        return [f"-D{key}={val}" for (key, val) in self.settings.items()]

    def set_verification(self):
        """Make this a verification build"""
        self.settings["VERIFICATION"] = "TRUE"

    def is_verification(self) -> bool:
        return self.settings.get("VERIFICATION") != None

    def can_release(self):
        # Bamboo excludes RELEASE for RPI3:
        return not self.get_platform().name == 'RPI3'

    def set_release(self):
        if not self.can_release():
            raise ValidationException("not Build.can_release()")
        self.settings["RELEASE"] = "TRUE"

    def is_release(self) -> bool:
        return self.settings.get("RELEASE") != None

    def is_debug(self) -> bool:
        return not self.is_release() and not self.is_verification()

    def can_hyp(self) -> bool:
        # Bamboo config says no MCS for arm_hyp 64 yet, and
        # no VTX for SMP or verification
        return not (
            self.get_mode() == 64 and self.get_platform().arch == 'arm' and self.is_mcs() or
            self.get_platform().name == 'PC99' and (self.is_smp() or self.is_verification())
        ) and (
            self.get_platform().name == 'PC99' or
            self.get_mode() in self.get_platform().aarch_hyp
        )

    def set_hyp(self):
        if not self.can_hyp():
            raise ValidationException("not Build.can_hyp()")

        if self.get_mode() in self.get_platform().aarch_hyp:
            self.settings['ARM_HYP'] = "TRUE"
        elif self.get_platform().name == 'PC99':
            self.settings['KernelVTX'] = "TRUE"
        else:
            # should be unreachable because of self.can_hyp():
            raise ValidationException

    def is_hyp(self) -> bool:
        return self.settings.get("ARM_HYP") != None or self.settings.get("KernelVTX") != None

    def can_clang(self) -> bool:
        # clang 8 does not support riscv, and Bamboo has no clang for TX1 64:
        return not (
            self.get_platform().arch == 'riscv' or
            self.get_platform().name == 'TX1' and self.get_mode() == 64
        )

    def set_clang(self):
        if not self.can_clang():
            raise ValidationException("not Build.can_clang()")
        self.settings["TRIPLE"] = self.get_platform().get_triple(self.get_mode())

    def is_clang(self) -> bool:
        return self.settings.get("TRIPLE") != None

    def is_gcc(self) -> bool:
        return not self.is_clang()

    def can_mcs(self) -> bool:
        # Bamboo config says no MCS from arm_hyp 64 yet, and
        # no MCS for debug+SMP on x86_64
        return not (
            self.get_platform().name in mcs_unsupported or
            self.get_mode() == 64 and self.is_hyp() and self.get_platform().arch == 'arm' or
            self.get_platform().name == 'PC99' and self.get_mode() == 64 and not self.is_release() and self.is_smp()
        )

    def set_mcs(self):
        if not self.can_mcs():
            raise ValidationException("not Build.can_mcs()")
        self.settings['MCS'] = "TRUE"

    def is_mcs(self) -> bool:
        return self.settings.get('MCS') != None

    def can_smp(self) -> bool:
        return self.get_mode() in self.get_platform().smp

    def set_smp(self) -> bool:
        if not self.can_smp():
            raise ValidationException("not Build.can_smp()")
        self.settings['SMP'] = "TRUE"

    def is_smp(self) -> bool:
        return self.settings.get('SMP') != None

    def validate(self):
        if not self.get_mode():
            raise ValidationException("Build: no unique mode")
        if not self.get_platform():
            raise ValidationException("Build: no platform")
        if self.is_clang() and not self.can_clang():
            raise ValidationException("not Build.can_clang()")
        if self.is_mcs() and not self.can_mcs():
            raise ValidationException("not Build.can_mcs()")
        if self.is_smp() and not self.can_smp():
            raise ValidationException("not Build.can_smp()")
        if self.is_release() and not self.can_release():
            raise ValidationException("not Build.can_release()")
        if self.is_hyp() and not self.can_hyp():
            raise ValidationException("not Build.can_hyp()")

    def __repr__(self) -> str:
        return \
            f"Build('{self.name}': " '{' \
            f"'platform': {self.platform}, 'mode': {self.get_mode()}, 'settings': {self.settings}" '})'


def run(args: list):
    """Echo + run command with arguments; raise exception on exit != 0"""

    print("+++ " + " ".join(args))
    # Print output as it arrives. Some of the build commands take too long to
    # wait until all output is there. Keep stderr separate, but flush it.
    process = subprocess.Popen(args, text=True, stdout=subprocess.PIPE,
                               stderr=sys.stderr, bufsize=1)
    for line in process.stdout:
        print(line.rstrip())
        sys.stdout.flush()
        sys.stderr.flush()
    ret = process.wait()
    if not ret == 0:
        raise subprocess.CalledProcessError(ret, args)


def summarise_junit(file_path: str) -> bool:
    """Parse jUnit output and show a summary.

    Preprocesses input to increase the chances of getting valid XML.
    Returns True if there were no failures or errors, raises exception
    on IOError or XML parse errors."""

    with open(file_path, 'r') as file:
        # Skip log text before and after the XML, escape some of the test output to get valid XML
        lines = StringIO()
        take = False
        for line in file:
            if line.strip() == '<testsuite>':
                take = True
            if take:
                lines.write(line.replace('<<', '&lt;&lt;'))
            if line.strip() == "</testsuite>":
                break

        xml = JUnitXml.fromstring(strip_ansi(lines.getvalue()))

        print("")
        print("Test summary")
        print("------------")
        print(f"tests:    {xml.tests}")
        print(f"skipped:  {xml.skipped}")
        print(f"failures: {xml.failures}")
        print(f"errors:   {xml.errors}\n")

        return xml.failures == 0 and xml.errors == 0


def run_build_script(manifest_dir: str, name: str, script: list, junit: bool = False, junit_file: str = default_junit_results) -> bool:
    """Run a build script in a separate `build/` directory

    A build script is a list of commands, which itself is a list of command and
    arguments passed to subprocess.run().

    The build stops at the first failing step (or the end) and fails if any
    step fails.
    """

    print(f"::group::{name}")
    print(f"-----------[ start test {name} ]-----------")

    os.chdir(manifest_dir)

    build_dir = 'build'
    try:
        shutil.rmtree(build_dir)
    except IOError:
        pass

    os.mkdir(build_dir)
    os.chdir(build_dir)

    success = True
    try:
        for line in script:
            run(line)
    except subprocess.CalledProcessError:
        success = False

    if success and junit:
        try:
            success = summarise_junit(junit_file)
        except IOError:
            print(f"Error reading {junit_file}")
            success = False
        except:
            print(f"Error parsing {junit_file}")
            success = False

    print("SUCCESS" if success else "FAILED")
    print(f"-----------[ end test {name} ]-----------\n")
    print("::endgroup::")

    return success


def list_mult(xs: list, ys: list) -> list:
    """Cross product of two lists. The first list is expected to be a list of lists.
    Returns a list of lists.

    `list_mult([[a],[b]], [c,d]) == [[a,c], [a,d], [b,c], [b,d]]`
    """
    combinations = []
    for x in xs:
        for y in ys:
            combinations.append(x + [y])
    return combinations


def variants(var_dict: dict) -> list:
    """Generate the matrix (=list of lists) of all variants in a variant dict."""

    keys = list(var_dict.keys())
    if keys == []:
        return []

    all = [[(keys[0], v)] for v in var_dict[keys[0]]]
    for k in keys[1:]:
        all = list_mult(all, [(k, v) for v in var_dict[k]])

    return all


def variant_name(variant):
    """Return the naming postfix for a build variant."""
    return "_".join([str(v) for _, v in variant if v != ''])


def get_build_for_variant(platform, variant, default={}, filter_fun=lambda x: True):
    """Make a build definition from a supplied platform and a build variant.

    Optionally takes a dict of defaults and a filter/validation function to
    set default attributes and and build settings, and to reject specific
    build settings combinations respectively."""

    var_dict = dict(variant)
    mode = default.get("mode") or var_dict.get("mode")
    if mode and not mode in platform.modes:
        return None
    mode = mode or platform.get_mode()
    if not mode:
        return None

    the_build = copy.deepcopy(default)
    the_build["mode"] = mode
    the_build["platform"] = platform.name
    build = Build({platform.name+"_"+variant_name(variant): the_build})

    try:
        for feature, val in variant:
            if feature == 'mcs' and val != '':
                build.set_mcs()
            elif feature == 'smp' and val != '':
                build.set_smp()
            elif feature == 'hyp' and val != '':
                build.set_hyp()
            elif feature == 'debug' and val == 'release':
                build.set_release()
            elif feature == 'debug' and val == 'verification':
                build.set_verification()
            elif feature == 'debug' and val not in ['debug', 'verification', 'release']:
                print(f"Warning: ignoring unknown setting {feature}: {val}")
                raise ValidationException
            elif feature == 'compiler' and val == 'clang':
                build.set_clang()
            else:
                pass
        build.validate()
    except ValidationException:
        return None

    if filter_fun(build):
        return build
    else:
        return None


def filtered(build: Build, build_filters: dict) -> Optional[Build]:
    """Return build if build matches filter criteria, otherwise None."""

    def match_dict(build, f):
        """Return true if all criteria in the filter are true for this build."""
        for k, v in f.items():
            if k == 'arch':
                if not build.get_platform().arch in v:
                    return False
            elif k == 'march':
                if not build.get_platform().march in v:
                    return False
            elif k == 'platform':
                if not build.get_platform().platform in v:
                    return False
            elif k == 'debug':
                if not build.is_debug():
                    return False
            elif k == 'compiler':
                if build.is_clang():
                    if not 'clang' in v:
                        return False
                else:
                    if not 'gcc' in v:
                        return False
            elif k == 'mode':
                if build.get_mode() not in v:
                    return False
            elif k == 'mcs':
                if v != '' and not build.is_mcs():
                    return False
            elif k == 'smp':
                if v != '' and not build.is_smp():
                    return False
            elif k == 'hyp':
                if v != '' and not build.is_hyp():
                    return False
            elif not vars(build.get_platform()).get(k):
                return False
        return True

    if not build:
        return None

    if not build_filters or build_filters == []:
        return build

    for f in build_filters:
        if match_dict(build, f):
            return build

    return None


def load_builds(file_name: str, filter_fun=lambda x: True) -> list:
    """Load a list of build definitions from yaml.

    Applies defaults, variants, and build-filter from the yaml file.
    Takes an optional filtering function for removing unwanted builds."""

    yml = load_yaml(file_name)

    default_build = yml.get("default", {})
    build_filters = yml.get("build-filter", [])
    all_variants = variants(yml.get("variants", {}))
    yml_builds = yml.get("builds", [])

    if yml_builds == []:
        builds = []
        for p in platforms.keys():
            for v in all_variants:
                build = filtered(get_build_for_variant(
                    platforms[p], v, default_build, filter_fun), build_filters)
                if build:
                    builds.append(build)
    else:
        # TODO: would be nice to apply variants to base builds, not only platforms
        if all_variants != []:
            print("Warning: ignoring variants for explicit build list.")

        builds = [Build(b, default_build) for b in yml_builds]

    return builds


def run_builds(builds: list, run_fun) -> int:
    """Run a list of build definitions, given a test driver function.

    Expects the current directory to be a manifest directory, in which
    tests are started (usually creating `build/` directory and running there).

    The driver function `run_fun` should take a directory (manifest dir)
    and a Build, and run this build, returning true iff the build was successful.
    """

    manifest_dir = os.getcwd()
    successes = []
    fails = []
    for build in builds:
        (successes if run_fun(manifest_dir, build) else fails).append(build.name)

    print("Successful tests: " + ", ".join(successes))
    if fails != []:
        print("FAILED tests: " + ", ".join(fails))

    return 0 if fails == [] else 1
