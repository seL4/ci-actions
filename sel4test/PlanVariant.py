from dataclasses import dataclass, field
from typing import Callable
from copy import deepcopy
from BuildDefinition import BuildDefinition

@dataclass
class PlanVariant:
    setting : str = None
    value : str = None
    nameExt : str = None
    altNameExt : str = None
    validator : Callable[[BuildDefinition], bool] = lambda _ : True
    essential : bool = False

    def addVariation(template_buildDef : BuildDefinition, variants : list):
        if self.validator(template_buildDef):
            if not essential:
                new_var = deepcopy(template_buildDef)
                self.apply_changes(new_var)
            else:
                self.apply_changes(new_var)

        if self.altNameExt:
            build_definition.jobName += f"-{self.altNameExt}"

    def apply_changes(build_definition : BuildDefinition):
        build_definition.putSetting(self.setting, self.value)
        build_definition.jobName += f"-{self.nameExt}"

    def makeVariants(template_buildDef : BuildDefinition, variants : list):
        print("hello")

        build_defs = []
        for v in variants:
            pass
        pass

