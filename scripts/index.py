# scripts/generate_pip_index.py
import os
import json
import urllib.request
from pathlib import Path
from urllib.parse import quote

def fetch_releases(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    with urllib.request.urlopen(url) as resp:
        return json.load(resp)

def generate_index_html(releases, output_dir="pip_index"):
    project_name = os.environ["GITHUB_REPOSITORY"].split("/")[-1].lower()
    index_dir = Path(output_dir) / project_name
    index_dir.mkdir(parents=True, exist_ok=True)

    # Collect all .whl assets
    wheels = []
    for release in releases:
        for asset in release.get("assets", []):
            if asset["name"].endswith(".whl"):
                # Normalize name for URL
                safe_name = quote(asset["name"])
                download_url = asset["browser_download_url"]
                wheels.append((asset["name"], download_url))

    # Write simple index
    html = "<!DOCTYPE html>\n<html><body>\n"
    for name, url in wheels:
        html += f'<a href="https://gh.927223.xyz/{url}">{name}</a><br>\n'
    html += "</body></html>"

    (index_dir / "index.html").write_text(html, encoding="utf-8")

    # Also write root index.html listing project
    root_index = Path(output_dir) / "index.html"
    root_html = f'''<!DOCTYPE html>
<html>
<body>
<a href="{project_name}/">{project_name}</a>
</body>
</html>'''
    root_index.write_text(root_html, encoding="utf-8")

    print(f"Generated pip index at {output_dir}")

if __name__ == "__main__":
    repo = os.environ["GITHUB_REPOSITORY"]  # e.g., "user/repo"
    owner, name = repo.split("/")
    releases = fetch_releases(owner, name)

    generate_index_html(releases)

