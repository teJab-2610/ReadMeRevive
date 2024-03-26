import pathlib
import textwrap
from IPython.display import display
from IPython.display import Markdown
from github_infofetcher import GitHubInfoFetcher
from pydriller_commit_store import CommitStore
from git import Repo 
from classifier.classifier import Classifier
from commit_summary_gen import SummaryGenerator_Gemini

from RM_Update.RmLines_KG import RmLines_KG
from RM_Update.Similarity import Similarity
from RM_Update.Commits_KG import Commits_KG
from RM_Update.RmCommits_KG import RmCommits_KG

import json

from Keys import GEMINI_API_KEY
from Keys import GITHUB_API_KEY


def pre_processing(commit_store, commit_list):
    merge_commit_shas =[]
    commit_msgs=[]

    for merge_commit_sha,commit in commit_list:
        merge_commit_shas.append(merge_commit_sha)
        commit_msgs.append(commit.msg)
        summaries = []
        c=0

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

                    #TODO: Summarise even big commits
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
    print("Summary of commits written to commits_summary.json")

def update_readme(repo_url, commit_summary):

    readme_kg = RmLines_KG()
    readme_content = readme_kg.retrieve_readme_and_commits(repo_url)
    readme_dict = readme_kg.create_readme_dict(readme_content)

    rm_commits_kg = RmCommits_KG()
    readme_commits = rm_commits_kg.get_commits(repo_url)
    readme_commit_dict = rm_commits_kg.create_commit_dict(readme_commits, readme_dict)

    commits_kg = Commits_KG()
    code_commits = commits_kg.get_commits(repo_url)
    commit_dict = commits_kg.create_commit_dict(code_commits, commit_summary)

    text1 = (commit_dict[0][2][0] + commit_dict[0][2][1] + commit_dict[0][2][2])
    threshold = 0.1
    similarity = Similarity()

    similar_key, is_similar = similarity.find_similar_text(text1, readme_dict, threshold)
    if not is_similar:
        t = len(readme_dict)
        triples = list(similarity.processSentence(text1))
        readme_dict[triples[0] + triples[1] + triples[2]] = t + 1


def main():

    # llm_model = SummaryGenerator_Gemini()
    # if(llm_model.test):
    #     print("Model is running")
    # else:
    #     print("Model is not running")

    #get repo_url from user
    repo_url = input("Enter the repository URL: ")
    #TODO: Check if it is a valid github repository url it is of the form "https://github.com/repo_owner/repo_name"
     
    print("\nFetching commits linked with issue in the repository....")
    fetcher = GitHubInfoFetcher(GITHUB_API_KEY)
    fetcher.main(repo_url) 

    #if it is a valid github repository url, then extract the owner and repo name
    owner = repo_url.split('/')[3]
    repo = repo_url.split('/')[4]
    
    #if repo present in root folder, then use the repo name else clone it 
    if pathlib.Path(repo).exists():
        print("\nRepository found in root folder.\n")
        repo_url = repo
    else:
        #clone the repository
        print("\nCloning the repository....")
        Repo.clone_from(repo_url, '.')
        print("\nRepository cloned successfully.\n")
        
    commit_store = CommitStore("./"+repo)
    commit_list=commit_store.get_hash_and_commit()

    #TODO: Get start and end commits to summarise
    # start_commit = input("Enter the start commit: ")
    # end_commit = input("Enter the end commit: ")

    # pre_processing(commit_store, commit_list)

    #classify the commits
    classifier = Classifier()
    while True:
        commit_hash= input("Enter the commit hash to classify or 'exit' to exit :")
        if commit_hash == 'exit':
            break
        
        #if given commit hash is not in the commit_list.commit_map print error
        if commit_hash not in commit_store.commit_map:
            print("Commit hash not found in the commit list")
            continue

        #generate a summary for it 
        summary = commit_store.get_files_summarise_code_2(commit_hash, commit_store.commit_map[commit_hash].msg, [])
        print(f"Summary generated for commit {commit_hash}")
        
        #classify the commit
        cluster_number = classifier.classify_commit(summary)


        update_readme("./"+repo, summary)

if __name__ == "__main__":
    main() 