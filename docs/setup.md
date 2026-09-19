# Production Deployment Runbook (Phase 26)
**Project:** IELTS Personal Learning Agent (`ielts-hermes`)  
**Document ID:** `DOC-P26-DEPLOYMENT`  
**Date:** 2026-09-19  
**Target Environment:** Ubuntu 24.04 LTS (x86_64) on 2-4 vCPU, 4-8GB RAM VPS  

---

## 1. Host Preparation & Prerequisites

### 1.1 System Packages
```bash
sudo apt-get update && sudo apt-get install -y \
    curl git ffmpeg portaudio19-dev libpq-dev build-essential jq \
    ca-certificates gnupg
```

### 1.2 Docker & Docker Compose v2
```bash
# Add official Docker repository and install
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update && sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Enable and add current user to docker group
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

### 1.3 Python 3.13 & uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
uv python install 3.13
```

---

## 2. Hermes Agent Installation & Profile Setup

### 2.1 Install Hermes Agent (v0.21.0+)
```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/setup-hermes.sh | bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```

### 2.2 Configure Dedicated Profile
```bash
# Create dedicated ielts-tutor profile
hermes profile create ielts-tutor
hermes profile use ielts-tutor

# Copy verified configs and skills
mkdir -p ~/.hermes/profiles/ielts-tutor
cp hermes/config.yaml.example ~/.hermes/profiles/ielts-tutor/config.yaml
cp hermes/SOUL.md ~/.hermes/profiles/ielts-tutor/SOUL.md
cp hermes/.env.example ~/.hermes/profiles/ielts-tutor/.env

# Edit .env with actual API keys and Telegram User ID
nano ~/.hermes/profiles/ielts-tutor/.env
```

---

## 3. Infrastructure Deployment

### 3.1 Supporting Services via Docker Compose
```bash
# Start PostgreSQL 18 with pgvector and Honcho
docker compose up -d postgres honcho

# Verify healthy containers
docker compose ps
```

### 3.2 Database Migrations
```bash
cd apps/learning-service
uv sync
uv run alembic upgrade head
```

---

## 4. Systemd Service Configuration

### 4.1 Install Systemd Units
```bash
sudo cp infra/systemd/ielts-learning.service /etc/systemd/system/
sudo cp infra/systemd/hermes-gateway.service /etc/systemd/system/
sudo systemctl daemon-reload
```

### 4.2 Start and Enable Services
```bash
sudo systemctl enable --now ielts-learning
sudo systemctl enable --now hermes-gateway

# Check status
sudo systemctl status ielts-learning
sudo systemctl status hermes-gateway
```

---

## 5. Verification Gate
```bash
python infra/scripts/verify_production_health.py --base-url http://127.0.0.1:8000
```
