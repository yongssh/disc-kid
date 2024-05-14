import urllib.request
from bs4 import BeautifulSoup
import json

def scrape_data(url):
    with urllib.request.urlopen(url) as response:
        html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    #print(soup)

    name_span = soup.find(id='productTitle')
    #print(name_span.prettify())
    if name_span:
        name = name_span.get_text(strip=True)
    else:
        name = "Product name not found"

    # extract brand
    brand_span = soup.find(class_='a-spacing-small po-brand')
    if brand_span:
        brand = brand_span.find(class_="a-size-base po-break-word").get_text()
        print(brand)
    else:
        brand = "Brand not found" 

    # extract product description
    description = " "

    feature_bullets_div = soup.find('div', id='feature-bullets')
    if feature_bullets_div:
        list_items = feature_bullets_div.find_all('span', class_='a-list-item')
    else:
        description = "Description not found"
    if list_items:
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
    print(json_data)
    return json_data
    

if __name__ == "__main__":
    #test url 
    url = "https://www.amazon.com/dp/B08W1ZNRSR/ref=sspa_dk_detail_2?psc=1&pd_rd_i=B08W1ZNRSR&pd_rd_w=UxWOb&content-id=amzn1.sym.248b5e31-60e8-4934-96cf-b3789198461a&pf_rd_p=248b5e31-60e8-4934-96cf-b3789198461a&pf_rd_r=R79K1VR825SE8X1N11X1&pd_rd_wg=POLXB&pd_rd_r=50b50b3e-f455-4e00-937f-b38a76708501&s=pc&sp_csd=d2lkZ2V0TmFtZT1zcF9kZXRhaWxfdGhlbWF0aWM"
    scrape_data(url)
