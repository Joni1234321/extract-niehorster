import sys
import pathlib
import json
import shlex
from typing import List, Dict

import pyperclip

from util.org_util import from_replicate


def create_objects_from_path(path):
    file = open(pathlib.Path(__file__).parent / path, "r")

    parent_idx = 0
    parents = [{"children": []}]

    lines = file.readlines()

    for index, line in enumerate(lines):
        indents = 0
        for c in line:
            if c is "\t":
                indents += 1
            else:
                break

        line = line.strip()

        # Skip if line is empty
        if line == "":
            continue

        # Update parent
        if indents > parent_idx:
            new_parent = parents[-1]["children"][-1]
            # If the new parent is just a command
            if type(new_parent) is list:
                parents[-1]["children"][-1] = {"command": new_parent, "children": []}

            parents.append(parents[-1]["children"][-1])

        # Set index
        child_idx = indents + 1
        parent_idx = indents
        parents = parents[:child_idx]

        # If comment
        if line[:2] == "//":
            print("FAILED FOUND LINE WITH //:")
            print("Line " + str(index) + " -> " + line)
            # quit()  # COMMENT THIS TO REMOVE ERROR
            parents[-1]["children"].append(line)
            continue

        org: object
        # Create new group
        if line[-1] == ":":
            name, ref_link = line[:-1].split(",")
            org = {}
            if ref_link is not None:
                org = {"ref_link": ref_link}
            org.update({"name": name, "children": []})
        else:
            org = shlex.split(line)

        parents[-1]["children"].append(org)
    file.close()
    return parents[0]


def dfs(generated: dict, child: dict, ref_link: str):
    ref_link = ref_link.split(".")[0]
    target = generated
    queue = []
    while target["link"].split(".")[0] != ref_link:
        queue += target["children"]
        target = queue.pop()
        while "link" not in target:
            target = queue.pop()

    target["children"] += child["children"]

def generate_child(child):
    print(child)
    if type(child) is list:
        return from_replicate(child)

    print(child)
    children = [generate_child(c) for c in child["children"]]
    if "command" in child:
        child = from_replicate(child["command"])
    child["children"] = children
    return child

def merge_obj_with_generated_org(obj: dict, generated: dict):
    for child in obj["children"]:
        dfs(generated, generate_child(child), child["ref_link"])
    return generated


obj = create_objects_from_path(sys.argv[1])

file = open(pathlib.Path(__file__).parent / sys.argv[2], "r")
org = merge_obj_with_generated_org(obj, json.loads(file.read()))
file.close()

print(json.dumps(org, indent=4))
pyperclip.copy(json.dumps(org))
