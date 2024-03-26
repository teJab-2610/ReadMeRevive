from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Similarity:
    def __init__(self):
        pass

    def calculate_cosine_similarity(self, text1, text2):
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([text1, text2])
        cosine_sim = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        return cosine_sim

    def is_similar_enough(self, text1, text2, threshold):
        similarity = self.calculate_cosine_similarity(text1, text2)
        if similarity >= threshold:
            return True
        else:
            return False

    def find_similar_text(self, text1, readme_dict, threshold):
        for key, value in readme_dict.items():
            text2 = key
            if self.is_similar_enough(text1, text2, threshold):
                print("text2", text2)
                print("The texts are similar enough hence update line .", readme_dict[key])
                return key, True
        print("The texts are not similar hence add this summary at ", len(readme_dict))
        return None, False

# if __name__ == "__main__":
#     # Assuming 'commit_dict' and 'readme_dict' are already defined
#     text1 = (commit_dict[0][2][0] + commit_dict[0][2][1] + commit_dict[0][2][2])
#     threshold = 0.1

#     # Instantiate the Similarity class
#     similarity = Similarity()

#     # Find similar text in the readme_dict
#     similar_key, is_similar = similarity.find_similar_text(text1, readme_dict, threshold)
#     if not is_similar:
#         t = len(readme_dict)
#         triples = list(processSentence(text1))
#         readme_dict[triples[0] + triples[1] + triples[2]] = t + 1
