import json
from pathlib import Path
from typing import Dict
from urllib.request import urlopen
from Organization import Organization
from bs4 import BeautifulSoup
import pyperclip
import sys

#http://niehorster.org/011_germany/41-oob/ag-mitte/_ag_mitte.html
[_, TOTAL_URL, NAME, COUNTRY, YEAR] = sys.argv


# NAME = "Rifle Battalion"
# COUNTRY = "ussr"
# YEAR = 1944


# TOTAL_URL = "012_ussr/44_organ/brig_tank/44_brig_tk.htm"
# TOTAL_URL = "012_ussr/44_organ/div_rifle-gds/44_grd.html"
# TOTAL_URL = "012_ussr/44_organ/div_rifle/44_rd_inf-bn.htm"

class Main:
    READ_FROM_DISK = False

    def read_file(self, unit_url: str):
        if not Main.READ_FROM_DISK:
            html_bytes = urlopen(self.web_url + unit_url).read()
            # Use cp1252 instead of UTF-8 because UTF-8 gives an error
            return html_bytes.decode("cp1252")
        else:
            with open(self.disk_url / unit_url) as f:
                txt = f.read()
                return txt

    def get_areas(self, url: str):
        soup = BeautifulSoup(self.read_file(url), "html.parser")

        html_map = soup.find("map")
        if soup.map is None:
            return
        return html_map.find_all("area")

    def load_units(self, url: str):
        areas = self.get_areas(url)
        for area in areas or []:
            # Skip empty objects
            if area["alt"] == "" or area["alt"] == " ":
                continue
            if not area.has_attr("href"):
                print(area)
                continue

            link = area["href"]

            # Add the child
            self.units[url].add_child(link)

            # Create object if it doesn't exist
            if link not in self.units.keys():
                self.units[link] = Organization(area["title"], link)
                self.load_units(link)

    def __init__(self, name: str, full_url):
        self.name = name
        self.full_url = full_url

        # List of all units in division
        # Link -> Organization
        self.units: Dict[str, Organization] = {}

        # SPLIT URL INTO IMPORTANT PARTS
        full_url = full_url.replace("http://niehorster.org/", "")
        url_ar = full_url.split("/")
        sub_url, self.unit_url = ("/".join(url_ar[:-1]) + "/"), url_ar[-1]

        self.disk_url = Path("niehorster/niehorster/niehorster.org/") / sub_url
        self.web_url = "http://niehorster.org/" + sub_url

        # Load
        self.units[self.unit_url] = Organization(self.name, self.unit_url)
        self.load_units(self.unit_url)

    # dumps json
    def dumps(self):
        # Important information
        json_out = {"schema_version": 1, "country": COUNTRY, "year": YEAR}
        json_out.update(self.unit_to_json(self.unit_url))
        return json.dumps(json_out, indent=4)

    # to json
    def unit_to_json(self, url: str):
        children_obj = []
        unit = self.units[url]
        for (link, n) in unit.children.items():
            child_obj = {"n": n}
            child_obj.update(self.unit_to_json(link))
            children_obj.append(child_obj)

        return {"name": unit.name, "link": unit.link, "type": unit.type, "size": unit.size, "children": children_obj}

    # to string
    def unit_to_str(self, url: str):
        unit = self.units[url]
        return self.name + ": " + str([(n, str(self.units[link])) for (link, n) in unit.children.items()])


# Run program
main = Main(NAME, TOTAL_URL)
print(main.dumps())
pyperclip.copy(main.dumps())
