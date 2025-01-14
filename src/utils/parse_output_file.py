from models.result import Result

def parse_second_output_file(result: Result, file_name: str) -> None:
    with open(file_name, "w") as f:
        f.write(f"{len(result.assignments)}\n")
        for assignment in result.assignments:
            f.write(f"{assignment.project.name}\n")
            f.write(" ".join(contributor.name for contributor in assignment.contributors) + "\n")