import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import random
import re

# ---------- INPUT ----------
CATEGORY_URL = input("Category URL: ").strip()
LIMIT = int(input("Max products (0 = all): ") or 0)

# ---------- HELPERS ----------

def clean_price(text):
    if not text:
        return 0
    text = re.sub(r"[^\d,.\s]", "", text)
    text = text.replace(" ", "")
    if "," in text and "." in text:
        if text.find(",") < text.find("."):
            text = text.replace(",", "")
        else:
            text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return float(text)
    except:
        return 0

def generate_sku(name):
    return "SKU-" + str(abs(hash(name)))[:10]

def generate_barcode():
    return "".join([str(random.randint(0,9)) for _ in range(13)])

def generate_cost(price):
    return round(price * random.uniform(0.6, 0.85), 2) if price else 0

# ---------- EXTRACT FROM PRODUCT PAGE (SAFE FALLBACK) ----------

async def extract_product(context, url):
    page = await context.new_page()
    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(3000)

    # ---------- NAME ----------
    name_el = await page.query_selector("h1")
    name = await name_el.inner_text() if name_el else ""

    # ---------- PRICE (ULTIMATE FIX) ----------
    body = await page.inner_text("body")

    # extract ALL numbers
    matches = re.findall(r"\d[\d\s.,]*", body)

    candidates = []

    for m in matches:
        price = clean_price(m)

        # filter realistic prices (Algeria context)
        if 10 <= price <= 100000:
            candidates.append(price)

    # choose best candidate
    price = max(candidates) if candidates else 0

    # ---------- IMAGE ----------
    imgs = await page.query_selector_all("img")

    image = ""
    best_score = 0

    for img in imgs:
        src = await img.get_attribute("src")
        if not src:
            continue

        if any(x in src.lower() for x in ["logo", "icon", "banner"]):
            continue

        score = len(src)

        if score > best_score:
            best_score = score
            image = src

    await page.close()

    return {
        "Image": image,
        "Name": name.strip(),
        "SKU": generate_sku(name),
        "Category": CATEGORY_URL.split("/")[-2],
        "Price": price,
        "Cost": generate_cost(price),
        "Stock": random.randint(5,50),
        "Barcode": generate_barcode()
    }
    
    
# ---------- MAIN SCRAPER ----------

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()

        page = await context.new_page()
        await page.goto(CATEGORY_URL)
        await page.wait_for_timeout(5000)

        # ---------- GET PRODUCT LINKS ----------
        links = await page.query_selector_all("a")

        product_links = []
        seen = set()

        for l in links:
            href = await l.get_attribute("href")
            if href and "/product/" in href and href not in seen:
                seen.add(href)
                product_links.append(href)

        print(f"Found {len(product_links)} product links")

        if LIMIT:
            product_links = product_links[:LIMIT]

        # ---------- PARALLEL SCRAPING ----------
        tasks = [
            extract_product(context, url)
            for url in product_links
        ]

        results = await asyncio.gather(*tasks)

        await browser.close()

        return results

# ---------- EXPORT ----------

def export(data):
    df = pd.DataFrame(data, columns=[
        "Image","Name","SKU","Category",
        "Price","Cost","Stock","Barcode"
    ])
    df.to_csv("products.csv", index=False, encoding="utf-8-sig")

# ---------- RUN ----------

data = asyncio.run(scrape())
export(data)

print(f"\n✅ DONE: {len(data)} products")
