# SearXNG Deployment on AWS EC2

This guide walks you through deploying SearXNG (metasearch engine) on an AWS EC2 instance.

---

## 📋 Prerequisites

- AWS account with EC2 access
- Basic knowledge of Linux terminal
- SSH key pair for EC2 access

---

## 🚀 Step 1: Launch EC2 Instance

1. **Go to AWS Console** → EC2 → Launch Instance

2. **Choose AMI**: Ubuntu 22.04 LTS or Amazon Linux 2023

3. **Instance Type**: 
   - Minimum: `t3.small` (2 vCPU, 2 GB RAM)
   - Recommended: `t3.medium` (2 vCPU, 4 GB RAM)

4. **Configure Security Group**:
   - **SSH (22)**: Your IP only
   - **HTTP (80)**: 0.0.0.0/0 (public access)
   - **HTTPS (443)**: 0.0.0.0/0 (public access)
   - **Custom TCP (8080)**: 0.0.0.0/0 (for SearXNG)

5. **Storage**: At least 20 GB

6. **Launch** and save your `.pem` key file

---

## 🔧 Step 2: Connect to EC2 Instance

```bash
ssh -i "your-key.pem" ubuntu@<your-ec2-public-ip>
```
or connect through the aws terminal

---

## 📦 Step 3: Install Dependencies

### Update system packages
```bash
sudo apt update && sudo apt upgrade -y
```

### Install Python and required packages
```bash
# Install Python 3.11+ and pip
sudo apt install -y python3 python3-pip python3-venv git

# Install additional system dependencies
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev

# Verify installation
python3 --version
pip3 --version
```

---

## 🚀 Step 4: Clone and Setup GolligogBackend Repository

1. **Clone the GolligogBackend repository**
```bash
cd ~
git clone https://github.com/BOCK-CHAIN/GolligogBackend.git
cd GolligogBackend
```

2. **Navigate to the searxng directory**
```bash
cd searxng
```

3. **Create a Python virtual environment**
```bash
python3 -m venv venv
```

4. **Activate the virtual environment**
```bash
source venv/bin/activate
```

5. **Install SearXNG dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

6. **Configure SearXNG settings** (optional)
```bash
# Copy the default settings file if it doesn't exist
mkdir -p searx
cp -n searx/settings.yml searx/settings.yml.backup 2>/dev/null || true

# Edit settings if needed
nano searx/settings.yml
```

Key settings to modify in `searx/settings.yml`:
- `server.secret_key`: Generate with `openssl rand -hex 32`
- `server.bind_address`: "0.0.0.0"
- `server.port`: 8080
- `server.base_url`: "http://<your-ec2-ip>:8080"

7. **Run SearXNG**
```bash
# Make sure you're in the searxng directory with venv activated
python -m searx.webapp
```

8. **Access SearXNG**
   - Open browser: `http://<your-ec2-public-ip>:8080`

---



Here’s a **step-by-step guide** to install **Docker** and **Docker Compose** on an **Ubuntu EC2 instance**, along with the most useful commands you’ll need 👇

---

## 🧠 Step 1: Update your system

```bash
sudo apt update -y && sudo apt upgrade -y
```

---

## 🐳 Step 2: Install prerequisites

These allow `apt` to use repositories over HTTPS.

```bash
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y
```

---

## 🧩 Step 3: Add Docker’s official GPG key

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```

---

## 🧭 Step 4: Add Docker repository

```bash
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
```

---

## 🧱 Step 5: Install Docker Engine

```bash
sudo apt update -y
sudo apt install docker-ce docker-ce-cli containerd.io -y
```

---

## ✅ Step 6: Verify Docker installation

```bash
sudo systemctl status docker
```

To see version:

```bash
docker --version
```

---

## ⚙️ Step 7: Run Docker without sudo (optional but recommended)

```bash
sudo usermod -aG docker $USER
```

Then log out and log back in (or run `newgrp docker`).

---

## 🧩 Step 8: Install Docker Compose (v2+)

Docker Compose is now included as a **plugin** in Docker, but if you want standalone:

### Option 1: Using apt (recommended for Ubuntu 22.04+)

```bash
sudo apt install docker-compose-plugin -y
```

Then check:

```bash
docker compose version
```

### Option 2: Install manually (for older Ubuntu)

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.6/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

---

## 🚀 Step 9: Enable Docker on startup

```bash
sudo systemctl enable docker
```

---

## 🔥 Common Docker Commands

| Command                        | Description                                          |
| ------------------------------ | ---------------------------------------------------- |
| `docker ps`                    | List running containers                              |
| `docker ps -a`                 | List all containers                                  |
| `docker images`                | Show all downloaded images                           |
| `docker pull <image>`          | Download image (e.g. `docker pull nginx`)            |
| `docker run -d -p 80:80 nginx` | Run container in background on port 80               |
| `docker stop <container_id>`   | Stop container                                       |
| `docker rm <container_id>`     | Remove container                                     |
| `docker rmi <image_id>`        | Remove image                                         |
| `docker system prune -a`       | Clean up unused data                                 |
| `docker compose up -d`         | Run services in background (from docker-compose.yml) |
| `docker compose down`          | Stop and remove containers, networks, etc.           |

---
