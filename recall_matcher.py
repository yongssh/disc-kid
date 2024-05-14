import string
import re

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import pytorch_cos_sim

# ------------------------------

def text_cleaner(text): # this function just standardizes the text to be more uniform for comparison
    lowercased_text = text.lower()
    remove_punctuation_table = str.maketrans('', '', string.punctuation)
    normalized_text = lowercased_text.translate(remove_punctuation_table)
    normalized_text = re.sub('(\s+)(a|an|and|the|with)(\s+)', '\1\3', normalized_text)   # remove article and filler words, can add other things to remove as well
    return normalized_text

# ------------------------------

def string_comparer1(text1, text2): # uses the ratio of common unique words between two strings as the similarity
    
    text1_words = set(text_cleaner(text1).split())
    text2_words = set(text_cleaner(text2).split())
    
    common_words = text1_words.intersection(text2_words)
    
    similarity_score = round(len(common_words) / min([len(text1_words), len(text2_words)]), 3)
    
    return similarity_score

# ------------------------------

transformer = SentenceTransformer('distilbert-base-nli-mean-tokens')                    # This is the transformer that should be instated ONCE prior to function call
def string_comparer2(text1, text2, model=transformer): # uses transformer embeddings and cosine similarity to compute similarity
    
    # model = SentenceTransformer('distilbert-base-nli-mean-tokens')                    # Used to be contained here but it increases time cost of calling function significantly

    text1_clean = text_cleaner(text1)
    text2_clean = text_cleaner(text2)
    
    text1_encoding = model.encode(text1_clean)
    text2_encoding = model.encode(text2_clean)
    
    similarity_score = round(float(pytorch_cos_sim(text1_encoding, text2_encoding)), 3)

    return similarity_score

def query_cpsc(manufacturer_key=None, productname_key=None):
    
    base_url = "https://www.saferproducts.gov/RestWebServices/Recall?format=json"
    
    query_string = ""
    
    if manufacturer_key:
        query_string += f"&Manufacturer={manufacturer_key}"
    if productname_key:
        query_string += f"&ProductName={productname_key}"
        
    query_results = requests.get(base_url + query_string, headers=header).json()
        
    return query_results

# ------------------------------------------------ 

def RecallSimilarity(recall): # add amazon info as param later?
    
    # calculate description similarity if a description exists for both
    desc_similarity = None
    recall_desc = recall['Description']
    if recall_desc and amazon_desc:
        desc_similarity = string_comparer2(recall_desc, amazon_desc)  # compare by cosine similarity

    # calculate product name similarity if product name exists for both
    product_name_max_similarity = None
    for product in recall['Products']:
        if product['Name'] and amazon_title:
            product_name_similarity = string_comparer2(product['Name'], amazon_title)  # compare by cosine similarity
            if product_name_similarity > float(product_name_max_similarity or 0): 
                product_name_max_similarity = product_name_similarity
                
    # calculate manufacturer name similarity if exists for both
    manufacturer_max_similarity = None
    for manufacturer in recall['Manufacturers']:
        if manufacturer['Name'] and amazon_manufacturer:
            manufacturer_similarity = string_comparer1(manufacturer['Name'], amazon_manufacturer)  # compare by common words
            if manufacturer_similarity > float(manufacturer_max_similarity or 0):
                manufacturer_max_similarity = manufacturer_similarity
    
    recall_similarity_score = 0
    
    valid_scores = list(filter(None, [desc_similarity, product_name_max_similarity, manufacturer_max_similarity]))
    
    for score in valid_scores:
        if score == desc_similarity:
            recall_similarity_score += score
        elif score == product_name_max_similarity:
            recall_similarity_score += score*2
        elif score == manufacturer_max_similarity:
            recall_similarity_score += score*2
            
    # normalize by number of valid scores 
    recall_similarity_score = round( recall_similarity_score * (3/len(valid_scores))**0.5 , 3)
    
    return recall_similarity_score

# --------------------------------------------------------

def GetMatchingRecalls(query_results, similarity_threshold=2.5):
    matching_recalls = []

    for recall in query_results:
        recall['SimilarityScore'] = RecallSimilarity(recall)    # add similarity score to recall dictionary
        if recall['SimilarityScore'] > similarity_threshold:      # arbitrary default threshold of 2.5 for similarity score
            matching_recalls.append(recall)

    return matching_recalls

# ------------------------------------------------------- EXAMPLE USAGE FOR GEL BLASTER SURGE

# query_results = query_cpsc(productname_key="Gel")
# GetMatchingRecalls(query_results)
