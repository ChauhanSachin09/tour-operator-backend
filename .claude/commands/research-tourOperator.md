Research tour package price comparison for one or more cities. If cities are provided as $ARGUMENTS, use those; otherwise default to a curated mix of popular Indian and international destinations (Goa, Kerala, Rajasthan, Manali, Andaman, Paris, Bali, Dubai).

## Instructions

You are a tour package research assistant. Use the WebSearch tool to gather current, real-world pricing and package data for each city, then deliver a structured comparison.

### Detecting Indian vs. International cities

Before searching, classify each city as **Indian** or **International**:

- **Indian destinations** include (but are not limited to): Goa, Kerala, Manali, Shimla, Ooty, Coorg, Munnar, Darjeeling, Leh, Ladakh, Andaman, Rajasthan, Jaisalmer, Jaipur, Udaipur, Agra, Varanasi, Rishikesh, Mysore, Hampi, Kodaikanal, Spiti, Nainital, Mussoorie, Jim Corbett, Ranthambore, Mahabaleshwar, Lonavala, Pondicherry, Amritsar, Kochi, Hyderabad, Kolkata, Mumbai, Delhi, Bangalore, Chennai.
- Everything else is treated as **International**.

### Search queries per city type

**Indian city:**
- `"[city] tour package price 2025 per person"`
- `"[city] holiday package INR inclusions 2025"`
- `"best tour packages [city] India cost"`

**International city:**
- `"[city] tour package price 2025 2026 inclusions"`
- `"[city] holiday package cost per person USD"`

### For each city extract:
1. Price range in the **appropriate currency** — INR for Indian destinations, USD for international (show both if available)
2. Budget / mid-range / luxury tiers
3. Typical inclusions, duration, best travel season, and visa/permit requirements

### Output format

Present findings as:

---

## Tour Package Price Comparison — [Cities]

| City | Type | Budget (per person) | Mid-Range | Luxury | Duration | Inclusions | Best Season |
|------|------|---------------------|-----------|--------|----------|------------|-------------|
| ...  | Indian / Intl | ... | ...  | ...    | ...      | ...        | ...         |

> Prices for Indian destinations are in INR; international destinations in USD.

### City-by-City Breakdown

For each city provide:
- **Price tiers** with ranges in the appropriate currency (INR / USD)
- **What's typically included** (flights/trains, hotel, transfers, meals, excursions)
- **What's usually excluded** (visa fees, travel insurance, adventure charges, personal expenses)
- **Permit requirements** — note any special permits needed (e.g., Ladakh inner-line permit, Andaman restricted area permit)
- **Best season to visit** and why
- **Value verdict** (1-sentence summary of who this destination suits best)

### Summary & Recommendation

End with a 3-5 sentence overall recommendation comparing the destinations on value-for-money, crowd levels, and experience type (beach, culture, adventure, luxury, hill station, wildlife).

---

Always cite the sources (website names) where you found pricing data. If live search results are unavailable, clearly state estimates are approximate and advise the user to verify with a travel agent or booking platform such as MakeMyTrip, Cleartrip, Thomas Cook India, or Cox & Kings.

---

## After presenting results — update content.json

Once the comparison output is complete, update `data/content.json` in the project with the researched data.

### Steps

1. **Read** the current `data/content.json` to get existing entries and the `contact` field.
2. **Merge** — for each researched city, create or update its entry in the `destinations` array. Do NOT remove cities that are already in the file and were not part of this research run.
3. **Write** the updated JSON back to `data/content.json`.

### Entry format for each city

```json
{
  "name": "<City Name>",
  "price": "<mid-range price per person e.g. ₹15,000 – ₹25,000 / $800 – $1,500>",
  "contact": "<name of the primary booking platform found in search results e.g. MakeMyTrip, Yatra, TravelTriangle, Thomas Cook India, Expedia, Orbitz, Travelocity>"
}
```

Use the **mid-range price tier** as the representative `price` value (most useful for customers comparing options).

For Indian cities use INR (e.g. `"₹15,000 – ₹25,000"`); for international cities use USD (e.g. `"$800 – $1,500"`).

For the `contact` field, use the **name of the most prominent booking website** that appeared in the search results for that city — do NOT use a phone number or WhatsApp URL. Examples:
- Indian cities → MakeMyTrip, Yatra, TravelTriangle, Thomas Cook India, Cleartrip, SOTC
- International cities → Expedia, Orbitz, Travelocity, TourRadar, Booking.com

### Final content.json shape

```json
{
  "destinations": [
    { "name": "City A", "price": "₹X – ₹Y", "contact": "<contact>" },
    { "name": "City B", "price": "$X – $Y", "contact": "<contact>" }
  ],
  "contact": "<preserve existing value>"
}
```

After writing, confirm to the user: `content.json updated with [list of cities added/updated].`

---

## Final step — regenerate the dashboard

After `content.json` is saved, update the live dashboard by following these steps:

1. **Read** `src/main/resources/static/dashboard.html`.
2. **Replace** the `DESTINATIONS` array literal (between `const DESTINATIONS = [` and its closing `];`) with the full, updated destinations array from the `content.json` you just wrote, formatted as compact JSON — one object per line:
   ```js
   // Auto-injected by /research-tourOperator — do not edit manually
   const DESTINATIONS = [
     {"name":"City","price":"₹X – ₹Y","contact":"Platform"},
     ...
   ];
   ```
3. **Write** the updated file back to `src/main/resources/static/dashboard.html`.
4. Confirm: `Dashboard updated — X destinations now shown (Y Indian, Z International). View at http://localhost:8080/dashboard.html`

Do NOT change any HTML, CSS, or JS outside the `DESTINATIONS` array block.
