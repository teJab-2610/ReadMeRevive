import re
from pydriller import Repository
import subprocess

from Treemaker import TreeMaker
from commit_summary_gen import SummaryGenerator_Gemini

class CommitStore:
    def __init__(self, repo_url):
        self.commit_map = {}
        self.populate_commits(repo_url)

    def populate_commits(self, repo_url):
        repo = Repository(repo_url)
        # print(len(self.commit_map))
        for commit in repo.traverse_commits():
            # print("Commit Hash:", commit.hash, "Branches:", ", ".join(commit.branches),"\n")
            self.commit_map[commit.hash] = commit
        print("map len", len(self.commit_map))


    def print_commit_hashes(self):
        print("Number of commits: ", )
        print("Commit Hashes:")
        for commit_hash in self.commit_map:
              print(commit_hash)

    def get_hash_and_commit(self):
        l=[]
        for commit_hash in self.commit_map:
          l.append((commit_hash,self.commit_map.get(commit_hash)))
        return l


    def get_commit_info(self, commit_hash):
        commit = self.commit_map.get(commit_hash)
        # print(commit)
        for attribute, value in commit.__dict__.items():
            print(f"{attribute}: {value}")


        if commit:
            modified_files = commit.modified_files
            # commit_body = commit.commit
            message = commit.msg
            print(message)
            for file in modified_files:
                print("FileName:", file.filename)
                print("FileDiff:", file.diff)

                for method in file.changed_methods:
                    method_before = next((x for x in file.methods_before if x == method),"")
                    method_after = next((x for x in file.methods if x == method), "")
                    body_before = _getMethodBody(method_before, file.source_code_before, file)
                    body_after = _getMethodBody(method_after, file.source_code, file)

                    print("MethodName:", method.name)
                    print("MethodBodyBefore:", body_before)
                    print("MethodBodyAfter:", body_after)
                    print()

        else:
            print(f"Commit with hash {commit_hash} not found.")

    def get_files_summarise(self, commit_hash, tree_type,issue_title):

        commit = self.commit_map.get(commit_hash)
        summary_gen = SummaryGenerator_Gemini()

        # print(commit)
        if commit:
            if(issue_title==None):
              issue_title=""
            message = commit.msg
            modified_files = commit.modified_files
            all_modified_methods_summaries = []

            for file in modified_files:
                # print("FileName:", file.filename)
                # print("FileDiff:", file.diff)

                for method in file.changed_methods:
                    method_before = next((x for x in file.methods_before if x == method), None)
                    method_after = next((x for x in file.methods if x == method), None)
                    body_before = _getMethodBody(method_before, file.source_code_before, file)
                    body_after = _getMethodBody(method_after, file.source_code, file)

                    # print("MethodName:", method.name)
                    # print("MethodBodyBefore:", body_before)
                    # print("MethodBodyAfter:", body_after)
                    # print()
                    extension = get_file_extension(file.filename)

                    # Write method_before to file if not None
                    if body_before is not None and extension:
                        with open(f"{method.name}_before.{extension}", "w") as f:
                            f.write(body_before)

                    # Write method_after to file if not None
                    if body_after is not None and extension:
                        with open(f"{method.name}_after.{extension}", "w") as f:
                            f.write(body_after)
                    treemaker = TreeMaker(f"{method.name}_before.{extension}",f"{method.name}_after.{extension}","method_before","method_after","dot")
                    if(tree_type=="ast"):
                      treemaker.generate_AST_trees()
                      summary_of_method = ""
                      if(issue_title):
                        summary_of_method = ""+summary_gen.ast_summaries(issue_title)
                      all_modified_methods_summaries.append("In file " + file.filename + " for the method " + method.name + " the change is as follows " + summary_of_method)

                    elif tree_type=="all":
                      treemaker.generate_ALL_trees()
                      summary_of_method = ""
                      if(issue_title):
                        summary_of_method = ""+summary_gen.all_summaries(issue_title)
                      all_modified_methods_summaries.append("In file " + file.filename + " for the method " + method.name + " the change is as follows " + summary_of_method)

                    elif tree_type=="cdg":
                      treemaker.generate_CDG_trees()
                      summary_of_method = ""
                      if(issue_title):
                        summary_of_method = ""+summary_gen.cdg_summaries(issue_title)
                      all_modified_methods_summaries.append("In file " + file.filename + " for the method " + method.name + " the change is as follows " + summary_of_method)

                    elif tree_type=="cpg":
                      treemaker.generate_CPG_trees()
                      summary_of_method = ""
                      if(issue_title):
                        summary_of_method = ""+summary_gen.cpg_summaries(issue_title)
                      all_modified_methods_summaries.append("In file " + file.filename + " for the method " + method.name + " the change is as follows " + summary_of_method)

                    elif tree_type=="cfg":
                      treemaker.generate_CFG_trees()
                      summary_of_method = ""
                      if(issue_title):
                        summary_of_method = ""+summary_gen.cfg_summaries(issue_title)
                      all_modified_methods_summaries.append("In file " + file.filename + " for the method " + method.name + " the change is as follows " + summary_of_method)

                    elif tree_type=="ddg":
                      treemaker.generate_DDG_trees()
                      summary_of_method = ""
                      if(issue_title):
                        summary_of_method = ""+summary_gen.ddg_summaries(issue_title)
                      all_modified_methods_summaries.append("In file " + file.filename + " for the method " + method.name + " the change is as follows " + summary_of_method)

                    elif tree_type=="pdg":
                      treemaker.generate_PDG_trees()
                      summary_of_method = ""
                      if(issue_title):
                        summary_of_method = ""+summary_gen.pdg_summaries(issue_title)
                      all_modified_methods_summaries.append("In file " + file.filename + " for the method " + method.name + " the change is as follows " + summary_of_method)

                    subprocess.run(["rm", f"{method.name}_before.{extension}", f"{method.name}_after.{extension}"])
            # if(issue_title):
            summarise_commit = summary_gen.commit_summary(all_modified_methods_summaries, issue_title)
            print("Commit Summary for the commit hash ", commit_hash," : \n")
            return summarise_commit
            # else:
            #   summarise_commit = summary_gen.commit_summary(all_modified_methods_summaries)


            # print(summarise_commit)

        else:
            print(f"Commit with hash {commit_hash} not found.")
        #             summary_of_method = ""
        #             if(issue_title):
        #               summary_of_method = ""+summary_gen.ast_summaries(issue_title)
        #             all_modified_methods_summaries.append("In file " + file.filename + " for the method " + method.name + " the change is as follows " + summary_of_method)
        #     if(issue_title):
        #       summarise_commit = summary_gen.commit_summary(all_modified_methods_summaries, issue_title)
        #     else:
        #       summarise_commit = summary_gen.commit_summary(all_modified_methods_summaries)


        #     print("Commit Summary for the commit hash ", commit_hash," : \n")
        #     print(summarise_commit)

        # else:
        #     print(f"Commit with hash {commit_hash} not found.")
    def get_files_summarise_code(self, commit_hash,commit_msg,issue_title=None, summaries=[]):
          summaries=[]
          commit = self.commit_map.get(commit_hash)
          summary_gen = SummaryGenerator_Gemini()
          # print(commit)
          if commit:
              if(issue_title==None):
                issue_title=""
              message = commit.msg
              modified_files = commit.modified_files
              all_modified_methods_summaries = []
              file_summaries=[]
              i=0
              for file in modified_files:
                  # print("FileName:", file.filename)
                  # print("FileDiff:", file.diff)

                  fileName=file.filename
                  for method in file.changed_methods:

                      method_before = next((x for x in file.methods_before if x == method), None)
                      method_after = next((x for x in file.methods if x == method), None)
                      body_before = _getMethodBody(method_before, file.source_code_before, file)
                      body_after = _getMethodBody(method_after, file.source_code, file)

                      # print("MethodName:", method.name)
                      # print("MethodBodyBefore:", body_before)
                      # print("MethodBodyAfter:", body_after)
                      summary_of_method = ""
                      summary_of_method = ""+summary_gen.method_summary(body_before,body_after)
                      # print("method summary :\n", summary_of_method)
                      all_modified_methods_summaries.append((file.filename,method.name,summary_of_method))

                  i=i+1
                  # print(f"gbbeuwxi 35D S{get_files(fileName,files,i)}")
                  # f,file_bf, file_af,c = get_files(fileName,files,i)
                  f,file_bf, file_af = fileName,file.source_code_before,file.source_code
                  if file_bf is None:
                    file_bf=""
                  if file_af is None:
                    file_af=""
                  file_summarie = ""+summary_gen.file_summary(fileName,file_bf,file_af,all_modified_methods_summaries)
                  file_summaries.append((fileName,file_summarie))
                  all_modified_methods_summaries = []


              # if(issue_title):
              #   summarise_commit = summary_gen.commit_summary(all_modified_methods_summaries, issue_title)
              # else:
              #   summarise_commit = summary_gen.commit_summary(all_modified_methods_summaries)
              summarise_commit=summary_gen.commit_summary_code(commit_msg, file_summaries)
              summaries.append({
                  'commitId': commit_hash,
                  'commit_message': commit_msg,
                  'file_summaries' : file_summaries,
                  'summary' : summarise_commit
              })
              print("Commit Summary for the commit hash ", commit_hash," : \n")
              print(summarise_commit)
              return summaries

    def get_files_summarise_code_2(self, commit_hash,commit_msg,issue_title=None):

          commit = self.commit_map.get(commit_hash)
          summary_gen = SummaryGenerator_Gemini()
          # print(commit)
          if commit:
              if(issue_title==None):
                issue_title=""
              message = commit.msg
              modified_files = commit.modified_files
              # all_modified_methods_summaries = []
              file_summaries=[]
              file_diff_summaries=[]
              i=0
              for file in modified_files:
                  fileName=file.filename
                  f,file_bf, file_af = fileName,file.source_code_before,file.source_code
                  if file_bf is None:
                    file_bf=""
                  if file_af is None:
                    file_af=""
                  file_summarie = ""+summary_gen.file_summary_individual(fileName,file_bf,file_af)
                  file_diff_summarie=""+summary_gen.file_summary_fdiff(fileName,file.diff)
                  file_summaries.append((fileName,file_summarie))
                  file_diff_summaries.append((fileName,file_diff_summarie))
              summarise_commit=summary_gen.commit_summary_code_diff(message,file_summaries,file_diff_summaries)

              print("Commit Summary for the commit hash ", commit_hash," : \n")
              print(summarise_commit)
              return summarise_commit

    def get_files_summarise_code_3(self, commit_hash,commit_msg,issue_title):

          commit = self.commit_map.get(commit_hash)
          summary_gen = SummaryGenerator_Gemini()
          # print(commit)
          if commit:
              if(issue_title==None):
                issue_title=""
              message = commit.msg
              modified_files = commit.modified_files
              # all_modified_methods_summaries = []
              file_summaries=[]
              file_diff_summaries=[]
              i=0
              for file in modified_files:
                  fileName=file.filename
                  f,file_bf, file_af = fileName,file.source_code_before,file.source_code
                  if file_bf is None:
                    file_bf=""
                  if file_af is None:
                    file_af=""
                  file_summarie = ""+summary_gen.file_summary_individual(fileName,file_bf,file_af)
                  file_diff_summarie=""+summary_gen.file_summary_fdiff(fileName,file.diff)
                  file_summaries.append((fileName,file_summarie))
                  file_diff_summaries.append((fileName,file_diff_summarie))
              summarise_commit=summary_gen.commit_summary_code_issue_diff(message,file_summaries,file_diff_summaries,issue_title)

              print("Commit Summary for the commit hash ", commit_hash," : \n")
            #   print(summarise_commit)
              return summarise_commit

def _getMethodBody(method, source_code, file):
    if method and source_code:
        lines = source_code.split("\n")
        start = method.start_line
        end = method.end_line
        method_body = "\n".join(lines[start - 1: end])

        # Calculate the indentation level of the method
        indentation_level = len(lines[start - 1]) - len(lines[start - 1].lstrip())

        # Remove leading whitespace based on the indentation level
        method_body_stripped = "\n".join([line[indentation_level:] if len(line) >= indentation_level else '' for line in method_body.split("\n")])

        return method_body_stripped
    return None

def get_files(filename,files,checksum):
  # print(f"fileName: {filename}   checksum: {checksum}")
  # print(f"files: {files}")
  for f,x,y,c in files:
    n=get_filename_from_path(f)
    # print(f"n: {n}   filename: {filename}  c: {c}   checksum: {checksum}")
    if(n==filename and c==checksum):
      return f,x,y,c
  return None

def get_file_extension(filename):
  # Use regex to match the file extension
  match = re.search(r'\.([^.]+)$', filename)
  if match:
      return match.group(1)
  else:
      return None

def get_filename_from_path(file_path):
    # Using regular expression to extract filename with extension
    match = re.search(r'([^/]+)$', file_path)
    # print(f"match {match}")
    # print(f"matchjb wcyg {match.group(1)}")

    if match:
        return match.group(1)
    else:
        return None
