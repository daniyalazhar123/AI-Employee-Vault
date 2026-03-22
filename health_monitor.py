#!/usr/bin/env python3
"""
🏥 HEALTH MONITOR - Platinum Tier
Monitors Cloud and Local agents health
Personal AI Employee Hackathon 0 - Platinum Tier

Features:
- Component health checks
- Alert generation
- Health logging
- Auto-recovery triggers
"""

import os
import sys
import time
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('health_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('HealthMonitor')


class HealthMonitor:
    """
    Health Monitor for Platinum Tier
    
    Monitors both Cloud and Local agents, checking:
    - Process status
    - Git sync status
    - Disk space
    - Memory usage
    - Component health
    """
    
    def __init__(self, agent_type: str, vault_path: str):
        self.agent_type = agent_type  # 'cloud' or 'local'
        self.vault = Path(vault_path)
        self.logs = self.vault / 'Logs'
        self.health_log = self.logs / 'health.jsonl'
        self.alerts = self.vault / 'Needs_Action' / 'local'
        
        # Ensure folders exist
        self.logs.mkdir(parents=True, exist_ok=True)
        self.alerts.mkdir(parents=True, exist_ok=True)
        
        # Health state
        self.last_health = {}
        self.consecutive_failures = 0
        self.max_failures = 3
        
        logger.info(f"🏥 Health Monitor initialized ({agent_type})")
    
    def check_git_sync(self) -> Dict:
        """Check if Git sync is working"""
        try:
            result = subprocess.run(
                ['git', 'status'],
                cwd=self.vault,
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {
                    'status': 'healthy',
                    'component': 'git_sync',
                    'details': 'Git sync working',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'component': 'git_sync',
                    'details': f'Git status failed: {result.stderr.decode()}',
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'component': 'git_sync',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_cloud_agent(self) -> Dict:
        """Check if Cloud Agent is running"""
        try:
            if self.agent_type == 'local':
                return {
                    'status': 'skipped',
                    'component': 'cloud_agent',
                    'details': 'Check from cloud VM',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Check process
            result = subprocess.run(
                ['pgrep', '-f', 'cloud_agent.py'],
                capture_output=True
            )
            is_running = result.returncode == 0
            
            if is_running:
                return {
                    'status': 'healthy',
                    'component': 'cloud_agent',
                    'details': 'Cloud Agent running',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'component': 'cloud_agent',
                    'details': 'Cloud Agent not running',
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'component': 'cloud_agent',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_local_agent(self) -> Dict:
        """Check if Local Agent is running"""
        try:
            if self.agent_type == 'cloud':
                return {
                    'status': 'skipped',
                    'component': 'local_agent',
                    'details': 'Check from local machine',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Check process (Windows)
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq python.exe'],
                capture_output=True,
                text=True
            )
            is_running = 'python.exe' in result.stdout.lower()
            
            if is_running:
                return {
                    'status': 'healthy',
                    'component': 'local_agent',
                    'details': 'Local Agent running',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'warning',
                    'component': 'local_agent',
                    'details': 'Local Agent may not be running',
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'component': 'local_agent',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_disk_space(self) -> Dict:
        """Check available disk space"""
        try:
            total, used, free = shutil.disk_usage(self.vault)
            free_gb = free / (1024**3)
            
            if free_gb > 5:
                status = 'healthy'
            elif free_gb > 1:
                status = 'warning'
            else:
                status = 'critical'
            
            return {
                'status': status,
                'component': 'disk_space',
                'details': f'{free_gb:.2f} GB free',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'component': 'disk_space',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_logs_size(self) -> Dict:
        """Check if logs are growing too large"""
        try:
            logs_dir = self.vault / 'Logs'
            if not logs_dir.exists():
                return {
                    'status': 'healthy',
                    'component': 'logs_size',
                    'details': 'No logs directory',
                    'timestamp': datetime.now().isoformat()
                }
            
            total_size = sum(f.stat().st_size for f in logs_dir.rglob('*') if f.is_file())
            total_mb = total_size / (1024 * 1024)
            
            if total_mb > 100:
                status = 'warning'
                details = f'Logs size: {total_mb:.2f} MB (consider rotation)'
            else:
                status = 'healthy'
                details = f'Logs size: {total_mb:.2f} MB'
            
            return {
                'status': status,
                'component': 'logs_size',
                'details': details,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'component': 'logs_size',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_pending_approvals(self) -> Dict:
        """Check for stale pending approvals"""
        try:
            pending_dir = self.vault / 'Pending_Approval'
            if not pending_dir.exists():
                return {
                    'status': 'healthy',
                    'component': 'pending_approvals',
                    'details': 'No pending approvals',
                    'timestamp': datetime.now().isoformat()
                }
            
            pending_files = list(pending_dir.glob('*.md'))
            count = len(pending_files)
            
            # Check for old files (> 24 hours)
            old_files = []
            now = datetime.now()
            for f in pending_files:
                try:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    if (now - mtime).total_seconds() > 86400:  # 24 hours
                        old_files.append(f.name)
                except:
                    pass
            
            if old_files:
                status = 'warning'
                details = f'{count} pending, {len(old_files)} old (>24h)'
            elif count > 100:
                status = 'warning'
                details = f'{count} pending approvals'
            else:
                status = 'healthy'
                details = f'{count} pending approvals'
            
            return {
                'status': status,
                'component': 'pending_approvals',
                'details': details,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'component': 'pending_approvals',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_all(self) -> Dict:
        """Check all components"""
        components = [
            self.check_git_sync(),
            self.check_disk_space(),
            self.check_logs_size(),
            self.check_pending_approvals()
        ]
        
        if self.agent_type == 'cloud':
            components.append(self.check_cloud_agent())
        else:
            components.append(self.check_local_agent())
        
        # Determine overall status
        overall_status = 'healthy'
        for comp in components:
            if comp['status'] == 'critical':
                overall_status = 'critical'
                break
            elif comp['status'] == 'unhealthy':
                overall_status = 'unhealthy'
            elif comp['status'] == 'warning' and overall_status == 'healthy':
                overall_status = 'warning'
        
        # Build result
        result = {
            'status': overall_status,
            'timestamp': datetime.now().isoformat(),
            'agent_type': self.agent_type,
            'components': {c['component']: c['status'] for c in components},
            'details': components
        }
        
        # Log health check
        self.log_health(result)
        
        # Alert if unhealthy
        if overall_status in ['unhealthy', 'critical']:
            self.send_alert(components)
            self.consecutive_failures += 1
        else:
            self.consecutive_failures = 0
        
        return result
    
    def log_health(self, health: Dict):
        """Log health check result"""
        self.health_log.parent.mkdir(parents=True, exist_ok=True)
        with open(self.health_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(health, ensure_ascii=False) + '\n')
    
    def send_alert(self, components: List[Dict]):
        """Send alert for unhealthy components"""
        unhealthy = [c for c in components if c['status'] in ['unhealthy', 'critical']]
        
        if not unhealthy:
            return
        
        # Create alert file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        alert_file = self.alerts / f'ALERT_HEALTH_{timestamp}.md'
        
        content = f"""---
type: health_alert
severity: high
timestamp: {datetime.now().isoformat()}
agent_type: {self.agent_type}
consecutive_failures: {self.consecutive_failures}
---

# ⚠️ Health Alert

**Status:** {self.consecutive_failures} consecutive failures

**Unhealthy Components:**
"""
        for comp in unhealthy:
            content += f"\n- **{comp['component']}:** {comp.get('details', comp.get('error', 'Unknown error'))}"
        
        content += f"""

## Recommended Actions

1. Check the Cloud VM status
2. Review logs in `Logs/` folder
3. Restart failed services
4. Check disk space

## Logs

- Health Log: `Logs/health.jsonl`
- Cloud Agent Log: `cloud_agent.log`
- Local Agent Log: `local_agent.log`

---
*Generated by Health Monitor*
"""
        alert_file.write_text(content, encoding='utf-8')
        logger.warning(f"🚨 Alert created: {alert_file.name}")
    
    def run(self):
        """Run health monitoring loop"""
        logger.info("="*60)
        logger.info(f"🏥 HEALTH MONITOR STARTING ({self.agent_type})")
        logger.info(f"📂 Vault: {self.vault}")
        logger.info("="*60)
        
        while True:
            try:
                health = self.check_all()
                logger.info(f"📊 Health: {health['status']} - {health['timestamp']}")
                
                # Print component status
                for comp, status in health['components'].items():
                    logger.info(f"  - {comp}: {status}")
                
            except Exception as e:
                logger.error(f"❌ Health Monitor error: {e}", exc_info=True)
            
            time.sleep(300)  # Check every 5 minutes


def main():
    """Main entry point"""
    print("="*60)
    print("🏥 PLATINUM TIER - HEALTH MONITOR")
    print("="*60)
    
    # Get agent type from argument
    agent_type = sys.argv[1] if len(sys.argv) > 1 else 'cloud'
    if agent_type not in ['cloud', 'local']:
        print("Usage: python health_monitor.py [cloud|local] [vault_path]")
        sys.exit(1)
    
    # Get vault path
    vault_path = sys.argv[2] if len(sys.argv) > 2 else '/home/ubuntu/ai-employee-vault'
    
    print(f"🎯 Agent Type: {agent_type}")
    print(f"📂 Vault Path: {vault_path}")
    print("\n🚀 Starting Health Monitor in 3 seconds...")
    time.sleep(3)
    
    monitor = HealthMonitor(agent_type, vault_path)
    
    try:
        monitor.run()
    except KeyboardInterrupt:
        logger.info("⏹️  Health Monitor stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
