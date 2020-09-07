#!/usr/bin/env python3
from dataclasses import dataclass, field
from Platform import *

@dataclass
class BuildDefinition:

    dockerImage : str = None
    cMakeSettings : dict = field(default_factory=dict)
    jobName : str = None
    scriptName : str = "../init-build.sh"
    platform : Platform = None
    disabled : bool = False

    commands : list = field(default_factory=list)
    mode : MODE = MODE.MODE_32


    def getBuildStep(self, ninjaCommand : str = "ninja", postBuildCommands : list = None):
        def commentStep(comment : str):
            return f"# {comment}"
        cmds = []
        if not postBuildCommands:
            postBuildCommands = []

        cmakeInit = f"{self.scriptName} "
        cmakeInit += " ".join([ f"-D{k}={v}" for k, v in self.cMakeSettings.items()])

        cmds.append(commentStep("Set up and build"))
        cmds.append("rm -rf build")
        cmds.append("mkdir build")
        cmds.append("cd build")
        cmds.append(commentStep("Init CMake"))
        cmds.append(cmakeInit)
        cmds.append(ninjaCommand)
        cmds.extend(postBuildCommands)

        return "\n".join(cmds)

    def putSetting(setting : str, value : str):
        self.cMakeSettings[setting] = value

    def getSetting(setting : str):
        return self.cMakeSettings[setting]

    def hasSetting(setting : str):
        return setting in self.cMakeSettings.keys()
