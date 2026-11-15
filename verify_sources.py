"""Check every synced project against the committed source lock."""

import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def verify(tree):
    manifest = Path(__file__).resolve().parent / "manifests/pinned.xml"
    projects = ET.parse(manifest).getroot().findall("project")
    for project in projects:
        revision = project.attrib["revision"]
        if not re.fullmatch("[0-9a-f]{40}", revision):
            raise ValueError("Unpinned project: " + project.attrib["name"])
        path = tree / project.attrib.get("path", project.attrib["name"])
        actual = subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
        ).strip()
        if actual != revision:
            raise ValueError("Source revision differs: " + str(path))
    print(f"Verified {len(projects)} pinned source revisions")


if __name__ == "__main__":
    verify(Path(sys.argv[1]))
