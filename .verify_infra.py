import sys, os, subprocess, json

print('=== ORACLE CLOUD ===')
ssh_dir = os.path.expanduser('~/.ssh')
ssh_config = os.path.join(ssh_dir, 'config')
oracle_found = False

if os.path.exists(ssh_config):
    with open(ssh_config) as f:
        for line in f:
            if 'oracle' in line.lower() or 'oci' in line.lower() or 'compute' in line.lower():
                oracle_found = True
                print(f'SSH config: {line.strip()}')

if os.path.exists(ssh_dir):
    for f in os.listdir(ssh_dir):
        if 'oracle' in f.lower() or 'oci' in f.lower():
            oracle_found = True
            print(f'SSH key: {f}')

# Try pinging the cloud orchestrator
sys.path.insert(0, r'D:\Desktop4\Obsidian Vault')
try:
    from cloud_orchestrator import CloudOrchestrator
    print('CloudOrchestrator module: AVAILABLE')
except Exception as e:
    print(f'CloudOrchestrator module: {e}')

# Check deploy scripts
deploy_sh = os.path.join(r'D:\Desktop4\Obsidian Vault', 'cloud', 'deploy.py')
deploy_cloud = os.path.join(r'D:\Desktop4\Obsidian Vault', 'cloud', 'deploy_cloud.py')
print(f'deploy.py exists: {os.path.exists(deploy_sh)}')
print(f'deploy_cloud.py exists: {os.path.exists(deploy_cloud)}')

if not oracle_found:
    print('ORACLE CLOUD: NOT CONFIGURED (no SSH keys/config found)')
    print('Deployment scripts exist but cloud VM is not set up on this machine')
else:
    print('ORACLE CLOUD: CONFIGURED')

print()
print('=== KUBERNETES ===')
kube_dir = os.path.expanduser('~/.kube')
config_file = os.path.join(kube_dir, 'config')

if os.path.exists(config_file):
    with open(config_file) as f:
        content = f.read()
    print('Kubeconfig exists')

# Check contexts
result = subprocess.run(['kubectl', 'config', 'get-contexts'], capture_output=True, text=True, timeout=10)
print(f'Contexts:\n{result.stdout}')

# Check if minikube or any cluster is reachable
result = subprocess.run(['kubectl', 'cluster-info', '--request-timeout', '5s'], capture_output=True, text=True, timeout=15)
if result.returncode == 0:
    print('Kubernetes cluster: REACHABLE')
else:
    err = result.stderr[:300]
    print(f'Kubernetes cluster: NOT REACHABLE ({err.strip()})')

print()
print('=== PM2 ===')
result = subprocess.run(['pm2', 'list'], capture_output=True, text=True, timeout=10)
print(result.stdout)
if 'pm2' in result.stdout.lower() or 'id' in result.stdout.lower():
    print('PM2: RUNNING')

# Check ecosystem
eco = os.path.join(r'D:\Desktop4\Obsidian Vault', 'ecosystem.config.js')
print(f'ecosystem.config.js: {os.path.exists(eco)}')

print()
print('=== WINDOWS TASK SCHEDULER ===')
result = subprocess.run(['powershell', '-Command', 'Get-ScheduledTask | Where-Object { $_.TaskName -like "*AI*" -or $_.TaskName -like "*Employee*" -or $_.TaskName -like "*Vault*" } | Select-Object TaskName,State'], capture_output=True, text=True, timeout=10)
output = result.stdout.strip()
if output:
    print(output)
    print('Windows Task Scheduler: TASKS FOUND')
else:
    print('No AI Employee scheduled tasks found')
    print('Windows Task Scheduler: NOT CONFIGURED (install_scheduled_tasks.ps1 available)')

# Check install script
install_script = os.path.join(r'D:\Desktop4\Obsidian Vault', 'install_scheduled_tasks.ps1')
print(f'install_scheduled_tasks.ps1 exists: {os.path.exists(install_script)}')

print()
print('=== VAULT SYNC (GIT) ===')
result = subprocess.run(['git', '-C', r'D:\Desktop4\Obsidian Vault', 'remote', '-v'], capture_output=True, text=True, timeout=10)
if result.returncode == 0:
    print(f'Git remotes:\n{result.stdout}')
    result2 = subprocess.run(['git', '-C', r'D:\Desktop4\Obsidian Vault', 'log', '--oneline', '-5'], capture_output=True, text=True, timeout=10)
    print(f'Recent commits:\n{result2.stdout}')
    print('VAULT SYNC: GIT CONFIGURED')
