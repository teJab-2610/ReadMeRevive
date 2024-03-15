from classifier.classifier import Classifier

c = Classifier()
new_commit_summary = "Adds documentation about getting source along with the answer"
predicted_cluster = c.classify_commit(new_commit_summary)
print(f"The new commit is most likely related to Cluster {predicted_cluster}")