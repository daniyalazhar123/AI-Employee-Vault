#!/usr/bin/env python3
"""
AI Employee Dashboard API - FastAPI Backend
Real-time stats from vault

Personal AI Employee Hackathon 0
Platinum Tier: Dashboard UI
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import json
import os
from datetime import datetime
from typing import Dict, List

app = FastAPI(title="AI Employee Dashboard API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vault path
VAULT_PATH = Path(os.getenv('VAULT_PATH', Path(__file__).parent.parent))

# Mount static files
app.mount("/static", StaticFiles(directory=str(VAULT_PATH / 'dashboard')), name="static")


@app.get("/")
async def root():
    """Serve dashboard HTML"""
    return FileResponse(VAULT_PATH / 'dashboard' / 'index.html')


@app.get("/api/stats")
async def get_stats() -> Dict:
    """Get overall statistics"""
    try:
        # Count files in folders
        needs_action = len(list((VAULT_PATH / 'Needs_Action').glob('*.md'))) if (VAULT_PATH / 'Needs_Action').exists() else 0
        pending_approval = len(list((VAULT_PATH / 'Pending_Approval').glob('*.md'))) if (VAULT_PATH / 'Pending_Approval').exists() else 0
        done = len(list((VAULT_PATH / 'Done').glob('*.md'))) if (VAULT_PATH / 'Done').exists() else 0
        approved = len(list((VAULT_PATH / 'Approved').glob('*.md'))) if (VAULT_PATH / 'Approved').exists() else 0
        
        # Read Dashboard.md for revenue
        revenue = "113,000"  # Default
        dashboard_file = VAULT_PATH / 'Dashboard.md'
        if dashboard_file.exists():
            content = dashboard_file.read_text(encoding='utf-8')
            if 'Total' in content and 'Rs.' in content:
                # Extract revenue
                import re
                match = re.search(r'Total[^\n]*\|\s*\*\*([\d,]+)\*\*', content)
                if match:
                    revenue = match.group(1)
        
        return {
            "success": True,
            "stats": {
                "revenue": revenue,
                "processed": needs_action + pending_approval + done,
                "pending": needs_action,
                "pending_approval": pending_approval,
                "completed": done,
                "approved": approved
            },
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/activity")
async def get_activity(limit: int = 10) -> Dict:
    """Get recent activity"""
    try:
        activity = []
        
        # Get recent Done files
        done_folder = VAULT_PATH / 'Done'
        if done_folder.exists():
            done_files = sorted(done_folder.glob('*.md'), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]
            for f in done_files:
                activity.append({
                    "type": "completed",
                    "file": f.name,
                    "timestamp": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                })
        
        # Get recent Pending_Approval files
        pending_folder = VAULT_PATH / 'Pending_Approval'
        if pending_folder.exists():
            pending_files = sorted(pending_folder.glob('*.md'), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]
            for f in pending_files:
                activity.append({
                    "type": "pending",
                    "file": f.name,
                    "timestamp": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                })
        
        # Sort by timestamp
        activity.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {
            "success": True,
            "activity": activity[:limit],
            "count": len(activity)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/charts")
async def get_chart_data() -> Dict:
    """Get chart data for dashboard"""
    try:
        # Get files by date (last 7 days)
        from collections import defaultdict
        daily_stats = defaultdict(lambda: {"completed": 0, "pending": 0})
        
        done_folder = VAULT_PATH / 'Done'
        if done_folder.exists():
            for f in done_folder.glob('*.md'):
                date = datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d')
                daily_stats[date]["completed"] += 1
        
        pending_folder = VAULT_PATH / 'Needs_Action'
        if pending_folder.exists():
            for f in pending_folder.glob('*.md'):
                date = datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d')
                daily_stats[date]["pending"] += 1
        
        # Sort by date
        sorted_dates = sorted(daily_stats.keys())[-7:]  # Last 7 days
        
        return {
            "success": True,
            "dates": sorted_dates,
            "completed": [daily_stats[d]["completed"] for d in sorted_dates],
            "pending": [daily_stats[d]["pending"] for d in sorted_dates]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check() -> Dict:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "vault_path": str(VAULT_PATH)
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
