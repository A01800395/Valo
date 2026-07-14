# Product Requirements Document (PRD): Valo Heuristic Rules Engine

## 1. Product Overview & Value Proposition

Valo is a dynamic pricing automation platform designed for independent hotels and short-term rental operators. By bypassing complex, unpredictable Machine Learning models, Valo uses a highly transparent, deterministic **Parametric Heuristic Rules Engine**. This allows hoteliers to see exactly why prices are adjusted based on events, weather, competitor rates, and current occupancy.

The business operates as a high-value CapEx model ($5,000–$12,000 one-time setup fee + $1,200/year retainer after year 1) to eliminate SaaS subscription fatigue.

---

## 2. User Personas

* **The Hotel General Manager (GM):** Needs an automated way to capture peak market rates without losing margin to manual updates or trusting "black-box" machine learning algorithms.
* **The Valo Integration Engineer (Internal):** Performs the "white-glove" deployment. Maps PMS room types, configures competitor scraper endpoints, and inputs safety boundaries within the admin panel.

---

## 3. Core Features Matrix

| Feature | Description | Requirement Level |
| --- | --- | --- |
| **Environmental Monitoring** | Pulls local events (PredictHQ API) and weather forecast data (OpenWeatherMap API). | Must-Have |
| **Competitor Intelligence** | Triggers daily scans of 5 user-defined competitors via scraped data. | Must-Have |
| **Bi-directional PMS Integration** | Reads live occupancy from PMS platforms (Cloudbeds/Mews) and pushes final rates back. | Must-Have |
| **Dual Operational Modes** | **Co-Pilot Mode:** Suggestions require one-click dashboard approval.<br>**Auto-Pilot Mode:** Automated execution every 4 hours. | Must-Have |
| **Hard Safety Envelopes** | Hardcoded Price Floors & Ceilings that act as an absolute shield against extreme rates. | Must-Have |
| **Transparent Audit Log** | A breakdown explaining the mathematical modifiers applied to the base rate. | Must-Have |
