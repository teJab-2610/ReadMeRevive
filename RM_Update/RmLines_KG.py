import spacy
from spacy.lang.en import English
import networkx as nx
import matplotlib.pyplot as plt
import os
from pydriller import Repository

class RmLines_KG:
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

    def retrieve_readme_and_commits(self, repo_path):
        readme_content = None
        commit_messages = []

        # Find the README file recursively within the repository directory
        readme_path = self.find_readme_file(repo_path)
        if readme_path:
            with open(readme_path, 'r') as file:
                readme_content = file.read()

        return readme_content

    def create_readme_dict(self, readme_content):
        sentences = self.getSentences(readme_content)
        print(sentences)
        readme_dict = {}
        count = 1
        for sentence in sentences:
            triples = []
            triples = list(self.processSentence(sentence))
            readme_dict[triples[0] + triples[1] + triples[2]] = count
            count = count + 1
            print("triples length is:", triples[0] + triples[1] + triples[2])
            # printGraph(triples)
        return readme_dict  # dictionary of readme lines with line number

    def printGraph(self, triples):
        G = nx.Graph()
        # for i, triple in enumerate(triples):
        G.add_node(triples[0])
        G.add_node(triples[1])
        print(triples[2])
        G.add_node(triples[2])
        G.add_edge(triples[0], triples[1], label="entity 1")
        G.add_edge(triples[1], triples[2], label="entity 2")

        components = nx.connected_components(G)
        print(components)
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
#     readme_kg = Readme_KG()

#     # Specify the path to the cloned repository
#     repo_path = '/content/embedchain'

#     # Retrieve the README file content and commit messages
#     readme_content = readme_kg.retrieve_readme_and_commits(repo_path)
#     readme_dict = readme_kg.create_readme_dict(readme_content)
#     print(len(readme_dict))
