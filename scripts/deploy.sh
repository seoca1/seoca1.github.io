#!/bin/bash
set -euo pipefail

BLOG_DIR="/Users/emilio/.openclaw/workspace/multilingual-blog"
LOG_FILE="$BLOG_DIR/deploy.log"

cd "$BLOG_DIR"

echo "[$(date)] Starting blog build..." | tee -a "$LOG_FILE"

# Hugo 빌드
hugo --minify 2>&1 | tee -a "$LOG_FILE"

if [ $? -ne 0 ]; then
    echo "[$(date)] ❌ Hugo build failed" | tee -a "$LOG_FILE"
    exit 1
fi

# Git commit & push (변경사항 있을 때만)
if git diff --quiet public/; then
    echo "[$(date)] No changes to deploy" | tee -a "$LOG_FILE"
    exit 0
fi

cd public/
git add .
git commit -m "Auto-deploy: $(date +%Y-%m-%d)"
git push origin main

echo "[$(date)] ✅ Deploy completed" | tee -a "$LOG_FILE"
