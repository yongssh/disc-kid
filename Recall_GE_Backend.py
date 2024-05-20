############################################## USING THIS FLASH BACKEND ##############################################
# INPUTS -> amazon page link
# OUTPUTS -> JSON object with information from matching recalls
#
# OPERATING INSTRUCTIONS:
#   In a Bash Terminal, run the following command to intialize the Flask Backend server and make it listen for requests on http://localhost:5000.
    #    python Recall_GE_Backend.py
# 
#   In the JSON script, use the below example JS code to send a POST request to the Flask Backend server.
    #    document.getElementById('process-button').addEventListener('click', () => {
    #        const amazonLink = document.getElementById('amazon-link').value;
    #        processAmazonLink(amazonLink);
    #    });

    #    function processAmazonLink(amazon_link) {
    #        fetch('http://localhost:5000/process', {
    #            method: 'POST',
    #            headers: {
    #                'Content-Type': 'application/json'
    #            },
    #            body: JSON.stringify({ amazon_link: amazon_link })
    #        })
    #        .then(response => response.json())
    #        .then(data => {
    #            console.log('Success:', data);
    #            document.getElementById('output').innerText = JSON.stringify(data, null, 2);
    #        })
    #        .catch((error) => {
    #            console.error('Error:', error);
    #        });
    #    }
# 
#   Also make sure that the necessary permissions are allowed in manifest.json file, an example is below
    # {
    #   "manifest_version": 2,
    #   "name": "Amazon Link Processor",
    #   "version": "1.0",
    #   "permissions": [
    #     "activeTab",
    #     "http://localhost:5000/*"
    #   ],
    #   "browser_action": {
    #     "default_popup": "popup.html",
    #     "default_icon": "icon.png"
    #   },
    #   "content_scripts": [
    #     {
    #       "matches": ["<all_urls>"],
    #       "js": ["popup.js"]
    #     }
    #   ]
    # }
#
# 
# 
############################################## USING THIS FLASH BACKEND ##############################################

import urllib.request
from bs4 import BeautifulSoup
import json

import requests
import string
import re

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------------- AMAZON WEBSCRAPING COMPONENT --------------------------------------------------------

def scrape_data(url):
    try:
        with urllib.request.urlopen(url) as response:
            html = response.read()
        soup = BeautifulSoup(html, 'html.parser')

        name_span = soup.find(id='productTitle')
        name = name_span.get_text(strip=True) if name_span else "Product name not found"

        brand_span = soup.find(class_='a-spacing-small po-brand')
        brand = brand_span.find(class_="a-size-base po-break-word").get_text() if brand_span else "Brand not found"

        description = ""
        feature_bullets_div = soup.find('div', id='feature-bullets')
        if feature_bullets_div:
            list_items = feature_bullets_div.find_all('span', class_='a-list-item')
            for item in list_items:
                description += str(item.text.strip())
        else:
            description = "Description not found"

        data = {
            'Product Name': name,
            'Brand': brand,
            'Product Description': description
        }

        json_data = json.dumps(data, indent=4)
        logger.info(f"Scraped data: {json_data}")
        return json_data
    except Exception as e:
        logger.error(f"Error in scrape_data: {e}")
        return None

# -------------------------------------------------------- RECALL MATCHING COMPONENT --------------------------------------------------------

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

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import pytorch_cos_sim

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
    try:
        query_results = requests.get(base_url + query_string, headers=header).json()
        print(query_results)
        return query_results
    except Exception as e:
        logger.error(f"Error in query_cpsc: {e}")
        return []

"""
def query_cpsc(manufacturer_key=None, productname_key=None):
    #header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}

    import requests
    from urllib. request import urlopen
    # import json
    import json
   
    base_url = "https://www.saferproducts.gov/RestWebServices/Recall?format=json"
    query_string = ""
    if manufacturer_key:
        query_string += f"&Manufacturer={manufacturer_key}"
    if productname_key:
        query_string += f"&ProductName={productname_key}"
    try:
         # store the URL in url as
        # parameter for urlopen
        url = base_url + query_string
        # store the response of URL
        response = urlopen(url)
        # storing the JSON response
        # from url in data
        data_json = json.loads(response. read ())
        # print the json response
        print(data_json)
        return data_json
        #query_results = requests.get(base_url + query_string, headers=header).json()
        return query_results
    except Exception as e:
        logger.error(f"Error in query_cpsc: {e}")
        return []
"""
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

# -------------------------------------------------------- FLASK BACKEND COMPONENT --------------------------------------------------------

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    amazon_link = data.get('amazon_link')

    if not amazon_link:
        return jsonify({"error": "amazon_link is required"}), 400

    scraped_info = scrape_data(amazon_link)
    if not scraped_info:
        return jsonify({"error": "Failed to scrape data"}), 500

    scraped_info = json.loads(scraped_info)
    ## PLACEHOLDER HARD-CODED AMAZON DATA BELOW - USE ACTUAL SCRAPER INFORMATION LATER ##
    scraped_info = { 
        'Product Name' : "The Original Gel Blaster Surge - Extended 100+ Foot Range - Toy Gel Blasters with Water Based Beads - Semi & Automatic Modes with Powerful 170 FPS - Outdoor Games & Toys - Ages 14+",
        'Brand' : "Gel Blaster",
        'Description' : """
        Surge Into Action: The Gel Blaster Surge boasts superior power and distance with an incredible range of over 100 feet per blast and an included high-velocity barrel that launches Gellets at a blazing speed of 170 feet per second.
        Less Time Cleaning, More Time Having a Blast: Gel Blaster water-based Gellets are non-toxic, non-staining, burst on impact and evaporate in the backyard, ensuring safe and mess-free fun.
        Adjustable Blaster Modes: Single Blast mode hones your precision and training, and Fully Automatic mode helps you dominate the competition with a barrage of 10 Gellets per second. You can even easily swap out the standard barrel for the included low-velocity barrel, reducing the intensity to 90 feet per second for less experienced players.
        Long-Lasting Battery: Surge features a hassle-free built-in battery, providing 4 hours of play on a 45-minute USB-C charge. It also includes a low battery indicator to signal when it's time to charge up as well as a lightning-fast USB-C cable that gets you back in action in half the time.
        Ready to Blast Right Out of the Box: This kit contains everything you need right out of the box! 1 Surge blaster, 1 pre-loaded gravity fed hopper with 800 pre-hydrated Gellets, 1 USB-C fast charging cable, 1 set of 2 adjustable velocity barrels (orange - low velocity; white - high velocity), 1 pair of adjustable safety glasses, and 1 pack of 10,000 Gellets.
        """
    }
    ## PLACEHOLDER AMAZON DATA - LINK TO SCRAPER INFORMATION LATER ##
    
    query_result = query_cpsc(productname_key="Gel", manufacturer_key=None) # later on it'll be scraped_info['Product Name'], scraped_info['Manufacturer'], etc from scraped_info
    recall_info = GetMatchingRecalls(query_result, scraped_info)
    #print(recall_info)
    try:
        return jsonify(recall_info[0])
    except:
        return "No Recalls Found"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
    
