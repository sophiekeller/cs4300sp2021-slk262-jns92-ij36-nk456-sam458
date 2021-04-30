
import nltk
# from nltk.corpus import wordnet
import json
import math
from PyDictionary import PyDictionary
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy.linalg as LA

import numpy as np
# import word_forms
from word_forms.word_forms import get_word_forms
import app.irsystem.models.vectorizer as precomp

# from nltk import PorterStemmer

# porter = PorterStemmer()

dictionary=PyDictionary()






def get_query_antonyms(query):
    antonyms = []
    synonyms = []
    for q in query.split(" "):
        if not dictionary.synonym(q):
            synonyms += [q]
            antonyms += [q]
        else:
            synonyms += dictionary.synonym(q)[:10] + [q]
            antonyms += dictionary.antonym(q)[:10]
    # print(synonyms)
    antonyms = " ".join(antonyms)
    synonyms = " ".join(synonyms) 

    return antonyms, synonyms

def word_forms(word): 
    dic = get_word_forms(word)
    words = "" 
    for form in dic: 
        for w in dic[form]: 
            words += w + " "
    return words

def many_word_forms(query): 
    words = "" 
    query = query.split(" ")
    for tok in query: 
        words += word_forms(tok)
    return words


def get_cos_sim(query, reviews):
    """Returns the cosine similarity of two movie scripts.
    
    Params: {mov1: String,
             mov2: String,
             input_doc_mat: np.ndarray,
             movie_name_to_index: Dict}
    Returns: Float 
    """
    numerator = np.dot(query, reviews)
    denomenator = (np.linalg.norm(query) * np.linalg.norm(reviews))
    if numerator == 0 or denomenator == 0:
        return 0.0
    return numerator/ (np.linalg.norm(query) * np.linalg.norm(reviews))

def cosineSim(city, category, query):
    with open('app/irsystem/models/tokens_mapping.json') as f:
        tokens_map = json.load(f)
    with open('app/irsystem/models/ranking_mapping.json') as f:
        rankings_map = json.load(f)
    if not query:
        return sorted(rankings_map[city][category].items(), key=lambda x: x[1], reverse=True)

    vec, doc_vectorizer_array = precomp.vec_arr_dict[city][category]
    reverse_index = precomp.reverse_dict[city][category]
    
    query_antonyms, query_synonyms = get_query_antonyms(query)

    synonyms_forms = many_word_forms(query_synonyms).split(" ")
    antonyms_forms = many_word_forms(query_antonyms).split(" ")


    query_vectorizer_array = np.zeros((doc_vectorizer_array.shape[1],))
    ants_vectorizer_array = np.zeros((doc_vectorizer_array.shape[1],))
    # feature_list = vec.get_feature_names()


    for w in synonyms_forms:
        idx = reverse_index.get(w, -1)

        if idx > 0:
            query_vectorizer_array[idx] += 1.0
    
    for w in antonyms_forms:
        idx = reverse_index.get(w, -1)
        if idx > 0:
            ants_vectorizer_array[idx] += 1.0

    query_vectorizer_array *= vec.idf_
    ants_vectorizer_array *= vec.idf_
    
    if query_vectorizer_array.sum() == 0:
        return []

    num = query_vectorizer_array.dot(doc_vectorizer_array.T)
    denom = LA.norm(query_vectorizer_array)*LA.norm(doc_vectorizer_array,axis=1)
    sim = num/denom

    num2 = ants_vectorizer_array.dot(doc_vectorizer_array.T)
    denom2 = LA.norm(ants_vectorizer_array)*LA.norm(doc_vectorizer_array,axis=1)
    sim2 = num2/denom2

    final_sim = sim - sim2
    sims_idx = [(i, sim) for i, sim in enumerate(final_sim)]
    ranked = sorted(sims_idx, key=lambda x: x[1], reverse=True)  # slice off query
    
    keys = list(tokens_map[city][category].keys())

    ranked_translated = [(keys[x[0]], x[1]) for x in ranked]

    return ranked_translated


def get_matchings_cos_sim(city, category, query):
    with open('app/irsystem/models/tokens_mapping.json') as f:
        tokens_map = json.load(f)

    # with open('app/irsystem/models/stemmed_mapping.json') as f:
    #     tokens_map = json.load(f)
    with open('app/irsystem/models/ranking_mapping.json') as f:
        rankings_map = json.load(f)
    if not query:
        return sorted(tokens_map[city][category].items(), key=lambda x: x[1], reverse=True)

    query_antonyms, query_synonyms = get_query_antonyms(query)

    synonyms_forms = many_word_forms(query_synonyms)
    antonyms_forms = many_word_forms(query_antonyms)

    # list of all review strings (each place has a single review string of all reviews) with
    # the query string as the last vector
    to_vectorize = [tokens_map[city][category][x] for x in tokens_map[city][category]]  + [antonyms_forms] + [synonyms_forms]
    tfidf_vec = build_vectorizer()
    tfidf_mat = tfidf_vec.fit_transform(to_vectorize).toarray()
    vocab = tfidf_vec.get_feature_names()


    # calculate cosine sims between each place's tf-idf vector and the query string vector
    cos_sims = [get_cos_sim(tfidf_mat[i], tfidf_mat[-1]) - get_cos_sim(tfidf_mat[i], tfidf_mat[-2]) for i in range(len(tfidf_mat)- 2)]
    sims_idx = [(i, sim) for i, sim in enumerate(cos_sims)]
    ranked = sorted(sims_idx, key=lambda x: x[1], reverse=True)  # slice off query

    # translate from id's to names
    keys = list(tokens_map[city][category].keys())

    ranked_translated = [(keys[x[0]], x[1]) for x in ranked]

    return ranked_translated
    

def within_rad(city, top_hotels, top_rests, top_attract, radius):  # top_attract,
    with open('app/irsystem/models/inverted-index.json') as f:
        inv_ind = json.load(f)
    with open('app/irsystem/models/distance-matrices.json') as f:
        distances = json.load(f)
    within_rad = {}
    for h in top_hotels:
        restaurants = []
        for r in top_rests:
            #dist = distances[city][order[1]][inv_ind[city][order[1]][r]][inv_ind[city][order[0]][h]]
            dist = distances[city]['restaurant'][inv_ind[city]['restaurant'][r]][inv_ind[city]['accommodation'][h]]
            if dist <= radius:
                restaurants.append(r)
        attractions = []
        for a in top_attract:
            #dist = distances[city][order[2]][inv_ind[city][order[2]][a]][inv_ind[city][order[0]][h]]
            dist = distances[city]['attraction'][inv_ind[city]['attraction'][a]][inv_ind[city]['accommodation'][h]]
            if dist <= radius:
                attractions.append(a)
        within_rad[h] = {'restaurants': restaurants, 'attractions': attractions}

    return within_rad

# rests = getMatchings('london', 'accommodation', 'clean');
# hots =  getMatchings('london', 'accommodation', 'clean');
# print(list(withinRad('london',hots, rests, 10000000)));

