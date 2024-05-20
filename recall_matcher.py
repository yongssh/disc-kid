#####################################################################################################################################################################
####################################################### OLD, NOW DIRECTLY IMPLEMENTED IN Recall_GE_Backend.py #######################################################
#####################################################################################################################################################################

import string
import re

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import pytorch_cos_sim

# -----------------------------

def text_cleaner(text):
    lowercased_text = text.lower()
    remove_punctuation_table = str.maketrans('', '', string.punctuation)
    normalized_text = lowercased_text.translate(remove_punctuation_table)
    normalized_text = re.sub('(\s+)(a|an|and|the|with)(\s+)', '\1\3', normalized_text)
    return normalized_text

# ------------------------------

def string_comparer1(text1, text2):
    text1_words = set(text_cleaner(text1).split())
    text2_words = set(text_cleaner(text2).split())
    common_words = text1_words.intersection(text2_words)
    similarity_score = round(len(common_words) / min([len(text1_words), len(text2_words)]), 3)
    return similarity_score

# ------------------------------

transformer = SentenceTransformer('distilbert-base-nli-mean-tokens')

def string_comparer2(text1, text2, model=transformer):
    text1_clean = text_cleaner(text1)
    text2_clean = text_cleaner(text2)
    text1_encoding = model.encode(text1_clean)
    text2_encoding = model.encode(text2_clean)
    similarity_score = round(float(pytorch_cos_sim(text1_encoding, text2_encoding)), 3)
    return similarity_score

# ------------------------------

def query_cpsc(manufacturer_key=None, productname_key=None):
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}
    base_url = "https://www.saferproducts.gov/RestWebServices/Recall?format=json"
    query_string = ""
    if manufacturer_key:
        query_string += f"&Manufacturer={manufacturer_key}"
    if productname_key:
        query_string += f"&ProductName={productname_key}"
    query_results = requests.get(base_url + query_string, headers=header).json()
    return query_results

# ------------------------------------------------

def RecallSimilarity(recall, amazon_info):
    
    desc_similarity = None
    recall_desc = recall.get('Description', '')

    if recall_desc and (amazon_info['Description'] != 'Description not found'):
        desc_similarity = string_comparer2(recall_desc, amazon_info['Description'])

    product_name_max_similarity = None

    for product in recall.get('Products', []):
        if product.get('Name') and (amazon_info['Product Name'] != 'Product name not found'):
            product_name_similarity = string_comparer2(product['Name'], amazon_info['Product Name'])
            if product_name_similarity > float(product_name_max_similarity or 0):
                product_name_max_similarity = product_name_similarity

    manufacturer_max_similarity = None
    
    for manufacturer in recall.get('Manufacturers', []):
        if manufacturer.get('Name') and (amazon_info['Brand'] != 'Brand not found'):
            manufacturer_similarity = string_comparer1(manufacturer['Name'], amazon_info['Brand'])
            if manufacturer_similarity > float(manufacturer_max_similarity or 0):
                manufacturer_max_similarity = manufacturer_similarity

    recall_similarity_score = 0
    valid_scores = list(filter(None, [desc_similarity, product_name_max_similarity, manufacturer_max_similarity]))

    for score in valid_scores:
        if score == desc_similarity:
            recall_similarity_score += score
        elif score == product_name_max_similarity:
            recall_similarity_score += score * 2
        elif score == manufacturer_max_similarity:
            recall_similarity_score += score * 2

    recall_similarity_score = round(recall_similarity_score * (3 / len(valid_scores)) ** 0.5, 3)
    return recall_similarity_score

# --------------------------------------------------------

def GetMatchingRecalls(query_results, amazon_info, similarity_threshold=2.0):
    matching_recalls = []
    for recall in query_results:
        recall['SimilarityScore'] = RecallSimilarity(recall, amazon_info)
        if recall['SimilarityScore'] > similarity_threshold:
            matching_recalls.append(recall)
    matching_recalls.sort(key=lambda x: x['SimilarityScore'], reverse=True)
    return matching_recalls

# ------------------------------------------------------- EXAMPLE USAGE FOR GEL BLASTER SURGE

# query_results = query_cpsc(productname_key="Gel")
# GetMatchingRecalls(query_results)
