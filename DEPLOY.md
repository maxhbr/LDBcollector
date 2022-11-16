# LicenseRec Deployment

We recommend using Docker to deploy LicenseRec. If you are testing / developing LicenseRec and want goodies like HMR / auto-reload, you may refer to the manual deployment instructions.
This setup has been tested on Ubuntu 20.04 x64 + Docker 20.10.8 + Docker Compose 1.29.2, and should work on other Debian-based Linux distributions.

## Setup with Docker

### Install Docker

The installation of Docker is described in the [official documentation](https://docs.docker.com/engine/install/). The script below installs docker on Debian/Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
```

### Run Containers

The LicenseRec Tool consists of three containers: the backend, the frontend and a MongoDB database. 

The backend is a Flask server, and the frontend is a Caddy server. The backend and the frontend communicate with each other through the network. 

The MongoDB database is pulled from the official Docker Hub. The backend and the frontend are built from the Dockerfile in the `deploy` directory. The `docker-compose.yml` file defines the network and the volumes.

#### 1. Edit `.env`

The `.env` file defines the environment variables for the backend and the frontend.

```bash
cp .env.example .env
vim .env  # or any other editor
```

Edit the following variables:

```env
# MongoDB port exposed to the host
RECLIC_MONGO_PORT=127.0.0.1:27020
# Flask app port exposed to the host
RECLIC_BACKEND_PORT=127.0.0.1:5000
# Website port exposed to the host
RECLIC_HTTPS_PORT=443
RECLIC_HTTP_PORT=80
# Data directory (Flask app and MongoDB)
RECLIC_DATA_DIR=~/reclic-data
# Domain
RECLIC_DOMAIN=dev.licenserec.com
# Container name (Docker container name prefix)
COMPOSE_PROJECT_NAME=reclic_sample
# Github token used to clone repositories
GITHUB_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 2. Run Containers

```bash
cd deploy
sudo docker-compose up -d
```

#### 3. Check Containers

```bash
sudo docker ps
```

You should see the following containers:

```bash
CONTAINER ID   IMAGE                 COMMAND                  CREATED          STATUS          PORTS                                                                 NAMES
c0e1b0b8b8b0   reclic_sample_frontend   "/bin/caddy run …"   20 seconds ago   Up 19 seconds
f1b1b0b8b8b0   reclic_sample_backend   "flask run …"         20 seconds ago   Up 19 seconds
e0e1b0b8b8b0   mongo:4.4.6-bionic   "docker-entrypoint.s…"   20 seconds ago   Up 19 seconds
```

#### 4. Check Logs

```bash
sudo docker logs -f reclic_sample_backend
sudo docker logs -f reclic_sample_frontend
```

#### 5. Stop Containers

```bash
sudo docker-compose down
```

## Manual Deployment

### 1. Install Dependencies

#### 1.1 Install MongoDB & Python

```bash
sudo apt-get install mongodb python3.8 python3.8-venv python3.8-pip
```

#### 1.2 Install Node.js

Official documentation: https://nodejs.org/en/download/package-manager/

```bash
curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### 1.3 Install Caddy

Official documentation: https://caddyserver.com/docs/install

```bash
curl -fsSL https://dl.cloudsmith.io/public/caddy/stable/cfg/gpg/gpg.155B6D79CA56EA34.key | sudo apt-key add -
curl -fsSL https://dl.cloudsmith.io/public/caddy/stable/cfg/setup/config.deb.txt | sudo tee -a /etc/apt/sources.list.d/caddy-stable.list
sudo apt-get update
sudo apt-get install caddy
```


#### 1.4 Configure Scancode

Note that we forked the scancode-toolkit repository and made some modifications to the code.

```bash
cd ./scancode-toolkit
./configure --clean && ./configure
```

#### 1.5 Install LicenseRec Dependencies

```bash
cd ./backend
pip3 install -r requirements.txt
```

#### 1.6 Install Frontend Dependencies

```bash
cd ./frontend
npm install
```
  

### 2. Setup Development Environment

### 2.1 MongoDB

```bash
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### 2.2 Backend

Use `screen` or `nohup` to run the backend in the background. 
LicenseRec requires a Github token to clone repositories. You can create a Github token [here](https://github.com/settings/tokens) and supply it to the backend through the `GITHUB_TOKEN` environment variable or `app/token` file.

```bash
screen -R reclic_backend
# LicenseRec requires a Github token to clone repositories
echo "YOUR_GITHUB_TOKEN" > ./backend/app/token
# or:
# export GITHUB_TOKEN=YOUR_GITHUB_TOKEN
cd ./backend
flask run --host=127.0.0.1 --port=5000
(Ctrl+A+D to detach)
```

### 2.3 Frontend

Use `screen` or `nohup` to run the frontend in the background.

```bash
screen -R reclic_frontend
cd ./frontend
export PORT=3333
npm run dev
(Ctrl+A+D to detach)
```

### 2.4 Caddy

```bash
sudo vim /etc/caddy/Caddyfile  # or any other editor
```

```caddyfile
# Caddyfile
# https://caddyserver.com/docs/caddyfile
licenserec.com {  # or your domain
    route {
        handle_path /api/* {
            reverse_proxy localhost:5000
        }
        reverse_proxy localhost:3333
    }
    log
}
```

```bash
sudo systemctl restart caddy
```

Caddyserver will automatically obtain a TLS certificate from Let's Encrypt, and you should see the LicenseRec website with a valid TLS certificate after a few seconds.


### 3. Check Logs

#### 3.1 Backend and Frontend

```bash
screen -R reclic_backend
screen -R reclic_frontend
```

#### 3.2 Caddy

```bash
sudo journalctl -u caddy -f
```

### 4. Stop Services

```bash
sudo systemctl stop mongodb
sudo systemctl stop caddy
screen -X -S reclic_backend quit
screen -X -S reclic_frontend quit
```

## Copy Data

The LicenseRec Tool stores all the data in the MongoDB database and the `backend/temp_files` directory. You can copy the data to another machine and restore the data. (double check to make sure the containers are stopped)

### 1. Copy MongoDB Data

LicenseRec reuses the [libraries.io](https://libraries.io/) dataset to indentify the license of project dependencies. The dataset is stored in the `projects` collection in the MongoDB database. You can download the dataset from [here](https://drive.google.com/file/d/1os3KffCzM_psR5Fv3v5WKe0r397s4E1i/view?usp=sharing) and import it to the MongoDB database.

**TODO**: google drive leaks the file owner's google account, thus the share is not suitable for double-blind review. Please upload the dataset to another place (e.g. figshare/zenodo) and update the link here.


If another instance of LicenseRec is already running, just copy the whole MongoDB data directory will do the trick:

```bash
sudo cp -r /var/lib/mongodb /path/to/your/data/dir/mongodb
```

Make sure the MongoDB service is stopped before copying the data directory, else the data may be corrupted. To fix:
    
```bash
sudo systemctl stop mongodb
sudo mongod --repair --dbpath /path/to/your/data/dir/mongodb
```

### 2. Copy Backend Data

```bash
sudo cp -r /path/to/your/data/dir/backend /path/to/your/data/dir/backend
```