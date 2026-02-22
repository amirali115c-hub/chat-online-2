"""
Leo Self-Heal Module
Adds monitoring and self-healing capabilities to Leo 2.0
"""

import subprocess
import json
import os
import time
from datetime import datetime
from pathlib import Path


class SelfHeal:
    def __init__(self):
        self.openclaw_path = os.path.expanduser("~/.openclaw")
        self.logs_path = os.path.join(self.openclaw_path, "logs")
    
    def check_gateway_status(self):
        """Check if OpenClaw gateway is running"""
        try:
            result = subprocess.run(
                ["openclaw", "status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                "status": "running" if result.returncode == 0 else "stopped",
                "output": result.stdout,
                "error": result.stderr
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def check_logs_for_errors(self, lines=50):
        """Check recent logs for errors"""
        try:
            log_dir = Path(self.logs_path)
            if not log_dir.exists():
                return {"errors": [], "message": "No logs directory found"}
            
            # Get most recent log file
            log_files = sorted(log_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
            if not log_files:
                return {"errors": [], "message": "No log files found"}
            
            # Read last N lines
            with open(log_files[0], 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
                recent = all_lines[-lines:]
            
            # Find errors
            error_keywords = ["error", "Error", "ERROR", "401", "404", "500", "401", "Exception", "Traceback"]
            errors = []
            for line in recent:
                if any(kw in line for kw in error_keywords):
                    errors.append(line.strip())
            
            return {"errors": errors, "count": len(errors)}
        except Exception as e:
            return {"errors": [], "message": str(e)}
    
    def restart_gateway(self):
        """Restart OpenClaw gateway"""
        try:
            result = subprocess.run(
                ["openclaw", "gateway", "restart"],
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def run_diagnostics(self):
        """Run full diagnostics"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "gateway": self.check_gateway_status(),
            "errors": self.check_logs_for_errors(),
        }
        
        # Determine overall health
        if results["gateway"]["status"] == "running" and results["errors"]["count"] == 0:
            results["health"] = "healthy"
        elif results["gateway"]["status"] == "running":
            results["health"] = "degraded"
        else:
            results["health"] = "critical"
        
        return results
    
    def auto_heal(self):
        """Attempt automatic healing"""
        diagnostics = self.run_diagnostics()
        actions_taken = []
        
        # If gateway not running, try to start it
        if diagnostics["gateway"]["status"] == "stopped":
            result = self.restart_gateway()
            if result["success"]:
                actions_taken.append("Gateway restarted")
            else:
                actions_taken.append(f"Failed to restart: {result.get('error', 'Unknown')}")
        
        # If errors found, try doctor --fix
        if diagnostics["errors"]["count"] > 5:
            try:
                result = subprocess.run(
                    ["openclaw", "doctor", "--fix"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    actions_taken.append("Ran doctor --fix")
            except:
                pass
        
        return {
            "diagnostics": diagnostics,
            "actions": actions_taken
        }


# Singleton instance
_self_heal = None

def get_self_heal():
    global _self_heal
    if _self_heal is None:
        _self_heal = SelfHeal()
    return _self_heal
