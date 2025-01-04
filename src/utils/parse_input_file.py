from typing import TextIO, Tuple, List

from models.contributor import Contributor
from models.project import Project
from models.skill import Skill

def parse_input_file(file_path: str) -> Tuple[List[Contributor], List[Project]]:
    with open(file_path, 'r') as f:
        contributors_count, projects_count = map(int, f.readline().split())
        contributors = parse_contributors(f, contributors_count)
        projects = parse_projects(f, projects_count)
        return contributors, projects
        

def parse_contributors(file_handle: TextIO, contributors_count: int) -> List[Contributor]:
    contributors = []
    for i in range(contributors_count):
        name, skills_count = file_handle.readline().split()
        skills = parse_skills(file_handle, int(skills_count))
        contributors.append(Contributor(i, name, skills))
    return contributors 


def parse_projects(file_handle: TextIO, projects_count: int) -> List[Project]:
    projects = []
    for i in range(projects_count):
        name, days, score, best_before, roles_count = file_handle.readline().split()
        required_skills = parse_skills(file_handle, int(roles_count))
        projects.append(Project(i, name, days, score, best_before, required_skills))
    return projects


def parse_skills(file_handle: TextIO, skills_count: int) -> List[Skill]:
    skills = []
    for _ in range(skills_count):
        skill_name, level = file_handle.readline().split()
        skills.append(Skill(skill_name, level))
    return skills
    