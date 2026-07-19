# Shop Development Fund — Investment Landing Page

A classic, professional landing page for the **Shop Development Fund**
investment project (proposal Option 2: Basic Information Website).
All payment buttons point to the official Paystack payment link:

> https://paystack.shop/pay/shop-development-fund

## What's included

- **Hero + call-to-action** — project introduction with prominent
  "Invest Now" buttons.
- **About section** — project purpose and objectives.
- **Investment opportunity** — why-invest cards.
- **How to invest** — three-step payment walkthrough.
- **Project updates** — announcements section the team can extend by
  copying an `<article class="update">` block in `index.html`.
- **Contact & enquiry** — contact details plus an enquiry form that
  opens the visitor's email app pre-filled (no backend required).
- **Fully mobile responsive** — phones, tablets and desktops.

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

- **Payment link** — search `index.html` for `paystack.shop` and
  replace the URL (it appears on every payment button).
- **Contact email** — search for `sale@301atech.com` in `index.html`
  and `js/main.js`.
- **Colours** — edit the CSS variables at the top of `css/styles.css`.
