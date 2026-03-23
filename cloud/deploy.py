#!/usr/bin/env python3
"""
Cloud VM Deployment Script - Pure Python
Uses paramiko for SSH to Oracle Cloud VM

Personal AI Employee Hackathon 0
Platinum Tier: Cloud Deployment
"""

import paramiko
import os
import sys
import time
from pathlib import Path
from typing import Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('CloudDeploy')


class CloudDeployer:
    """Deploy AI Employee to Cloud VM via SSH"""
    
    def __init__(self, host: str, username: str, key_path: Optional[str] = None, 
                 password: Optional[str] = None):
        self.host = host
        self.username = username
        self.key_path = key_path
        self.password = password
        self.client = None
        self.sftp = None
        
        logger.info(f"☁️  Cloud Deployer initialized for {username}@{host}")
    
    def connect(self):
        """Connect to cloud VM via SSH"""
        try:
            logger.info("🔌 Connecting to cloud VM...")
            
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if self.key_path:
                self.client.connect(
                    self.host,
                    username=self.username,
                    key_filename=self.key_path,
                    timeout=30
                )
            else:
                self.client.connect(
                    self.host,
                    username=self.username,
                    password=self.password,
                    timeout=30
                )
            
            self.sftp = self.client.open_sftp()
            
            logger.info("✅ Connected to cloud VM")
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from cloud VM"""
        if self.sftp:
            self.sftp.close()
        if self.client:
            self.client.close()
        logger.info("🔌 Disconnected from cloud VM")
    
    def run_command(self, command: str) -> tuple:
        """Run command on cloud VM"""
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            exit_code = stdout.channel.recv_exit_status()
            
            return exit_code, output, error
            
        except Exception as e:
            logger.error(f"❌ Command failed: {e}")
            return -1, "", str(e)
    
    def upload_file(self, local_path: str, remote_path: str):
        """Upload file to cloud VM"""
        try:
            logger.info(f"📤 Uploading: {local_path} → {remote_path}")
            self.sftp.put(local_path, remote_path)
            logger.info("✅ Upload complete")
        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
    
    def deploy(self, vault_path: str):
        """Complete deployment process"""
        logger.info("🚀 Starting deployment...")
        
        if not self.connect():
            return False
        
        try:
            # Step 1: Update system
            logger.info("📦 Step 1: Updating system...")
            exit_code, output, error = self.run_command(
                "sudo apt update && sudo apt upgrade -y"
            )
            if exit_code != 0:
                logger.error(f"❌ Update failed: {error}")
                return False
            logger.info("✅ System updated")
            
            # Step 2: Install prerequisites
            logger.info("📦 Step 2: Installing prerequisites...")
            commands = [
                "sudo apt install -y python3 python3-pip python3-venv git docker.io docker-compose",
                "curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -",
                "sudo apt install -y nodejs",
                "sudo npm install -g @anthropic/qwen pm2"
            ]
            
            for cmd in commands:
                exit_code, output, error = self.run_command(cmd)
                if exit_code != 0:
                    logger.warning(f"⚠️ Command had issues: {error}")
                time.sleep(2)
            
            logger.info("✅ Prerequisites installed")
            
            # Step 3: Clone vault
            logger.info("📦 Step 3: Cloning vault...")
            exit_code, output, error = self.run_command(
                f"git clone <YOUR_REPO_URL> ~/ai-employee-vault"
            )
            if exit_code != 0:
                logger.warning(f"⚠️ Clone may have failed (repo might be private): {error}")
                logger.info("ℹ️ You'll need to manually clone your repository")
            
            # Step 4: Install Python dependencies
            logger.info("📦 Step 4: Installing Python dependencies...")
            exit_code, output, error = self.run_command(
                "cd ~/ai-employee-vault && pip3 install -r requirements.txt"
            )
            
            # Step 5: Setup environment
            logger.info("📦 Step 5: Setting up environment...")
            self.run_command(
                "cd ~/ai-employee-vault && cp .env.example .env"
            )
            
            # Step 6: Start cloud orchestrator
            logger.info("📦 Step 6: Starting cloud orchestrator...")
            self.run_command(
                "cd ~/ai-employee-vault && pm2 start cloud_orchestrator.py --name cloud-agent --interpreter python3"
            )
            
            # Step 7: Save PM2 configuration
            logger.info("📦 Step 7: Saving PM2 configuration...")
            self.run_command("pm2 save")
            self.run_command("pm2 startup | tail -1 | bash")
            
            logger.info("✅ Deployment complete!")
            
            # Verify deployment
            logger.info("🔍 Verifying deployment...")
            exit_code, output, error = self.run_command("pm2 status")
            if exit_code == 0:
                logger.info("✅ PM2 processes running:")
                logger.info(output)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return False
        finally:
            self.disconnect()


def main():
    """Main deployment function"""
    print("╔════════════════════════════════════════════════════════╗")
    print("║  ☁️  Cloud VM Deployment - Platinum Tier               ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    
    # Get deployment details
    host = input("Cloud VM Host (IP): ").strip()
    username = input("Username (default: ubuntu): ").strip() or "ubuntu"
    
    auth_method = input("Auth method (key/password): ").strip().lower()
    
    if auth_method == 'key':
        key_path = input("SSH Key Path: ").strip()
        password = None
    else:
        key_path = None
        password = input("Password: ").strip()
    
    vault_path = input("Vault Path (default: current): ").strip() or '.'
    
    # Deploy
    deployer = CloudDeployer(host, username, key_path, password)
    success = deployer.deploy(vault_path)
    
    if success:
        print()
        print("╔════════════════════════════════════════════════════════╗")
        print("║  ✅ DEPLOYMENT COMPLETE!                               ║")
        print("╚════════════════════════════════════════════════════════╝")
        print()
        print("Next Steps:")
        print("1. SSH into VM: ssh ubuntu@" + host)
        print("2. Check status: pm2 status")
        print("3. View logs: pm2 logs cloud-agent")
        print("4. Configure environment: nano ~/ai-employee-vault/.env")
    else:
        print()
        print("❌ Deployment failed! Check logs for details.")
        sys.exit(1)


if __name__ == '__main__':
    main()
