# IELTS Tutor Profile

This directory contains the Hermes profile for the IELTS tutor bot.

## Setup

1. Copy the parent directory's config files:
   ```bash
   cp ../config.yaml.example config.yaml
   cp ../.env.example .env
   cp ../SOUL.md SOUL.md
   ```

2. Edit `.env` with your actual credentials
3. Edit `config.yaml` with your Telegram user ID
4. Create the profile:
   ```bash
   hermes profile create ielts-tutor
   ```

5. Copy files to the profile:
   ```bash
   cp SOUL.md ~/.hermes/profiles/ielts-tutor/SOUL.md
   cp config.yaml ~/.hermes/profiles/ielts-tutor/config.yaml
   cp .env ~/.hermes/profiles/ielts-tutor/.env
   ```

6. Start the gateway:
   ```bash
   hermes -p ielts-tutor gateway start
   ```
