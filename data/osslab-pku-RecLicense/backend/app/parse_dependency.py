import ast
import os
import re
import json
from struct import pack
from xml.etree import ElementTree
import pandas as pd
from packaging.requirements import Requirement, InvalidRequirement
import logging
P2I_FILE = './app/knowledgebase/p2i.csv'
p2idf = pd.read_csv(P2I_FILE)
p2idf['import_lower'] = p2idf['import'].str.lower()
def parse_requirements_txt(file_path):
    dependencies = set()
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                dependencies.add(line)
    return dependencies

def parse_setup_py(file_path):
    dependencies = set()
    with open(file_path, 'r') as file:
        content = file.read()
        ast_tree = ast.parse(content)
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == 'setup':
                    for keyword in node.keywords:
                        if keyword.arg in ['install_requires', 'requires']:
                            if isinstance(keyword.value, ast.List):
                                for elt in keyword.value.elts:
                                    if isinstance(elt, ast.Str):
                                        dependencies.add(elt.s)
    return dependencies
def is_conatin(d, python_dependencies):
    for pd in python_dependencies:
        try:
            req = Requirement(pd)
            pkg_name = req.name.lower()
            if pkg_name == d.lower():
                return True
        except:
            continue
    return False
def traverse(project_name):
    dependencies = {}
    python_dependencies = set()
    
    # 首先查找 requirements.txt 和 setup.py
    for root, dirs, files in os.walk(project_name):
        if 'requirements.txt' in files:
            python_dependencies.update(parse_requirements_txt(os.path.join(root, 'requirements.txt')))
        if 'setup.py' in files:
            python_dependencies.update(parse_setup_py(os.path.join(root, 'setup.py')))
    
    structure = {'dirname': project_name, 'child_dirs': [], 'files': []}
    dir_stack = [structure]
    while dir_stack:
        now_dir = dir_stack.pop()
        son_dir = os.listdir(now_dir['dirname'])
        for t in son_dir:
            temp = os.path.join(now_dir['dirname'], t)
            if os.path.isdir(temp):
                temp_dir = {'dirname': temp, 'child_dirs': [], 'files': []}
                now_dir['child_dirs'].append(temp_dir)
                dir_stack.append(temp_dir)
            else:
                now_dir['files'].append(temp)
                if is_py_file(temp):
                    dependency = parse_pyfile(temp,son_dir)
                    remove_lst = [d for d in dependency if is_conatin(d,python_dependencies)]

                    for d in remove_lst:
                        dependency.remove(d)
                    python_dependencies.update(dependency)
                elif is_pom_file(temp):
                    dependency = parse_pom_content(temp)
                    dependencies["Java"] = dependency
                elif "node_modules" not in temp and is_package_json_file(temp):
                    with open(temp, "r") as f:
                        json_content = f.read()
                    dependency = parse_package_json(json_content)
                    dependencies["JavaScript"] = dependency

    dependencies["Python"] = python_dependencies
    return dependencies

def is_py_file(path):
    filename = path.split('/')[-1]
    suffix = filename.split('.')[-1]
    if suffix == 'py':
        return True
    else:
        return False

def is_pom_file(path):
    filename = path.split('/')[-1]
    if filename == 'pom.xml':
        return True
    else:
        return False

def is_package_json_file(path):
    filename = path.split('/')[-1]
    if filename == 'package.json':
        return True
    else:
        return False

def parse_pyfile(filename,sondir):
    content = open(filename, 'r').read()
    return parse_python_content(content,sondir)

def get_packages(import_name: str) -> set:
    p = set(p2idf[p2idf['import_lower'] == import_name.lower()]['package'].values)
    if len(p) == 0:
        return {import_name}
    else:
        return p
def parse_python_content(content: str,sondir) -> set:
    imports = set()
    try:
        t = ast.parse(content)
        for expr in ast.walk(t):
            if isinstance(expr, ast.ImportFrom):
                if expr.module is not None:
                    imports.add(expr.module.split('.')[0])
            elif isinstance(expr, ast.Import):
                for name in expr.names:
                    imports.add(name.name.split('.')[0])
    except Exception as e:
        for line in content.split('\n'):
            lib = lib_extraction(line)
            if lib is not None:
                imports.add(lib)
    packages = set()
    for import_name in imports:
        if import_name+".py" in sondir:
            continue
        packages = packages.union(get_packages(import_name))
    return packages

def replace_variables_in_pom(text, properties):
    pattern = re.compile(r"\${([^}]+)\}")
    for s in pattern.findall(text):
        if s in properties:
            text = text.replace("${" + s + "}", properties[s])
    return text

def parse_package_json(package_json):
    result = set()
    try:
        if package_json is None:
            return {}
        content = json.loads(package_json)
        if 'dependencies' in content.keys():
            result = result.union(set(content['dependencies'].keys()))
        if 'devDependencies' in content.keys():
            result = result.union(set(content['devDependencies'].keys()))
    except Exception as e:
        return set()
    return result
    



def parse_pom_content(pom_xml):
    if pom_xml is None:
        return {}
    result = set()

    namespaces = {'xmlns': 'http://maven.apache.org/POM/4.0.0'}
    root = ElementTree.parse(pom_xml)
    properties = {}
    properties_node = root.find(".//xmlns:properties", namespaces=namespaces)
    if properties_node is not None:
        for prop in properties_node:
            tag = prop.tag
            i = tag.find('}')
            if i >= 0:
                tag = tag[i + 1:]
            properties[tag] = prop.text

    deps = root.findall(".//xmlns:dependency", namespaces=namespaces)
    for d in deps:
        group_id = d.find("xmlns:groupId", namespaces=namespaces)
        artifact_id = d.find("xmlns:artifactId", namespaces=namespaces)
        version = d.find("xmlns:version", namespaces=namespaces)
        group_id_text = ""
        artifact_id_text = ""
        #version_text = ""
        if group_id is not None and group_id.text is not None:
            group_id_text = replace_variables_in_pom(group_id.text, properties)
        if artifact_id is not None and artifact_id.text is not None:
            artifact_id_text = replace_variables_in_pom(artifact_id.text, properties)
        # if version is not None and version.text is not None:
        #     version_text = replace_variables_in_pom(version.text, properties)
        result.add(group_id_text + ":" + artifact_id_text)
    return result

def lib_extraction(line):
    t = '(^\s*import\s+([a-zA-Z0-9]*))|(^\s*from\s+([a-zA-Z0-9]*))'
    r = re.match(t, line)
    if r is not None:
        return r.groups()[1] if r.groups()[1] is not None else r.groups()[
            3]  # one of 1 and 3 will be None
    else:
        return None


if __name__ == '__main__':
    logging.basicConfig(
        format="%(asctime)s (Process %(process)d) [%(levelname)s] %(filename)s:%(lineno)d %(message)s",
        level=logging.DEBUG,
    )
    # dep = traverse('/home/wwxu/RecLicense/backend/temp_files/2024-08-08 23:29:39.537093/osslab-pku_gfi-bot/osslab-pku-gfi-bot-751f41f')
    # require_dist = list(dep['Python'])
    # print(require_dist)
    # mongo_uri = "mongodb://localhost:27017/"
    # dr = Z3DependencyResolver(mongo_uri, "gfi-bot")
    # dep_tree = dr.resolve(require_dist)

    # print(dep_tree)
    exit()