import spacy
from spacy.lang.en import English
import networkx as nx
import matplotlib.pyplot as plt
import os
import re
from pydriller import Repository

class RmCommits_KG:
    def __init__(self):
        self.nlp_model = spacy.load('en_core_web_sm')

    def getSentences(self, text):
        nlp = English()
        nlp.add_pipe('sentencizer')
        document = nlp(text)
        return [sentence.text.strip() for sentence in document.sents]

    def printToken(self, token):
        pass

    def appendChunk(self, original, chunk):
        return original + ' ' + chunk

    def isRelationCandidate(self, token):
        deps = ["ROOT", "adj", "attr", "agent", "amod"]
        return any(subs in token.dep_ for subs in deps)

    def isConstructionCandidate(self, token):
        deps = ["compound", "prep", "conj", "mod"]
        return any(subs in token.dep_ for subs in deps)

    def processSubjectObjectPairs(self, tokens):
        subject = ''
        object = ''
        relation = ''
        subjectConstruction = ''
        objectConstruction = ''
        for token in tokens:
            self.printToken(token)
            if "punct" in token.dep_:
                continue
            if self.isRelationCandidate(token):
                relation = self.appendChunk(relation, token.lemma_)
            if self.isConstructionCandidate(token):
                if subjectConstruction:
                    subjectConstruction = self.appendChunk(subjectConstruction, token.text)
                if objectConstruction:
                    objectConstruction = self.appendChunk(objectConstruction, token.text)
            if "subj" in token.dep_:
                subject = self.appendChunk(subject, token.text)
                subject = self.appendChunk(subjectConstruction, subject)
                subjectConstruction = ''
            if "obj" in token.dep_:
                object = self.appendChunk(object, token.text)
                object = self.appendChunk(objectConstruction, object)
                objectConstruction = ''

        return (subject.strip(), relation.strip(), object.strip())

    def processSentence(self, sentence):
        tokens = self.nlp_model(sentence)
        return self.processSubjectObjectPairs(tokens)

    def find_readme_file(self, directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower() == 'readme.md':
                    return os.path.join(root, file)
        return None

    def get_commits(self, repo_path):
        readme_commits = []

        for commit in Repository(repo_path).traverse_commits():
            for modified_file in commit.modified_files:
                if modified_file.filename.lower() == 'readme.md':
                    commit_info = {
                        'title': commit.msg,
                        'patch': modified_file.diff,
                        'commit_id': commit.hash
                    }
                    readme_commits.append(commit_info)

        return readme_commits

    def create_commit_dict(self, readme_commits, readme_dict):
        readme_commit_dict = {}
        count_read = 1
        for commit in readme_commits:
            sentences = self.getSentences(commit['patch'])
            for sentence in sentences:
                sentence = re.sub(r'@@\s*.*?\s*@@', '', sentence)
                sentence = sentence.replace('-', '')
                sentence = sentence.replace('+', '')
                sentence = sentence.replace('```', '')
                quadruple = []
                triples = []
                quadruple.append(commit['commit_id'])
                triples = list(self.processSentence(sentence))
                if (triples[0] + triples[1] + triples[2]) in readme_dict:
                    quadruple.append(readme_dict[triples[0] + triples[1] + triples[2]])
                    quadruple.append(triples)
                    readme_commit_dict[count_read] = quadruple
                    count_read = count_read + 1
                    self.printGraph(quadruple)
        return readme_commit_dict

    def diff_type(self, commit_diff):
        lines = commit_diff.split('\n')
        additions = sum(1 for line in lines if line.startswith('+') and not line.startswith('+++'))
        deletions = sum(1 for line in lines if line.startswith('-') and not line.startswith('---'))

        if additions > 0 and deletions == 0:
            return "Addition"
        elif deletions > 0 and additions == 0:
            return "Deletion"
        else:
            return "Mixed (Additions and Deletions)"

    def printGraph(self, quadruple):
        G = nx.Graph()
        G.add_node(quadruple[0])
        G.add_node(quadruple[1])
        G.add_node(quadruple[2][0])
        G.add_node(quadruple[2][1])
        G.add_node(quadruple[2][2])
        G.add_edge(quadruple[0], quadruple[1], label="line_no")
        G.add_edge(quadruple[0], quadruple[2][1], label="commit_data")
        G.add_edge(quadruple[2][0], quadruple[2][1], label="entity 1")
        G.add_edge(quadruple[2][1], quadruple[2][2], label="entity 2")

        components = nx.connected_components(G)
        for i in components:
            print(i)
        pos = nx.spring_layout(G)
        plt.figure(figsize=(50, 20))
        nx.draw(G, pos, edge_color='black', width=1, linewidths=1,
                node_size=500, node_color='seagreen', alpha=0.9,
                labels={node: node for node in G.nodes()})

        edge_labels = {(edge[0], edge[1]): attr['label'] for edge, attr in G.edges.items()}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        plt.axis('off')
        plt.show()

# if __name__ == "__main__":
#     # Instantiate the class
#     rm_commits = RmCommits()

#     # Specify the path to the cloned repository
#     repo_path = '/content/embedchain'

#     # Retrieve the README file content and commit messages
#     readme_commits = rm_commits.get_commits(repo_path)

#     # Assuming 'readme_dict' is already created or you can create it using the previous class
#     readme_dict = {...}  # Fill in the dictionary here

#     # Create the commit dictionary
#     readme_commit_dict = rm_commits.create_commit_dict(readme_commits, readme_dict)
