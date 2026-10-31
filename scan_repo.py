"""Scanner script to parse OpenSSF OSV reports, analyze them with gemma4:12b, and export to a Markdown report."""

import os
import sys
import json
from checker.explain import explain

def scan_osv_repo(repo_path, output_report="audit_report.md", limit=5):
    malicious_dir = os.path.join(repo_path, "osv", "malicious")
    
    if not os.path.exists(malicious_dir):
        print(f"[ERROR] Could not find 'osv/malicious/' directory inside '{repo_path}'.")
        return

    print(f"Scanning OSV database path: {malicious_dir}\n" + "="*50)

    scanned_count = 0

    # Open the markdown report file for writing
    with open(output_report, "w", encoding="utf-8") as report_file:
        report_file.write("# Supply Chain Security Audit Report\n\n")
        report_file.write("Generated locally using **gemma4:12b** via Ollama and OpenSSF OSV threat data.\n\n")
        report_file.write("---\n\n")

        for root, dirs, files in os.walk(malicious_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            data = json.load(f)
                            
                        pkg_id = data.get('id', 'Unknown ID')
                        summary = data.get('summary', 'No summary provided')
                        details = data.get('details', 'No details provided')
                        
                        scanned_count += 1
                        print(f"\n[{scanned_count}] Analyzing Advisory ID: {pkg_id}")
                        print(f"Summary: {summary}")
                        
                        finding = {
                            "path": file_path,
                            "category": "malicious_package_advisory",
                            "reason": summary,
                            "severity": "high",
                            "signals": [
                                {
                                    "kind": "osv_advisory_details",
                                    "snippet": details[:800]
                                }
                            ]
                        }
                        
                        print("-> Asking gemma4:12b to evaluate this threat report...")
                        analysis = explain(finding)
                        print(analysis)
                        print("-" * 50)
                        
                        # Write entry to the Markdown report file
                        report_file.write(f"## Advisory: `{pkg_id}`\n\n")
                        report_file.write(f"- **Summary:** {summary}\n")
                        report_file.write(f"- **Source File:** `{file_path}`\n\n")
                        report_file.write(f"### AI Threat Analysis (`gemma4:12b`)\n\n")
                        report_file.write(f"{analysis}\n\n")
                        report_file.write("---\n\n")
                        
                        # Limit batch size so it runs quickly (change or set to None to scan more)
                        if limit and scanned_count >= limit:
                            print(f"\n[INFO] Reached batch limit of {limit} advisories.")
                            break

                    except Exception as e:
                        print(f"[WARNING] Could not parse JSON file {file_path}: {e}")
            
            if limit and scanned_count >= limit:
                break

    print(f"\nScan complete. Total malicious advisories analyzed: {scanned_count}")
    print(f"✅ Audit report successfully generated and saved to: {output_report}")

if __name__ == "__main__":
    target_repo = sys.argv[1] if len(sys.argv) > 1 else "./malicious-packages"
    # You can change the 'limit' parameter below to process more packages per run
    scan_osv_repo(target_repo, output_report="audit_report.md", limit=5)