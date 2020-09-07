#!/usr/bin/env python3

from Platform import *
from BuildDefinition import *
from PlanVariant import *

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

platforms = [sabre, haswell, hifive]

release = PlanVariant("RELEASE", "TRUE", "release", "debug")
verif   = PlanVariant("VERIFICATION", "TRUE", "verification", None, lambda bd : not bd.hasSetting("RELEASE"))
mcs     = PlanVariant("MCS", "TRUE", "mcs")
smp     = PlanVariant("SMP", "TRUE", "smp")
armHyp  = PlanVariant("ARM_HYP", "TRUE", "armhyp")
aarch32 = PlanVariant("AARCH32", "TRUE", "aarch32")
aarch64 = PlanVariant("AARCH64", "TRUE", "aarch32")


for p in [ p for p in platforms if p.arch is ARCH.ARM ]:
    if p.can32Bit:
        # This is an ordered list of variations
        variants = []


        clang = PlanVariant("TRIPLE", p.getTriple(MODE.MODE_32), "clang", "gcc")
        variants.append(clang)

        variants.append(aarch32)
        variants.append(mcs)

        if p.can32SMP:
            variants.append(smp)

        variants.append(release)

        if p.canAarch32Hyp:
            variants.append(armHyp)

        variants.append(verif)




        bd = BuildDefinition(
                dockerImage = "trustworthysystems/sel4",
                platform = p,
                mode = MODE.MODE_64,)

        bds = PlanVariant.makeVariants(bd, variants)

        print(p.imagePlatform, '\n\n', bd.getBuildStep(), '\n===========\n')
            
