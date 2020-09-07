#!/usr/bin/env python3
from dataclasses import dataclass
from Platform import MODE

@dataclass
class BuildDefinition:

    dockerImage : str = None
    cMakeSettings : dict = {}
    jobName : str = None
    scriptName : str = None
    platform = None
    mode : MODE
    disabled : bool = False

    commands = []


    def getBuildStep(self, ninjaCommand : str, postBuildCommands = None):
        def commentStep(self, comment):
            return f"# {comment}"
        cmds = []
        if not postBuildCommands:
            postBuildCommands = []

        cmakeInit = f"../{this.scriptName}"
        cmakeInit += " ".join([ f"-D{k}={v}" for k, v in cMakeSettings.items()])

        cmd.append(commentStep("Set up and build"))
        cmd.append("rm -rf build")
        cmd.append("mkdir build")
        cmd.append("cd build")
        cmd.append(commentStep("Init CMake"))
        cmd.append(cmakeInit)
        cmd.append(ninjaCommand)
        cmd.extend(postBuildCommands)



