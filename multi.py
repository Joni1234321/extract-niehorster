import sys
import pathlib
import json
import shlex
from datetime import datetime

from abbreviations import elongate_string, elongate_word
from util.mongo_util import mongo_update_organization
from util.org_util import from_replicate


def create_objects_from_path(path):
    with open(pathlib.Path(__file__).parent / path, "r") as file:
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
    if type(child) is list:
        return from_replicate(child)

    children = [generate_child(c) for c in child["children"]]
    if "command" in child:
        child = from_replicate(child["command"])
    child["children"] = children
    return child


def setHQNameToParents(organization):
    queue = [organization]
    # bfs
    while len(queue) is not 0:
        parent = queue.pop()
        for org in parent["children"]:
            if "children" in org:
                queue.append(org)
            # if is hq of any type
            if ("name" in org and elongate_word(org["name"]) == elongate_word("hq")) \
                   or (elongate_word("hq") in (org["type"].split() + [org["size"]])):

                if "name" not in org:
                    org["name"] = ""

                # Remove hq, type and size
                remove_words = [elongate_word("hq")] + parent["type"].split() + [parent["size"]]
                name_list = org["type"].split()
                for w in remove_words:
                    if w in name_list:
                        name_list.remove(w)

                # Set types
                org["type"] = " ".join(name_list + [elongate_word("hq"), parent["type"]])
                org["size"] = parent["size"]
                org["name"] = " ".join([org["type"], org["size"]])

def merge_obj_with_generated_org(obj: dict, generated: dict):
    for child in obj["children"]:
        dfs(generated, generate_child(child), child["ref_link"])
    return generated

org_path = ""
json_path = ""
if len(sys.argv) == 2:
    org_path = sys.argv[1] + ".org"
    json_path = sys.argv[1] + ".json"
if len(sys.argv) == 3:
    org_path = sys.argv[1]
    json_path = sys.argv[2]

# Create objects
obj = create_objects_from_path(org_path)

# Merge
with open(pathlib.Path(__file__).parent / json_path, "r") as json_file:
    json_obj = json.loads(json_file.read())
    # dfs replace types and sizes
    queue = [json_obj]
    while len(queue) is not 0:
        item = queue.pop()

        item["type"] = elongate_string(item["type"])
        item["size"] = elongate_word(item["size"])

        queue += item["children"]
    org = merge_obj_with_generated_org(obj, json_obj)

# SET HQ
setHQNameToParents(org)


with open(pathlib.Path(__file__).parent / (json_path.split(".")[0] + "-final.json"), "w") as final_out:
    final_out.write(json.dumps(org, indent=4))

obj_id = org["_id"]["$oid"]
del org["_id"]
org["last_modified"] = datetime.now().utcnow()
print("Updating db entry...")
mongo_update_organization(obj_id, org)
print("Updated entry!")
