#!/usr/bin/env python3
"""
ClawForge Permission Test Script
================================
This script tests whether ClawForge's permission system is working.
It attempts various operations that require permissions.

Usage:
    1. Give this script to ClawForge to run
    2. ClawForge should either:
       - Ask for permission (if AUTO_APPROVE_MODE=False)
       - Auto-approve and execute (if AUTO_APPROVE_MODE=True)
    3. Check logs/permissions.jsonl for audit trail
"""

import os
import json
import datetime
from pathlib import Path

# Test operations
TEST_OPERATIONS = [
    {
        "name": "List Directory",
        "type": "terminal_command",
        "action": lambda: os.listdir("."),
        "risk": "LOW"
    },
    {
        "name": "Check Current Directory",
        "type": "terminal_command", 
        "action": lambda: os.getcwd(),
        "risk": "LOW"
    },
    {
        "name": "Read This Script",
        "type": "download_file",
        "action": lambda: open(__file__).read()[:100],
        "risk": "MEDIUM"
    },
]

def run_permission_test():
    """Run all test operations and report results."""
    
    results = {
        "timestamp": datetime.datetime.now().isoformat(),
        "tests": [],
        "summary": {
            "total": len(TEST_OPERATIONS),
            "passed": 0,
            "failed": 0
        }
    }
    
    print("=" * 60)
    print("🦁 CLAWFORGE PERMISSION TEST")
    print("=" * 60)
    print()
    
    for i, test in enumerate(TEST_OPERATIONS, 1):
        print(f"[{i}/{len(TEST_OPERATIONS)}] Testing: {test['name']} ({test['type']})")
        print(f"           Risk Level: {test['risk']}")
        
        try:
            # Check if AUTO_APPROVE_MODE is enabled
            try:
                from backend.permissions import AUTO_APPROVE_MODE
                print(f"           Auto-Approve: {AUTO_APPROVE_MODE}")
            except ImportError:
                print("           Auto-Approve: UNKNOWN (module not found)")
            
            # Attempt the action
            result = test["action"]()
            print(f"           ✅ Result: {str(result)[:50]}...")
            
            results["tests"].append({
                "name": test["name"],
                "type": test["type"],
                "risk": test["risk"],
                "status": "PASSED",
                "result": str(result)[:100]
            })
            results["summary"]["passed"] += 1
            
        except Exception as e:
            print(f"           ❌ Error: {str(e)}")
            
            results["tests"].append({
                "name": test["name"],
                "type": test["type"],
                "risk": test["risk"],
                "status": "FAILED",
                "error": str(e)
            })
            results["summary"]["failed"] += 1
        
        print()
    
    # Print summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {results['summary']['total']}")
    print(f"Passed: {results['summary']['passed']}")
    print(f"Failed: {results['summary']['failed']}")
    print()
    
    # Save results
    output_file = "workspace/outputs/permission_test_results.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📄 Results saved to: {output_file}")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    run_permission_test()
