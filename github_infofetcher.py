import requests
from urllib.parse import urlparse
import re
import json
from datetime import datetime, timedelta
import base64

class GitHubInfoFetcher:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {"Authorization": f"Bearer {token}"}

    def get_issue_body(self, owner, repo, issue_number):
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
        headers = {'Authorization': f'token {self.token}'}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            issue_details = response.json()
            issue_title = issue_details.get("title")
            return issue_title
        else:
            print(f"Failed to fetch issue body for issue {issue_number}: {response.status_code}")
            print("Response body:", response.text)
            return None

    def get_pr_commits(self, owner, repo, pull_request_id):
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_request_id}/commits"
        headers = {'Authorization': f'token {self.token}'}
        commits_sha = []
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            commits = response.json()
            for commit in commits :
                commits_sha.append(commit.get('sha'))

            return commits_sha
        else:
            print(f"Failed to fetch commits for pull request {pull_request_id}: {response.status_code}")
            print("Response body:", response.text)
            return None

    def get_issue_number_from_pull_request(self, pr):
        pull_request_body = pr.get('body')
        if pull_request_body:
            match = re.search(r'(?:fix(?:es)?(?:ed)?|resolve(?:d)?|close(?:s)?(?:d)?|solve(?:d)?)[^\S\r\n]*:?\s*(https://github\.com/[^/]+/[^/]+/issues/(\d+))', pull_request_body, re.IGNORECASE)
            if match:
                issue_number = match.group(2)
                return issue_number
            else:
                return "No issue reference found in the pull request body.\n"

    def get_merged_pull_requests(self, owner, repo, since):
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=closed"
        headers = {'Authorization': f'token {self.token}'}
        pr_issue_numbers = []

        params = {'per_page': 100}  # Adjust per_page as needed
        page = 1
        edge_pr = None

        while True:
            response = requests.get(url + f"&page={page}", headers=headers, params=params)

            if response.status_code == 200:
                pull_requests = response.json()
                if not pull_requests:  # No more pull requests left
                    break

                last_pr = pull_requests[-1]

                merged_at_str = last_pr.get("merged_at")
                if merged_at_str:
                    merged_at = datetime.strptime(merged_at_str, "%Y-%m-%dT%H:%M:%SZ")
                else:
                    merged_at = None

                 # Stop fetching if last pull request is before 'since' date

                for pr in pull_requests:
                    if pr.get("merged_at"):
                        pr_number = pr.get("number")
                        merged_at = datetime.strptime(pr.get("merged_at"), "%Y-%m-%dT%H:%M:%SZ")
                        # print(pr_number," ", merged_at)
                        if merged_at >= since:
                            issue_number = self.get_issue_number_from_pull_request(pr)
                            # print(issue_number)
                            if issue_number and issue_number.isdigit():
                                #print(pr_number, " ", merged_at)
                                # print("Complete",pr)
                                pr_issue_numbers.append({'pull_request_id': pr_number, 'issue_number': issue_number})
                        else:
                            edge_pr = pr  # Update edge pull request

                page += 1
                if merged_at < since or merged_at is None:
                    break
            else:
                print(f"Failed to fetch merged pull requests: {response.status_code}")
                print("Response body:", response.text)
                break

        return pr_issue_numbers

    def get_all_merged_pull_requests(self, owner, repo, since):
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=closed"
        headers = {'Authorization': f'token {self.token}'}
        pr_issue_numbers = []

        params = {'per_page': 100}  # Adjust per_page as needed
        page = 1
        edge_pr = None

        while True:
            response = requests.get(url + f"&page={page}", headers=headers, params=params)

            if response.status_code == 200:
                pull_requests = response.json()
                if not pull_requests:  # No more pull requests left
                    break

                last_pr = pull_requests[-1]

                merged_at_str = last_pr.get("merged_at")
                if merged_at_str:
                    merged_at = datetime.strptime(merged_at_str, "%Y-%m-%dT%H:%M:%SZ")
                else:
                    merged_at = None

                 # Stop fetching if last pull request is before 'since' date

                for pr in pull_requests:
                    if pr.get("merged_at"):
                        pr_number = pr.get("number")
                        merged_at = datetime.strptime(pr.get("merged_at"), "%Y-%m-%dT%H:%M:%SZ")
                        # print(pr_number," ", merged_at)
                        pr_issue_numbers.append({'pull_request_id': pr_number})
                page += 1
                if merged_at < since or merged_at is None:
                    break
            else:
                print(f"Failed to fetch merged pull requests: {response.status_code}")
                print("Response body:", response.text)
                break

        return pr_issue_numbers

    def get_owner_and_repo_name(self, repo_url):
        parsed_url = urlparse(repo_url)
        path_components = parsed_url.path.strip('/').split('/')
        owner_username = path_components[0]
        repo_name = path_components[1]
        return owner_username, repo_name

    def get_merge_commit_sha(self, owner, repo, pull_request_id):
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_request_id}"
        headers = {'Authorization': f'token {self.token}'}
        merged_commit_sha = "";
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            #print(response.json())
            merge_commit_sha = response.json().get('merge_commit_sha')
            return merge_commit_sha
        else:
            print(f"Failed to fetch commits for pull request {pull_request_id}: {response.status_code}")
            print("Response body:", response.text)
            return None

    def get_file_before(self, owner, repo, mergee_commit_sha, file_path):
        # Get the parent commit of the specified commit
        url = f"{self.base_url}/repos/{owner}/{repo}/commits/{mergee_commit_sha}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        commit_info = response.json()

        # Get the parent commit's tree
        parent_sha = commit_info['parents'][0]['sha'] if commit_info['parents'] else None
        if parent_sha:
            # print("\n\n\n\n\n")
            # print(parent_sha)
            url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/{parent_sha}?recursive=1"
            # print(url)
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            tree_info = response.json()

            # Find the file in the tree
            file_info = next((item for item in tree_info['tree'] if item['path'] == file_path),None)
            if file_info is None:
              return ""
            # Get the content of the file
            url = file_info['url']
            # print(url)
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            file_content = response.json()['content']
            # print("\n\n\n\n\n")
            formatted_code = f"{base64.b64decode(file_content).decode('utf-8')}"
            # print(formatted_code)
            # print(file_content)
            # # Decode the Base64-encoded content

            # file_content = file_content.encode('utf-8')
            # print("\n\n\n\n\n")

            # print(file_content)
            # file_content = file_content.decode()

            return formatted_code
        else:
            return ""
    def get_file_after(self, owner, repo, merge_commit_sha, file_path):
        # Get the commit information
        url = f"{self.base_url}/repos/{owner}/{repo}/commits/{merge_commit_sha}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        commit_info = response.json()

        # Get the tree of the commit
        tree_sha = commit_info['commit']['tree']['sha']
        url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/{tree_sha}?recursive=1"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        tree_info = response.json()

        # Find the file in the tree
        file_info = next(item for item in tree_info['tree'] if item['path'] == file_path)

        # Get the content of the file
        url = file_info['url']
        print(f'After {url}')
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        file_content = response.json()['content']

        # Format file_content as a generic code block
        formatted_code = f"{base64.b64decode(file_content).decode('utf-8')}"

        return formatted_code
    def get_files(self,owner, repo, merge_commit_sha,checksum):
        # GitHub API URL to get the commit details
        commit_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{merge_commit_sha}"

        # Make a request to the GitHub API
        response = requests.get(commit_url)
        files=[]

        # Check if the request was successful
        if response.status_code == 200:
            commit_details = response.json()

            # Check if the file exists in the commit
            for file_info in commit_details['files']:
                # print("\n\n\n\n\n")
                # print(file_info)
                # print("\n\n\n\n\n")
                # print(file_info['filename'])
                # print(self.get_file_before(owner,repo,merge_commit_sha,file_info['filename']))


                files.append((file_info['filename'],self.get_file_before(owner,repo,merge_commit_sha,file_info['filename']),self.get_file_after(owner,repo,merge_commit_sha,file_info['filename']),checksum))
                print(files)
                checksum=checksum+1
        # If the file was not found in the commit, return None
        return files

    def main(self, repo_url):
        owner_username, repo_name = self.get_owner_and_repo_name(repo_url)
        since_date = datetime.now() - timedelta(days=1000)
        # #print(since_date)

        # merged_pull_requests = self.get_merged_pull_requests(owner_username, repo_name, since_date)
        merged_pull_requests = self.get_merged_pull_requests(owner_username, repo_name, since_date)

        # print(len(merged_pull_requests))
        # print(merged_pull_requests)
        final_response = []
        for merged_pr in merged_pull_requests:
            pr_number = merged_pr.get('pull_request_id')
            issue_number = merged_pr.get('issue_number')
            issue_title = self.get_issue_body(owner_username, repo_name,issue_number)
            commits = self.get_pr_commits(owner_username, repo_name,pr_number)
            merge_commit_sha = self.get_merge_commit_sha(owner_username, repo_name,pr_number)
            final_response.append({'pull_request_id': pr_number, 'issue_number': issue_number, 'issue_title': issue_title, 'commits_sha':commits, 'merge_commit_sha':merge_commit_sha})

        #Uncomment the below print command to see the json
        print(json.dumps(final_response, indent=4))

        with open('pr_info.json', 'w') as f:
            json.dump(final_response, f)
        # files=self.get_filename("embedchain","embedchain","200f11a0e0590c554a0379e40c94e82a0da7ce7c",1)

        # for f,x,y,c in files:
        #   print(f+"\n\n")
        #   print("Before:   \n")
        #   print(x)
        #   print("After:    \n")
        #   print(y)
        #   print("\n\n\n")

repo_url = "https://github.com/embedchain/embedchain"
token = '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'

fetcher = GitHubInfoFetcher(token)
fetcher.main(repo_url)

