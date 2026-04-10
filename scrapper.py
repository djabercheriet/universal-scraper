import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import random
import re

# ---------- USER INPUT ----------
CATEGORY_URL = input("Category URL: ").strip()
START_PAGE = int(input("Start page (default 1): ") or 1)
MAX_PAGES = int(input("Number of pages: ") or 1)
LIMIT = int(input("Max products (0 = no limit): ") or 0)

# ---------- HELPERS ----------

def generate_sku(name):
    return "SKU-" + str(abs(hash(name)))[:10]

def generate_barcode():
    return "".join([str(random.randint(0, 9)) for _ in range(13)])

def generate_cost(price):
    return round(price * random.uniform(0.6, 0.85), 2) if price else 0

def build_page_url(base, page):
    if page == 1:
        return base
    return base.rstrip("/") + f"/page/{page}/"

# ---------- PRICE CLEANER ----------

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

# ---------- PRICE EXTRACTOR (FINAL FIX) ----------

async def extract_price(page):
    await page.wait_for_timeout(3000)

    # ---------- 1. SCAN ALL SCRIPT TAGS ----------
    scripts = await page.query_selector_all("script")

    for s in scripts:
        content = await s.inner_text()

        # find price patterns inside JS
        matches = re.findall(r'"price"\s*:\s*"?(\d+[.,]?\d*)"?', content)
        for m in matches:
            price = clean_price(m)
            if price > 0:
                print("JS PRICE:", price)
                return price

        # WooCommerce variation price
        matches = re.findall(r'"display_price"\s*:\s*(\d+\.?\d*)', content)
        for m in matches:
            price = float(m)
            if price > 0:
                print("VARIATION PRICE:", price)
                return price

    # ---------- 2. META TAG ----------
    meta = await page.query_selector("meta[property='product:price:amount']")
    if meta:
        price = await meta.get_attribute("content")
        price = clean_price(price)
        if price > 0:
            print("META PRICE:", price)
            return price

    # ---------- 3. FORCE EXTRACT FROM FULL HTML ----------
    html = await page.content()

    matches = re.findall(r'\d{2,6}[.,]?\d*\s?(?:DA|د\.ج)', html)
    for m in matches:
        price = clean_price(m)
        if price > 0:
            print("HTML PRICE:", m)
            return price

    print("❌ PRICE NOT FOUND (JS protected)")
    return 0


# ---------- SCRAPER ----------

async def scrape():
    products = []
    seen_links = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        for page_num in range(START_PAGE, START_PAGE + MAX_PAGES):
            url = build_page_url(CATEGORY_URL, page_num)
            print(f"\nLoading page {page_num}: {url}")

            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(4000)

            links = await page.query_selector_all("a")

            product_links = []
            for l in links:
                href = await l.get_attribute("href")
                if href and "/product/" in href and href not in seen_links:
                    seen_links.add(href)
                    product_links.append(href)

            print(f"Found {len(product_links)} products")

            # ---------- SCRAPE PRODUCTS ----------
            for link in product_links:
                if LIMIT and len(products) >= LIMIT:
                    break

                ppage = await context.new_page()
                await ppage.goto(link)
                await ppage.wait_for_timeout(3000)

                # NAME
                name_el = await ppage.query_selector("h1")
                name = (await name_el.inner_text()).strip() if name_el else ""

                # PRICE (FIXED)
                price = await extract_price(ppage)

                # IMAGE (URL ONLY - BEST)
                img_el = await ppage.query_selector("img.wp-post-image")
                image = await img_el.get_attribute("src") if img_el else ""

                if name:
                    products.append({
                        "Image": image,
                        "Name": name,
                        "SKU": generate_sku(name),
                        "Category": CATEGORY_URL.split("/")[-2],
                        "Price": price,
                        "Cost": generate_cost(price),
                        "Stock": random.randint(5, 50),
                        "Barcode": generate_barcode()
                    })

                    print(f"✔ {name} | {price} DA")

                await ppage.close()

            await page.close()

            if LIMIT and len(products) >= LIMIT:
                break

        await browser.close()

    return products

# ---------- EXPORT ----------

def export(data):
    df = pd.DataFrame(data, columns=[
        "Image", "Name", "SKU", "Category",
        "Price", "Cost", "Stock", "Barcode"
    ])
    df.to_csv("products.csv", index=False, encoding="utf-8-sig")

# ---------- RUN ----------

data = asyncio.run(scrape())
export(data)

print(f"\n✅ Done: {len(data)} products exported")