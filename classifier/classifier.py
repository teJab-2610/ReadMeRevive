import nltk, re, json, os, csv
import pandas as pd
from nltk.corpus import stopwords  # stopwords
from nltk.tokenize import word_tokenize
from sklearn.decomposition import LatentDirichletAllocation
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


nltk.download("punkt")
nltk.download("wordnet")
nltk.download("stopwords")
stop_words = list(stopwords.words("english"))

SUMMARY_JSON = "./commit_summary.json"
CSV_FILE = "./commits.csv"
DELIMITER = "#"
chunk_size = 100
TOPICS_NUMBER = 7

class Classifier:
    def __init__(self):
        print("Classifier object created")
        self.create_csv()
        print("CSV file created")
        self.topic_modeling()
        print("Topic modeling done")
    
    def create_csv(self):
        with open(SUMMARY_JSON, "r") as file:
            data = json.load(file)
            with open(CSV_FILE, "w", newline='') as file:
                file.write("commitId#comment\n")
                for commit in data:
                    commit_hash = commit["commit_hash"]
                    # clean the text
                    summary = self.clean_text(commit["summary"])
                    file.write(commit_hash + DELIMITER + summary + "\n")
        file.close()

    def clean_text(self, text):
        cleaned_text = text.replace("\n", " ")
        cleaned_text = cleaned_text.replace("$", "")
        cleaned_text = cleaned_text.replace(":", "")
        cleaned_text = cleaned_text.replace("*", "")
        cleaned_text = re.sub(r"`.*?`", "", cleaned_text)
        cleaned_text = re.sub(r"'.*?'","", cleaned_text)
        cleaned_text = cleaned_text.replace("'", "")
        cleaned_text = cleaned_text.replace(".", " ")
        cleaned_text = cleaned_text.replace(",", "")
        cleaned_text = cleaned_text.replace("-", "")
        cleaned_text = cleaned_text.replace("#", "")
        cleaned_text = cleaned_text.replace("(", "")
        cleaned_text = cleaned_text.replace(")", "")
        cleaned_text = re.sub(r"\b\w{1,2}\b", "", cleaned_text)
        cleaned_text = re.sub(r"\d+(?:\.\d*(?:[eE]\d+))?", " ", cleaned_text)
        cleaned_text = cleaned_text.replace("_", " ")
        cleaned_text = cleaned_text.lower()
        return cleaned_text
    
    def topic_modeling(self):
        file_path = CSV_FILE
        vect = TfidfVectorizer(stop_words="english", max_features=1000)
        lda_model = LatentDirichletAllocation(
            n_components=TOPICS_NUMBER, learning_method="online", max_iter=10
        )

        # Dataframe to store the cluster information for each commit
        cluster_data = pd.DataFrame(columns=["commitId", "cleaned_text", "clusters"])

        for rev in pd.read_csv(file_path, chunksize=chunk_size, delimiter=DELIMITER):
            # rev["cleaned_text"] = rev["comment"].apply(self.clean_text)  # Clean the text
            
            rev["cleaned_text"] = rev["comment"]
            vect_text = vect.fit_transform(rev["cleaned_text"])

            lda_top = lda_model.fit_transform(vect_text)

            # Find the clusters (topics) for each commit based on the threshold
            topics = []
            for row in lda_top:
                topic_indices = [i for i, val in enumerate(row) if val > 0.4]
                topics.append(topic_indices)
                
            # Add cluster information to the overall dataframe
            rev["clusters"] = topics
            cluster_data = pd.concat([cluster_data, rev[["commitId", "cleaned_text", "clusters"]]])

            vocab = vect.get_feature_names_out()
            for i, comp in enumerate(lda_model.components_):
                vocab_comp = zip(vocab, comp)
                sorted_words = sorted(vocab_comp, key=lambda x: x[1], reverse=True)[:10]
                print("Topic", i, ":")
                for t in sorted_words:
                    print(t[0], end=" ")
                print("\n")

        # Store the cluster information to a CSV file
        cluster_data.to_csv("commit_clusters.csv", index=False)


    def classify_commit(self, new_commit_summary):
        # Load the cluster information from the CSV file
        cluster_data = pd.read_csv("commit_clusters.csv")

        # Vectorize the existing commit summaries
        vect = TfidfVectorizer(stop_words="english", max_features=1000)
        existing_commit_vectors = vect.fit_transform(cluster_data["cleaned_text"])

        # Vectorize the new commit summary
        new_commit_vector = vect.transform([self.clean_text(new_commit_summary)])

         # Get the cluster centroids
        cluster_centroids = []
        for cluster_id in sorted(cluster_data["clusters"].unique()):
            cluster_subset = existing_commit_vectors[
                cluster_data["clusters"] == cluster_id
            ]
            cluster_centroids.append(cluster_subset.mean(axis=0))

        # Convert cluster_centroids to NumPy array
        cluster_centroids = np.asarray(cluster_centroids)

        # Calculate cosine similarity between the new commit and each cluster centroid
        similarities = [
            cosine_similarity(new_commit_vector, np.asarray(centroid))
            for centroid in cluster_centroids
        ]

        # Find the most similar cluster
        most_similar_cluster = np.argmax(similarities)

        return most_similar_cluster


    def print_all_clusters(self):
        cluster_data = pd.read_csv("commit_clusters.csv")
        for cluster_id in sorted(cluster_data["cluster"].unique()):
            print(f"Cluster {cluster_id}:")
            print(
                cluster_data[cluster_data["cluster"] == cluster_id]["commitId"].values
            )

