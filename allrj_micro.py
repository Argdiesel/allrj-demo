"""
ALLRJ Price Intelligence — Micro Demo
Single page. URL in. Price out. Payment link at bottom.
This is the MVP test vehicle.
"""
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import json
import time
from urllib.parse import urlparse

st.set_page_config(
    page_title="ALLRJ Price Intelligence",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── STRIPE PAYMENT LINK ───────────────────────────────────
# Replace this with your actual Stripe payment link
STRIPE_LINK = "https://buy.stripe.com/YOUR_LINK_HERE"
PRICE       = "£29/mo"

# ── CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sora:wght@700;800&display=swap');

:root {
    --bg:       #0A0C12;
    --surface:  #161926;
    --border:   #252840;
    --accent:   #6366F1;
    --accent-lt:#A5B4FC;
    --text:     #F1F5F9;
    --text2:    #A8B8CC;
    --muted:    #5A6A80;
    --green:    #34D399;
    --red:      #F87171;
    --yellow:   #FBBF24;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
    -webkit-font-smoothing: antialiased !important;
}

/* Hide all Streamlit chrome */
[data-testid="stHeader"]        { display: none !important; }
[data-testid="stToolbar"]       { display: none !important; }
[data-testid="stDecoration"]    { display: none !important; }
[data-testid="stSidebarNav"]    { display: none !important; }
[data-testid="stStatusWidget"]  { display: none !important; }
.stDeployButton                 { display: none !important; }
#MainMenu                       { display: none !important; }
footer                          { display: none !important; }
header                          { display: none !important; }

/* Force dark */
.main, .stApp, [data-testid="stAppViewContainer"],
[data-testid="block-container"] {
    background-color: var(--bg) !important;
}

.block-container {
    padding: 3rem 1.5rem 4rem !important;
    max-width: 680px !important;
    margin: 0 auto !important;
}

/* Logo */
.logo {
    font-family: 'Sora', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.5px;
    margin-bottom: 4px;
}
.logo span { color: var(--accent-lt); }
.tagline {
    font-size: 0.82rem;
    color: var(--text2);
    margin-bottom: 2rem;
}

/* Hero headline */
.hero {
    font-family: 'Sora', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: var(--text);
    line-height: 1.25;
    letter-spacing: -0.5px;
    margin-bottom: 10px;
}
.hero span { color: var(--accent-lt); }
.hero-sub {
    font-size: 0.95rem;
    color: var(--text2);
    line-height: 1.7;
    margin-bottom: 2rem;
}

/* Input */
.stTextInput input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-size: 0.95rem !important;
    padding: 12px 16px !important;
    transition: border-color 0.15s !important;
}
.stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}
.stTextInput label {
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: var(--text2) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
}

/* Button */
.stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    width: 100% !important;
    transition: all 0.15s !important;
    box-shadow: 0 2px 12px rgba(99,102,241,0.3) !important;
}
.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.45) !important;
}

/* Result card */
.result-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 28px 28px 24px;
    margin: 1.5rem 0;
    position: relative;
    overflow: hidden;
}
.result-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent-lt));
}
.result-brand {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: var(--accent-lt);
    margin-bottom: 6px;
}
.result-product {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text);
    line-height: 1.4;
    margin-bottom: 16px;
}
.result-price-row {
    display: flex;
    align-items: flex-end;
    gap: 16px;
    margin-bottom: 16px;
}
.result-price {
    font-family: 'Sora', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -2px;
    line-height: 1;
}
.result-method {
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    background: rgba(52,211,153,0.1);
    color: var(--green);
    border: 1px solid rgba(52,211,153,0.2);
    margin-bottom: 6px;
}
.result-url {
    font-size: 0.72rem;
    color: var(--muted);
    word-break: break-all;
    margin-bottom: 16px;
    padding-top: 12px;
    border-top: 1px solid var(--border);
}
.result-insight {
    background: rgba(99,102,241,0.06);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 0.84rem;
    color: var(--text2);
    line-height: 1.6;
}

/* CTA section */
.cta-box {
    background: var(--surface);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 14px;
    padding: 28px;
    text-align: center;
    margin-top: 1.5rem;
}
.cta-title {
    font-family: 'Sora', sans-serif;
    font-size: 1.25rem;
    font-weight: 800;
    color: var(--text);
    margin-bottom: 8px;
}
.cta-sub {
    font-size: 0.88rem;
    color: var(--text2);
    line-height: 1.6;
    margin-bottom: 20px;
}
.cta-features {
    display: flex;
    justify-content: center;
    gap: 20px;
    flex-wrap: wrap;
    margin-bottom: 20px;
}
.cta-feature {
    font-size: 0.78rem;
    color: var(--text2);
}
.cta-feature span { color: var(--green); margin-right: 4px; }
.cta-price {
    font-family: 'Sora', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--text);
    margin-bottom: 4px;
}
.cta-price-sub {
    font-size: 0.78rem;
    color: var(--muted);
    margin-bottom: 20px;
}
.cta-btn {
    display: block;
    background: var(--accent);
    color: #fff !important;
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    padding: 14px 32px;
    border-radius: 10px;
    text-decoration: none !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.4);
    transition: all 0.15s;
    margin: 0 auto;
    max-width: 320px;
}
.cta-btn:hover { opacity: 0.9; transform: translateY(-1px); }
.cta-guarantee {
    font-size: 0.72rem;
    color: var(--muted);
    margin-top: 12px;
}

/* Social proof */
.proof-row {
    display: flex;
    gap: 20px;
    justify-content: center;
    flex-wrap: wrap;
    margin: 2rem 0 1rem;
}
.proof-item {
    font-size: 0.78rem;
    color: var(--muted);
    text-align: center;
}
.proof-num {
    font-family: 'Sora', sans-serif;
    font-size: 1.2rem;
    font-weight: 800;
    color: var(--text2);
    display: block;
}

/* Error */
.error-box {
    background: rgba(248,113,113,0.06);
    border: 1px solid rgba(248,113,113,0.2);
    border-radius: 10px;
    padding: 16px 20px;
    font-size: 0.88rem;
    color: var(--red);
    margin: 1rem 0;
}

/* Divider */
.divider {
    height: 1px;
    background: var(--border);
    margin: 2rem 0;
}

/* Scanning animation */
.scanning {
    text-align: center;
    padding: 2rem;
    color: var(--text2);
    font-size: 0.9rem;
}

@media (max-width: 480px) {
    .hero { font-size: 1.5rem; }
    .result-price { font-size: 2.2rem; }
    .cta-features { flex-direction: column; align-items: center; gap: 8px; }
}
</style>
""", unsafe_allow_html=True)


# ── SCRAPING ENGINE ───────────────────────────────────────

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

BRAND_MAP = {
    'gymshark': 'Gymshark', 'underarmour': 'Under Armour',
    'nike': 'Nike', 'adidas': 'Adidas', 'lululemon': 'Lululemon',
    'alphalete': 'Alphalete', 'aybl': 'AYBL', 'gymking': 'Gym King',
    'vuori': 'Vuori', 'puma': 'Puma', 'reebok': 'Reebok',
    'newbalance': 'New Balance', 'youngla': 'YoungLA',
    'nvgtn': 'NVGTN', 'ryderwear': 'Ryderwear',
    'aloyoga': 'Alo Yoga', 'rhone': 'Rhone', 'fabletics': 'Fabletics',
}

def detect_brand(url):
    domain = urlparse(url).netloc.lower()
    for key, name in BRAND_MAP.items():
        if key in domain:
            return name
    return domain.replace('www.', '').split('.')[0].title()

def try_shopify(url):
    try:
        parsed = urlparse(url)
        path = parsed.path.rstrip('/').split('?')[0]
        json_url = f"{parsed.scheme}://{parsed.netloc}{path}.json"
        r = requests.get(json_url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json().get('product', {})
            variants = data.get('variants', [])
            if variants:
                prices = [float(v['price']) for v in variants]
                return {
                    'price': min(prices),
                    'title': data.get('title', 'Product'),
                    'method': 'Live price feed',
                }
    except Exception:
        pass
    return None

def try_html(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, 'html.parser')

        # JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string or '')
                items = data if isinstance(data, list) else [data]
                for item in items:
                    offers = item.get('offers') or item.get('Offers')
                    if offers:
                        if isinstance(offers, list):
                            offers = offers[0]
                        p = offers.get('price') or offers.get('lowPrice')
                        if p:
                            n = float(str(p).replace(',', ''))
                            title = item.get('name', 'Product')
                            return {'price': n, 'title': title, 'method': 'Live price feed'}
            except Exception:
                continue

        # OG price
        og = soup.find('meta', property='product:price:amount')
        if og and og.get('content'):
            try:
                n = float(og['content'])
                title_tag = soup.find('meta', property='og:title')
                title = title_tag['content'] if title_tag else 'Product'
                return {'price': n, 'title': title, 'method': 'Live price feed'}
            except Exception:
                pass

        # CSS selectors
        for sel in ['[itemprop="price"]', '[class*="price"]', '[class*="Price"]', '[data-price]']:
            for tag in soup.select(sel):
                text = tag.get_text(strip=True)
                m = re.search(r'[\$£€]?\s*(\d{1,4}(?:[.,]\d{2})?)', text)
                if m:
                    try:
                        n = float(m.group(1).replace(',', ''))
                        if 1 < n < 9999:
                            title_tag = soup.find('meta', property='og:title') or soup.find('title')
                            title = (title_tag.get('content') or title_tag.get_text())[:80] if title_tag else 'Product'
                            return {'price': n, 'title': title.strip(), 'method': 'Live price feed'}
                    except Exception:
                        continue
    except Exception:
        pass
    return None

def scrape(url):
    result = try_shopify(url)
    if result:
        return result
    result = try_html(url)
    if result:
        return result
    return None

def get_insight(brand, price):
    insights = {
        'Gymshark':    f"Gymshark prices this category between £20–£55. At £{price:.0f}, they're in their mid-range — they typically discount 20–30% during sale periods every 6–8 weeks.",
        'Lululemon':   f"Lululemon rarely discounts. At £{price:.0f}, this is close to their standard price. Use this as your premium anchor — your product at 70% of this price looks like great value.",
        'Under Armour':f"Under Armour is mid-market. At £{price:.0f}, they're competing on performance value. There's room above and below this price depending on your brand positioning.",
        'Nike':        f"Nike anchors the mass market. At £{price:.0f}, this is their volume price point. DTC brands that match Nike on quality but price 10–20% higher win on brand story.",
        'AYBL':        f"AYBL prices aggressively to grow. At £{price:.0f}, they're targeting acquisition. If they raise prices — which growing DTC brands always do — that's your window.",
        'Alphalete':   f"Alphalete commands premium DTC pricing. At £{price:.0f}, they've built enough brand equity to hold margin. A strong benchmark for where DTC can go.",
    }
    default = f"At £{price:.0f}, this sits in the mid-market range for activewear. The DTC sweet spot for this category is typically £35–£75 depending on positioning and fabric story."
    return insights.get(brand, default)


# ── PAGE CONTENT ──────────────────────────────────────────

# Logo
st.markdown("""
<div class="logo">ALL<span>RJ</span></div>
<div class="tagline">Price Intelligence for activewear brands</div>
""", unsafe_allow_html=True)

# Hero
st.markdown("""
<div class="hero">Know what your competitors<br>charge <span>before your customers do</span></div>
<div class="hero-sub">
  Paste any competitor product URL below. We'll pull the live price instantly —
  no signup, no setup, no waiting.
</div>
""", unsafe_allow_html=True)

# URL Input
url = st.text_input(
    "Competitor product URL",
    placeholder="https://www.gymshark.com/products/...",
    label_visibility="visible",
)

scan_btn = st.button("⚡  Get Live Price", type="primary")

# Social proof
st.markdown("""
<div class="proof-row">
  <div class="proof-item"><span class="proof-num">25+</span>brands tracked</div>
  <div class="proof-item"><span class="proof-num">£0</span>to try</div>
  <div class="proof-item"><span class="proof-num">10s</span>avg scan time</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── SCAN LOGIC ────────────────────────────────────────────
if scan_btn and url.strip():
    if not url.startswith('http'):
        st.markdown("""
        <div class="error-box">
          Please enter a full URL starting with https://
        </div>
        """, unsafe_allow_html=True)
    else:
        with st.spinner("Scanning live price..."):
            time.sleep(0.5)
            data = scrape(url.strip())

        if data:
            brand   = detect_brand(url)
            price   = data['price']
            title   = data['title']
            method  = data['method']
            insight = get_insight(brand, price)

            # Detect currency symbol
            domain = urlparse(url).netloc.lower()
            symbol = "£" if any(x in domain for x in ['.co.uk', 'gymshark', 'gymking', 'aybl']) else "$"

            # Result card
            st.markdown(f"""
            <div class="result-card">
              <div class="result-brand">{brand}</div>
              <div class="result-product">{title[:80]}</div>
              <div class="result-price-row">
                <div class="result-price">{symbol}{price:.2f}</div>
                <div class="result-method">{method}</div>
              </div>
              <div class="result-insight">
                💡 {insight}
              </div>
              <div class="result-url">{url[:80]}{'...' if len(url) > 80 else ''}</div>
            </div>
            """, unsafe_allow_html=True)

            # CTA
            st.markdown(f"""
            <div class="cta-box">
              <div class="cta-title">Track this automatically — every single day</div>
              <div class="cta-sub">
                You just saw what ALLRJ does in 10 seconds.<br>
                Imagine waking up every morning knowing exactly what changed overnight.
              </div>
              <div class="cta-features">
                <div class="cta-feature"><span>✓</span> 25+ brands tracked daily</div>
                <div class="cta-feature"><span>✓</span> Sale alerts the moment they happen</div>
                <div class="cta-feature"><span>✓</span> Price history and trend charts</div>
                <div class="cta-feature"><span>✓</span> AI-generated weekly brief</div>
                <div class="cta-feature"><span>✓</span> No setup — brands pre-loaded</div>
              </div>
              <div class="cta-price">{PRICE}</div>
              <div class="cta-price-sub">Cancel anytime · No contract · 14-day free trial</div>
              <a href="{STRIPE_LINK}" target="_blank" class="cta-btn">
                Start Free Trial — {PRICE}
              </a>
              <div class="cta-guarantee">✓ 14-day free trial &nbsp;·&nbsp; ✓ Cancel anytime &nbsp;·&nbsp; ✓ No credit card to start trial</div>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown(f"""
            <div class="error-box">
              We couldn't pull a price from that URL. This sometimes happens with
              heavily JS-rendered sites like Nike or Adidas. Try a Gymshark,
              Lululemon, AYBL, or Alphalete product URL — those work great.
            </div>
            """, unsafe_allow_html=True)

            # Still show CTA even on failure
            st.markdown(f"""
            <div class="cta-box">
              <div class="cta-title">Want us to track any brand — including this one?</div>
              <div class="cta-sub">
                The full ALLRJ platform handles JS-rendered sites, tracks 25+ brands
                automatically, and sends you alerts the moment a price changes.
              </div>
              <div class="cta-price">{PRICE}</div>
              <div class="cta-price-sub">14-day free trial · Cancel anytime</div>
              <a href="{STRIPE_LINK}" target="_blank" class="cta-btn">
                Start Free Trial — {PRICE}
              </a>
            </div>
            """, unsafe_allow_html=True)

elif scan_btn and not url.strip():
    st.markdown("""
    <div class="error-box">Please paste a competitor product URL above.</div>
    """, unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-top:3rem;padding-top:1.5rem;
            border-top:1px solid var(--border);">
  <div style="font-size:0.72rem;color:var(--muted);">
    ALLRJ Price Intelligence &nbsp;·&nbsp; Built for DTC activewear brands
  </div>
</div>
""", unsafe_allow_html=True)
