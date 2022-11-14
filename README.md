# LicenseRec

The tool is available at [licenserec.com](http://licenserec.com/).

Environment: Ubantu20.04, Python3.8, Java1.8, Node.js v18.10.0
## Backend
### configure scancode:
```
cd scancode-toolkit

./configure --clean

./configure

source venv/bin/activate
```

### Github API Access

You should create a file named ```token``` which contains your own Github token in ```backend/app/token```.


### MongoDB

File ```backend/app/compatibility_check.py``` uses MongoDB to query the license of a package.
You can generate the collection ```projects``` by [projects.json](https://drive.google.com/file/d/1os3KffCzM_psR5Fv3v5WKe0r397s4E1i/view?usp=sharing) which is from [libraries.io](https://libraries.io/).

### run flask:
```
cd backend

pip install -r requirements.txt

flask run -p 1120
```

## Frontend
### Dev 
``` bash
# install dependencies

cd frontend
npm install

# serve with hot reload at localhost:1121
npm run dev
```
Then you can visit http://localhost:1121/

### Build
```
# build for production with minification
npm run build

# build for production and view the bundle analyzer report
npm run build --report
```


![Image text](https://github.com/osslab-pku/RecLicense/blob/246743e3500447a2214816f22ee63fbeb0be985e/frontend/src/assets/tool.png)





* Mulan PSL v2 as the overall license.
* Apache-2.0 for [scancode-tookit](https://github.com/nexB/scancode-toolkit). We modified detection rules of Mulan series licenses in ```scancode-toolkit/src/licensedcode/data/rules``` and ```scancode-toolkit/src/licensedcode/data/licenses```.
* The third-party tool, depends, is from [https://github.com/multilang-depends/depends](https://github.com/multilang-depends/depends).
