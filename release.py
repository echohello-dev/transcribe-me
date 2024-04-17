import os
import subprocess
import requests

def get_new_version():
    result = subprocess.run(["cz", "version", "-p"], capture_output=True, text=True)
    if result.returncode != 0:
        raise ValueError(f"Failed to get new version: {result.stderr}")
    return result.stdout.strip()

def get_changelog():
    result = subprocess.run(["cz", "changelog", "--dry-run"], capture_output=True, text=True)
    if result.returncode != 0:
        raise ValueError(f"Failed to get changelog: {result.stderr}")
    return result.stdout.strip()

def push_tags():
    result = subprocess.run(["git", "push", "--tags"], capture_output=True, text=True)
    if result.returncode != 0:
        raise ValueError(f"Failed to push tags: {result.stderr}")

def create_github_release(version, changelog, github_token, github_repository):
    headers = {
        "Authorization": f"token {github_token}",
        "Content-Type": "application/json",
    }
    data = {
        "tag_name": f"v{version}",
        "name": f"v{version}",
        "body": changelog,
    }
    response = requests.post(
        f"https://api.github.com/repos/{github_repository}/releases",
        headers=headers,
        json=data,
    )
    response.raise_for_status()

if __name__ == "__main__":
    github_token = os.environ.get("GITHUB_TOKEN")
    github_repository = os.environ.get("GITHUB_REPOSITORY")

    if not github_token or not github_repository:
        print("Error: GITHUB_TOKEN and REPO_SLUG environment variables are required.")
        exit(1)

    new_version = get_new_version()
    changelog = get_changelog()
    push_tags()
    create_github_release(new_version, changelog, github_token, github_repository)
    print(f"Successfully created GitHub release v{new_version}")