from typing import List

from models.result import Result
from models.contributor import Contributor

def parse_output_file(result: Result, file_name: str, contributors: List[Contributor]) -> None:
    with open(file_name, "w") as f:
        f.write(f"{len(result.assignments)}\n")
        for project in result.assignments:
            f.write(f"{project.name}\n")
            f.write(" ".join(contributor.name for contributor in contributors 
            if contributor in project.assignments.values()) + "\n")

def parse_second_output_file(result: Result, file_name: str) -> None:
    with open(file_name, "w") as f:
        f.write(f"{len(result.assignments)}\n")
        for assignment in result.assignments:
            f.write(f"{assignment.project.name}\n")
            f.write(" ".join(contributor.name for contributor in assignment.contributors) + "\n")
            # if contributor in assignment.project.assignments.values()) + "\n")