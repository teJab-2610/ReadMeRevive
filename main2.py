import json

from pydriller_install import install_pydriller
install_pydriller()

from genai_install import install_genai
install_genai()
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
# commit_hashes = ["6fcc33ec4ec075090adc292368ece5afc30e9995","fd0c44b91363455f5a3d156a9500d14ed87bde92","54287653298e18ef5661e3224958de0bb06d5864","200f11a0e0590c554a0379e40c94e82a0da7ce7c"]

commit_hashes_issues=[]
with open('pr_info.json', 'r') as file:
    data = json.load(file)
merge_commit_shas = []
commits=[]
for pr_json in data:
  merge_commit_shas.append(pr_json['merge_commit_sha'])
  commit_hashes_issues.append(pr_json['issue_title'])
  commits.append(commit_store.commit_map[pr_json['merge_commit_sha']])

# print("mcs , issue title:")
# for sha in merge_commit_shas:
#     print(sha)
#     print(commit_hashes_issues[merge_commit_shas.index(sha)])
checksum=1
for merge_commit_sha,commit, issue_title in zip(merge_commit_shas,commits, commit_hashes_issues):
    # print(f"Commit hash: {commit_hash}")
    # commit_store.get_commit_info(merge_commit_sha)
    # files=fetcher.get_files(owner,repo,merge_commit_sha,checksum)
    summary = commit_store.get_files_summarise_code_3(merge_commit_sha,commit.msg,issue_title)
    print(summary)
    # checksum = checksum+1

    print("===============================================")