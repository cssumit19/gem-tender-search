import json
import re
from playwright.sync_api import sync_playwright

def scrape_gem():
    tenders = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            # GeM active bids page
            page.goto("https://bidplus.gem.gov.in/all-bids", wait_until="networkidle", timeout=60000)
            
            # Wait for bid cards to render
            page.wait_for_selector(".bid_box, .card", timeout=15000)
            cards = page.query_selector_all(".bid_box, .card")

            for card in cards[:30]:  # Top 30 active bids
                text_content = card.inner_text()
                
                # Bid Number extract
                bid_match = re.search(r'GEM/\d{4}/[B|R]/\d+', text_content)
                bid_no = bid_match.group(0) if bid_match else "N/A"

                # Link extract
                link_tag = card.query_selector("a[href*='showbidDocument'], a[href*='bidlists']")
                pdf_url = ("https://bidplus.gem.gov.in" + link_tag.get_attribute("href")) if link_tag else "https://bidplus.gem.gov.in/all-bids"

                # Items extract
                items_match = re.findall(r'(?:Items:|Category:|Item:)\s*([^\n]+)', text_content, re.IGNORECASE)
                items = [i.strip() for i in items_match] if items_match else ["Procurement Supplies"]

                # Consignee District / State location extract
                loc_match = re.search(r'(?:Location|Consignee|State)[:\s]+([^\n,]+)', text_content, re.IGNORECASE)
                district = loc_match.group(1).strip() if loc_match else "India Wide"

                if bid_no != "N/A":
                    tenders.append({
                        "bid_no": bid_no,
                        "district": district,
                        "items": items,
                        "pdf_url": pdf_url
                    })
        except Exception as e:
            print("Extraction error:", e)
        finally:
            browser.close()

    if tenders:
        with open('tenders.json', 'w', encoding='utf-8') as f:
            json.dump(tenders, f, indent=2)
        print(f"Successfully saved {len(tenders)} live tenders.")

if __name__ == "__main__":
    scrape_gem()
