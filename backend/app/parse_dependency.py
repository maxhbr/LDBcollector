import ast
import os
import re
import json
from struct import pack
from xml.etree import ElementTree
import pandas as pd

P2I_FILE = './app/konwledgebase/p2i.csv'
p2idf = pd.read_csv(P2I_FILE)

def traverse(project_name):  # path为folder的绝对路径
    dependencies = {}
    structure = {'dirname': project_name, 'child_dirs': [], 'files': []}
    dir_stack = [structure]
    while dir_stack:
        now_dir = dir_stack.pop()
        son_dir = os.listdir(now_dir['dirname'])
        for t in son_dir:
            temp = os.path.join(now_dir['dirname'], t)
            if os.path.isdir(temp):  # if now is a dir
                temp_dir = {'dirname': temp, 'child_dirs': [], 'files': []}
                now_dir['child_dirs'].append(temp_dir)
                dir_stack.append(temp_dir)
            else:  # now is a file
                now_dir['files'].append(temp)
                if is_py_file(temp):
                    # print(temp)
                    dependency = parse_pyfile(temp)
                    remove_lst=[]
                    for d in dependency:
                        if d in son_dir:
                            remove_lst.append(d)
                    for d in remove_lst:
                        dependency.remove(d)
                    dependencies["Python"]=dependencies.get("Python",set()).union(dependency)
                elif is_pom_file(temp):
                    
                    dependency=parse_pom_content(temp)
                    dependencies["Java"]=dependency
                elif "node_modules" not in temp and is_package_json_file(temp):
                    json_content=open(temp,"r").read()
                    dependency=parse_package_json(json_content)
                    dependencies["JS"]=dependency

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

def parse_pyfile(filename):
    content = open(filename, 'r').read()
    return parse_python_content(content)

def get_packages(import_name: str) -> set:
    return set(p2idf[p2idf['import']==import_name]['package'].values)

def parse_python_content(content: str) -> set:
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
    print(traverse('/data/wwxu/PySC/backend/temp_files/2022-11-10 20:20:37.095448/Easesgr_reggie/Easesgr-reggie-6bfbdc2'))
