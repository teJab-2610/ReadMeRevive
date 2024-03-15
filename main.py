import json

from installations.pydriller_install import install_pydriller
install_pydriller()

from installations.genai_install import install_genai
install_genai()

from installations.joern_install import install_joern

from github_infofetcher import GitHubInfoFetcher
from pydriller_commit_store import CommitStore
from shared_prompy import shared_prompt

import subprocess

def run():
    # Clone the repository
    # print("run")
    subprocess.run(['git', 'clone', 'https://github.com/embedchain/embedchain.git'])
    
    # Example code
    
    
    # Print commit_list if needed
    # print(commit_list)




run()
repo_url = "./embedchain"
commit_store = CommitStore(repo_url)

    # Assuming the definition of `CommitStore` is present in your code
    # Define `CommitStore` and other necessary imports in your script

repo_url = "https://github.com/embedchain/embedchain"
token = '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'
owner = "embedchain"
repo = "embedchain"

fetcher = GitHubInfoFetcher(token)
fetcher.main(repo_url)
commit_list = commit_store.get_hash_and_commit()
commit_hashes_issues=[]
merge_commit_shas =[]
commit_msgs=[]
commit_sum=[]

for merge_commit_sha,commit in commit_list:
  merge_commit_shas.append(merge_commit_sha)
  commit_msgs.append(commit.msg)
checksum=1
c=0
summaries = []

commits_summary = []
for merge_commit_sha, commit in commit_list:

    try:
        if c <560:
            c += 1
            continue
        if c == 571:
            break
        if len(commit.modified_files) > 3:
            c += 1
            print(f"Skipping commit {merge_commit_sha} with commit number {c} as it has {len(commit.modified_files)} files")
            continue
        summary = commit_store.get_files_summarise_code_2(merge_commit_sha, commit.msg, summaries)

        # Append commit hash and summary to the list
        commits_summary.append({"commit_hash": merge_commit_sha, "summary": summary})

        # Print information
        print(f"Summary generated for COMMIT NUMBER {c} with commit hash {merge_commit_sha}")

    except Exception as e:
        print(f"Error processing commit {merge_commit_sha}: {e}")

    c += 1

# Write the commits_summary list to commits_summary.json
with open("commits_summary.json", "w") as f:
    json.dump(commits_summary, f)


print("===============================================")