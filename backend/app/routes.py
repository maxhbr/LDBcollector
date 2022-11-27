from flask import render_template
from flask import request, send_from_directory
from app import app
from werkzeug.utils import secure_filename
import os
import datetime
import zipfile
from pathlib import Path
import rarfile
from .compatibility_check import *
from .query import license_compatibility_judge
from .download_github import download_git
from .question import license_terms_choice
from .compare import license_compare
import logging
import threading
logging.basicConfig(
    filename=f"./app/logging/backend.log",
    filemode='a',
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)
job = {}
lock = threading.Lock()

def git_check(unzip_path):
    licenses_in_files=license_detection_files(unzip_path, unzip_path+".json")
    dependecy=depend_detection(unzip_path,unzip_path+"/temp.json")

    confilct_copyleft_list,confilct_depend_dict=conflict_dection(licenses_in_files,dependecy)
    compatible_licenses, compatible_both_list, compatible_secondary_list, compatible_combine_list = license_compatibility_filter(licenses_in_files.values())
    
    lock.acquire()
    job[unzip_path] =  {"licenses_in_files":licenses_in_files,"confilct_depend_dict":confilct_depend_dict,
    "confilct_copyleft_list":confilct_copyleft_list,"compatible_licenses":compatible_licenses,
    "compatible_both_list":compatible_both_list,"compatible_secondary_list":compatible_secondary_list,
    "compatible_combine_list":compatible_combine_list}
    lock.release()

# 主页面
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/zip', methods=['POST'])
def upload():
    f = request.files.get("file")
    file_path = './temp_files/' + str( datetime.datetime.now())
    os.makedirs(file_path)
    file_path = os.path.join(file_path, secure_filename(f.filename))
    unzip_path=file_path[:-4]
    f.save(file_path)
    if ".zip" in file_path:
        z = zipfile.ZipFile(file_path, "r")
        z.extractall(unzip_path)
        z.close()
    elif ".rar" in file_path:
        z = rarfile.RarFile(file_path, "r")
        z.extractall(unzip_path)
        z.close()

    # licenses_in_files=license_detection_files(unzip_path, unzip_path+".json")
    # dependecy=depend_detection(unzip_path,unzip_path+"/temp.json")
    # # print(licenses_in_files)
    # # print(dependecy)
    # confilct_copyleft_list,confilct_depend_dict=conflict_dection(licenses_in_files,dependecy)
    # compatible_licenses, compatible_both_list, compatible_secondary_list, compatible_combine_list = license_compatibility_filter(licenses_in_files.values())
    
    # return {"licenses_in_files":licenses_in_files,"confilct_depend_dict":confilct_depend_dict,
    # "confilct_copyleft_list":confilct_copyleft_list,"compatible_licenses":compatible_licenses,
    # "compatible_both_list":compatible_both_list,"compatible_secondary_list":compatible_secondary_list,
    # "compatible_combine_list":compatible_combine_list}

    threading.Thread(target=git_check, args=(unzip_path,)).start()
    return unzip_path

@app.route('/git', methods=['POST'])
def download():
    username= request.json.get("username")
    reponame = request.json.get("reponame")
    print(reponame)
    file_path=download_git(username,reponame)
    if file_path == "URL ERROR":
        return "URL ERROR"
    unzip_path=file_path[:-4]
    z = zipfile.ZipFile(file_path, "r")
    z.extractall(unzip_path)
    z.close()
    # licenses_in_files=license_detection_files(unzip_path, unzip_path+".json")
    # dependecy=depend_detection(unzip_path,unzip_path+"/temp.json")

    # confilct_copyleft_list,confilct_depend_dict=conflict_dection(licenses_in_files,dependecy)
    # compatible_licenses, compatible_both_list, compatible_secondary_list, compatible_combine_list = license_compatibility_filter(licenses_in_files.values())
    
    # return {"licenses_in_files":licenses_in_files,"confilct_depend_dict":confilct_depend_dict,
    # "confilct_copyleft_list":confilct_copyleft_list,"compatible_licenses":compatible_licenses,
    # "compatible_both_list":compatible_both_list,"compatible_secondary_list":compatible_secondary_list,
    # "compatible_combine_list":compatible_combine_list}
    threading.Thread(target=git_check, args=(unzip_path,)).start()
    return unzip_path

@app.route('/poll', methods=['POST'])
def status():
    path = request.json.get("path")
    # print("path:", path)
    lock.acquire()
    res = job.get(path, 'doing')
    if res != 'doing':
        del job[path]
    lock.release()
    return res

@app.route('/support_list', methods=['POST'])
def support_lst():
    df1 = pd.read_csv('./app/knowledgebase/compatibility_63.csv', index_col=0)
    license_list = df1.index.tolist()
    return license_list

@app.route('/query', methods=['POST'])
def query():
    l1 = request.json.get("licenseA")
    l2 = request.json.get("licenseB")
    return license_compatibility_judge(l1,l2)

@app.route('/choice', methods=['POST'])
def choice():
    answer = request.json.get("answer")
    return license_terms_choice(answer)

@app.route('/compare',methods=['POST'])
def compare():
    lst = request.json.get("recommend_list")
    return license_compare(lst)

@app.route('/test', methods=['POST'])
def test():
    data = request.json.get("testdata")
    print(data)
    return 'success'

@app.route('/favico.ico', methods=['GET'])
def ico():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')