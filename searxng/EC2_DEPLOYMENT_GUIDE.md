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
