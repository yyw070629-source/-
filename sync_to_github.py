import os
import json
import base64
import urllib.request
from github import Github

REPO_NAME = "yyw070629-source/-"

IGNORE_PATTERNS = [
    '.git', '.cache', '.config', '.local', '.pythonlibs',
    '__pycache__', '.env', '.replit', '.venv',
    'node_modules', '.upm'
]

def get_access_token():
    hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
    repl_identity = os.environ.get('REPL_IDENTITY')
    web_repl = os.environ.get('WEB_REPL_RENEWAL')

    if repl_identity:
        token = 'repl ' + repl_identity
    elif web_repl:
        token = 'depl ' + web_repl
    else:
        raise RuntimeError('Authentication token not found')

    url = f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=github'
    req = urllib.request.Request(url, headers={
        'Accept': 'application/json',
        'X_REPLIT_TOKEN': token
    })
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    item = data.get('items', [None])[0]
    if not item:
        raise RuntimeError('GitHub connection not found')
    settings = item.get('settings', {})
    access_token = settings.get('access_token') or settings.get('oauth', {}).get('credentials', {}).get('access_token')
    if not access_token:
        raise RuntimeError('GitHub access token not found')
    return access_token

def should_ignore(path):
    parts = path.split('/')
    for part in parts:
        if part in IGNORE_PATTERNS:
            return True
    return False

def get_local_files(base_dir):
    files = {}
    for root, dirs, filenames in os.walk(base_dir):
        dirs[:] = [d for d in dirs if not should_ignore(d)]
        for filename in filenames:
            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, base_dir)
            if should_ignore(rel_path):
                continue
            try:
                with open(full_path, 'rb') as f:
                    content = f.read()
                files[rel_path] = content
            except (PermissionError, OSError):
                continue
    return files

def sync():
    print("Getting GitHub access token...")
    token = get_access_token()

    g = Github(token)
    repo = g.get_repo(REPO_NAME)
    print(f"Connected to repository: {repo.full_name}")

    print("Reading local files...")
    local_files = get_local_files('/home/runner/workspace')
    print(f"Found {len(local_files)} files to sync")

    print("Getting existing files from GitHub...")
    existing_files = {}
    try:
        contents = repo.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                existing_files[file_content.path] = file_content
    except Exception:
        pass

    updated = 0
    created = 0

    for rel_path, content in local_files.items():
        encoded = base64.b64encode(content).decode('utf-8')
        try:
            if rel_path in existing_files:
                existing = existing_files[rel_path]
                if existing.content and base64.b64decode(existing.content.replace('\n', '')) == content:
                    continue
                repo.update_file(
                    rel_path,
                    f"Update {rel_path}",
                    content,
                    existing.sha
                )
                updated += 1
                print(f"  Updated: {rel_path}")
            else:
                repo.create_file(
                    rel_path,
                    f"Add {rel_path}",
                    content
                )
                created += 1
                print(f"  Created: {rel_path}")
        except Exception as e:
            print(f"  Error syncing {rel_path}: {e}")

    print(f"\nSync complete! Created: {created}, Updated: {updated}")

if __name__ == "__main__":
    sync()
