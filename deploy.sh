#!/bin/bash
# Redeploys the app on the host from the latest main branch.
# Invoked by the GitHub Actions workflow (.github/workflows/deploy.yml) over SSH.
set -e

cd /root/ytit
git fetch origin main
git reset --hard origin/main
docker compose build
docker compose up -d
docker image prune -f
