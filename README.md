# LicenseRec
The tool is under development now.

Environment: Ubantu20.04, Python3.8, Java1.8, Node.js v18.10.0
## Backend
### configure scancode:
```
cd scancode-toolkit

./configure clean

./configure

source venv/bin/activate
```

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