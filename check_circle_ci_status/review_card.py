import sys
import os
import re
from dotenv import load_dotenv
from github import Github
from redminelib import Redmine
import requests
import base64
import time

g = Github("<GITHUB_TOKEN>")
api_token = "<CLICKUP_API_TOKEN>"

api_base_url = "https://api.clickup.com/api/v2"

headers = {
    "Authorization": api_token,
}

def get_cards_details(tag_card):
    try:
        tag_card_id = tag_card
        endpoint_to_get_task = f"{api_base_url}/task/{tag_card_id}"
        response = requests.get(endpoint_to_get_task, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result

        else:
            print("Error:", response.status_code, response.text)
    except Exception as e:
        print("An error occurred:", e)

def get_pr_links(issue_description):
    # match_real = re.search(r'^[# ]*?(?:PR|pull request)[\s\w\d]*?merged.*?$(.*?https://github.com/[^#]*)', issue_description, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    match_real = re.search(r'^\s*(?:PR|pull request)[\s\w\d]*?merged.*?$(.*?https://github.com/[^#\s]*)', issue_description, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    match_dummy = re.search(r'^[# ]*?Dummy.*?$(.*?https://github.com/[^#]*)', issue_description, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    
    pr_links1 = []
    pr_links2 = []
    if match_real:
        prs = match_real.group(1)
        
        pr_links1 = re.findall(r'https?://github\.com/[^/\s]+/[^/\s]+/pull/\d+', prs)

    if match_dummy:
        prs2 = match_dummy.group(1)
        pr_links2 = re.findall(r'https?://github\.com/[^/\s]+/[^/\s]+/pull/\d+', prs2)


    all_pr_links = pr_links1 + pr_links2
    # print(f'pr_links1 : {pr_links1}')
    # print(f'pr_links2 : {pr_links2}')
    # print(f'{all_pr_links}')

    return all_pr_links

def get_pr_status(github, repo_path, pull_number, pr_link, card_url):
    arr=[]
    url_printed = False
    repo = github.get_repo(repo_path)
    pr = repo.get_pull(int(pull_number))
    commit_sha = pr.head.sha
    files_changed = pr.get_files()

    for file_changed in files_changed:
        chef_cookbook=file_changed.filename.split('/')

        if repo_path == "regentmarkets/chef" :
            if re.search('metadata.rb', file_changed.filename):
                content = file_changed.raw_data['patch']
                f = open("myfile.txt", "w")
                f.write(content)
                f.close
                f = open("myfile.txt", "r")

                fh = f.readlines()

                for line in fh:
                    arr=[]
                    if line.startswith("-version"):
                        old_changes = line.split()
                        old_version = old_changes[1].strip("'")
                f.close

                branch_name='master'
                master_branch=repo.get_contents(file_changed.filename,ref=branch_name)
                master_branch_readable=master_branch.content
                decoded_content = base64.b64decode(master_branch_readable)
                version_pattern = r"version\s*'([^']+)'"
                match = re.search(version_pattern, str(decoded_content))
                if match.group(1)== old_version:
                    print("success chef changes")
                else:
                    print(f'Ask dev to update chef version for ,{pr_link}, {card_url}')

    get_pr_checks_status(repo, commit_sha, pr_link, card_url)
    mergeable_status = pr.mergeable
    # print(f'{pr.mergeable} : {pr_link}')
    if mergeable_status == None and pr.merged != True:
        if not url_printed: 
            print(f'RUN THE SCRIPT AGAIN. GITHUB BACKGROUND ACTIVITY ONGOING')
            # print(f'CANNOT MERGE for {pr_link}  {card_url}')
            url_printed = True
    elif pr.merged == True:
        print(f'PR is merged : {pr_link}')
    elif mergeable_status == False or pr.mergeable_state == 'blocked':
        print(f'CANNOT MERGE for {pr_link}  {card_url}')

        

def get_pr_checks_status(repo, commit_sha, pr_link, card_url):
    url_printed = False
    check_runs = repo.get_commit(commit_sha).get_check_runs()
    for check_run in check_runs:
        check_run_status = check_run.conclusion
        if check_run_status != "success":
            if not url_printed:
                print(f'Checks not passing for {pr_link}  {card_url}')
                url_printed = True

start_time = time.time()
if len(sys.argv) != 2:
    sys.exit("Program terminated unexpectedly")

url_clickup_tag_card=sys.argv[1]
split_url_tag_card=url_clickup_tag_card.split('/')
tag_card_details = get_cards_details(split_url_tag_card[-1])

for card in tag_card_details["custom_fields"]:
    if card["type"] == "list_relationship":
        for i in card["value"]: 
            task_card_data = get_cards_details(i["id"])
            print(f'{task_card_data["name"]}\n')
            task_card_description = task_card_data["description"]
            all_pr_links = get_pr_links(task_card_description)
            for item in all_pr_links:
                pattern = r".+\.com/(.+)/pull/(\d+)$"
                match = re.match(pattern, item)

                if match:
                    repo_path = match.group(1)
                    pull_number = match.group(2)
                    get_pr_status(g, repo_path, pull_number, item, i["url"])
                else:
                    print("No match found.")
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Script execution time: {elapsed_time} seconds")        