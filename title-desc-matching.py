import re
from sentence_transformers import SentenceTransformer, util

def preprocess_text(text):

    if text is None:
        return None
    text = re.sub(r"[^\w\s]", '', text)  # punctuation
    text = re.sub(r"\s+", ' ', text)     # a single space
    text = text.lower()                  # all to lowercase
    return text

def remove_common_words(text):

    if text is None:
        return None
    common_words = {'and', 'the', 'that', 'just', 'with', 'for', 'on', 'in', 'to'}
    words = text.split()
    filtered_words = [word for word in words if word not in common_words]
    return ' '.join(filtered_words)

def bert_semantic_similarity(a, b, model_name='all-MiniLM-L6-v2'):

    if a is None or b is None:
        return 0
    model = SentenceTransformer(model_name)
    embeddings = model.encode([a, b], convert_to_tensor=True)
    cosine_similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
    return cosine_similarity * 100

def compare_products(recall_title, recall_desc, amazon_title, amazon_desc):


    processed_recall_title = preprocess_text(recall_title)
    processed_amazon_title = preprocess_text(amazon_title)
    title_similarity = bert_semantic_similarity(processed_recall_title, processed_amazon_title)

    if title_similarity > 70:
        return True
    elif amazon_desc is None or recall_desc is None:
        return False
    else:

        processed_recall_desc = remove_common_words(preprocess_text(recall_desc))
        processed_amazon_desc = remove_common_words(preprocess_text(amazon_desc))
        desc_similarity = bert_semantic_similarity(processed_recall_desc, processed_amazon_desc)

        return desc_similarity > 60