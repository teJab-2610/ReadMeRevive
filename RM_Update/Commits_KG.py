import spacy
import os
from spacy.lang.en import English
import networkx as nx
import matplotlib.pyplot as plt
from pydriller import Repository


class Commits_KG:
    def __init__(self):
        self.nlp_model = spacy.load('en_core_web_sm')

    def getSentences(self, text):
        nlp = English()
        nlp.add_pipe('sentencizer')
        document = nlp(text)
        return [sentence.text.strip() for sentence in document.sents]

    def printToken(self, token):
        print(token.text, "->", token.dep_)

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
        c = 0
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
            if ("compound" in token.dep_) and ("subj" in tokens[c+1].dep_):
                subject = self.appendChunk(token.text, subject)

            if "obj" in token.dep_:
                object = self.appendChunk(object, token.text)
                object = self.appendChunk(objectConstruction, object)
                objectConstruction = ''
            if ("compound" in token.dep_) and ("obj" in tokens[c+1].dep_):
                object = self.appendChunk(token.text, object)
            c = c + 1

        print(subject.strip(), ",", relation.strip(), ",", object.strip())
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
        code_commits = []

        # for commit in Repository(repo_path).traverse_commits():
        # for modified_file in commit.modified_files:
        # if modified_file.filename.lower() == 'readme.md':

        commit_info = {
            'title': "Its trial",  # commit.msg,
            'patch': "hi",  # modified_file.diff,
            'commit_id': 66789  # commit.hash
        }
        code_commits.append(commit_info)

        return code_commits

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

    def printGraph(self, pentagons):
        G = nx.Graph()

        G.add_node(pentagons[0])
        G.add_node(pentagons[1])
        G.add_node(pentagons[2][0])
        G.add_node(pentagons[2][1])
        G.add_node(pentagons[2][2])
        G.add_edge(pentagons[0], pentagons[1], label="diff_type")
        G.add_edge(pentagons[0], pentagons[2][1], label="commit_summary")
        G.add_edge(pentagons[2][0], pentagons[2][1], label="entity 1")
        G.add_edge(pentagons[2][1], pentagons[2][2], label="entity 2")

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

    def create_commit_dict(self, readme_commits, commit_summ):
        commit_dict = {}
        count = 0
        #commit_summ = "Embedchain is an Open Source wireframe for personalizing LLM responses"
        for commit in readme_commits:
            pentagons = []
            triples = []
            pentagons.append(commit['commit_id'])
            pentagons.append("addition")
            triples = list(self.processSentence(commit_summ))
            pentagons.append(triples)
            commit_dict[count] = pentagons
            count = count + 1
            self.printGraph(pentagons)
        return commit_dict

# if __name__ == "__main__":
#     # Instantiate the class
#     commits_kg = Commits_KG()

#     # Specify the path to the cloned repository
#     repo_path = '/content/embedchain'

#     # Retrieve the README file content and commit messages
#     code_commits = commits_kg.get_commits(repo_path)
#     commit_dict = commits_kg.create_commit_dict(code_commits)
#     print(commit_dict[0][2][0])
#     print(len(commit_dict))
