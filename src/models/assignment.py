from dataclasses import dataclass, field
from typing import List

from models.project import Project
from models.contributor import Contributor


@dataclass
class Assignment:
    project: Project
    contributors: List[Contributor] = field(default_factory=list)
