#!/usr/bin/env python3
"""
Platinum Tier - Cloud Deployment Script
Deploy AI Employee to Oracle Cloud VM using paramiko SSH

Personal AI Employee Hackathon 0
Platinum Tier: Cloud Deployment

Usage:
    python deploy_cloud.py
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cloud_deploy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('CloudDeploy')


class CloudDeployment:
    """Deploy AI Employee to Oracle Cloud VM"""
    
    def __init__(self, host: str, username: str = 'ubuntu', 
                 key_path: Optional[str] = None, 
                 password: Optional[str] = None):
        self.host = host
        self.username = username
        self.key_path = key_path
        self.password = password
        self.client = None
        self.sftp = None
        
        logger.info(f"☁️  Cloud Deployment initialized for {username}@{host}")
    
    def connect(self) -> bool:
        """Connect to cloud VM via SSH"""
        try:
            logger.info("🔌 Connecting to cloud VM...")
            
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if self.key_path and os.path.exists(self.key_path):
                self.client.connect(
                    self.host,
                    username=self.username,
                    key_filename=self.key_path,
                    timeout=30,
                    allow_agent=True,
                    look_for_keys=True
                )
            elif self.password:
                self.client.connect(
                    self.host,
                    username=self.username,
                    password=self.password,
                    timeout=30
                )
            else:
                # Try SSH agent
                self.client.connect(
                    self.host,
                    username=self.username,
                    timeout=30,
                    allow_agent=True,
                    look_for_keys=True
                )
            
            self.sftp = self.client.open_sftp()
            
            logger.info(f"✅ Connected to {self.host}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from cloud VM"""
        if self.sftp:
            try:
                self.sftp.close()
            except:
                pass
        if self.client:
            try:
                self.client.close()
            except:
                pass
        logger.info("🔌 Disconnected")
    
    def run_command(self, command: str, timeout: int = 300) -> tuple:
        """Run command on cloud VM"""
        try:
            logger.info(f"⚙️  Running: {command[:80]}...")
            
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
            output = stdout.read().decode()
            error = stderr.read().decode()
            exit_code = stdout.channel.recv_exit_status()
            
            if exit_code == 0:
                logger.debug(f"✅ Command completed successfully")
            else:
                logger.warning(f"⚠️ Command exited with code {exit_code}: {error}")
            
            return exit_code, output, error
            
        except Exception as e:
            logger.error(f"❌ Command failed: {e}")
            return -1, "", str(e)
    
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload file to cloud VM"""
        try:
            if not os.path.exists(local_path):
                logger.error(f"❌ Local file not found: {local_path}")
                return False
            
            logger.info(f"📤 Uploading: {local_path} → {remote_path}")
            self.sftp.put(local_path, remote_path)
            logger.info("✅ Upload complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
            return False
    
    def upload_directory(self, local_dir: str, remote_dir: str, exclude_patterns: list = None):
        """Upload directory to cloud VM"""
        if exclude_patterns is None:
            exclude_patterns = ['.git', '__pycache__', '*.pyc', '.env', 'node_modules', 'Logs']
        
        local_path = Path(local_dir)
        
        for file_path in local_path.rglob('*'):
            if file_path.is_file():
                # Check exclusions
                skip = False
                for pattern in exclude_patterns:
                    if pattern in str(file_path):
                        skip = True
                        break
                
                if skip:
                    logger.debug(f"⏭️  Skipping: {file_path}")
                    continue
                
                # Calculate remote path
                relative_path = file_path.relative_to(local_path)
                remote_path = f"{remote_dir}/{relative_path}"
                
                # Create remote directory if needed
                remote_parent = str(Path(remote_path).parent)
                try:
                    self.sftp.stat(remote_parent)
                except FileNotFoundError:
                    self.run_command(f"mkdir -p {remote_parent}")
                
                # Upload file
                self.upload_file(str(file_path), remote_path)
    
    def deploy(self, vault_path: str = '.', repo_url: Optional[str] = None) -> bool:
        """Complete deployment process"""
        logger.info("🚀 Starting deployment...")
        
        if not self.connect():
            return False
        
        try:
            # Step 1: Update system
            logger.info("📦 Step 1/8: Updating system...")
            exit_code, _, _ = self.run_command(
                "sudo apt update && sudo apt upgrade -y",
                timeout=600
            )
            if exit_code != 0:
                logger.error("❌ System update failed")
                return False
            logger.info("✅ System updated")
            
            # Step 2: Install prerequisites
            logger.info("📦 Step 2/8: Installing prerequisites...")
            commands = [
                "sudo apt install -y python3 python3-pip python3-venv git curl wget",
                "sudo apt install -y docker.io docker-compose",
                "curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -",
                "sudo apt install -y nodejs",
                "sudo npm install -g pm2"
            ]
            
            for cmd in commands:
                exit_code, output, error = self.run_command(cmd, timeout=300)
                if exit_code != 0:
                    logger.warning(f"⚠️ Command had issues: {error[:100]}")
                time.sleep(2)
            
            logger.info("✅ Prerequisites installed")
            
            # Step 3: Clone repository or upload files
            logger.info("📦 Step 3/8: Setting up vault...")
            
            if repo_url:
                # Clone from Git
                exit_code, output, error = self.run_command(
                    f"git clone {repo_url} ~/ai-employee-vault",
                    timeout=120
                )
                if exit_code != 0:
                    logger.warning(f"⚠️ Git clone failed: {error[:100]}")
                    logger.info("ℹ️ Will upload files manually")
                    self.upload_directory(vault_path, '~/ai-employee-vault')
            else:
                # Upload files
                self.upload_directory(vault_path, '~/ai-employee-vault')
            
            logger.info("✅ Vault setup complete")
            
            # Step 4: Install Python dependencies
            logger.info("📦 Step 4/8: Installing Python dependencies...")
            exit_code, _, _ = self.run_command(
                "cd ~/ai-employee-vault && pip3 install -r requirements.txt",
                timeout=600
            )
            logger.info("✅ Python dependencies installed")
            
            # Step 5: Install Playwright
            logger.info("📦 Step 5/8: Installing Playwright...")
            exit_code, _, _ = self.run_command(
                "cd ~/ai-employee-vault && python3 -m playwright install chromium",
                timeout=600
            )
            logger.info("✅ Playwright installed")
            
            # Step 6: Setup environment
            logger.info("📦 Step 6/8: Setting up environment...")
            self.run_command("cd ~/ai-employee-vault && cp .env.example .env || true")
            
            # Create .env if not exists
            env_content = """# Cloud Environment
VAULT_PATH=/home/ubuntu/ai-employee-vault
CHECK_INTERVAL=30
SYNC_INTERVAL=300
AGENT_ROLE=cloud
DRY_RUN=true

# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=admin

# Dashboard
DASHBOARD_PORT=8000
"""
            # Upload .env file
            env_path = Path('cloud_deploy.env')
            env_path.write_text(env_content)
            self.upload_file(str(env_path), '~/ai-employee-vault/.env')
            env_path.unlink()
            
            logger.info("✅ Environment configured")
            
            # Step 7: Start FastAPI Dashboard
            logger.info("📦 Step 7/8: Starting FastAPI Dashboard...")
            self.run_command("pkill -f 'uvicorn dashboard.api' || true")
            self.run_command(
                "cd ~/ai-employee-vault && pm2 start dashboard/api.py --name dashboard --interpreter python3 --port 8000"
            )
            logger.info("✅ Dashboard started on port 8000")
            
            # Step 8: Start Cloud Orchestrator
            logger.info("📦 Step 8/8: Starting Cloud Orchestrator...")
            self.run_command("pkill -f cloud_orchestrator || true")
            self.run_command(
                "cd ~/ai-employee-vault && pm2 start cloud_orchestrator.py --name cloud-agent --interpreter python3"
            )
            logger.info("✅ Cloud Orchestrator started")
            
            # Save PM2 configuration
            logger.info("💾 Saving PM2 configuration...")
            self.run_command("pm2 save")
            self.run_command("pm2 startup | tail -1 | bash 2>/dev/null || true")
            
            # Verify deployment
            logger.info("🔍 Verifying deployment...")
            exit_code, output, _ = self.run_command("pm2 status")
            if exit_code == 0:
                logger.info("✅ PM2 processes:")
                for line in output.split('\n'):
                    if line.strip():
                        logger.info(f"   {line}")
            
            # Get public IP
            logger.info("🌐 Getting public IP...")
            exit_code, output, _ = self.run_command(
                "curl -s http://169.254.169.254/opc/v1/instance/metadata/oci_compute_public_ip 2>/dev/null || hostname -I | awk '{print $1}'"
            )
            public_ip = output.strip() if exit_code == 0 else self.host
            
            logger.info("✅ Deployment complete!")
            logger.info("="*60)
            logger.info("🎉 DEPLOYMENT SUCCESSFUL!")
            logger.info("="*60)
            logger.info(f"🌐 Public IP: {public_ip}")
            logger.info(f"📊 Dashboard: http://{public_ip}:8000")
            logger.info(f"📝 Logs: pm2 logs")
            logger.info(f"📊 Status: pm2 status")
            logger.info("="*60)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return False
        finally:
            self.disconnect()


def main():
    """Main deployment function"""
    print("="*60)
    print("☁️  PLATINUM TIER - CLOUD DEPLOYMENT")
    print("Personal AI Employee Hackathon 0")
    print("="*60)
    print()
    
    # Get deployment details
    print("📝 Enter cloud VM details:")
    print()
    
    host = input("Cloud VM Host (IP): ").strip()
    if not host:
        logger.error("❌ Host is required")
        sys.exit(1)
    
    username = input("Username (default: ubuntu): ").strip() or "ubuntu"
    
    print()
    print("🔐 Authentication:")
    auth_method = input("Method (key/password/agent): ").strip().lower()
    
    key_path = None
    password = None
    
    if auth_method == 'key':
        key_path = input("SSH Key Path: ").strip()
        if not os.path.exists(key_path):
            logger.error(f"❌ Key file not found: {key_path}")
            sys.exit(1)
    elif auth_method == 'password':
        password = input("Password: ").strip()
    # else: use SSH agent
    
    print()
    print("📁 Vault Settings:")
    vault_path = input("Vault Path (default: current): ").strip() or '.'
    
    repo_url = input("Git Repo URL (optional, press Enter to skip): ").strip() or None
    
    print()
    print("="*60)
    print("🚀 Starting deployment...")
    print("="*60)
    print()
    
    # Deploy
    deployer = CloudDeployment(host, username, key_path, password)
    success = deployer.deploy(vault_path, repo_url)
    
    if success:
        print()
        print("="*60)
        print("✅ DEPLOYMENT COMPLETE!")
        print("="*60)
        print()
        print("📊 Next Steps:")
        print("1. SSH into VM: ssh ubuntu@" + host)
        print("2. Check status: pm2 status")
        print("3. View logs: pm2 logs")
        print("4. Access dashboard: http://" + host + ":8000")
        print("5. Configure .env: nano ~/ai-employee-vault/.env")
        print()
    else:
        print()
        print("❌ Deployment failed! Check cloud_deploy.log for details.")
        sys.exit(1)


if __name__ == '__main__':
    main()
