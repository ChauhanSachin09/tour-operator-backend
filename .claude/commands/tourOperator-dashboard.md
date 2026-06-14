Regenerate the TourOperator dashboard UI from the current `data/content.json`.

## Instructions

1. **Read** `data/content.json` to get the latest destinations array.

2. **Read** `src/main/resources/static/dashboard.html` to get the current dashboard file.

3. **Replace** the `DESTINATIONS` array literal inside the `<script>` block of `dashboard.html` with the up-to-date data from `content.json`. The array is clearly marked with the comment:
   ```
   // Auto-injected by /research-tourOperator — do not edit manually
   const DESTINATIONS = [ ... ];
   ```
   Replace everything between `const DESTINATIONS = [` and the closing `];` (inclusive of both lines) with the new data formatted as a compact JSON array of objects, each on its own line, e.g.:
   ```js
   const DESTINATIONS = [
     {"name":"Goa","price":"₹20,000 – ₹35,000","contact":"MakeMyTrip"},
     ...
   ];
   ```

4. **Write** the updated file back to `src/main/resources/static/dashboard.html`.

5. Confirm to the user: `Dashboard updated — X destinations now shown (Y Indian, Z International).`

## Notes

- Do NOT change any HTML, CSS, or JS outside the `DESTINATIONS` array.
- Preserve the marker comment `// Auto-injected by /research-tourOperator — do not edit manually` above the array.
- The dashboard is served by Spring Boot at `http://localhost:8080/dashboard.html` when the app is running.
