from typing import List, Dict
from abbreviations import elongate_word

LIST_SEPERATOR = "_"
ITEM_SEPERATOR = ","
COUNT_SEPERATOR = ":"


# ARGS:
# 1 - NAME [split into type and size]
# 2 - Equipment in lowest level unit
# 3 - List of amount of subunits [2,3]
# 4 - List of equipment in HQ        [7,hmg:2|4,horse:1]
# 5 - Notes
# 6 - n

# Converts truck:2 into {n: 2, name: truck}
def _generate_equipment(eq_str: str):
    eq = eq_str.split(COUNT_SEPERATOR)
    n = "ERROR"
    if len(eq) == 1:
        n = 1
    elif len(eq) == 2:
        n = eq[1]
    else:
        print("FAILURE, EQUIPMENT DOESNT HAVE 1 OR 2 VALUES")
        quit()
    return {"n": int(n), "name": " ".join([elongate_word(w) for w in eq[0].split(" ")])}


# Converts an equipment string 2,truck,hmg:2 into a dictionary of objects
def equipment_string_to_dictionary(equipment_string: str):
    if equipment_string == "" or equipment_string is None:
        return {"men": "Ø", "equipment": []}

    item_strings = equipment_string.split(ITEM_SEPERATOR)
    men = item_strings[0]
    equipment = [_generate_equipment(eq_str) for eq_str in item_strings[1:]]
    dic = {"men": men, "equipment": equipment}
    return dic


# Save
def to_replicate(name: str, last_child_equipment: Dict = None, sub_units: List[int] = None,
                 hq_equipment: List[Dict] = None, notes=None, unit_n=None):
    def generate_equipment_string(equipment_dict):
        ar = [str(equipment_dict['men'])] + [f"{item['name']}{COUNT_SEPERATOR}{item['n']}" for item in
                                             equipment_dict["equipment"]]
        return ITEM_SEPERATOR.join(ar)

    out = [name]

    if last_child_equipment is not None:
        eq_str = generate_equipment_string(last_child_equipment)
        out.append(eq_str)

    if sub_units is not None:
        sub_str = LIST_SEPERATOR.join([str(i) for i in sub_units])
        out.append(sub_str)

    if hq_equipment is not None:
        hq_str = LIST_SEPERATOR.join([generate_equipment_string(eq) for eq in hq_equipment])
        out.append(hq_str)

    if notes is not None:
        out.append(notes)

    if unit_n is not None:
        out.append(str(unit_n))

    return out


# Load
def from_replicate(replicate_strings: List[str]):
    global idx_next
    idx_next = 0

    def next_str():
        global idx_next
        idx_next += 1
        if len(replicate_strings) < idx_next:
            return None
        return replicate_strings[idx_next - 1]


    name = next_str()

    last = equipment_string_to_dictionary(next_str())

    # Do this because, split doesnt work on type None
    s = next_str()
    sub = s.split(LIST_SEPERATOR) if s is not None else None

    # Do this because Split doesnt work on None
    s = next_str()
    hq = [equipment_string_to_dictionary(eq) for eq in (s.split(LIST_SEPERATOR) if s is not None else [])]

    notes = next_str()

    unit_n = next_str()

    return create_obj(name, last, sub, hq if len(hq) is not 0 else None, notes, unit_n)


def create_obj(name: str, last_child_equipment: Dict = None, sub_units: List[int] = None,
               hq_equipment: List[Dict] = None, notes=None, unit_n=None):
    # Split size and type of name
    words = [elongate_word(w) for w in name.split()]
    size, type = words[-1], " ".join(words[:-1])
    obj = ({"name": name, "type": type, "size": size})

    # Automatically Create Sub Units
    sizes = ['undefined', 'squad', 'platoon', 'company', 'battalion', 'regiment', 'brigade', 'division']
    last_child = obj

    if sub_units is not None:

        if size.lower() == "battery":
            from_size = sizes.index("company")
        else:
            from_size = sizes.index(size.lower())

        for i in range(len(sub_units)):
            # Skip units if they are 0
            if sub_units[i] == 0:
                continue

            hq_unit = {"n": 1, "type": elongate_word("hq"), "size": last_child["size"], "men": 0, "equipment": []}
            sub_unit = {"n": sub_units[i], "type": type, "size": sizes[from_size - i - 1]}

            # Set HQ
            if hq_equipment is not None:
                hq_unit.update(hq_equipment[i])

            # Set children
            last_child["children"] = [hq_unit, sub_unit]

            last_child = sub_unit

    # Update List Child Equipment
    last_child.update(last_child_equipment)

    if notes is not None:
        obj["notes"] = notes

    if unit_n is not None:
        new_obj = {"n": int(unit_n)}
        new_obj.update(obj)
        obj = new_obj

    obj["replicate"] = to_replicate(name, last_child_equipment, sub_units, hq_equipment, notes, unit_n)

    return obj
