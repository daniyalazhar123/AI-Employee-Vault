#!/bin/bash
# ============================================
# 💿 PLATINUM TIER - VAULT SYNC (CLOUD VM)
# ============================================
# Run on Cloud VM every 5 minutes
# Syncs vault with Local via Git

VAULT_DIR="/home/ubuntu/ai-employee-vault"
LOG_FILE="/home/ubuntu/sync.log"

cd $VAULT_DIR

echo "============================================" >> $LOG_FILE
echo "$(date): Starting Git sync..." >> $LOG_FILE

# Git pull - get changes from Local
echo "$(date): Pulling from remote..." >> $LOG_FILE
git pull origin main >> $LOG_FILE 2>&1
if [ $? -ne 0 ]; then
    echo "$(date): ERROR - Git pull failed" >> $LOG_FILE
else
    echo "$(date): Git pull successful" >> $LOG_FILE
fi

# Git add - stage cloud changes
git add .

# Git status check - any changes to commit?
git diff --cached --quiet
if [ $? -eq 0 ]; then
    echo "$(date): No changes to commit" >> $LOG_FILE
else
    echo "$(date): Committing cloud changes..." >> $LOG_FILE
    git commit -m "Cloud Agent sync $(date '+%Y-%m-%d %H:%M:%S')" >> $LOG_FILE 2>&1
    
    echo "$(date): Pushing to remote..." >> $LOG_FILE
    git push origin main >> $LOG_FILE 2>&1
    if [ $? -ne 0 ]; then
        echo "$(date): ERROR - Git push failed (may need pull first)" >> $LOG_FILE
    else
        echo "$(date): Git push successful" >> $LOG_FILE
    fi
fi

echo "$(date): Sync complete" >> $LOG_FILE
echo "" >> $LOG_FILE
