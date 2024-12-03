from dataclasses import dataclass
from typing import List
from skill import Skill

@dataclass
class Contributor:
    name: str
    skills: list[Skill]