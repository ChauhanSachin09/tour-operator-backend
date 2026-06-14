# /research-tourOperator

**Prompt file:** `research-tourOperator.md`

Researches real-time tour package prices for one or more cities, delivers a structured comparison, and automatically updates both `data/content.json` and the live dashboard.

## Usage

```
/research-tourOperator                          # defaults to Goa, Kerala, Rajasthan, Manali, Andaman, Paris, Bali, Dubai
/research-tourOperator Paris Bali
/research-tourOperator Pune Mumbai Jaipur
```

## What it does

1. Classifies each city as **Indian** or **International** and picks the right search queries and currency (INR / USD).
2. Runs live `WebSearch` queries for each city to pull current budget / mid-range / luxury price tiers.
3. Renders a Markdown comparison table + city-by-city breakdown + summary recommendation.
4. **Updates `data/content.json`** — merges researched cities (name, mid-range price, booking platform) without removing existing entries.
5. **Regenerates `src/main/resources/static/dashboard.html`** — replaces the `DESTINATIONS` array so the UI reflects the latest data.

## Outputs

| Artifact | Location |
|----------|----------|
| Price comparison table | Chat output |
| Destination data | `data/content.json` |
| Live dashboard | `src/main/resources/static/dashboard.html` → `http://localhost:8080/dashboard.html` |

## Entry written per city

```json
{ "name": "Goa", "price": "₹20,000 – ₹35,000", "contact": "MakeMyTrip" }
```

- `price` — mid-range tier (INR for Indian, USD for International)
- `contact` — most prominent booking platform found in search results

## Internally uses

`WebSearch`, `Read`, `Write`
