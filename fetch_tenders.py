import json
import xml.etree.ElementTree as ET
import urllib.request
import re

def fetch_live_gem_feed():
    # GeM official active public bids RSS/XML feed (No bot block, no captcha)
    feed_url = "https://bidplus.gem.gov.in/feed"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    req = urllib.request.Request(feed_url, headers=headers)
    tenders = []

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)

            # Parse standard RSS items
            for item in root.findall('.//item'):
                title = item.find('title').text if item.find('title') is not None else ""
                link = item.find('link').text if item.find('link') is not None else ""
                desc = item.find('description').text if item.find('description') is not None else ""

                # Bid number match
                bid_match = re.search(r'GEM/\d{4}/[B|R]/\d+', title + " " + desc)
                bid_no = bid_match.group(0) if bid_match else title

                # Extract line items / categories
                items = []
                item_match = re.search(r'Items?:\s*([^<\n]+)', desc, re.IGNORECASE)
                if item_match:
                    items = [x.strip() for x in item_match.group(1).split(',')]
                else:
                    items = [title.strip()] if title else ["General Procurement Supplies"]

                # Extract delivery district / consignee location
                loc_match = re.search(r'(?:Location|District|Consignee):\s*([^<\n]+)', desc, re.IGNORECASE)
                district = loc_match.group(1).strip() if loc_match else "India Wide"

                tenders.append({
                    "bid_no": bid_no,
                    "district": district,
                    "items": items,
                    "pdf_url": link if link else "https://bidplus.gem.gov.in/all-bids"
                })

    except Exception as e:
        print("Feed parsing error:", e)

    # Ensure file always writes
    if tenders:
        with open('tenders.json', 'w', encoding='utf-8') as f:
            json.dump(tenders, f, indent=2)
        print(f"Total live tenders saved: {len(tenders)}")
    else:
        print("No tenders received from feed.")

if __name__ == "__main__":
    fetch_live_gem_feed()
