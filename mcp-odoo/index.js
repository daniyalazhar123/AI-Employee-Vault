#!/usr/bin/env node

/**
 * MCP Odoo Server for AI Employee Vault
 * 
 * Provides Odoo ERP capabilities to Claude Code:
 * - create_invoice: Create customer invoices
 * - record_payment: Record payments
 * - get_invoices: List invoices
 * - get_leads: Get CRM leads
 * - update_lead: Update lead status
 * - get_transactions: Get bank transactions
 * - create_partner: Create customer/partner
 * 
 * Usage:
 *   node index.js
 * 
 * Configuration:
 *   Set ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD environment variables
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import xmlrpc from 'xmlrpc';

// Configuration
const ODOO_URL = process.env.ODOO_URL || 'http://localhost:8069';
const ODOO_DB = process.env.ODOO_DB || 'odoo';
const ODOO_USERNAME = process.env.ODOO_USERNAME || 'admin';
const ODOO_PASSWORD = process.env.ODOO_PASSWORD || 'admin';
const ODOO_API_KEY = process.env.ODOO_API_KEY || null;

// Odoo client
let odooUid = null;

/**
 * Parse Odoo URL to extract host and port
 */
function parseOdooUrl(url) {
  const parsed = new URL(url);
  return {
    host: parsed.hostname,
    port: parseInt(parsed.port) || 8069,
    path: parsed.pathname
  };
}

/**
 * Create Odoo XML-RPC client
 */
function createOdooClient() {
  const { host, port } = parseOdooUrl(ODOO_URL);
  
  return {
    common: xmlrpc.createClient({ host, port, path: '/xmlrpc/2/common' }),
    models: xmlrpc.createClient({ host, port, path: '/xmlrpc/2/object' })
  };
}

/**
 * Authenticate with Odoo
 */
async function authenticate() {
  return new Promise((resolve, reject) => {
    if (odooUid) {
      resolve(odooUid);
      return;
    }
    
    const client = createOdooClient();
    const params = ODOO_API_KEY ? { api_key: ODOO_API_KEY } : {};
    
    client.common.method_call(
      'authenticate',
      [ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, params],
      (error, uid) => {
        if (error) {
          reject(new Error(`Odoo authentication failed: ${error.message}`));
        } else if (!uid || typeof uid !== 'number') {
          reject(new Error('Odoo authentication failed: Invalid response'));
        } else {
          odooUid = uid;
          console.error(`Odoo authenticated as UID: ${uid}`);
          resolve(uid);
        }
      }
    );
  });
}

/**
 * Execute Odoo model method
 */
async function executeModel(method, model, args = [], kwargs = {}) {
  try {
    const uid = await authenticate();
    const client = createOdooClient();
    
    return new Promise((resolve, reject) => {
      client.models.method_call(
        method,
        [ODOO_DB, uid, ODOO_PASSWORD, model, ...args],
        kwargs,
        (error, result) => {
          if (error) {
            reject(new Error(`Odoo ${method} failed: ${error.message}`));
          } else {
            resolve(result);
          }
        }
      );
    });
  } catch (error) {
    console.error('Error executing model method:', error.message);
    throw error;
  }
}

/**
 * Search records
 */
async function searchRecords(model, domain, options = {}) {
  try {
    const kwargs = {
      context: options.context || {},
      offset: options.offset || 0,
      limit: options.limit || 80,
      order: options.order || ''
    };
    
    const ids = await executeModel('execute_kw', model, [domain], kwargs);
    return ids;
  } catch (error) {
    console.error(`Error searching ${model}:`, error.message);
    throw error;
  }
}

/**
 * Search and read records
 */
async function searchReadRecords(model, domain, fields = [], options = {}) {
  try {
    const kwargs = {
      context: options.context || {},
      offset: options.offset || 0,
      limit: options.limit || 80,
      order: options.order || '',
      fields: fields
    };
    
    const records = await executeModel('execute_kw', model, [domain], kwargs);
    return records;
  } catch (error) {
    console.error(`Error search_read ${model}:`, error.message);
    throw error;
  }
}

/**
 * Create record
 */
async function createRecord(model, values) {
  try {
    const id = await executeModel('execute_kw', model, [[values]]);
    return id;
  } catch (error) {
    console.error(`Error creating ${model}:`, error.message);
    throw error;
  }
}

/**
 * Update record
 */
async function updateRecord(model, id, values) {
  try {
    await executeModel('execute_kw', model, [[id], values]);
    return true;
  } catch (error) {
    console.error(`Error updating ${model}:`, error.message);
    throw error;
  }
}

/**
 * Delete record
 */
async function deleteRecord(model, id) {
  try {
    await executeModel('execute_kw', model, [[id]]);
    return true;
  } catch (error) {
    console.error(`Error deleting ${model}:`, error.message);
    throw error;
  }
}

/**
 * Create customer invoice
 */
async function createInvoice({ partner_id, invoice_date, due_date, lines, payment_term_id = null }) {
  try {
    // Create invoice
    const invoiceData = {
      move_type: 'out_invoice',
      partner_id: partner_id,
      invoice_date: invoice_date || new Date().toISOString().split('T')[0],
      invoice_date_due: due_date,
      payment_term_id: payment_term_id,
      invoice_line_ids: []
    };
    
    // Add invoice lines
    for (const line of lines) {
      invoiceData.invoice_line_ids.push([0, 0, {
        product_id: line.product_id,
        name: line.name || line.description,
        quantity: line.quantity || 1,
        price_unit: line.price_unit || line.price,
        tax_ids: line.tax_ids ? [[6, 0, line.tax_ids]] : []
      }]);
    }
    
    const invoiceId = await createRecord('account.move', invoiceData);
    
    return {
      success: true,
      invoice_id: invoiceId,
      message: `Invoice ${invoiceId} created successfully`
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Record payment
 */
async function recordPayment({ invoice_id, amount, payment_date, payment_method = 'manual', reference = null }) {
  try {
    // Create payment register
    const paymentData = {
      move_ids: [[6, 0, [invoice_id]]],
      payment_date: payment_date || new Date().toISOString().split('T')[0],
      amount: amount,
      payment_method_id: payment_method,
      payment_reference: reference
    };
    
    // In Odoo 19+, use account.payment.register
    const registerId = await createRecord('account.payment.register', paymentData);
    
    // Create payments
    await executeModel('execute_kw', 'account.payment.register', [[registerId], 'create_payments']);
    
    return {
      success: true,
      message: `Payment of ${amount} recorded for invoice ${invoice_id}`
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Get invoices
 */
async function getInvoices({ state = 'posted', limit = 10, partner_id = null }) {
  try {
    const domain = [
      ['move_type', 'in', ['out_invoice', 'in_invoice']],
      ['state', '=', state]
    ];
    
    if (partner_id) {
      domain.push(['partner_id', '=', partner_id]);
    }
    
    const invoices = await searchReadRecords(
      'account.move',
      domain,
      ['id', 'name', 'partner_id', 'invoice_date', 'amount_total', 'amount_residual', 'state'],
      { limit }
    );
    
    return {
      success: true,
      count: invoices.length,
      invoices: invoices.map(inv => ({
        id: inv.id,
        number: inv.name,
        partner: inv.partner_id?.[1] || 'Unknown',
        date: inv.invoice_date,
        total: inv.amount_total,
        due: inv.amount_residual,
        state: inv.state
      })),
      message: `Retrieved ${invoices.length} invoices`
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Get CRM leads
 */
async function getLeads({ stage = null, limit = 10, my_leads = false }) {
  try {
    const domain = [];
    
    if (stage) {
      domain.push(['stage_id', '=', stage]);
    }
    
    if (my_leads) {
      domain.push(['user_id', '=', odooUid]);
    }
    
    const leads = await searchReadRecords(
      'crm.lead',
      domain,
      ['id', 'name', 'partner_name', 'email_from', 'phone', 'company_name', 'priority', 'stage_id', 'create_date'],
      { limit }
    );
    
    return {
      success: true,
      count: leads.length,
      leads: leads.map(lead => ({
        id: lead.id,
        name: lead.name,
        partner: lead.partner_name,
        email: lead.email_from,
        phone: lead.phone,
        company: lead.company_name,
        priority: lead.priority,
        stage: lead.stage_id?.[1] || 'Unknown',
        created: lead.create_date
      })),
      message: `Retrieved ${leads.length} leads`
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Update lead
 */
async function updateLead({ lead_id, values }) {
  try {
    await updateRecord('crm.lead', lead_id, values);
    
    return {
      success: true,
      message: `Lead ${lead_id} updated successfully`
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Get bank transactions
 */
async function getTransactions({ account_id = null, limit = 20 }) {
  try {
    const domain = [];
    
    if (account_id) {
      domain.push(['account_id', '=', account_id]);
    }
    
    const transactions = await searchReadRecords(
      'account.bank.statement.line',
      domain,
      ['id', 'name', 'amount', 'date', 'partner_name', 'ref', 'narration'],
      { limit, order: 'date DESC' }
    );
    
    return {
      success: true,
      count: transactions.length,
      transactions: transactions.map(txn => ({
        id: txn.id,
        name: txn.name,
        amount: txn.amount,
        date: txn.date,
        partner: txn.partner_name,
        ref: txn.ref,
        description: txn.narration
      })),
      message: `Retrieved ${transactions.length} transactions`
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Create partner (customer/vendor)
 */
async function createPartner({ name, email = null, phone = null, company_name = null, is_customer = true }) {
  try {
    const partnerData = {
      name: name,
      email: email,
      phone: phone,
      company_name: company_name,
      customer_rank: is_customer ? 1 : 0
    };
    
    const partnerId = await createRecord('res.partner', partnerData);
    
    return {
      success: true,
      partner_id: partnerId,
      message: `Partner ${name} created successfully`
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Search partners
 */
async function searchPartners({ query, limit = 10 }) {
  try {
    const domain = query ? [
      ['|', ['name', 'ilike', query], ['email', 'ilike', query]]
    ] : [];
    
    const partners = await searchReadRecords(
      'res.partner',
      domain,
      ['id', 'name', 'email', 'phone', 'company_name'],
      { limit }
    );
    
    return {
      success: true,
      count: partners.length,
      partners: partners.map(p => ({
        id: p.id,
        name: p.name,
        email: p.email,
        phone: p.phone,
        company: p.company_name
      })),
      message: `Found ${partners.length} partners`
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

// Create MCP Server
const server = new Server(
  {
    name: 'mcp-odoo-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'create_invoice',
        description: 'Create a customer invoice in Odoo',
        inputSchema: {
          type: 'object',
          properties: {
            partner_id: {
              type: 'number',
              description: 'Customer/partner ID'
            },
            invoice_date: {
              type: 'string',
              description: 'Invoice date (YYYY-MM-DD)'
            },
            due_date: {
              type: 'string',
              description: 'Due date (YYYY-MM-DD)'
            },
            lines: {
              type: 'array',
              description: 'Invoice line items',
              items: {
                type: 'object',
                properties: {
                  product_id: { type: 'number' },
                  name: { type: 'string' },
                  quantity: { type: 'number' },
                  price_unit: { type: 'number' }
                }
              }
            }
          },
          required: ['partner_id', 'lines']
        }
      },
      {
        name: 'record_payment',
        description: 'Record a payment for an invoice',
        inputSchema: {
          type: 'object',
          properties: {
            invoice_id: {
              type: 'number',
              description: 'Invoice ID'
            },
            amount: {
              type: 'number',
              description: 'Payment amount'
            },
            payment_date: {
              type: 'string',
              description: 'Payment date (YYYY-MM-DD)'
            },
            reference: {
              type: 'string',
              description: 'Payment reference'
            }
          },
          required: ['invoice_id', 'amount']
        }
      },
      {
        name: 'get_invoices',
        description: 'List invoices from Odoo',
        inputSchema: {
          type: 'object',
          properties: {
            state: {
              type: 'string',
              description: 'Invoice state (draft, posted, cancel)',
              default: 'posted'
            },
            limit: {
              type: 'number',
              description: 'Maximum results',
              default: 10
            },
            partner_id: {
              type: 'number',
              description: 'Filter by partner ID'
            }
          }
        }
      },
      {
        name: 'get_leads',
        description: 'Get CRM leads from Odoo',
        inputSchema: {
          type: 'object',
          properties: {
            stage: {
              type: 'string',
              description: 'Filter by stage'
            },
            limit: {
              type: 'number',
              description: 'Maximum results',
              default: 10
            },
            my_leads: {
              type: 'boolean',
              description: 'Only show my leads',
              default: false
            }
          }
        }
      },
      {
        name: 'update_lead',
        description: 'Update a CRM lead',
        inputSchema: {
          type: 'object',
          properties: {
            lead_id: {
              type: 'number',
              description: 'Lead ID'
            },
            values: {
              type: 'object',
              description: 'Fields to update'
            }
          },
          required: ['lead_id', 'values']
        }
      },
      {
        name: 'get_transactions',
        description: 'Get bank transactions',
        inputSchema: {
          type: 'object',
          properties: {
            account_id: {
              type: 'number',
              description: 'Bank account ID'
            },
            limit: {
              type: 'number',
              description: 'Maximum results',
              default: 20
            }
          }
        }
      },
      {
        name: 'create_partner',
        description: 'Create a new customer/partner',
        inputSchema: {
          type: 'object',
          properties: {
            name: {
              type: 'string',
              description: 'Partner name'
            },
            email: {
              type: 'string',
              description: 'Email address'
            },
            phone: {
              type: 'string',
              description: 'Phone number'
            },
            company_name: {
              type: 'string',
              description: 'Company name'
            },
            is_customer: {
              type: 'boolean',
              description: 'Mark as customer',
              default: true
            }
          },
          required: ['name']
        }
      },
      {
        name: 'search_partners',
        description: 'Search for partners/customers',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Search query (name or email)'
            },
            limit: {
              type: 'number',
              description: 'Maximum results',
              default: 10
            }
          }
        }
      }
    ]
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  try {
    switch (name) {
      case 'create_invoice':
        return { content: [{ type: 'text', text: JSON.stringify(await createInvoice(args), null, 2) }] };
      case 'record_payment':
        return { content: [{ type: 'text', text: JSON.stringify(await recordPayment(args), null, 2) }] };
      case 'get_invoices':
        return { content: [{ type: 'text', text: JSON.stringify(await getInvoices(args), null, 2) }] };
      case 'get_leads':
        return { content: [{ type: 'text', text: JSON.stringify(await getLeads(args), null, 2) }] };
      case 'update_lead':
        return { content: [{ type: 'text', text: JSON.stringify(await updateLead(args), null, 2) }] };
      case 'get_transactions':
        return { content: [{ type: 'text', text: JSON.stringify(await getTransactions(args), null, 2) }] };
      case 'create_partner':
        return { content: [{ type: 'text', text: JSON.stringify(await createPartner(args), null, 2) }] };
      case 'search_partners':
        return { content: [{ type: 'text', text: JSON.stringify(await searchPartners(args), null, 2) }] };
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [{ type: 'text', text: JSON.stringify({ success: false, error: error.message }, null, 2) }],
      isError: true
    };
  }
});

// Start server
async function main() {
  console.error('MCP Odoo Server starting...');
  console.error(`Odoo URL: ${ODOO_URL}`);
  console.error(`Database: ${ODOO_DB}`);
  console.error(`Username: ${ODOO_USERNAME}`);
  
  try {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error('MCP Odoo Server running on stdio');
    
    // Test connection
    try {
      await authenticate();
      console.error('✅ Odoo connection successful');
    } catch (error) {
      console.error('⚠️ Odoo connection failed:', error.message);
    }
  } catch (error) {
    console.error('Error starting server:', error);
    process.exit(1);
  }
}

main();
