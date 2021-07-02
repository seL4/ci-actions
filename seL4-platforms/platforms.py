# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse and represent platform and build definitions.

This module contains two main classes, Platform and Build, which represent
test platforms and build definitions respectively. Use VerBuild for build
definitions with setting VERIFICATION=TRUE.

The main data for both is represented in yaml files, see platforms.yml and
(for instance) cparser-run/builds.yml for examples.

The module loads platforms.yml on init, which includes available architectures,
modes, platforms, a list of unsupported platforms, and a list of named machines.
"""

from io import StringIO
from typing import Optional
from pprint import pprint
import yaml
import os

# exported names:
__all__ = [
    "Platform", "PlatformValidationException", "Build", "VerBuild"
    "load_builds", "load_ver_builds",
    "all_architectures", "all_modes", "platforms", "unsupported", "machines"
]


class PlatformValidationException(Exception):
    """Raised when a platform definition contains inconsistent or incomplete yaml data"""
    pass


class Platform:
    """Represents a build platform.

    See platforms.yml for a list of required and optional fields.
    """

    def __init__(self, name: str, **entries: dict):
        """Construct a Platform object from a yaml dictionary.

        See platforms.yml for examples, and validate() for constraints.
        """
        self.name = name
        self.smp = []
        self.aarch_hyp = []
        self.image_platform = None
        self.simulation_binary = None
        self.march = None
        self.req = None
        self.disabled = False
        self.__dict__.update(entries)
        if not self.validate():
            raise PlatformValidationException

    def validate(self) -> bool:
        """Validate the fields of this object for type and invariants"""

        def sublist(sub, container):
            # not exactly efficient, but we are talking lists of length < 5 here:
            if not isinstance(sub, list):
                return False
            for x in sub:
                if not x in container:
                    return False
            return True

        def mode_list(modes):
            return sublist(modes, all_modes)

        def opt_str(name):
            return name == None or isinstance(name, str)

        return isinstance(self.name, str) and \
            self.arch in all_architectures and \
            mode_list(self.modes) and len(self.modes) > 0 and \
            mode_list(self.smp) and \
            mode_list(self.aarch_hyp) and \
            opt_str(self.image_platform) and \
            opt_str(self.simulation_binary) and \
            opt_str(self.march) and \
            opt_str(self.req) and \
            isinstance(self.disabled, bool)

    def __repr__(self):
        """Return a string representation of this object."""

        # This is not quite sufficient for parsing, but good enough for debugging.
        result = StringIO()
        result.writelines([s+"\n" for s in [
            "{",
            f"    name: {self.name},",
            f"    arch: {self.arch},",
            f"    modes: {self.modes}",
            f"    smp: {self.smp}",
            f"    aarch_hyp: {self.aarch_hyp}",
            f"    image_platform: {self.image_platform}",
            f"    simulation_binary: {self.simulation_binary}",
            f"    march: {self.march}",
            f"    req: {self.req}",
            f"    disabled: {self.disabled}",
            "  }"
        ]])
        return result.getvalue()

    def can_32(self) -> bool:
        """Does the platform support 32 bit execution?"""
        return 32 in self.modes

    def can_64(self) -> bool:
        """Does the platform support 64 bit execution?"""
        return 64 in self.modes

    def can_smp_32(self) -> bool:
        """Does the platform support SMP in mode 32?"""
        return 32 in self.smp

    def can_smp_64(self) -> bool:
        """Does the platform support SMP in mode 64?"""
        return 64 in self.smp

    def can_aarch_hyp_32(self) -> bool:
        """Does the platform support ARM_HYP in mode 32?"""
        return 32 in self.aarch_hyp

    def can_aarch_hyp_64(self) -> bool:
        """Does the platform support ARM_HYP in mode 64?"""
        return 64 in self.aarch_hyp

    def get_mode(self) -> Optional[int]:
        """Return mode (32/64) of this platform if unique, otherwise None"""
        if len(self.modes) == 1:
            return self.modes[0]
        else:
            return None

    def get_platform(self, mode: int) -> str:
        """Return platform string, including for x86"""
        if self.arch == "x86":
            return {32: "ia32", 64: "x86_64"}[mode]
        else:
            return self.platform

    def toolchain_arch_str(self) -> str:
        """Return toolchain string for arm/riscv"""
        return {"arm": "AARCH", "riscv": "RISCV"}.get(self.arch, "")

    def cmake_toolchain_setting(self, mode: int) -> str:
        return self.toolchain_arch_str() + str(mode)

    def get_image_platform(self, mode: int) -> str:
        return self.image_platform or self.get_platform(mode)

    def get_triple(self, mode: int) -> str:
        """Return toolchain prefix triple"""
        return {"x86":   {32: "x86_64-linux-gnu",
                          64: "x86_64-linux-gnu"},
                "arm":   {32: "arm-linux-gnueabi",
                          64: "aarch64-linux-gnu"},
                "riscv": {32: "riscv32-linux-gnu",
                          64: "riscv64-linux-gnu"}}[self.arch][mode]

    def image_names(self, mode: int, root_task: str) -> list:
        """Return generated image name"""
        im_plat = self.get_image_platform(mode)
        return {
            'arm':   [f"images/{root_task}-image-arm-{im_plat}"],
            'x86':   [f"images/kernel-{im_plat}-pc99",
                      f"images/{root_task}-image-{im_plat}-pc99"],
            'riscv': [f"images/{root_task}-image-riscv-{im_plat}"],
        }[self.arch]


class Build:
    """Represents a build definition.

    Currently, this is mainly a name and a platform, with mode if not determined
    by platform, and optional build settings.

    See cparser-run/builds.yml for examples.
    """

    def __init__(self, **entries):
        """Construct a Build from yaml dictionary, with default build settings."""
        self.mode = None
        self.settings = {}
        [self.name] = entries.keys()
        attribs = entries[self.name]
        self.__dict__.update(**attribs)

        p = self.get_platform()
        m = self.get_mode()
        if p.arch != "x86":
            self.settings[p.cmake_toolchain_setting(m)] = "TRUE"
        self.settings["PLATFORM"] = p.get_platform(m)
        # somewhat misnamed now; sets test output to parsable xml:
        self.settings["BAMBOO"] = "TRUE"
        self.files = p.image_names(m, "sel4test-driver")

    def set_verification(self):
        """Make this a verification build"""
        self.settings["VERIFICATION"] = "TRUE"

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


class VerBuild(Build):
    """A verification build definition."""

    def __init__(self, **entries):
        """Construct a Build object and set verification to true."""
        super().__init__(**entries)
        self.set_verification()


def load_yaml(file_name):
    """Load a yaml file"""
    return yaml.safe_load(open(file_name, 'r'))


def yaml_builds(file_name):
    """Return the 'builds' entry of a yaml file"""
    return load_yaml(file_name)["builds"]


def load_builds(file_name):
    """Load a yaml file as a list of Build objects"""
    return [Build(**b) for b in yaml_builds(file_name)]


def load_ver_builds(file_name):
    """Load a yaml file as a list of VerBuild objects"""
    return [VerBuild(**b) for b in yaml_builds(file_name)]


# module init:
_yaml_platforms = load_yaml(os.path.dirname(__file__) + "/platforms.yml")

all_architectures = _yaml_platforms["architectures"]
all_modes = _yaml_platforms["modes"]

platforms = {name: Platform(name, **plat)
             for (name, plat) in _yaml_platforms["platforms"].items()}

mcs_unsupported = _yaml_platforms["mcs_unsupported_platforms"]
for p in mcs_unsupported:
    if not platforms.get(p):
        print(f"Warning: unknown platform '{p}' in mcs_unsupported list")

machines = _yaml_platforms["machines"]

# if called as main, dump info:
if __name__ == '__main__':
    print("\n# Architectures:")
    pprint(all_architectures)

    print("\n# Modes:")
    pprint(all_modes)

    print("\n# Platforms:")
    pprint(platforms)

    print("\n# Unsupported:")
    pprint(mcs_unsupported)

    print("\n# Machines:")
    pprint(machines)

    def sup(p: Platform) -> str:
        return p.name + (" (unsupported)" if p.name in mcs_unsupported else "")

    for arch in all_architectures:
        print(f"\n# all {arch}:")
        pprint([sup(p) for p in platforms.values() if p.arch == arch])

    print("\n# all sim:")
    pprint([p.name for p in platforms.values() if p.simulation_binary])
