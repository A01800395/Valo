# System Proposal & Design Document (SPD): Valo Architecture

## 1. High-Level Architecture Block Diagram

The system separates administrative configuration from client operations using **Next.js as a Backend-For-Frontend (BFF)** paired with **NocoBase** acting as the low-code master relational data manager and administrative database wrapper.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Next.js Frontend                               │
│                      (Dashboard UI / Co-Pilot Toggles)                      │
└──────────────────────┬──────────────────────────────▲───────────────────────┘
                       │ JSON API                             │ SSE / HTTP
                       ▼                                      │
┌─────────────────────────────────────────────────────────────┴───────────────┐
│                              Next.js BFF Layer                              │
│         (Next Auth / Session, Cache Orchestration, Rate-Limiting)           │
└──────────────────────┬──────────────────────────────▲───────────────────────┘
                       │ SQL Query / JSON API                 │ Engine Push
                       ▼                                      │
┌─────────────────────────────────────────────────────────────┴───────────────┐
│                         NocoBase Node.js Backend                            │
│           (Data Models, Access Controls, Admin Logs, Webhook Actions)        │
└──────────────────────┬──────────────────────────────▲───────────────────────┘
                       │ Read / Write                         │ Calculations
                       ▼                                      │
┌──────────────────────────────┐              ┌───────────────┴──────────────┐
│       PostgreSQL DB          │              │   Heuristic Pricing Engine   │
│ (Metadata, Logs, Competitors)│              │      (Python Microservice)   │
└──────────────────────────────┘              └───────────────┬──────────────┘
                                                              │
                                            ┌─────────────────┴────────────────┐
                                            ▼                                  ▼
                                    External APIs                     PMS (Cloudbeds/Mews)
                             (PredictHQ / OpenWeather)                (Read/Write Sync)
```

---

## 2. Structural Breakdown

### Next.js BFF (Backend-for-Frontend)
* **Responsibility:** Provides the UI views, handles user session state, hides backend API keys (such as NocoBase database tokens, weather, and event credentials), and acts as a rate-limiting proxy.
* **Security Isolation:** The Next.js frontend never directly interacts with NocoBase or the external APIs. It queries Next.js Route Handlers (`/app/api/*`), which sanitize input parameters and call downstream components securely.

### NocoBase (Engine Metadata & Admin Console)
* **Responsibility:** Acts as the high-velocity database schema manager, API router, and administration panel.
* **Usage:** Our internal integration engineers use NocoBase's UI Editor mode to setup new hotels, link PMS API webhooks, configure competitor URLs, map room classifications, and inspect system audit tables.

### Heuristic Pricing Engine (Python Worker / FastAPI)
* **Responsibility:** Computes rates using strict mathematical formulations, processes large payloads from environmental endpoints, and pushes the final calculations to NocoBase and the hotel PMS.

---

## 3. Non-Functional Requirements (Enterprise Scalability)

```
                       ┌────────────────────────┐
                       │   Requests from Users  │
                       └───────────┬────────────┘
                                   │
                                   ▼
                       ┌────────────────────────┐
                       │  Cloudflare CDN Edge   │  (WAF & Static Asset Cache)
                       └───────────┬────────────┘
                                   │
                                   ▼
                       ┌────────────────────────┐
                       │  Next.js BFF Container │  (Stateless, Cloud Run Autoscaling)
                       └───────────┬────────────┘
                                   │
                                   ├─────────────────────────────┐
                    (Cache Hit)    │ (Cache Miss)                │
                         ┌─────────▼─────────┐                   ▼
                         │    Redis Cluster  │         ┌───────────────────┐
                         │   (Shared Cache)  │         │ NocoBase Backend  │
                         └───────────────────┘         └─────────┬─────────┘
                                                                 │
                                                                 ▼
                                                       ┌───────────────────┐
                                                       │ PostgreSQL Master │
                                                       │  (with pgBouncer) │
                                                       └───────────────────┘
```

### Performance
* **BFF Gateway Latency:** Must process and respond to API requests within $200\text{ ms}$ on a warm cache hit.
* **Concurrency:** The calculation worker must parse environmental calculations across all clients asynchronously, utilizing connection pooling (via `pgBouncer`) to the PostgreSQL database instance.

### Scalability
* **State Separation:** The Next.js BFF and NocoBase services must remain completely stateless to allow horizontal scaling inside container systems (ECS/Cloud Run).
* **Persistence Isolation:** Persistent states (such as competitor arrays, pricing rules, logs) must reside solely within the PostgreSQL Database and Redis instances.

### Reliability & Fallbacks
* **API Outage Resilience:** If OpenWeatherMap, PredictHQ, or scraping APIs fail, their respective modifiers fallback immediately to $0.00$.
* **PMS Connection Loss:** If writing to the PMS fails after 3 retries (using exponential backoff), the system alerts the hoteliers via Webhook notifications, locks the local interface status, and stops autonomous rate changes until communication is verified.
