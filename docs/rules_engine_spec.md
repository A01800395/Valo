# Functional Requirements: Heuristic Rules Engine Spec

## 1. Core Workflow

The Heuristic Rules Engine processes rate adjustments on a regular schedule using a deterministic rules engine. The following diagram illustrates the execution flow:

```
  Step 1: CRON Trigger (Every 4 hours)
                 │
                 ▼
  Step 2: Pull environmental data & current PMS occupancy
                 │
                 ▼
  Step 3: Execute Parametric Heuristic Equation
                 │
                 ▼
  Step 4: Check calculated rate against Safety Boundaries (Floor/Ceiling)
                 │
                 ├───────────────────────────────────────┐
                 │ PASS                                  │ FAIL
                 ▼                                       ▼
  Step 5: Write to NocoBase Audit Database               Trigger System Alert & Keep Baseline
                 │
                 ├───────────────────────────────┐
                 │                               │
                 ▼ (If Auto-Pilot)               ▼ (If Co-Pilot)
  Step 6A: Direct API Push to PMS             Step 6B: Show Notification in Next.js Dashboard
```

---

## 2. The Parametric Heuristic Rules Formula

The mathematical computation of the final rate is governed by the following equations:

\[Rate_{final} = Rate_{base} \times (1 + S_{event} + S_{occupancy} + S_{weather} + S_{competitor})\]

Where each modifier \(S\) is computed as follows:

### 1. Event Modifier (\(S_{event}\))

Triggered by event capacity (\(A\)) and proximity (\(d\) in km). If \(A > 20,000\) and \(d \le 3\):

\[S_{event} = \min\left(0.40, \frac{A}{100,000} \times \frac{1}{d}\right)\]

Otherwise:
\[S_{event} = 0.00\]

### 2. Occupancy Modifier (\(S_{occupancy}\))

Determined by PMS occupancy rate at \(D\) days prior to arrival:

* If Occupancy \(> 80\%\) and \(D \le 7\):
\[S_{occupancy} = +0.20\]

* If Occupancy \(< 30\%\) and \(D \le 3\):
\[S_{occupancy} = -0.15\]

* Otherwise:
\[S_{occupancy} = 0.00\]

### 3. Weather Modifier (\(S_{weather}\))

Based on Friday–Sunday forecast parameters:

* If forecast is clear/sunny and average temperature \(> 18^\circ\text{C}\):
\[S_{weather} = +0.10\]

* If an active heavy rain or storm warning exists:
\[S_{weather} = -0.05\]

* Otherwise:
\[S_{weather} = 0.00\]

### 4. Competitor Modifier (\(S_{competitor}\))

Triggered by comparing average competitor rates (\(P_{comp}\)) of 5 direct hotels against the base rate:

* If \(P_{comp} > 1.25 \times Rate_{base}\):
\[S_{competitor} = +0.15\]

* If \(P_{comp} < 0.85 \times Rate_{base}\):
\[S_{competitor} = -0.10\]

* Otherwise:
\[S_{competitor} = 0.00\]
