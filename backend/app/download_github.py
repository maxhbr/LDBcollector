import subprocess
import os
import datetime
import random
import json
def download_git(OWNER,REPO):
        with open("./app/token","r") as f:
                token=f.readlines()
                token=list(map(lambda e:e.strip(),token))
                YOUR_TOKEN=token[random.randint(0,len(token)-1)]
        filepath="./temp_files/"+ str( datetime.datetime.now())
        print(YOUR_TOKEN)
        os.makedirs(filepath)

        pipe = subprocess.Popen(
                ["curl","-H" ,"Accept: application/vnd.github+json","-H",f"Authorization: Bearer {YOUR_TOKEN}",f"https://api.github.com/repos/{OWNER}/{REPO}"],
                stdout=subprocess.PIPE)
        return_code=pipe.wait()
        print(return_code)
        out=pipe.communicate()
        print(out)
        if json.loads(out[0]).get("message","") == 'Not Found':
                return 'URL ERROR'
        
        pipe = subprocess.Popen(
                ["curl","-H" ,"Accept: application/vnd.github+json","-H",f"Authorization: Bearer {YOUR_TOKEN}",f"https://api.github.com/repos/{OWNER}/{REPO}/zipball","-L","-o", f"{filepath}/"+OWNER+"_"+REPO+".zip"],
                stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        return_code=pipe.wait()
        out=pipe.communicate()
        print(out)


        if return_code == 0:
                return f"{filepath}/"+OWNER+"_"+REPO+".zip"
        return "URL ERROR"

# print(download_git("osslab-pku","licenserec"))