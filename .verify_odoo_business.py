import xmlrpc.client
from datetime import datetime

url = 'http://localhost:8069'
db = 'odoo'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
uid = common.authenticate(db, username, password, {})
print(f'UID: {uid}')

# 1. Create a customer (res.partner)
print('\n=== 1. CREATE CUSTOMER ===')
partner_id = models.execute_kw(db, uid, password, 'res.partner', 'create', [{
    'name': 'Production Test Client',
    'email': 'testclient@example.com',
    'phone': '+92-300-1234567',
    'company_type': 'company',
    'customer_rank': 1,
}])
print(f'Customer created: ID {partner_id}')
partner = models.execute_kw(db, uid, password, 'res.partner', 'read', [partner_id, ['name', 'email']])
print(f'  Name: {partner[0]["name"]}, Email: {partner[0]["email"]}')

# 2. Create a CRM lead
print('\n=== 2. CREATE CRM LEAD ===')
lead_id = models.execute_kw(db, uid, password, 'crm.lead', 'create', [{
    'name': 'Production Test Deal - AI Employee',
    'partner_name': 'Production Test Client',
    'email_from': 'testclient@example.com',
    'phone': '+92-300-1234567',
    'description': 'Interested in AI Employee Platinum Tier package',
    'priority': '3',
    'expected_revenue': 500000,
}])
print(f'Lead created: ID {lead_id}')
lead = models.execute_kw(db, uid, password, 'crm.lead', 'read', [lead_id, ['name', 'expected_revenue', 'priority']])
print(f'  Name: {lead[0]["name"]}, Revenue: {lead[0]["expected_revenue"]}, Priority: {lead[0]["priority"]}')

# 3. Create a sales quotation (sale.order)
print('\n=== 3. CREATE QUOTATION ===')
product_id = models.execute_kw(db, uid, password, 'product.product', 'search', [[('sale_ok','=',True)]], {'limit':1})
if product_id:
    product = models.execute_kw(db, uid, password, 'product.product', 'read', [product_id[0], ['name', 'list_price']])
    print(f'Using product: {product[0]["name"]} @ {product[0]["list_price"]}')
    order_id = models.execute_kw(db, uid, password, 'sale.order', 'create', [{
        'partner_id': partner_id,
        'date_order': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'order_line': [(0, 0, {
            'product_id': product_id[0],
            'name': product[0]['name'],
            'product_uom_qty': 1,
            'price_unit': product[0]['list_price'],
        })]
    }])
    print(f'Quotation created: ID {order_id}')
    order = models.execute_kw(db, uid, password, 'sale.order', 'read', [order_id, ['name', 'state', 'amount_total']])
    print(f'  Name: {order[0]["name"]}, State: {order[0]["state"]}, Total: {order[0]["amount_total"]}')
    
    # Confirm the quotation
    models.execute_kw(db, uid, password, 'sale.order', 'action_confirm', [[order_id]])
    order = models.execute_kw(db, uid, password, 'sale.order', 'read', [order_id, ['name', 'state', 'amount_total']])
    print(f'  After confirm: State={order[0]["state"]}')
    
    # 4. Create invoice from sale order
    print('\n=== 4. CREATE INVOICE ===')
    invoice_data = models.execute_kw(db, uid, password, 'sale.order', 'action_create_invoice', [[order_id]])
    print(f'Invoice creation result: {invoice_data}')
else:
    print('No saleable product found')

# 5. List all installed modules for audit
print('\n=== 5. INSTALLED BUSINESS MODULES ===')
installed = models.execute_kw(db, uid, password, 'ir.module.module', 'search_read',
    [[('state','=','installed')]],
    {'fields':['name','display_name'], 'limit':80})
business_modules = [m for m in installed if m['name'] in ['crm','sale','sale_management','account','purchase','stock']]
for m in business_modules:
    print(f'  {m["name"]:20s} -> {m["display_name"]}')

print('\n=== ODOO VERIFICATION COMPLETE ===')
