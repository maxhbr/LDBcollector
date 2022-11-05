from flask import render_template
from flask import request
from app import app
from werkzeug.utils import secure_filename
import io
import os
import base64
import json
import datetime
from .compatibility_check import *
import zipfile
from pathlib import Path
import rarfile
# 主页面
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/ispkg',methods=['POST'])
def ispkg():
    pkg = request.json.get("pkg")
    res= is_pkg(pkg)
    return res
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

    licenses_in_files=license_detection_files(unzip_path, unzip_path+".json")

    return licenses_in_files