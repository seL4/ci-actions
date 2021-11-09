# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse and represent platform and build definitions.

The main class of this module is Platform, used to represent test platforms.

The main data is represented in the yaml file platforms.yml, see there for the
expect data format.

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
    "Platform", "ValidationException", "load_yaml",
    "all_architectures", "all_modes", "platforms", "unsupported", "machines"
]


class ValidationException(Exception):
    """Raised when a platform or build definition contains inconsistent or incomplete data"""

    def __init__(self, reason: str):
        self.reason = reason

    def __repr__(self) -> str:
        return f"ValidationException({self.reason})"


class Platform:
    """Represents a build platform.

    See platforms.yml for a list of required and optional fields.
    """

    def __init__(self, name: str, entries: dict):
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
        self.no_hw_build = False
        self.__dict__.update(**entries)
        if not self.validate():
            raise ValidationException(f"Platform {name} validation")

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
            (self.req == None or isinstance(self.req, str) or isinstance(self.req, list)) and \
            isinstance(self.disabled, bool) and \
            isinstance(self.no_hw_build, bool)

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
            f"    no_hw_build: {self.no_hw_build}",
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

    def getISA(self, mode: int) -> str:
        """Return the ISA for this platform"""

        if self.arch == "x86":
            return {32: "IA32", 64: "x86_64"}[mode]

        if self.arch == "riscv":
            return {32: "RC32IMAC", 64: "RV64IMAC"}[mode]

        return self.march.capitalize()


def load_yaml(file_name):
    """Load a yaml file"""
    with open(file_name, 'r') as file:
        return yaml.safe_load(file)


# module init:
_yaml_platforms = load_yaml(os.path.dirname(__file__) + "/platforms.yml")

all_architectures = _yaml_platforms["architectures"]
all_modes = _yaml_platforms["modes"]

platforms = {name: Platform(name, plat)
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
