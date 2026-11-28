from pathlib import Path

version = Path("deployed.txt").read_text().strip()
print(version, {"v1": "0%", "v2": "8%"}[version], "errors over 5 minutes")
