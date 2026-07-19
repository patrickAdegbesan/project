# Rehoboth-Winners Shopping Mall — Shop Ownership Landing Page

A professional landing page for the **Rehoboth-Winners Shopping Mall**
development at Bluestone Garden City (proposal Option 2: Basic
Information Website). All payment buttons point to the official
Paystack payment link:

> https://paystack.shop/pay/shop-development-fund

## Page sections

- **Hero** — "Only 4 slots remaining" notice, headline, and a Project
  Summary panel (location, 16 shops, slot price, payment channel).
- **01 The Project** — the 500 sqm plot, 8 shops up / 8 down, estate
  road frontage, Bluestone Garden City context.
- **02 Why Own a Shop Here** — six reasons (lifetime investment,
  rental income, growing community, security, one-stop mall, expert
  support).
- **03 Slots & Pricing** — full slot ₦7.5m (2 shops + toilet space),
  pairing option for single shops, and the Stage 1 land-acquisition
  breakdown table (₦50m land + 5% agency + 10% legal + 5% development
  = ₦60m).
- **04 The Four Project Stages** — land, documentation & design,
  construction to roof level, individual finishing.
- **05 Business Ideas** — the 30+ suggested businesses grouped into
  Food & Grocery, Food Service & Leisure, Fashion & Beauty, and
  Services & Retail.
- **06 Enquiries** — phone numbers (0803 334 6916, 0907 719 5867),
  email, and an enquiry form that opens the visitor's email app
  pre-filled (no backend required).
- Fully mobile responsive — phones, tablets and desktops.

## Tech

Pure static HTML/CSS/JS — no frameworks, no build step, no external
CDNs. The only external destination is the Paystack payment page.

```
shop-development-fund/
├── index.html
├── css/styles.css
└── js/main.js
```

## Running locally

Open `index.html` directly in a browser, or serve the folder:

```bash
cd shop-development-fund
python3 -m http.server 8080   # → http://localhost:8080
```

## Deploying

Upload the folder contents to any static host (cPanel, Netlify,
GitHub Pages, Vercel, etc.). No server-side code is needed.

## Editing common things

- **Slots remaining** — search `index.html` for "4 of 8" (appears in
  the summary panel and the pricing table) and for "Only 4 slots".
- **Payment link** — search `index.html` for `paystack.shop`.
- **Phone numbers / email** — search for `0803` / `sale@301atech.com`
  in `index.html` (the email also appears in `js/main.js`).
- **Colours** — edit the CSS variables at the top of `css/styles.css`.
