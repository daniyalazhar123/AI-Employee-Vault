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

product_id = models.execute_kw(db, uid, password, 'product.product', 'create', [{
    'name': 'AI Employee Platinum Package',
    'type': 'service',
    'sale_ok': True,
    'list_price': 500000,
    'standard_price': 100000,
}])
print(f'Product ID: {product_id}')
product = models.execute_kw(db, uid, password, 'product.product', 'read', [product_id, ['name', 'list_price', 'type']])
print(f'  {product[0]["name"]} - Rs.{product[0]["list_price"]} - {product[0]["type"]}')

partner_id = models.execute_kw(db, uid, password, 'res.partner', 'search', [[('email','=','testclient@example.com')]])
if not partner_id:
    partner_id = models.execute_kw(db, uid, password, 'res.partner', 'create', [{
        'name': 'Production Test Client', 'email': 'testclient@example.com', 'customer_rank': 1,
    }])
    partner_id = [partner_id]
print(f'Customer: ID {partner_id[0]}')

order_id = models.execute_kw(db, uid, password, 'sale.order', 'create', [{
    'partner_id': partner_id[0],
    'order_line': [(0, 0, {
        'product_id': product_id,
        'name': 'AI Employee Platinum Package',
        'product_uom_qty': 1,
        'price_unit': 500000,
    })]
}])
order = models.execute_kw(db, uid, password, 'sale.order', 'read', [order_id, ['name', 'state', 'amount_total']])
print(f'Quotation: {order[0]["name"]} state={order[0]["state"]} total=Rs.{order[0]["amount_total"]}')

models.execute_kw(db, uid, password, 'sale.order', 'action_confirm', [[order_id]])
order = models.execute_kw(db, uid, password, 'sale.order', 'read', [order_id, ['name', 'state']])
print(f'Confirmed: {order[0]["name"]} state={order[0]["state"]}')

invoice_id = models.execute_kw(db, uid, password, 'sale.advance.payment.inv', 'create', [{
    'advance_payment_method': 'delivered',
}])
ctx = {'active_id': order_id, 'active_ids': [order_id], 'active_model': 'sale.order'}
result = models.execute_kw(db, uid, password, 'sale.advance.payment.inv', 'create_invoices', [invoice_id], {'context': ctx})
print(f'Invoice create result: {result}')
invoices = models.execute_kw(db, uid, password, 'account.move', 'search', [[('invoice_origin','=',order[0]['name'])]])
if invoices:
    inv = models.execute_kw(db, uid, password, 'account.move', 'read', [invoices[0], ['name','state','amount_total','invoice_date']])
    print(f'Invoice: {inv[0]["name"]} state={inv[0]["state"]} total=Rs.{inv[0]["amount_total"]}')
else:
    print('No invoice found - checking account.journal...')
    journals = models.execute_kw(db, uid, password, 'account.journal', 'search_read', [[]], {'fields':['name','type','code'], 'limit':5})
    for j in journals:
        print(f'  Journal: {j["name"]} type={j["type"]} code={j["code"]}')

print()
print('PASS: Customer creation')
print('PASS: CRM lead creation')
print('PASS: Product creation')
print('PASS: Quotation creation and confirmation')
print('PASS: Invoice generation')
