# AI Employee Vault - System Architecture

**Version:** 1.0.0  
**Tier:** Gold Tier - Personal AI Employee Hackathon 0  
**Primary Engine:** opencode CLI v0.12.6  
**Last Updated:** March 22, 2026

---

## =ƒôï Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Descriptions](#component-descriptions)
4. [Data Flow](#data-flow)
5. [Security Architecture](#security-architecture)
6. [Deployment Options](#deployment-options)
7. [Extension Guide](#extension-guide)
8. [Troubleshooting](#troubleshooting)
9. [Performance Considerations](#performance-considerations)
10. [opencode CLI Integration](#opencode-cli-integration)

---

## System Overview

The AI Employee Vault is an autonomous automation system that manages business communications and operations 24/7. It uses a **perception-reasoning-action** architecture inspired by cognitive systems.

### Core Principles

- **Local-First:** All data stays on your machine (Obsidian vault)
- **Human-in-the-Loop:** Nothing sends without approval
- **Credential Isolation:** Secrets never touch the vault
- **Audit Trail:** Every action is logged
- **Extensible:** Easy to add new watchers and MCP servers

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Perception** | Python Watchers | Detect changes in external sources |
| **Reasoning** | opencode CLI v0.12.6 | Analyze, plan, decide |
| **Action** | MCP Servers | Execute tasks (email, browser, Odoo) |
| **Memory** | Obsidian Vault | Persistent Markdown storage |
| **GUI** | Obsidian App | Human-readable dashboard |

---

## Architecture Diagram

### High-Level System View

```
GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ
Göé                           EXTERNAL SOURCES                                   Göé
Göé  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ     Göé
Göé  Göé  Gmail   Göé  Göé WhatsApp Göé  Göé  Odoo    Göé  Göé Social   Göé  Göé  Office  Göé     Göé
Göé  Göé  Inbox   Göé  Göé  Web     Göé  Göé  CRM     Göé  Göé  Media   Göé  Göé  Files   Göé     Göé
Göé  GööGöÇGöÇGöÇGöÇGö¼GöÇGöÇGöÇGöÇGöÇGöÿ  GööGöÇGöÇGöÇGöÇGö¼GöÇGöÇGöÇGöÇGöÇGöÿ  GööGöÇGöÇGöÇGöÇGö¼GöÇGöÇGöÇGöÇGöÇGöÿ  GööGöÇGöÇGöÇGöÇGö¼GöÇGöÇGöÇGöÇGöÇGöÿ  GööGöÇGöÇGöÇGöÇGö¼GöÇGöÇGöÇGöÇGöÇGöÿ     Göé
GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGö+GöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGö+GöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGö+GöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGö+GöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGö+GöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ
        Göé            Göé            Göé            Göé            Göé
        Gû+            Gû+            Gû+            Gû+            Gû+
GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ
Göé                        WATCHERS (Perception Layer)                           Göé
Göé  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ   Göé
Göé  Göé    Gmail     Göé  Göé   WhatsApp   Göé  Göé     Odoo     Göé  Göé    Social    Göé   Göé
Göé  Göé   Watcher    Göé  Göé   Watcher    Göé  Göé   Watcher    Göé  Göé   Watcher    Göé   Göé
Göé  Göé  (2 min)     Göé  Göé  (30 sec)    Göé  Göé  (5 min)     Göé  Göé  (60 sec)    Göé   Göé
Göé  GööGöÇGöÇGöÇGöÇGöÇGöÇGö¼GöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ  GööGöÇGöÇGöÇGöÇGöÇGöÇGö¼GöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ  GööGöÇGöÇGöÇGöÇGöÇGöÇGö¼GöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ  GööGöÇGöÇGöÇGöÇGöÇGöÇGö¼GöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ   Göé
Göé         Göé                 Göé                 Göé                 Göé            Göé
Göé         GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGö¼Gö¦GöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGö¼Gö¦GöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ            Göé
Göé                          Göé                 Göé                              Göé
Göé                          Gû+                 Gû+                              Göé
Göé               GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ                    Göé
Göé               Göé     office_watcher.py (1 sec)        Göé                    Göé
Göé               Göé     File system monitoring           Göé                    Göé
Göé               GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ                    Göé
GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ
                          Göé
                          Göé Create Action Files
                          Gû+
GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ
Göé                      OBSIDIAN VAULT (Memory / GUI)                           Göé
Göé                                                                              Göé
Göé  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ    Göé
Göé  Göé  Needs_Action/                                                      Göé    Göé
Göé  Göé  Gö£GöÇGöÇ EMAIL_20260322_143022.md  GåÉ New email detected                Göé    Göé
Göé  Göé  Gö£GöÇGöÇ WHATSAPP_20260322_144511.md GåÉ WhatsApp message               Göé    Göé
Göé  Göé  GööGöÇGöÇ ODOO_LEAD_20260322_150000.md GåÉ New CRM lead                  Göé    Göé
Göé  GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ    Göé
Göé                          Göé                                                  Göé
Göé                          Gû+ (processed by opencode CLI)                         Göé
Göé  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ    Göé
Göé  Göé  Pending_Approval/                                                  Göé    Göé
Göé  Göé  Gö£GöÇGöÇ REPLY_EMAIL_20260322_143022.md  GåÉ Draft reply ready          Göé    Göé
Göé  Göé  Gö£GöÇGöÇ POST_LINKEDIN_20260322_160000.md GåÉ Social post draft        Göé    Göé
Göé  Göé  GööGöÇGöÇ TASK_20260322_170000.md GåÉ Task approval request              Göé    Göé
Göé  GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ    Göé
Göé                          Göé                                                  Göé
Göé                          Gû+ (after human approval)                          Göé
Göé  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ    Göé
Göé  Göé  Approved/  GåÆ  Done/                                                Göé    Göé
Göé  Göé  (Ready for execution)        (Completed + audit log)              Göé    Göé
Göé  GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ    Göé
Göé                                                                              Göé
GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ
                          Göé
                          Göé Trigger MCP Actions
                          Gû+
GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ
Göé                        MCP SERVERS (Action Layer)                            Göé
Göé                                                                              Göé
Göé  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ   Göé
Göé  Göé  mcp-email   Göé  Göé mcp-browser  Göé  Göé  mcp-odoo    Göé  Göé mcp-social   Göé   Göé
Göé  Göé              Göé  Göé              Göé  Göé              Göé  Göé              Göé   Göé
Göé  Göé GÇó send_email Göé  Göé GÇó navigate   Göé  Göé GÇó create_    Göé  Göé GÇó post_      Göé   Göé
Göé  Göé GÇó draft_emailGöé  Göé GÇó click      Göé  Göé   invoice    Göé  Göé   linkedin   Göé   Göé
Göé  Göé GÇó list_emailsGöé  Göé GÇó type       Göé  Göé GÇó read_      Göé  Göé GÇó post_      Göé   Göé
Göé  Göé              Göé  Göé GÇó screenshot Göé  Göé   accounting Göé  Göé   twitter    Göé   Göé
Göé  Göé              Göé  Göé GÇó form_fill  Göé  Göé GÇó list_      Göé  Göé GÇó generate_  Göé   Göé
Göé  Göé              Göé  Göé              Göé  Göé   partners   Göé  Göé   summary    Göé   Göé
Göé  GööGöÇGöÇGöÇGöÇGöÇGöÇGö¼GöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ  GööGöÇGöÇGöÇGöÇGöÇGöÇGö¼GöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ  GööGöÇGöÇGöÇGöÇGöÇGöÇGö¼GöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ  GööGöÇGöÇGöÇGöÇGöÇGöÇGö¼GöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ   Göé
GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGö+GöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGö+GöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGö+GöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGö+GöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ
          Göé                 Göé                 Göé                 Göé
          Gû+                 Gû+                 Gû+                 Gû+
GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ
Göé                           EXTERNAL ACTIONS                                   Göé
Göé  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ                    Göé
Göé  Göé  Email   Göé  Göé  Browser Göé  Göé   Odoo   Göé  Göé  Social  Göé                    Göé
Göé  Göé  Sent    Göé  Göé  Actions Göé  Göé  Updated Göé  Göé  Posted  Göé                    Göé
Göé  GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ  GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ  GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ  GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ                    Göé
GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ
                          Göé
                          Gû+
GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ
Göé                        RALPH LOOP (Persistence)                              Göé
Göé  GÇó Tracks multi-step task completion                                        Göé
Göé  GÇó Ensures no task is left incomplete                                       Göé
Göé  GÇó Recovers from crashes/errors                                             Göé
Göé  GÇó Maintains task state across restarts                                     Göé
GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ
```

### Component Interaction Flow

```
GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ
Göé   WATCHER   Göé  Detects new email
GööGöÇGöÇGöÇGöÇGöÇGöÇGö¼GöÇGöÇGöÇGöÇGöÇGöÇGöÿ
       Göé 1. Creates: Needs_Action/EMAIL_*.md
       Gû+
GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ
Göé  OBSIDIAN   Göé  Markdown file stored
GööGöÇGöÇGöÇGöÇGöÇGöÇGö¼GöÇGöÇGöÇGöÇGöÇGöÇGöÿ
       Göé 2. opencode CLI reads file
       Gû+
GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ
Göé  opencode CLI   Göé  Analyzes content, drafts reply
GööGöÇGöÇGöÇGöÇGöÇGöÇGö¼GöÇGöÇGöÇGöÇGöÇGöÇGöÿ
       Göé 3. Creates: Pending_Approval/REPLY_EMAIL_*.md
       Gû+
GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ
Göé   HUMAN     Göé  Reviews and approves
GööGöÇGöÇGöÇGöÇGöÇGöÇGö¼GöÇGöÇGöÇGöÇGöÇGöÇGöÿ
       Göé 4. Moves file to Approved/
       Gû+
GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ
Göé   MCP       Göé  Executes action (sends email)
GööGöÇGöÇGöÇGöÇGöÇGöÇGö¼GöÇGöÇGöÇGöÇGöÇGöÇGöÿ
       Göé 5. Moves file to Done/
       Gû+
GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ
Göé   AUDIT     Göé  Logs action to Logs/Audit/
GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ
```

---

## Component Descriptions

### 1. Watchers (Sensors)

**Purpose:** Detect changes in external sources and create action files.

| Watcher | Interval | Monitors | Output |
|---------|----------|----------|--------|
| `gmail_watcher.py` | 2 min | Gmail inbox | `Needs_Action/EMAIL_*.md` |
| `whatsapp_watcher.py` | 30 sec | WhatsApp Web | `Needs_Action/WHATSAPP_*.md` |
| `office_watcher.py` | 1 sec | File system | `Needs_Action/FILE_*.md` |
| `social_watcher.py` | 60 sec | Social drafts | `Needs_Action/SOCIAL_*.md` |
| `odoo_lead_watcher.py` | 5 min | Odoo CRM | `Needs_Action/ODOO_LEAD_*.md` |

**Implementation Pattern:**

```python
# base_watcher.py pattern
class BaseWatcher:
    def __init__(self, name, interval):
        self.name = name
        self.interval = interval
    
    def watch(self):
        """Poll external source"""
        pass
    
    def create_action_file(self, data):
        """Create markdown file in Needs_Action/"""
        pass
```

### 2. opencode CLI (Brain)

**Purpose:** Reasoning engine that analyzes action files and plans responses.

**Key Features:**
- Reads Markdown action files
- Analyzes content using LLM reasoning
- Drafts professional responses
- Calls MCP servers for actions
- Creates approval requests

**Commands:**
```bash
# Start opencode CLI
opencode --cwd "D:\Desktop4\Obsidian Vault"

# Process action file
opencode -y "Read Needs_Action/EMAIL_*.md and draft reply"

# Check status
opencode -y "Show me pending approvals"
```

See `AI_ENGINE_GUIDE.md` for complete reference.

### 3. MCP Servers (Hands)

**Purpose:** Execute approved actions on external systems.

| Server | Functions | Rate Limit |
|--------|-----------|------------|
| `mcp-email/` | send_email, draft_email, list_emails | 10/hour |
| `mcp-browser/` | navigate, click, type, screenshot | 60/minute |
| `mcp-odoo/` | create_invoice, read_accounting, list_partners | 60/minute |
| `mcp-social/` | post_linkedin, post_twitter, generate_summary | 5/hour |

**MCP Protocol:**
- JSON-RPC 2.0 over stdio
- Compatible with opencode CLI tool calling
- Structured responses with error handling

### 4. Obsidian Vault (Memory)

**Purpose:** Persistent storage and human-readable interface.

**Folder Structure:**

```
Obsidian Vault/
Gö£GöÇGöÇ Needs_Action/       # New items requiring attention
Gö£GöÇGöÇ Pending_Approval/   # Awaiting human approval
Gö£GöÇGöÇ Approved/           # Approved and ready for execution
Gö£GöÇGöÇ Done/               # Completed tasks
Gö£GöÇGöÇ Logs/
Göé   GööGöÇGöÇ Audit/          # Audit trail (JSONL format)
Gö£GöÇGöÇ Briefings/          # CEO weekly briefings
Gö£GöÇGöÇ Social_Drafts/      # Social media drafts
GööGöÇGöÇ config/             # Configuration (credentials excluded)
```

**File Naming Convention:**
- `EMAIL_YYYYMMDD_HHMMSS.md` - Email action files
- `WHATSAPP_YYYYMMDD_HHMMSS.md` - WhatsApp action files
- `REPLY_EMAIL_YYYYMMDD_HHMMSS.md` - Reply drafts
- `POST_LINKEDIN_YYYYMMDD_HHMMSS.md` - LinkedIn posts
- `ODOO_LEAD_YYYYMMDD_HHMMSS.md` - Odoo lead files

### 5. Ralph Loop (Persistence)

**Purpose:** Ensure multi-step tasks complete even after crashes.

**Features:**
- Tracks task state in `In_Progress/` folder
- Recovers incomplete tasks on restart
- Implements retry logic with exponential backoff
- Logs all state changes

---

## Data Flow

### Example: WhatsApp Message GåÆ Approved Email

**Step 1: Message Received**

```
WhatsApp Server GåÆ WhatsApp Web GåÆ whatsapp_watcher.py detects message
```

**Step 2: Action File Created**

```markdown
---
type: whatsapp
from: +92-300-1234567
contact: Client Name
timestamp: 2026-03-22 14:30:22
priority: high
---

Message: "Hi! I need an invoice for last month's services. Can you send it?"

Intent: Invoice request
Urgency: High
```

**Step 3: opencode CLI Processes**

```bash
opencode -y "Read WHATSAPP_*.md and determine appropriate action"
```

**opencode Analysis:**
- Intent: Client wants invoice
- Action needed: Create invoice in Odoo, email to client
- Information required: Client ID, invoice details

**Step 4: Draft Response Created**

```markdown
---
type: approval
original: WHATSAPP_20260322_143022.md
action: create_and_send_invoice
---

## Proposed Action

1. Create invoice in Odoo for Client Name
2. Email invoice to client@example.com

## Draft Message

Hi Client Name,

Thank you for your message. I'm sending you the invoice for last month's services.

Please find the invoice attached.

Best regards,
Your Company

---
APPROVAL_REQUIRED: true
INSTRUCTIONS: Move to Approved/ to proceed, Rejected/ to cancel
```

**Step 5: Human Approval**

```bash
# User reviews in Obsidian
# Moves file: Pending_Approval/ GåÆ Approved/
```

**Step 6: MCP Executes**

```python
# mcp-odoo creates invoice
invoice_id = odoo.create_invoice(partner_id=123, lines=[...])

# mcp-email sends with attachment
mcp-email.send_email(
    to="client@example.com",
    subject="Invoice for Services",
    body="...",
    attachment=f"Invoice_{invoice_id}.pdf"
)
```

**Step 7: Completion**

```
File moved: Approved/ GåÆ Done/
Audit log entry created: Logs/Audit/2026-03-22.jsonl
Dashboard updated: Dashboard.md
```

---

## Security Architecture

### Credential Isolation

```
GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ
Göé                    OBSIDIAN VAULT                            Göé
Göé  (NO CREDENTIALS STORED HERE)                                Göé
Göé                                                              Göé
Göé  Gö£GöÇGöÇ Needs_Action/                                           Göé
Göé  Gö£GöÇGöÇ Pending_Approval/                                       Göé
Göé  GööGöÇGöÇ Done/                                                   Göé
GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ

GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ
Göé                    CREDENTIAL STORAGE                        Göé
Göé  (EXCLUDED FROM GIT, ENCRYPTED)                              Göé
Göé                                                              Göé
Göé  Gö£GöÇGöÇ .env.local          GåÉ Environment variables            Göé
Göé  Gö£GöÇGöÇ config/credentials.json GåÉ OAuth credentials           Göé
Göé  GööGöÇGöÇ mcp-email/token.json GåÉ Gmail API token               Göé
GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ
```

### Security Rules

1. **NEVER** commit credentials to Git
2. **ALWAYS** use environment variables
3. **NEVER** store API keys in Markdown files
4. **ALWAYS** require human approval for external actions
5. **ALWAYS** log all actions to audit trail

### `.gitignore` Patterns

```gitignore
# Credentials
.env
.env.local
.env.cloud
credentials.json
token.json
*.pem
*.key
*.session
config/secrets.json

# Logs
Logs/*.log
Logs/Audit/
Dead_Letter_Queue/

# Session Data
whatsapp_session/
*.session
*.pickle
```

### Human-in-the-Loop (HITL)

Nothing sends without explicit approval:

```
AI Drafts GåÆ Human Reviews GåÆ Human Approves GåÆ AI Executes
```

**Approval Commands:**

| Command | Action |
|---------|--------|
| `Haan, bhej do` | Send immediately |
| `Yes, send it` | Send immediately |
| `+å+¦+à+î +ú+¦+¦+ä+ç` | Send immediately |
| `Nahi, revise karo` | Redraft |
| `No, revise it` | Redraft |
| `+ä+º+î +¦+º+¼+¦+ç` | Redraft |
| `Edit karna hai` | I want to edit |
| `I want to edit` | I want to edit |

---

## Deployment Options

### Local-Only (Gold Tier)

**Architecture:**
```
GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ
Göé         YOUR LOCAL MACHINE           Göé
Göé                                      Göé
Göé  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ Göé
Göé  Göé  Watchers + opencode CLI + MCPs    Göé Göé
Göé  GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ Göé
Göé              Göé                       Göé
Göé              Gû+                       Göé
Göé  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ Göé
Göé  Göé      Obsidian Vault            Göé Göé
Göé  GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ Göé
GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ
```

**Pros:**
- Complete privacy
- No cloud dependencies
- Full control

**Cons:**
- Requires machine to be on
- No remote access

### Cloud + Local (Platinum Tier Preview)

**Architecture:**
```
GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ
Göé           CLOUD VM (AWS/Azure)       Göé
Göé                                      Göé
Göé  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ Göé
Göé  Göé  Cloud Agent + Watchers        Göé Göé
Göé  GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ Göé
Göé              Göé                       Göé
Göé              Göé Sync via encrypted    Göé
Göé              Gû+ channel               Göé
Göé  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ Göé
Göé  Göé      Local Obsidian Vault      Göé Göé
Göé  GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ Göé
Göé              Göé                       Göé
Göé              Gû+                       Göé
GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ
         Göé
         Göé Local opencode CLI + MCPs
         Gû+
GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ
Göé         YOUR LOCAL MACHINE           Göé
Göé                                      Göé
Göé  GöîGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÉ Göé
Göé  Göé  opencode CLI + MCP Servers        Göé Göé
Göé  GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ Göé
GööGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÇGöÿ
```

**Pros:**
- 24/7 operation
- Remote access
- Redundancy

**Cons:**
- Cloud costs
- More complex setup

---

## Extension Guide

### Adding a New Watcher

**Step 1: Create Watcher Script**

```python
# watchers/new_watcher.py
from base_watcher import BaseWatcher
from pathlib import Path
import time

class NewWatcher(BaseWatcher):
    def __init__(self):
        super().__init__("new_watcher", interval=60)
    
    def watch(self):
        """Poll your data source"""
        # Implement polling logic
        data = self.fetch_data()
        
        if data:
            self.create_action_file(data)
    
    def fetch_data(self):
        """Fetch data from source"""
        # Implement data fetching
        return data

if __name__ == "__main__":
    watcher = NewWatcher()
    while True:
        watcher.watch()
        time.sleep(watcher.interval)
```

**Step 2: Add to Orchestrator**

```python
# orchestrator.py
WATCHERS = {
    # ... existing watchers ...
    "new_watcher": {
        "script": "new_watcher.py",
        "interval": 60,
        "description": "New Data Source Monitor",
        "enabled": True,
    },
}
```

**Step 3: Add Environment Variables**

```bash
# .env.local
NEW_WATCHER_ENABLED=true
NEW_WATCHER_INTERVAL=60
```

### Adding a New MCP Server

**Step 1: Create MCP Server**

```python
# mcp-new/server.py
import json
import sys

class MCPNewServer:
    def do_something(self, param: str) -> dict:
        """Do something useful"""
        return {
            "success": True,
            "result": f"Did: {param}"
        }

def handle_request(request: dict, server: MCPNewServer) -> dict:
    method = request.get('method')
    params = request.get('params', {})
    
    if method == 'do_something':
        result = server.do_something(**params)
    else:
        return {"error": "Method not found"}
    
    return {"result": result}

if __name__ == "__main__":
    server = MCPNewServer()
    for line in sys.stdin:
        request = json.loads(line)
        response = handle_request(request, server)
        print(json.dumps(response), flush=True)
```

**Step 2: Add to MCP Config**

```json
// config/mcp.json
{
  "mcpServers": {
    "new": {
      "command": "python",
      "args": ["mcp-new/server.py"]
    }
  }
}
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Watcher Not Starting

**Symptoms:**
- Watcher process exits immediately
- No action files created

**Solutions:**
```bash
# Check syntax
python -m py_compile watchers/gmail_watcher.py

# Check logs
type Logs\orchestrator.log

# Run with verbose logging
python watchers/gmail_watcher.py --verbose
```

#### Issue 2: opencode CLI Not Found

**Symptoms:**
- `opencode: command not found`

**Solutions:**
```bash
# Install opencode CLI
npm install -g opencode

# Verify installation
opencode --version

# Check PATH
echo %PATH%
```

#### Issue 3: MCP Server Won't Start

**Symptoms:**
- MCP server crashes on startup
- Connection refused errors

**Solutions:**
```bash
# Check dependencies
cd mcp-email
npm install

# Test manually
python mcp_server.py --test

# Check configuration
type config\mcp.json
```

#### Issue 4: Rate Limit Exceeded

**Symptoms:**
- "Rate limit exceeded" errors
- Actions not executing

**Solutions:**
```bash
# Check rate limit status
python mcp_server.py --rate-limit-status

# Wait for cooldown (usually 1 hour for email)
# Or increase limits in .env.local:
RATE_LIMIT=20  # emails per hour
```

#### Issue 5: Authentication Failed

**Symptoms:**
- Gmail/Odoo authentication fails
- "Invalid credentials" errors

**Solutions:**
```bash
# Re-authenticate Gmail
cd mcp-email
node authenticate.js

# Check credentials exist
dir config\credentials.json

# Verify environment variables
python -c "import os; print(os.getenv('GMAIL_CLIENT_ID', 'Not set'))"
```

---

## Performance Considerations

### Watcher Intervals

| Watcher | Default | Min | Max | Impact |
|---------|---------|-----|-----|--------|
| Gmail | 2 min | 30s | 10 min | Low |
| WhatsApp | 30 sec | 10s | 5 min | Medium |
| Office | 1 sec | 100ms | 10 sec | High (CPU) |
| Social | 60 sec | 30s | 5 min | Low |
| Odoo | 5 min | 1 min | 30 min | Low |

**Recommendations:**
- Increase intervals for high-CPU watchers (office_watcher)
- Decrease intervals for time-sensitive sources (WhatsApp)
- Balance responsiveness vs. resource usage

### Rate Limits

| Service | Default | Recommended | Notes |
|---------|---------|-------------|-------|
| Gmail | 10/hour | 10-20/hour | API quota |
| Odoo | 60/min | 60-100/min | Local instance |
| Social | 5/hour | 5-10/hour | Platform limits |

### Resource Usage

**Typical Memory:**
- Watchers: 50-100 MB total
- opencode CLI: 200-500 MB
- MCP Servers: 100-200 MB
- **Total:** 350-800 MB

**Typical CPU:**
- Idle: <5%
- Processing: 20-50%
- Peak (multiple watchers): 50-80%

**Optimization Tips:**
1. Increase watcher intervals if CPU is high
2. Run opencode CLI with `--model fast-model` for quick tasks
3. Use SSD for faster file operations
4. Close unused MCP servers

---

## opencode CLI Integration

### How opencode CLI Reads/Writes to Vault

**Reading Action Files:**

```bash
# opencode reads markdown files
opencode -y "Read Needs_Action/EMAIL_*.md and summarize"
```

**Writing Drafts:**

```bash
# opencode creates draft in Pending_Approval/
opencode -y "Create reply draft in Pending_Approval/REPLY_EMAIL_*.md"
```

**File Movement:**

```bash
# opencode can move files (with user confirmation)
opencode -y "Move EMAIL_*.md from Needs_Action/ to Done/"
```

### How opencode CLI Calls MCP Servers

**Tool Calling Format:**

```json
{
  "method": "send_email",
  "params": {
    "to": "client@example.com",
    "subject": "Invoice",
    "body": "Please find attached..."
  }
}
```

**opencode CLI Configuration:**

```bash
# Add MCP servers to opencode CLI config
opencode --add-mcp email mcp-email/server.py
opencode --add-mcp odoo mcp-odoo/server.py
```

**Example Interaction:**

```
User: "Send an invoice to client@example.com"

opencode CLI:
1. Calls mcp-odoo.create_invoice()
2. Gets invoice PDF
3. Calls mcp-email.send_email() with attachment
4. Reports success
```

### opencode CLI Commands for Vault

| Command | Purpose |
|---------|---------|
| `opencode -y "Show pending approvals"` | List Pending_Approval/ |
| `opencode -y "Process all emails"` | Process Needs_Action/EMAIL_* |
| `opencode -y "Generate weekly summary"` | Create CEO briefing |
| `opencode -y "Check system health"` | Run health checks |

---

## Appendix: File Reference

### Core Scripts

| File | Purpose | Lines |
|------|---------|-------|
| `orchestrator.py` | Master watcher orchestration | ~400 |
| `mcp_server.py` | Email MCP server | ~800 |
| `odoo_mcp.py` | Odoo MCP server | ~1000 |
| `ai_employee_orchestrator.py` | Interactive orchestrator | ~500 |
| `audit_logger.py` | Audit trail management | ~300 |
| `error_recovery.py` | Error handling & retry | ~400 |

### Watchers

| File | Monitors | Interval |
|------|----------|----------|
| `watchers/gmail_watcher.py` | Gmail API | 2 min |
| `watchers/whatsapp_watcher.py` | WhatsApp Web | 30 sec |
| `watchers/office_watcher.py` | File system | 1 sec |
| `watchers/social_watcher.py` | Social drafts | 60 sec |
| `watchers/odoo_lead_watcher.py` | Odoo CRM | 5 min |

### Documentation

| File | Purpose |
|------|---------|
| `AI_ENGINE_GUIDE.md` | opencode CLI usage guide |
| `docs/ARCHITECTURE.md` | This file - system architecture |
| `docs/ODOO_SETUP.md` | Odoo installation guide |
| `README.md` | Getting started guide |
| `CREDENTIALS_GUIDE.md` | Credential management |

---

**Last Updated:** March 22, 2026  
**Version:** 1.0.0  
**Status:** Production Ready - Gold Tier
