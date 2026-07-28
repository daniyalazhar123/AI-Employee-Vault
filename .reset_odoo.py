import psycopg2
conn = psycopg2.connect('host=localhost dbname=odoo user=odoo password=odoo')
cur = conn.cursor()
cur.execute("SELECT name, state FROM ir_module_module WHERE state='to install' ORDER BY name")
rows = cur.fetchall()
print('Modules stuck in to_install:', len(rows))
for r in rows[:10]:
    print(' ', r[0], r[1])
cur.execute("UPDATE ir_module_module SET state='uninstalled' WHERE state='to install'")
print('Reset', cur.rowcount, 'modules to uninstalled')
conn.commit()
cur.close()
conn.close()