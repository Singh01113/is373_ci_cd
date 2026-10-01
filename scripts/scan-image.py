"""Scan a Docker image ID and retain release identity and vulnerability evidence."""
import collections
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    image, output = sys.argv[1:]
    directory = Path(output)
    directory.mkdir(parents=True, exist_ok=True)
    metadata = json.loads(subprocess.check_output(["docker", "image", "inspect", image]))[0]
    identity = {
        "image_id": metadata["Id"],
        "repo_digests": metadata.get("RepoDigests", []),
        "architecture": metadata["Architecture"],
        "commit": (metadata["Config"].get("Labels") or {}).get("org.opencontainers.image.revision"),
        "policy": "report-only; scanner errors fail the job",
        "scanner_version": "0.75.0",
    }
    (directory / "image-identity.json").write_text(json.dumps(identity, indent=2) + "\n")
    report = directory / "vulnerabilities.json"
    subprocess.run([
        ".tools/trivy/trivy", "image", "--scanners", "vuln", "--format", "json",
        "--output", str(report), "--exit-code", "0", "--timeout", "10m",
        "--image-src", "docker", metadata["Id"],
    ], check=True)
    data = json.loads(report.read_text())
    counts = collections.Counter(
        vulnerability["Severity"]
        for result in data.get("Results", [])
        for vulnerability in result.get("Vulnerabilities", [])
    )
    summary = "\n".join([
        "### Image vulnerability scan",
        f"Image: `{identity['image_id']}` ({identity['architecture']})",
        f"Commit: `{identity['commit']}`",
        "Policy: report-only. Findings require review; scanner errors fail verification.",
        "",
        "| Severity | Findings |",
        "| --- | ---: |",
        *[f"| {severity} | {counts[severity]} |" for severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN")],
        "",
    ])
    (directory / "summary.md").write_text(summary)
    print(summary)
    if path := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(path, "a") as stream:
            stream.write(summary)
    if counts["CRITICAL"] or counts["HIGH"]:
        print("::warning::Image has HIGH/CRITICAL vulnerabilities; review the retained scan report.")


if __name__ == "__main__":
    main()
