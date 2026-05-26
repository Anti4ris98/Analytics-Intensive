# 📊 Marketing Performance Dashboard

A Tableau dashboard for **Monthly Marketing Performance** reporting with actionable budget recommendations across channels and geographies.

> **Dashboard walkthrough (video):** [Google Drive](https://drive.google.com/file/d/1A7G4TRC0HP6K517gHBlufVFeIfNaltqn/view?usp=sharing)

---

## Project Files

| File | Description |
|------|-------------|
| `Book1.twb` | Tableau workbook |
| `Marketing Performance Review.pdf` | Dashboard description & budget recommendations |
| `homework_brief.docx` | Assignment brief |
| `spend.csv` | Marketing spend data by channel |
| `users.csv` | User registration and revenue data |

---

## Dashboard Structure

The **Marketing Performance Dashboard** is built in Tableau and consists of three layers:

| Layer | Content |
|-------|---------|
| **Top** | KPI cards with key metrics & device-level breakdowns |
| **Middle** | Trend and comparative visualizations |
| **Bottom** | Detailed geographic breakdowns |

### Interactive Elements

| Element | Description |
|---------|-------------|
| **Parameter "Month Offset"** | Select the month for analysis (October – December). The team can open the report each month and choose the desired period. |
| **Parameter "Revenue Window"** | Toggle ROAS between 7-day and 90-day windows. 7d shows quick payback; 90d shows long-term value. |
| **Filter by Channel** | Narrow the analysis to a specific channel (Meta / Google / TikTok / Email). |
| **Filter by Geo** | Narrow the analysis to a specific geography (UA / PL / DE / US / UK). |

---

## Budget Recommendations for Next Month

### Context (April 2026)

| Metric | Value |
|--------|-------|
| Total Spend | $129,964 |
| Users Acquired | 13,139 |
| Total Revenue (7d) | $17,844 |
| Overall ROAS 7d | 0.14× |
| Overall ROAS 90d | 0.31× |
| Overall CVR | 13.30% |
| Overall CAC | $9.89 |

> [!WARNING]
> Overall ROAS 7d = 0.14× means the company only returns **$0.14 per $1 spent** within the first 7 days. ROAS 90d = 0.31× is also low. Current budget allocation is inefficient.

---

### Channel Recommendations

#### 🟢 Email — Increase +40–50%

Best ROAS among all channels: **0.65×** (vs. company average of 0.14×). Highest CVR = **24.8%**, lowest CAC = **$6.02**. At a current budget of $6,039/mo the channel is clearly underfunded — only 4.6% of total spend. Propose a test increase to **~$9,000/mo** to validate scalability. Special focus on geo **UK** (ROAS 0.77×) and **US** (ROAS 0.71×).

#### 🟢 Google — Increase +15–20%

Second most efficient channel: ROAS 7d = **0.23×**, CVR = **25.9%**. Compared to the previous month, ROAS is stable (−0.3%) and CVR improved (+3.1%). Best geos: **UK** (ROAS 0.36×) and **US** (ROAS 0.32×). Recommend reallocating budget from TikTok and increasing spend to **~$39,000–40,000/mo** with a focus on UK/US.

#### 🟡 Meta — No Change (0%)

ROAS 7d = **0.11×** — below average. However, the channel is stable: MoM ROAS change +1.0%, CVR +0.4%. Delivers significant traffic volume (~3,800 users/mo). Maintain budget at **~$43,000/mo** for now, but monitor performance by geo — **US** shows the best ROAS (0.15×), **UA** the worst (0.08×).

#### 🔴 TikTok — Decrease −20–25%

Worst ROAS among all channels: **0.02×** — the company returns only $0.02 for every $1 spent. CVR = only **4.6%** (lowest). Yet TikTok receives the largest budget — $46,813/mo (36% of total spend). This is a critical imbalance. Recommend cutting to **~$35,000–37,000/mo** and redirecting freed funds to Email and Google.

---

## Assumptions

1. **Revenue Window** — Primary analysis is based on `revenue_7d`. This is an early indicator; actual user LTV may be significantly higher. `revenue_90d` provides a broader picture, but the difference between 7d and 90d ROAS is minimal (~5%).

2. **ROMI in the Heatmap** — The `romi_7d` field in the source data is pre-calculated at the row level. When aggregating in Tableau, `SUM(romi_7d)` cannot be used — it is mathematically incorrect (sum of ratios ≠ ratio of sums). Correct formula: `(SUM(total_revenue_7d) - SUM(spend)) / SUM(spend)`.

3. **Attribution Model** — The data assumes **last-click attribution**. In reality, a user may interact with multiple channels. This can understate the role of awareness channels (TikTok, Meta) and overstate the role of lower-funnel channels (Email).

4. **Email as a Channel** — Email targets users from an existing database. Therefore, its high CVR and ROAS are partly explained by a "warm" audience. Scaling Email is limited by the size of the contact base.

5. **Organic Traffic** — The data does not include an organic channel. If some conversions are organic but incorrectly attributed to a paid channel, this inflates ROAS.

6. **Last Complete Month** — April 2026 is used for analysis. May 2026 is not yet complete.

7. **Linear Scaling** — Budget increase recommendations assume that with a moderate increase (up to +50%) the channel's efficiency remains approximately the same. In practice, significant budget increases typically lead to declining ROAS (diminishing returns).

---

## Additional Observations

- **TikTok** has shown a ROAS of 0.02× consistently for 3+ months. At a budget of $47K/mo, this amounts to **~$46K in net losses every month**.
- In **October 2025**, a Meta budget test nearly doubled spend. The test failed — the audience was saturated and ROAS dropped by half.
- **UK and US** are the best-performing geos for Google (ROAS 0.36× and 0.32×) and Email (0.77× and 0.71×).
- **UA** is the weakest geo across all channels (Meta ROAS 0.08×, Google 0.09×, TikTok 0.01×). Consider reducing UA budget and reallocating to UK/US.
