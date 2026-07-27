import xmlrpc.client
import time
import sys

url = 'http://localhost:8069'
db = 'odoo'
username = 'admin'
password = 'admin'

print('Waiting for Odoo to be ready...')
for i in range(30):
    try:
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        v = common.version()
        print(f'Odoo ready: {v["server_version"]}')
        break
    except Exception as e:
        print(f'  Attempt {i+1}: {e}')
        time.sleep(2)
else:
    print('Odoo did not become ready')
    sys.exit(1)

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
uid = common.authenticate(db, username, password, {})
print(f'UID: {uid}')

targets = ['crm', 'sale', 'sale_management', 'account', 'account_accountant', 'purchase', 'stock']

for mod_name in targets:
    available = models.execute_kw(db, uid, password, 'ir.module.module', 'search_read',
        [[('name','=',mod_name)]],
        {'fields':['name','display_name','state'], 'limit':1})
    if not available:
        print(f'{mod_name}: not found in Odoo')
        continue
    m = available[0]
    print(f'{m["name"]:25s} state={m["state"]:15s}', end='')
    if m['state'] == 'uninstalled':
        try:
            result = models.execute_kw(db, uid, password, 'ir.module.module',
                'button_immediate_install', [[m['id']]])
            print(f' INSTALLED')
        except Exception as e:
            print(f' INSTALL FAILED: {e}')
    elif m['state'] == 'installed':
        print(f' already installed')
    elif m['state'] == 'to install':
        print(f' queued for install')

print()
print('Verifying final state...')
installed = models.execute_kw(db, uid, password, 'ir.module.module', 'search_read',
    [[('name','in',targets)]],
    {'fields':['name','state'], 'limit':20})
for m in installed:
    print(f'  {m["name"]:25s} -> {m["state"]}')
