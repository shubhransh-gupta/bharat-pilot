# ✨ Niffler (`niffler-agent`)

[![Documentation](https://img.shields.io/badge/Documentation-Live%20Portal-blue?style=for-the-badge&logo=vercel)](https://agent-docs-coral.vercel.app)
[![GitHub Stars](https://img.shields.io/github/stars/shubhransh-gupta/bharat-pilot?style=for-the-badge&color=2997ff)](https://github.com/shubhransh-gupta/bharat-pilot/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

> **Autonomous Travel Concierge & Citizen FinTech Super-Agent** • Multi-Airline Fare Radar • IRCTC Tatkal & Live Berths • 1-Click Merchant Handoff • CA-Free ITR-1 Optimizer • EPFO Wealth Compounder

```
   _   _ ___ _____ _____ _     _____ ____  
  | \ | |_ _|  ___|  ___| |   | ____|  _ \ 
  |  \| || || |_  | |_  | |   |  _| | |_) |
  | |\  || ||  _| |  _| | |___| |___|  _ < 
  |_| \_|___|_|   |_|   |_____|_____|_| \_\
✨ The magical beast sniffing out every coin in fares & tax refunds ✨
```

---

## 🪙 Why "Niffler"?
In the Wizarding World, a **Niffler** is a long-snouted, burrowing creature with an irresistible, insatiable attraction to anything shiny — gold galleons, silver trinkets, and buried treasures.

In the digital world, **Niffler** sniffs out every hidden rupee:
1. **Airfares & Tatkal Tickets**: Digs through airline and railway matrices to unearth the absolute cheapest flights, boutique homestay rates, and confirmed Tatkal berths.
2. **Citizen Taxes & Form-16**: Sniffs out every eligible tax deduction under Section 80C, 80D, and HRA, running an Old vs New Tax Regime showdown so you keep more gold in your vault without paying a Chartered Accountant.
3. **EPF Compounding**: Tracks your retirement treasure chest with 8.25% EPFO compounding simulations.

---

## 💡 Real-World Problems We Solve

### 1. The CA Fee Problem: Autonomous Income Tax Filing (ITR)
Every July, millions of salaried employees pay ₹2,000 to ₹5,000 to Chartered Accountants just to upload their Form-16.
* **Autonomous Tax Regime Showdown**: Automatically computes tax under both the **New Tax Regime (Section 115BAC with Budget standard deduction of ₹75,000 and ₹7.75L zero-tax rebate)** and the **Old Tax Regime (80C, 80D, HRA, 24b)**.
* **Exact Savings Recommendation**: Tells you exactly which regime saves you more money (e.g. *"Choose New Regime: You save ₹17,940!"*).
* **1-Click ITR-1 JSON**: Exports schema-compliant ITR-1 (Sahaj) JSON ready to upload directly onto the official [incometax.gov.in](https://eportal.incometax.gov.in) portal without intermediaries.

### 2. The Travel & Tatkal Hassle: MakeMyTrip Alternative
Booking travel across flights, IRCTC trains, and hotels is fragmented across dozens of tabs.
* **Multi-Airline Fare Radar**: Scans across IndiGo, Air India, Akasa, and SpiceJet to identify the lowest direct fares.
* **IRCTC Live Train Berths & Tatkal Advisor**: Displays live berth availability (1A, 2A, 3A, SL, CC, EC), provides official Tatkal opening windows (10:00 AM AC / 11:00 AM Non-AC), and gives ML-backed PNR confirmation probabilities.
* **Hotel & Homestay Discovery**: Filters boutique homestays and resorts with couple-friendly, budget, and free-cancellation tags.
* **Auto-Fill & Payment Handoff**: Auto-populates passenger details and securely lands you directly on the final payment gateway screen (UPI/Card) so your financial credentials are never touched by an AI.

### 3. The EPFO Blackbox: EPF Passbook & Pension Explorer
* **Passbook Breakdown**: Deconstructs your 12% employee share, 3.67% employer PF share, and 8.33% EPS pension allocation.
* **Withdrawal Eligibility Checker**: Pre-checks eligibility for Form 31 (Medical, Housing, Marriage advances), Form 19 (Full PF settlement), and Form 10C (Pension scheme certificate).
* **Compounding Wealth Calculator**: Simulates your retirement nest-egg at age 58 with the government's 8.25% p.a. compounding rate.

---

## 🚀 Quick Start

### 1. Installation

Clone and install locally:

```bash
git clone https://github.com/shubhransh-gupta/bharat-pilot.git
cd bharat-pilot
pip install -e .
```

### 2. Launch the Interactive Web Dashboard

Launch the Apple HIG styled dual-hub dashboard:

```bash
niffler web --port 8501
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

## 💻 CLI Terminal Usage

### ✈️ Travel Operations

```bash
# 1. Search cheapest flights between cities
niffler travel flights DEL BLR

# 2. Filter direct flights under budget
niffler travel flights BOM GOI --direct --max-price 4500

# 3. Discover hotels and homestays
niffler travel hotels GOA --budget 6000 --couple

# 4. Check IRCTC trains and Tatkal windows
niffler travel trains NDLS MMCT
```

### 📑 Citizen FinTech Operations

```bash
# 1. Run ITR Tax Optimization with Form-16 inputs
niffler itr 1250000 --tds 75000 --sec80c 150000 --sec80d 25000 --hra 120000

# 2. Inspect EPF Passbook & Wealth Compounder
niffler epf 60000 --tenure 4.5 --balance 380000
```

---

## 🔄 Use as a GitHub Action in Any Project

Drop **Niffler** into any GitHub repository workflow to automate scheduled flight fare tracking or team travel budgets:

```yaml
name: Weekly Flight Fare Watcher

on:
  schedule:
    - cron: '0 8 * * 1'
  workflow_dispatch:

jobs:
  fare-watch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Niffler Fare Watcher
        uses: shubhransh-gupta/bharat-pilot@v1
        with:
          origin: 'DEL'
          destination: 'BLR'
          max-price: '4500'
```

---

## 📦 Architecture

```
bharat-pilot/ (Niffler)
├── niffler/
│   ├── travel/
│   │   ├── flights.py          # Multi-airline fare radar & cheapest date finder
│   │   ├── hotels.py           # Hotel, resort & homestay discovery engine
│   │   ├── trains.py           # IRCTC live berths, Tatkal advisor, PNR predictor
│   │   ├── buses.py            # Intercity AC sleeper bus comparator
│   │   └── booking_handoff.py  # Passenger auto-fill & payment gateway handoff
│   ├── citizen/
│   │   ├── itr_optimizer.py    # Old vs New Regime showdown & ITR-1 JSON exporter
│   │   └── epf_explorer.py     # EPFO passbook analyzer & retirement compounder
│   ├── web/
│   │   ├── server.py           # Embedded REST API backend & static file server
│   │   └── static/             # Apple HIG web portal (index.html, styles.css, app.js)
│   ├── llm.py                  # Universal LLM router (Gemini, Claude, GPT, DeepSeek, Ollama)
│   ├── config.py               # Passenger profile & configuration management
│   └── cli.py                  # Rich terminal user interface
├── tests/                      # Pytest automated test suite (100% passing)
├── action.yml                  # Reusable GitHub Action definition
└── pyproject.toml              # Build & packaging specifications
```

---

## 📄 License

MIT License. Copyright (c) 2026 Shubhransh Gupta.
