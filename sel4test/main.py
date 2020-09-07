#!/usr/bin/env python3

from Platform import *


rpi3 = Platform(arch = ARCH.ARM, can32Bit = True)
sabre   = Platform(
                arch = ARCH.ARM,
                platform = "sabre",
                imagePlatform = "imx6",
                can32SMP = True,
                can32Bit = True,
                simulationBinary = "sabre",
                march = "armv7a")

haswell   = Platform(
                arch = ARCH.X86,
                platform = "x86_64",
                can32SMP = True,
                can32Bit = True,
                can64SMP = True,
                can64Bit = True,
                simulationBinary = "x86",
                march = "nehalem")

hifive = Platform(
          arch = ARCH.RISCV,
          can64Bit = True,
          platform = "hifive",
          march = "rv64imac")

platforms = [rpi3, sabre, haswell, hifive]


