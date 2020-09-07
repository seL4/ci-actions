#!/usr/bin/env python3

from dataclasses import dataclass
from enum import Enum, auto

class MODE(Enum):
    MODE_32 = auto()
    MODE_64 = auto()

class ARCH(Enum):
    X86 =   lambda m : "x86_64-linux-gnu" if m is MODE.MODE_32 else "x86_64-linux-gnu" 
    ARM =   lambda m : "arm-linux-gnueabi" if m is MODE.MODE_32 else "aarch64-linux-gnu" 
    RISCV = lambda m : "riscv32-linux-gnu" if m is MODE.MODE_32 else "riscv64-linux-gnu" 

@dataclass
class Platform:
    arch : ARCH
    platform : str = None
    imagePlatform : str = None
    march : str = None
    simulationBinary : str = None
    can32SMP : bool = False
    can64SMP : bool = False
    can32Bit : bool = False
    can64Bit : bool = False
    canAarch32Hyp : bool = False
    canAarch64Hyp : bool = False
    disabled : bool = False

    def getTriple(self, mode : MODE):
        return self.arch(mode)

    def getImageNames(self, mode : MODE, rootTaskName : str):
        imageNames = []
        plat = self.getImagePlatform(mode)
        if self.arch is ARCH.ARM:
            imageNames.append( f"images/{rootTaskName}-image-arm-{plat}" )
        elif self.arch is ARCH.X86:
            imageNames.append( f"images/kernel-{plat}-pc99" )
            imageNames.append( f"images/{rootTaskName}-image-{plat}-pc99" )
        elif self.arch is ARCH.RISCV:
            imageNames.append( f"images/{rootTaskName}-image-riscv-{plat}" )
        return imageNames
        
    def getPlatform(self, mode: MODE):
        if self.arch is ARCH.X86:
            return self.getPC99Platform(mode)
        else:
            return self.platform

    def getPC99Platform(self, mode: MODE):
        if mode is MODE.MODE_32:
            return "ia32"
        elif mode is MODE.MODE_64:
            return "x86_64"
        else:
            raise ValueError("Invalid PC99 mode")

    def getModeString(self, mode : MODE):
        if self.arch is not ARCH.X86:
            if mode is MODE.MODE_32:
                return "32"
            elif mode is MODE.MODE_64:
                return "64"
        else:
            return ""

    def getImagePlatform(self, mode : MODE):
        if self.arch is ARCH.X86:
            return self.getPC99Platform(mode)
        elif not self.imagePlatform:
            return self.getPlatform(mode)
        else:
            return self.imagePlatform



