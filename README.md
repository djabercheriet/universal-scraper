# 🚀 Universal E-Commerce Scraper (POS-Ready)

A powerful, production-ready web scraping engine designed to extract product data from **any e-commerce website** and export it into a clean, structured CSV ready for **POS system import**.

---

## ✨ Features

* 🔍 **Universal scraping engine**

  * Works on most WooCommerce, Shopify, and standard e-commerce sites
* ⚡ **Hybrid extraction system**

  * API interception (when available)
  * DOM parsing fallback
  * Intelligent text scanning
* 💰 **Accurate price detection**

  * Handles formats like `1,270.00 د.ج`, `1270 DA`, etc.
* 🖼 **Smart image extraction**

  * Ignores logos/icons
  * Selects best-quality product image
* 🚀 **Parallel scraping**

  * Faster product extraction using async workers
* 🧠 **Auto-generated fields**

  * SKU
  * Barcode
  * Cost (based on price)
  * Stock
* 🧹 **Data cleaning**

  * Removes duplicates
  * Normalizes output
* 📦 **POS-ready CSV export**

  * Correct column order
  * UTF-8 encoding (no broken characters)

---

## 📁 Output Format

The scraper exports a `products.csv` file with the following structure:

| Column   | Description            |
| -------- | ---------------------- |
| Image    | Product image URL      |
| Name     | Product name           |
| SKU      | Auto-generated SKU     |
| Category | Extracted from URL     |
| Price    | Clean numeric price    |
| Cost     | Auto-calculated cost   |
| Stock    | Random stock value     |
| Barcode  | Auto-generated barcode |

---

## 🛠 Requirements

* Python **3.10+** (recommended: 3.11–3.13)
* Playwright
* Pandas

---

## ⚙️ Installation

```bash
# Clone repository
git clone https://github.com/yourusername/universal-scraper.git
cd universal-scraper

# Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

---

## 📦 requirements.txt

```txt
playwright
pandas
```

---

## 🚀 Usage

```bash
python scraper.py
```

### You will be prompted for:

* 🔗 Category URL
* 🔢 Maximum number of products (0 = all)

---

## 🧠 How It Works

### 1. Page Loading

Uses Playwright with:

* `domcontentloaded` strategy
* retry logic to prevent timeouts

### 2. Product Detection

* Automatically detects product links
* No manual selectors required

### 3. Data Extraction

Multi-layer strategy:

1. JavaScript / JSON data
2. DOM parsing
3. Full-page text scanning

### 4. Price Detection (Key Feature)

* Extracts all numeric candidates
* Filters realistic price ranges
* Selects the most probable value

### 5. Image Selection

* Ignores small/irrelevant images
* Picks highest-quality product image

### 6. Export

* Clean CSV
* UTF-8 encoding
* POS-ready structure

---

## ⚠️ Known Limitations

* Some sites with:

  * heavy anti-bot protection
  * private APIs
  * login requirements
    may require additional handling

---

## 🔧 Troubleshooting

### ❌ Timeout Error

```
TimeoutError: Page.goto: Timeout exceeded
```

✅ Fix:

* Ensure this is used:

```python
await page.goto(url, wait_until="domcontentloaded", timeout=60000)
```

---

### ❌ Price = 0

* Site uses dynamic rendering
* Solution:

  * Script already uses fallback extraction
  * Increase wait time if needed

---

### ❌ Playwright Not Found

```bash
pip install playwright
playwright install
```

---

## 🔒 Best Practices

* Use a VPN or proxy for large scraping jobs
* Avoid very high request rates
* Respect website terms of service

---

## 🚀 Roadmap

* [ ] Desktop GUI application
* [ ] Automatic pagination detection
* [ ] Multi-category scraping
* [ ] Image download + optimization
* [ ] Proxy rotation
* [ ] AI-based element detection

---

## 📄 License

MIT License — free to use and modify.

---

## 🤝 Contributing

Pull requests are welcome.
For major changes, open an issue first to discuss what you would like to change.

---

## 💡 Author

Built for high-performance POS data extraction and automation.

---

## ⭐ Support

If this project helped you:

👉 Star the repo
👉 Share it
👉 Build something powerful with it 🚀
