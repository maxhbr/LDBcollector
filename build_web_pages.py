import json
import os
import shutil
import re
import unicodedata

LICENSES_FOLDER = "licenses"
COMP_ACTIONS_FOLDER = "generics"
TEMPLATE_INDEX = "templates/template_index.html"
TEMPLATE_LICENSE = "templates/template_license.html"
TEMPLATE_ABOUT = "templates/template_about.html"
TEMPLATE_COMP_ACTIONS = "templates/template_comp_actions.html"
BUILD_FOLDER = "public"
JS_FOLDER = os.path.join(BUILD_FOLDER, "js")
IMG_FOLDER = os.path.join(BUILD_FOLDER, "img")
BUILD_FOLDER_LICENSES = os.path.join(BUILD_FOLDER, LICENSES_FOLDER)
BUILD_FOLDER_COMP_ACTIONS = os.path.join(BUILD_FOLDER, "compliance_actions")
COMP_ACTIONS_FILE = os.path.join(BUILD_FOLDER, "comp_actions.html")
OUTPUT_FILE = os.path.join(BUILD_FOLDER, "index.html")
ABOUT_FILE = os.path.join(BUILD_FOLDER, "about.html")


os.makedirs(BUILD_FOLDER_LICENSES, exist_ok=True)
os.makedirs(BUILD_FOLDER_COMP_ACTIONS, exist_ok=True)
for subd in [JS_FOLDER, IMG_FOLDER]:
    if os.path.exists(subd):
        shutil.rmtree(subd)

shutil.copytree("templates/img/", IMG_FOLDER)
shutil.copytree("templates/js/", JS_FOLDER)


def normalize(generic_name):
    filename = unicodedata.normalize("NFKD", generic_name)
    filename = re.sub(r"[^\w\s-]", "", filename).strip().lower()
    filename = re.sub(r"[-\s]+", "-", filename)
    return filename


def add_url(text, url):
    return f"<a href='{url}'>{text}</a>"


def license_table_row(data):
    return f"""    <tr>
      <td><a href="licenses/{data["spdx_id"]}.html">{data["spdx_id"]}</a></td>
      <td>{data["long_name"]}</td>
      <td>{data["copyleft"]}</td>
      <td><a href="https://spdx.org/licenses/{data["spdx_id"]}.html">Text</a> - <a href="https://gitlab.com/hermine-project/hermine-data/-/blob/main/licenses/{data["spdx_id"]}.json?ref_type=heads">JSON in git</a></td>
    </tr>"""


def comp_action_table_row(data, map_comp_actions_licenses):
    return f"""    <tr>
      <td><a href="compliance_actions/{normalize(data["name"])}.html">{data["name"]}</a></td>
      <td>{"<span class='tag is-dark'>"+data.get("passivity")+"</span>"}</td>
      <td>{data.get("metacategory")}</td>
      <td>{len(map_comp_actions_licenses[normalize(data["name"])]) if normalize(data["name"]) in map_comp_actions_licenses else " No licence related" }</td>

    </tr>"""


def with_link(license_id):
    return f"""<a href="../licenses/{license_id}.html">{license_id}</a>"""


def create_comp_action_page(data, map_comp_actions_licenses):
    html_output = f"""<h2>{data["name"]}</h2>
    <p><strong>Metacategory:</strong> {data["metacategory"]}</p>
    <p><strong>Description:</strong> {data["description"]}</p>
    """

    if normalize(data["name"]) in map_comp_actions_licenses:
        licenses_with_links = [
            with_link(license_id)
            for license_id in sorted(map_comp_actions_licenses[normalize(data["name"])])
        ]
        license_list_html = " – ".join(licenses_with_links)
        html_output += "<p> Related licences :" + license_list_html + "<p>"
    with open(TEMPLATE_LICENSE, "r") as f:
        html_content = f.read()
    html_content = html_content.replace("###HTMLCONTENT###", html_output)
    comp_action_file_name = f"{normalize(data['name'])}.html"
    comp_action_path = os.path.join(BUILD_FOLDER_COMP_ACTIONS, comp_action_file_name)
    with open(comp_action_path, "w") as f:
        f.write(html_content)


def create_licence_page(data):
    comp_action_list = list()
    html_output = f"""<h2>{data["long_name"]}</h2>
    <p>Copyleft :{data["copyleft"]} </p>
    <p>Actual FOSS licence : {data["foss"]}</p>
    """
    if data.get("obligations") and len(data["obligations"]) > 0:
        html_output += f"""
        <h3> Obligations attached to this license</h3>"""
        for obligation in data["obligations"]:
            html_output += f"""<h4>{obligation["name"]}</h4>"""
            if obligation.get("generic") and len(obligation["generic"]) > 0:
                comp_action_list.append(normalize(obligation["generic"][0]))
                html_output += f"""
            <p> Related to generic compliance action : <a href="../compliance_actions/{normalize(obligation["generic"][0])}.html">{obligation["generic"][0]}</a></p>

            <p>{obligation["verbatim"]}</p>
            """

    else:
        html_output += f"""
        <em>No obligation attached to this license</em>"""

    with open(TEMPLATE_LICENSE, "r") as f:
        html_content = f.read()
    html_content = html_content.replace("###HTMLCONTENT###", html_output)
    license_file_name = f"{data['spdx_id']}.html"
    licence_file_path = os.path.join(BUILD_FOLDER_LICENSES, license_file_name)

    with open(licence_file_path, "w") as f:
        f.write(html_content)
    return comp_action_list


license_files = [
    os.path.join(LICENSES_FOLDER, f)
    for f in os.listdir(LICENSES_FOLDER)
    if os.path.isfile(os.path.join(LICENSES_FOLDER, f))
]

comp_actions_files = [
    os.path.join(COMP_ACTIONS_FOLDER, f)
    for f in os.listdir(COMP_ACTIONS_FOLDER)
    if os.path.isfile(os.path.join(COMP_ACTIONS_FOLDER, f))
]
html_output = " "

map_comp_actions_licenses = dict()

for license_file in license_files:
    with open(license_file) as f:
        data = json.load(f)
    comp_actions_list = create_licence_page(data)
    if comp_actions_list:
        for comp_action in comp_actions_list:
            if comp_action in map_comp_actions_licenses:
                map_comp_actions_licenses[comp_action].add(data["spdx_id"])
            else:
                map_comp_actions_licenses[comp_action] = {data["spdx_id"]}
    html_output += license_table_row(data)


with open(TEMPLATE_INDEX, "r") as f:
    html_content = f.read()
html_content = html_content.replace("###HTMLCONTENT###", html_output)

with open(OUTPUT_FILE, "w") as f:
    f.write(html_content)

html_output = " "

for comp_actions_file in comp_actions_files:
    with open(comp_actions_file) as f:
        data = json.load(f)
    create_comp_action_page(data, map_comp_actions_licenses)
    html_output += comp_action_table_row(data, map_comp_actions_licenses)

with open(TEMPLATE_COMP_ACTIONS, "r") as f:
    html_content = f.read()
html_content = html_content.replace("###HTMLCONTENT###", html_output)

with open(COMP_ACTIONS_FILE, "w") as f:
    f.write(html_content)

html_output = """

"""

with open(TEMPLATE_ABOUT, "r") as f:
    html_content = f.read()
html_content = html_content.replace("###HTMLCONTENT###", html_output)

with open(ABOUT_FILE, "w") as f:
    f.write(html_content)
