import json
import re
import urllib.request
from bs4 import BeautifulSoup
from pypdf import PdfReader
import io

def parse_gem_bids():
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = "https://bidplus.gem.gov.in/all-bids"
    req = urllib.request.Request(url, headers=headers)
    
    try:
        html = urllib.request.urlopen(req, timeout=15).read()
    except Exception:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    bid_blocks = soup.find_all('div', class_='bid_box')
    parsed_bids = []

    for card in bid_blocks[:25]:
        try:
            bid_no_tag = card.find('a', class_='bid_no')
            if not bid_no_tag: 
                continue
            bid_no = bid_no_tag.text.strip()
            doc_link = "https://bidplus.gem.gov.in" + bid_no_tag.get('href')
            
            pdf_req = urllib.request.Request(doc_link, headers=headers)
            pdf_data = urllib.request.urlopen(pdf_req, timeout=15).read()
            reader = PdfReader(io.BytesIO(pdf_data))
            full_text = "\n".join([page.extract_text() or "" for page in reader.pages])

            district_match = re.search(r'Consignee[/\s\w]+Delivery\s*Location.*?(Meerut|Delhi|Ghaziabad|Lucknow|[A-Z][a-z]+)', full_text, re.IGNORECASE)
            delivery_district = district_match.group(1) if district_match else "India Wide"

            items_found = re.findall(r'(?:Item Title|BOQ Item|Item Description)[:\s]+([^\n\r,]+)', full_text, re.IGNORECASE)
            if not items_found:
                items_found = [bid_no_tag.find_next('span').text.strip() if bid_no_tag.find_next('span') else "General Supplies"]

            parsed_bids.append({
                "bid_no": bid_no,
                "district": delivery_district.capitalize(),
                "items": list(set(items_found)),
                "pdf_url": doc_link
            })
        except Exception:
            continue

    with open('tenders.json', 'w', encoding='utf-8') as f:
        json.dump(parsed_bids, f, indent=2)

if __name__ == "__main__":
    parse_gem_bids()
