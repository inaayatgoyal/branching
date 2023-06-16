import subprocess
import os


def get_commit_message(commit):
    command = f"git show --quiet --format=%B {commit}"
    output = subprocess.check_output(command, shell=True,stderr=subprocess.DEVNULL)
    return output.decode("utf-8").strip()


def get_changed_files(commit):
    command = f"git show --name-only --pretty=format: {commit}"
    output = subprocess.check_output(command, shell=True,stderr=subprocess.DEVNULL)
    files = output.decode("utf-8").split("\n")
    return [file.strip() for file in files if file.strip().endswith(".sql")]


def read_file_contents(file_path):
    with open(file_path, 'r') as f:
        return f.read()


def extract_sql_files(commit_id):
    command = f"git checkout {commit_id}"
    subprocess.check_output(command, shell=True,stderr=subprocess.DEVNULL)
    changed_files = get_changed_files(commit_id)
    return changed_files


def read_sql_file(commit_id, file_path):
    command = f"git show {commit_id}:{file_path}"
    try:
        output = subprocess.check_output(command, shell=True,stderr=subprocess.DEVNULL)
        return output.decode("utf-8")
    except subprocess.CalledProcessError:
        return None


def get_commit_ids(branch1, branch2):
    command = f"git log --cherry-pick --right-only {branch1}...{branch2} --pretty=format:%H"
    output = subprocess.check_output(command, shell=True,stderr=subprocess.DEVNULL)
    commit_ids = output.decode("utf-8").split("\n")
    return [commit_id for commit_id in commit_ids if commit_id]


def contains_create_or_alter_statements(file_contents):
    keywords = ["CREATE", "ALTER"]
    return any(keyword in file_contents.upper() for keyword in keywords)


def extract_sql_files_for_commits(branch1, branch2):
    commit_ids = get_commit_ids(branch1, branch2)
    sql_files = []
    for commit_id in commit_ids:
        files = extract_sql_files(commit_id)
        if files:
            sql_files.append((commit_id, files))
    return sql_files


def print_filtered_commits(branch1, branch2):
    sql_files = extract_sql_files_for_commits(branch1, branch2)
    if not sql_files:
        print("No files found.")
        return
    filtered_commit_ids = []
    for commit_id, files in sql_files:
        for file in files:
            file_contents = read_sql_file(commit_id, file)
            if file_contents is None:
                continue
            if contains_create_or_alter_statements(file_contents):
                filtered_commit_ids.append(commit_id)
                break

    print("Filtered Commit IDs and Messages:")
    for commit_id in filtered_commit_ids:
        if "HEAD" in commit_id or "Previous HEAD" in commit_id:
            continue
        commit_message = get_commit_message(commit_id)
        print(commit_id[:8], commit_message)


# Usage
branch1 = "v2.3.0"
branch2 = "v2.0.0"
print_filtered_commits(branch1, branch2)
