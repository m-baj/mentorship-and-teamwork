from dataclasses import dataclass
from typing import List
import logging

from assignment import Assignment


LOGGER = logging.getLogger(__name__)


@dataclass
class Simulation:
    solution: List[Assignment]

    def run(self):
        day = 0
        while true:
            pass