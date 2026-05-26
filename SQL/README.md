# 📊 Customer Acquisition Cost (CAC) Analysis Across Marketing Channels

> SQL homework — analyzing marketing funnel efficiency and CAC using BigQuery.

## Overview

This project analyzes the cost-effectiveness of three marketing channels — **Meta**, **TikTok**, and **Google** — by calculating key business metrics from raw advertising data. The analysis covers the full marketing funnel: from ad impressions through clicks and app installs to user registrations.

**Engine:** Google BigQuery  
**Source table:** `marketing_ads_raw`

## Project Structure

| File | Description |
|------|-------------|
| `cac_homework.sql` | Main SQL queries for CAC analysis (with deduplication, funnel metrics, and monthly breakdown) |
| `Lobachov_HW_Results.pdf` | Results summary with answers to business questions |
| `Lobachov_skelar_HW_SQL.pdf` | Step-by-step solution walkthrough |

🔗 [SQL Queries (Google Drive)](https://drive.google.com/file/d/1rDGpboZoobv-C2JsEi-n41DJmQaws5BO/view?usp=sharing)

---

## Methodology — Step-by-Step

### Step 1: Data Cleaning (Deduplication)

**Problem:** The source table contains multiple records (data snapshots) per ad (`ad_id`) per day, since they are updated throughout the day. Summing them directly would grossly inflate all metrics.

**Solution:** Using the `ROW_NUMBER()` window function, we keep only the latest snapshot (by `timestamp`) for each ad on each day.

**Result:** A `latest_snapshots` CTE where every ad has exactly one correct row per day.

### Step 2: Daily Metrics Calculation

**Action:** The deduplicated data is grouped by marketing channel (`source`) and date.

**Result:** Total spend, impressions, clicks, installs, and registrations for each channel on each day.

### Step 3: Global Aggregation

**Action:** All daily metrics are summed across the entire period to get the overall picture for each channel (`google`, `meta`, `tiktok`).

### Step 4: Business Metrics (Final SELECT)

At this stage, the marketing funnel efficiency is calculated:

| # | Metric | Description |
|---|--------|-------------|
| 1 | **Total Spend** | Total amount of money spent on the channel |
| 2 | **CPM** (Cost Per Mille) | Cost per 1,000 impressions |
| 3 | **CTR** (Click-Through Rate) | Percentage of impressions that resulted in clicks |
| 4 | **CR** (Conversion Rates) | Two funnel transitions: Click → Install, Install → Registration |
| 5 | **CAC** (Customer Acquisition Cost) | The key metric — cost to acquire one registered user |
| 6 | **LTV / CAC Ratio** | Bonus calculation for channel profitability assessment |

---

## Results

### Channel Performance Summary

| Source | Total Spend | CPM | CTR (%) | CR Click→Install (%) | CR Install→Reg (%) | CAC |
|--------|------------:|----:|--------:|----------------------:|--------------------:|----:|
| **Meta** | 4,992,140.64 | 14.00 | 1.20 | 39.99 | 93.98 | **3.10** |
| **TikTok** | 1,441,769.34 | 22.00 | 1.50 | 30.96 | 87.96 | **5.39** |
| **Google** | 1,519,991.83 | 50.00 | 0.98 | 36.94 | 95.94 | **14.12** |

---

## Answers to Business Questions

### 1. Which channel has the lowest CAC?

**Meta — $3.10** (vs TikTok — $5.39 and Google — $14.12).

### 2. Where are the biggest funnel losses?

The biggest drop-off occurs at the **ad click stage**. After that, the funnel narrows (fewer people reach the next step, but a higher percentage progresses):

```
Impressions → Clicks (CTR: ~1-1.5%)  ← biggest loss
    → Installs (CR: 31-40%)
        → Registrations (CR: 88-96%)
```

### 3. META spends ~3.3× more than TikTok and Google. Is this justified from a CAC perspective?

**Yes.** High spending is justified because the channel scales efficiently — Meta achieves the lowest CAC ($3.10) despite the highest total spend, indicating strong unit economics.

### 4. Bonus: LTV / CAC Ratios

Given LTV values from a prior workshop:

| Source | LTV ($) | CAC ($) | LTV / CAC |
|--------|--------:|--------:|----------:|
| **Meta** | 6.20 | 3.10 | **2.00** ✅ |
| **TikTok** | 8.50 | 5.39 | **1.58** |
| **Google** | 12.40 | 14.12 | **0.88** ⚠️ |

> An LTV/CAC ratio above 1.0 means the channel is profitable. Google is currently operating at a loss (0.88).

### 5. Bonus: Monthly CAC Breakdown

🔗 [Monthly Results (Google Drive)](https://drive.google.com/file/d/1IhS3bkx9U5zCYP_BYGAb68_eXUYMY_sS/view?usp=sharing)

**Answer:** CAC fluctuates slightly month-to-month but does not change dramatically — the channels show stable efficiency over time.

---

## SQL Query Overview

The repository contains three queries in `cac_homework.sql`:

1. **Main Query** — Full funnel analysis with CAC + LTV/CAC per channel (uses a 4-step CTE pipeline: `deduped` → `latest_snapshots` → `daily_metrics` → `channel_totals`)
2. **Bonus: Monthly Breakdown** — CAC by month per channel using `DATE_TRUNC(date, MONTH)`
3. **Validation Query** — Confirms deduplication correctness (ensures exactly 1 row per `ad_id` per `date`)
