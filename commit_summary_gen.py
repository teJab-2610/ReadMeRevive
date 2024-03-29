import pathlib
import textwrap
import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown

import requests

class SummaryGenerator_Gemini:


  def extract_contents(self, fpath):
    with open(fpath, 'r') as file:
      contents = file.read()
    return contents

  def promt_response(self, prompt, graph_before, graph_after, graph_type):
    response = model.generate_content(prompt +" "+graph_type+"  of code before commit : "+graph_before+"  "+graph_type + " of code after commit : "+ graph_after)
    return response.text

  def ast_summaries(self, issue_title = None):
    #prompt = "You are given a two Abstract Syntax Trees of some programming language code snippet before and after a commit. I need to know what both the code snippets do exactly. Explain briefly in few lines just the functinoality of both the codes. Also tell what was the change and how did it change the functionality of the code and what issue did it solve in the code."
    prompt = "You are given a two Abstract Syntax Trees of some programming language code snippet before and after a commit. Explain briefly what was the change and how did it change the functionality of the code and if possible what issue did it solve in the code."

    if(issue_title):
      prompt = prompt+ " This commit is linked to the issue "+issue_title

    method_before="/content/method_before/ast/1-ast.dot"
    method_after="/content/method_after/ast/1-ast.dot"

    digraph_before = self.extract_contents(method_before)
    digraph_after = self.extract_contents(method_after)

    summary = self.promt_response(prompt,digraph_before,digraph_after, "AST")

    print("Summary based on Ast: ")
    return summary

  def cdg_summaries(self, issue_title = None):
    prompt = "You are given a two Control Dependence graphs of some programming language code snippet before and after a commit. Summarize control dependence of both code snippets. Explain briefly in few lines how did the commit change the code and what issue did it solve in the code."

    if(issue_title):
      prompt = prompt+ " This commit is linked to the issue "+issue_title

    method_before="/content/method_before/cdg/1-cdg.dot"
    method_after="/content/method_after/cdg/1-cdg.dot"

    digraph_before = self.extract_contents(method_before)
    digraph_after = self.extract_contents(method_after)

    summary = self.promt_response(prompt,digraph_before,digraph_after, "CDG")

    print("Summary based on Cdg: ")
    return summary

  def cfg_summaries(self, issue_title = None):
    prompt = "You are given a two Control Flow graphs of some programming language code snippet before and after a commit. I need to know control flow of both the graphs. Explain briefly in few lines how did it change the functionality or the control flow of the code and what issue did it solve in the code."

    if(issue_title):
      prompt = prompt+ " This commit is linked to the issue "+issue_title

    method_before="/content/method_before/cfg/1-cfg.dot"
    method_after="/content/method_after/cfg/1-cfg.dot"

    digraph_before = self.extract_contents(method_before)
    digraph_after = self.extract_contents(method_after)

    summary = self.promt_response(prompt,digraph_before,digraph_after, "CFG")

    print("Summary based on Cfg: ")
    return summary

  def pdg_summeries(self, issue_title = None):
    prompt = "You are given a two Program dependence graphs of some programming language code snippet before and after a commit. I need to know if there is any dependency changes. Explain briefly in few lines how did it change the functionality of the code and what issue did it solve in the code."

    if(issue_title):
      prompt = prompt+ " This commit is linked to the issue "+issue_title

    method_before="/content/method_before/pdg/1-pdg.dot"
    method_after="/content/method_after/pdg/1-pdg.dot"

    digraph_before = self.extract_contents(method_before)
    digraph_after = self.extract_contents(method_after)

    summary = self.promt_response(prompt,digraph_before,digraph_after, "PDG")

    print("Summary based on Pdg: ")
    return summary

  def cpg_summaries(self, issue_title = None):
    prompt = "You are given two code property graphs of some programming language code snippet before and after a commit. I need to know what both the code snippets do exactly. Explain briefly in few lines just the functinoality of both the codes. Also tell what was the change and how did it change the functionality of the code and what issue did it solve in the code."

    if(issue_title):
      prompt = prompt+ " This commit is linked to the issue "+issue_title

    method_before="/content/method_before/cpg14/1-cpg.dot"
    method_after="/content/method_after/cpg14/1-cpg.dot"

    digraph_before = self.extract_contents(method_before)
    digraph_after = self.extract_contents(method_after)

    summary = self.promt_response(prompt,digraph_before,digraph_after, "CPG")

    print("Summary based on Cpg: ")
    return summary

  def all_summaries(self, issue_title = None):
    prompt = "You are given two code property graphs of some programming language code snippet before and after a commit. I need to know what both the code snippets do exactly. Explain briefly in few lines just the functinoality of both the codes. Also tell what was the change and how did it change the functionality of the code and what issue did it solve in the code."

    if(issue_title):
      prompt = prompt+ " This commit is linked to the issue "+issue_title

    method_before="/content/method_before/all/export.dot"
    method_after="/content/method_after/all/export.dot"

    digraph_before = self.extract_contents(method_before)
    digraph_after = self.extract_contents(method_after)

    summary = self.promt_response(prompt,digraph_before,digraph_after, "All")

    print("Summary based on All: ")

    return summary

  def commit_summary(self, method_wise_summaries, issue_title):
    x=""
    for single_method_sumamry in method_wise_summaries:
      x+= single_method_sumamry+"\n"
    print(x)
    prompt =     """In a given commmit, the summaries of changes in different methods in different files is generated based on before and after of methods code property graph are gives as\n"""+x+"""and the title of issue which the commit has solved is gives as\n"""+issue_title+""". Now based on the summaries and issue title , on a high level summaries the overall commit into one or multiple of following categories in software engineer point of view. For exaple if a commit is of the type bug fix and tests, give only two lines brief summary onoe for the bug fix and one for the tests.

Given below is a small explanation for each category:

Feature: Commits related to implementing new features or functionalities in the project.

Bug Fix: Commits addressing and fixing issues, bugs, or defects in the codebase.

Refactor: Commits focused on improving code quality, organization, or structure without changing its external behavior.

Documentation: Commits related to updating or adding documentation such as README files, inline comments, or documentation files.

Performance: Commits aimed at improving the performance of the codebase, such as optimizing algorithms, reducing resource usage, or enhancing execution speed.

Dependency Update: Commits updating dependencies, libraries, or third-party components used in the project to newer versions.

Tests: Commits related to adding, updating, or fixing tests to ensure code quality and reliability.

Configuration: Commits updating configuration files, such as environment variables, build scripts, or project settings.

Localization/Internationalization: Commits related to adding or updating translations, localization, or internationalization features in the project.

Style/Formatting: Commits focused on enforcing consistent code style, formatting, or coding conventions across the codebase.

Chore: Commits related to general maintenance tasks, administrative work, or other miscellaneous changes that don't fit into other categories.

Security: Commits addressing security vulnerabilities, implementing security measures, or ensuring compliance with security standards.
  After above, Also give a short summary on addition , deletion and modification due to the commit  """
    # if(issue_title):
    #   prompt+= "The commit is linked to the issue titled, "+ issue_title

    # prompt+= "Below I am giving you the summaries of different methods that got changed."



    response = model.generate_content(prompt)
    commit_summary = response.text
    return commit_summary

  def method_summary(self,method_bf,method_af):
    if(method_bf==None ):
      method_bf=""
    if(method_af==None ):
      method_af=""
    prompt= """" I have two versions of method code before and after a commit , give me key differences as concisely as possible in software engineer point of view, method before : """
    prompt=prompt+method_bf+"\n"+"method after: "+method_af
    response = model.generate_content(prompt)
    method_summary = response.text
    print(f"\n\n method: \n")
    return method_summary

  def file_summary(self,fileName,file_bf,file_af,all_modified_methods_summaries):
    prompt= """" I have two versions of file code before and after a commit and summaries of changes in the file's methods , give me key differences as concisely as possible in software engineer point of view, file before : """
    prompt=prompt+file_bf+"\n"+"file after: "+file_af
    for f,methodName,method_summary in all_modified_methods_summaries:
      prompt = prompt+"\n"+methodName+" change summary : \n"+method_summary
    response = model.generate_content(prompt)
    file_summary = response.text
    print(f"\n\n\n file  : \n ")
    return file_summary


  def file_summary_individual(self,fileName,file_bf,file_af):
    prompt= """" I have two versions of file code before and after a commit.
File before commit:
"""+file_bf+"""

File after commit:
"""+file_af+"""

Please summarize it in a comment, describing the changes made in the diff in high level.
Do it in the following way:
Write the file name and then write a brief summary of changes of what happend in the file. Keep it as simple as possible like headline which can help a software engineer understand easily. """
    prompt=prompt+file_bf+"\n"+"file after: "+file_af
    # for f,methodName,method_summary in all_modified_methods_summaries:
    #   prompt = prompt+"\n"+methodName+" change summary : \n"+method_summary
    response = model.generate_content(prompt)
    file_summary = response.text
    print(f"\n\n\n file: \n ")
    return file_summary

  def file_summary_fdiff(self,fileName,file_diff):
    # prompt= """" I have two versions of file code before and after a commit , give me key differences as concisely as possible in software engineer point of view, file before : """
    prompt="""You are an expert programmer, and you are trying to summarize a git diff.
Reminders about the git diff format:
For every file, there are a few metadata lines, like (for example):
\\\`
diff --git a/lib/index.js b/lib/index.js
index aadf691..bfef603 100644
--- a/lib/index.js
+++ b/lib/index.js
\\\`
This means that \lib/index.js\ was modified in this commit. Note that this is only an example.
Then there is a specifier of the lines that were modified.
A line starting with \+\ means it was added.
A line that starting with \-\ means that line was deleted.
A line that starts with neither \+\ nor \-\ is code given for context and better understanding.
It is not part of the diff.

The following is a git diff of a single file. """+file_diff+"""
Please summarize it in a comment, describing the changes made in the diff in high level.
Do it in the following way:
Write the file name and then write a brief summary of changes of what happend in the file. Keep it as simple as possible like headline which can help a software engineer understand easily."""
    # for f,methodName,method_summary in all_modified_methods_summaries:
    #   prompt = prompt+"\n"+methodName+" change summary : \n"+method_summary
    response = model.generate_content(prompt)
    file_summary = response.text
    print(f"\n\n\n file: \n ")
    return file_summary

  def commit_summary_code(self,commit_msg,file_summaries):

    prompt= """"
    I have file change summaries before and after a commit and commit message , give me key differences as concisely as possible in software engineer point of view,
    Summarise the commit and tell me what type of commit it might be from the following categories like "Bugfix", "Feature", "Dependencies", "Platform Support".
     Here "Bugfix" means anything related to fixing bugs or errors in the code.
     "Feature" means anything related to increasing functionality or features in the software
     "Dependencies" means anything related to solving current dependency issues
     "Platform Support" means anything related to increasing usability of the software on different platforms like linux and windows or ios and android"

    """
    # prompt = """
    # I have a commit in which some number of methods changed. Summarise the commit and tell me what type of commit it might be from the following categories like "Bugfix", "Feature", "Dependencies", "Platform Support".
    # Here "Bugfix" means anything related to fixing bugs or errors in the code.
    # "Feature" means anything related to increasing functionality or features in the software
    # "Dependencies" means anything related to solving current dependency issues
    # "Platform Support" means anything related to increasing usability of the software on different platforms like linux and windows or ios and android"
    # """
    for fileName , file_summary in file_summaries:
      prompt= prompt + "\nIn this file" + fileName + " the changes have been summarized like this : \n"+file_summary
    prompt=prompt+"\n Commit message : "+commit_msg+" don't give seperated file summaries"
    # print(prompt)
    response = model.generate_content(prompt)
    commit_summary = response.text
    # print("Commit summary: ", commit_summary)
    # print(f"\n\n\n\n\n\n commit : \n {commit_summary} ")
    return commit_summary

  def commit_summary_code_diff(self,commit_msg,file_summaries,FILE_SUMMARIES_BASED_ON_RAW_GIT_DIFF):
    file_summary=""
    file_summaries_diff=""
    for fn,fs in file_summaries:
      file_summary=file_summary+fn+" :\n"+fs+"\n"
    for fn,fs in FILE_SUMMARIES_BASED_ON_RAW_GIT_DIFF:
      file_summaries_diff=file_summaries_diff+fn+" :\n"+fs+"\n"
    prompt="""
In a given commmit, the summaries of changes in files generated based on before and after files are gives as\n"""+file_summary+"""and the summaries based on only the raw git diffs is gives as\n"""+file_summaries_diff+""". Now based on both the summaries, on a high level summaries the overall commit into one or multiple of following categories in software engineer point of view. For exaple if a commit is of the type bug fix and tests, give only two lines brief summary onoe for the bug fix and one for the tests.

Given below is a small explanation for each category:

Feature: Commits related to implementing new features or functionalities in the project.

Bug Fix: Commits addressing and fixing issues, bugs, or defects in the codebase.

Refactor: Commits focused on improving code quality, organization, or structure without changing its external behavior.

Documentation: Commits related to updating or adding documentation such as README files, inline comments, or documentation files.

Performance: Commits aimed at improving the performance of the codebase, such as optimizing algorithms, reducing resource usage, or enhancing execution speed.

Dependency Update: Commits updating dependencies, libraries, or third-party components used in the project to newer versions.

Tests: Commits related to adding, updating, or fixing tests to ensure code quality and reliability.

Configuration: Commits updating configuration files, such as environment variables, build scripts, or project settings.

Localization/Internationalization: Commits related to adding or updating translations, localization, or internationalization features in the project.

Style/Formatting: Commits focused on enforcing consistent code style, formatting, or coding conventions across the codebase.

Chore: Commits related to general maintenance tasks, administrative work, or other miscellaneous changes that don't fit into other categories.

Security: Commits addressing security vulnerabilities, implementing security measures, or ensuring compliance with security standards."""
    # print(prompt)
    response = model.generate_content(prompt)
    commit_summary = response.text
    # print("Commit summary: ", commit_summary)
    # print(f"\n\n\n\n\n\n commit : \n {commit_summary} ")
    return commit_summary
  def commit_summary_code_issue_diff(self,commit_msg,file_summaries,FILE_SUMMARIES_BASED_ON_RAW_GIT_DIFF,issue_title):
    file_summary=""
    file_summaries_diff=""
    for fn,fs in file_summaries:
      file_summary=file_summary+fn+" :\n"+fs+"\n"
    for fn,fs in FILE_SUMMARIES_BASED_ON_RAW_GIT_DIFF:
      file_summaries_diff=file_summaries_diff+fn+" :\n"+fs+"\n"
    prompt="""
In a given commmit, the summaries of changes in files generated based on before and after files are gives as\n"""+file_summary+"""and the summaries based on only the raw git diffs is gives as\n"""+file_summaries_diff+""" and the title of issue which the commit has solved is gives as\n"""+issue_title+""" . Now based on both the summaries and issue title , on a high level summaries the overall commit into one or multiple of following categories in software engineer point of view. For exaple if a commit is of the type bug fix and tests, give only two lines brief summary onoe for the bug fix and one for the tests.

Given below is a small explanation for each category:

Feature: Commits related to implementing new features or functionalities in the project.

Bug Fix: Commits addressing and fixing issues, bugs, or defects in the codebase.

Refactor: Commits focused on improving code quality, organization, or structure without changing its external behavior.

Documentation: Commits related to updating or adding documentation such as README files, inline comments, or documentation files.

Performance: Commits aimed at improving the performance of the codebase, such as optimizing algorithms, reducing resource usage, or enhancing execution speed.

Dependency Update: Commits updating dependencies, libraries, or third-party components used in the project to newer versions.

Tests: Commits related to adding, updating, or fixing tests to ensure code quality and reliability.

Configuration: Commits updating configuration files, such as environment variables, build scripts, or project settings.

Localization/Internationalization: Commits related to adding or updating translations, localization, or internationalization features in the project.

Style/Formatting: Commits focused on enforcing consistent code style, formatting, or coding conventions across the codebase.

Chore: Commits related to general maintenance tasks, administrative work, or other miscellaneous changes that don't fit into other categories.

Security: Commits addressing security vulnerabilities, implementing security measures, or ensuring compliance with security standards.
 After above, Also give a short summary on addition , deletion and modification due to the commit"""
    # print(prompt)
    response = model.generate_content(prompt)
    commit_summary = response.text
    # print("Commit summary: ", commit_summary)
    # print(f"\n\n\n\n\n\n commit : \n {commit_summary} ")
    return commit_summary

# genai.configure(api_key='AIzaSyBPes3Qot8ZqLb7hm1je4kcbSdK6B1SXCU')
genai.configure(api_key='AIzaSyBB0bRxLfGj6sunPywGHcHFjfqO3W6qAjk')
# genai.configure(api_key='AIzaSyB_xXjlHgJ7I6_0vH4MCILeu6IBQTb9soU')
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("What is life?")
print(response)