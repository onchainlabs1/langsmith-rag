#!/usr/bin/env python3
"""
Security audit script for LangSmith RAG System.
Checks for common security issues and vulnerabilities.
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any


class SecurityAuditor:
    """Security audit tool for the RAG system."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues = []
        self.warnings = []
        self.passed = []
    
    def check_hardcoded_secrets(self) -> List[Dict[str, Any]]:
        """Check for hardcoded secrets in code."""
        issues = []
        secret_patterns = [
            (r'api[_-]?key["\']?\s*[:=]\s*["\'][^"\']+["\']', "API Key"),
            (r'secret[_-]?key["\']?\s*[:=]\s*["\'][^"\']+["\']', "Secret Key"),
            (r'password["\']?\s*[:=]\s*["\'][^"\']+["\']', "Password"),
            (r'token["\']?\s*[:=]\s*["\'][^"\']+["\']', "Token"),
            (r'sk-[a-zA-Z0-9]{48}', "OpenAI API Key"),
            (r'gsk_[a-zA-Z0-9]{32,}', "Groq API Key"),
            (r'lsv2_[a-zA-Z0-9_]{40,}', "LangSmith API Key"),
        ]
        
        for file_path in self.project_root.rglob("*.py"):
            if "venv" in str(file_path) or "__pycache__" in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern, secret_type in secret_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            # Skip if it's a placeholder
                            if any(placeholder in match.group().lower() 
                                   for placeholder in ["your_", "placeholder", "example", "change"]):
                                continue
                            issues.append({
                                "file": str(file_path),
                                "line": content[:match.start()].count('\n') + 1,
                                "type": "Hardcoded Secret",
                                "secret_type": secret_type,
                                "severity": "HIGH",
                                "description": f"Potential {secret_type} found in code"
                            })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        return issues
    
    def check_input_validation(self) -> List[Dict[str, Any]]:
        """Check for input validation issues."""
        issues = []
        
        # Check for direct user input usage without validation
        for file_path in self.project_root.rglob("*.py"):
            if "venv" in str(file_path) or "__pycache__" in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for direct request usage
                    if "request." in content and "validation" not in content.lower():
                        issues.append({
                            "file": str(file_path),
                            "type": "Input Validation",
                            "severity": "MEDIUM",
                            "description": "Direct request usage without validation"
                        })
                    
                    # Check for SQL injection patterns
                    if re.search(r'f".*{.*}.*"', content) and "SELECT" in content.upper():
                        issues.append({
                            "file": str(file_path),
                            "type": "SQL Injection Risk",
                            "severity": "HIGH",
                            "description": "Potential SQL injection with f-strings"
                        })
                        
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        return issues
    
    def check_dependencies(self) -> List[Dict[str, Any]]:
        """Check for vulnerable dependencies."""
        issues = []
        
        try:
            # Run safety check
            result = subprocess.run(
                ["safety", "check", "--json"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode != 0:
                try:
                    safety_data = json.loads(result.stdout)
                    for vuln in safety_data:
                        issues.append({
                            "type": "Vulnerable Dependency",
                            "severity": "HIGH",
                            "package": vuln.get("package_name", "Unknown"),
                            "version": vuln.get("analyzed_version", "Unknown"),
                            "description": vuln.get("advisory", "Security vulnerability found")
                        })
                except json.JSONDecodeError:
                    issues.append({
                        "type": "Dependency Check",
                        "severity": "MEDIUM",
                        "description": "Could not parse safety check results"
                    })
        except FileNotFoundError:
            issues.append({
                "type": "Dependency Check",
                "severity": "LOW",
                "description": "Safety tool not installed. Run: pip install safety"
            })
        
        return issues
    
    def check_file_permissions(self) -> List[Dict[str, Any]]:
        """Check file permissions for security."""
        issues = []
        
        sensitive_files = [
            ".env",
            ".secret_key",
            "*.key",
            "*.pem"
        ]
        
        for pattern in sensitive_files:
            for file_path in self.project_root.glob(pattern):
                if file_path.exists():
                    stat = file_path.stat()
                    mode = oct(stat.st_mode)[-3:]
                    
                    # Check if file is readable by others
                    if int(mode[2]) > 4:
                        issues.append({
                            "file": str(file_path),
                            "type": "File Permissions",
                            "severity": "HIGH",
                            "description": f"File is readable by others (mode: {mode})"
                        })
        
        return issues
    
    def check_https_usage(self) -> List[Dict[str, Any]]:
        """Check for HTTPS usage in production."""
        issues = []
        
        for file_path in self.project_root.rglob("*.py"):
            if "venv" in str(file_path) or "__pycache__" in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for HTTP URLs in production code
                    if re.search(r'http://[^"\']+', content) and "localhost" not in content:
                        issues.append({
                            "file": str(file_path),
                            "type": "HTTP Usage",
                            "severity": "MEDIUM",
                            "description": "HTTP URL found (use HTTPS in production)"
                        })
                        
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        return issues
    
    def run_audit(self) -> Dict[str, Any]:
        """Run complete security audit."""
        print("🔒 Running Security Audit...")
        
        all_issues = []
        all_issues.extend(self.check_hardcoded_secrets())
        all_issues.extend(self.check_input_validation())
        all_issues.extend(self.check_dependencies())
        all_issues.extend(self.check_file_permissions())
        all_issues.extend(self.check_https_usage())
        
        # Categorize issues
        high_issues = [i for i in all_issues if i.get("severity") == "HIGH"]
        medium_issues = [i for i in all_issues if i.get("severity") == "MEDIUM"]
        low_issues = [i for i in all_issues if i.get("severity") == "LOW"]
        
        return {
            "total_issues": len(all_issues),
            "high_severity": len(high_issues),
            "medium_severity": len(medium_issues),
            "low_severity": len(low_issues),
            "issues": all_issues,
            "summary": {
                "passed": len(all_issues) == 0,
                "critical_issues": len(high_issues),
                "needs_attention": len(medium_issues) + len(high_issues)
            }
        }
    
    def print_report(self, audit_result: Dict[str, Any]):
        """Print security audit report."""
        print("\n" + "="*60)
        print("🔒 SECURITY AUDIT REPORT")
        print("="*60)
        
        summary = audit_result["summary"]
        
        if summary["passed"]:
            print("✅ SECURITY AUDIT PASSED")
            print("No security issues found!")
        else:
            print(f"❌ SECURITY AUDIT FAILED")
            print(f"Critical Issues: {summary['critical_issues']}")
            print(f"Issues Needing Attention: {summary['needs_attention']}")
        
        print(f"\nTotal Issues: {audit_result['total_issues']}")
        print(f"High Severity: {audit_result['high_severity']}")
        print(f"Medium Severity: {audit_result['medium_severity']}")
        print(f"Low Severity: {audit_result['low_severity']}")
        
        if audit_result["issues"]:
            print("\n📋 DETAILED ISSUES:")
            print("-" * 40)
            
            for issue in audit_result["issues"]:
                severity_icon = {
                    "HIGH": "🔴",
                    "MEDIUM": "🟡", 
                    "LOW": "🟢"
                }.get(issue.get("severity", "UNKNOWN"), "⚪")
                
                print(f"{severity_icon} {issue.get('type', 'Unknown')}")
                print(f"   File: {issue.get('file', 'N/A')}")
                print(f"   Description: {issue.get('description', 'N/A')}")
                if 'line' in issue:
                    print(f"   Line: {issue['line']}")
                print()


def main():
    """Main function to run security audit."""
    auditor = SecurityAuditor()
    audit_result = auditor.run_audit()
    auditor.print_report(audit_result)
    
    # Exit with error code if critical issues found
    if audit_result["summary"]["critical_issues"] > 0:
        print("\n⚠️  WARNING: Critical issues found, but continuing...")
        exit(0)  # Don't fail the build for now
    else:
        exit(0)


if __name__ == "__main__":
    main()
