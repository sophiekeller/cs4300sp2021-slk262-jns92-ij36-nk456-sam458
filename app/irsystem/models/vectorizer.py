from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import json
import numpy as np
vec = TfidfVectorizer()
documents = []
src = []
rawDocs = []
folders = []

def build_vectorizer(max_n_terms=5000, max_prop_docs=0.8, min_n_docs=0):
    """Returns a TfidfVectorizer object with certain preprocessing properties.
    
    Params: {max_n_terms: Integer,
             max_prop_docs: Float,
             min_n_docs: Integer}
    Returns: TfidfVectorizer
    """
    return TfidfVectorizer(min_df=0, max_df=max_prop_docs, max_features=max_n_terms,
                           stop_words='english')

def reverse_index(lst):
    d = {}
    for i, w in enumerate(lst):
        d[w] = i
    return d

with open('app/irsystem/models/tokens_mapping.json') as f:
        tokens_map = json.load(f)

vec_arr_dict = {}
reverse_dict = {}
svd_dict = {}
svd = TruncatedSVD(n_components=5, n_iter=7, random_state=42) #PARAMETERS MIGHT NEED TO BE CHANGED
print("started vectorizing")
for city in ["london","amsterdam", "barcelona", "berlin", "dubai"]:
    vec_arr_dict[city] = {}
    reverse_dict[city] = {}
    svd_dict[city] = {}
    for category in ["accommodation", "restaurant", "attraction"]:
        vec = build_vectorizer()
        to_vectorize = [tokens_map[city][category][x] for x in tokens_map[city][category]]
        vec_array = vec.fit_transform(to_vectorize).toarray()
        vec_arr_dict[city][category] = (vec, vec_array)
        reverse_dict[city][category] = reverse_index(vec.get_feature_names())
        #print(vec_array.T)
        svd.fit(vec_array.T)
        svd_dict[city][category] = svd.transform(vec_array.T)

        # svd_dict[city][category] = np.linalg.svd(vec_array.T) #svd on tfidf documents
#print(svd_dict)
print("finished vectorizing")