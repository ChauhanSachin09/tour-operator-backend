# /tourOperator-dashboard

**Prompt file:** `tourOperator-dashboard.md`

Manually regenerates the live dashboard HTML from the current `data/content.json`. Use this when you've edited `content.json` directly and want the UI to catch up — without running a full research cycle.

## Usage

```
/tourOperator-dashboard
```

No arguments.

## What it does

1. Reads `data/content.json`.
2. Replaces the `DESTINATIONS` array in `src/main/resources/static/dashboard.html` with the latest data.
3. Writes the updated file back to disk.
4. Confirms: `Dashboard updated — X destinations (Y Indian, Z International).`

## Dashboard

| Detail | Value |
|--------|-------|
| File | `src/main/resources/static/dashboard.html` |
| URL (app running) | `http://localhost:8080/dashboard.html` |
| Auto-updated by | `/research-tourOperator` (runs this step automatically at the end) |

## Internally uses

`Read`, `Edit`

> You only need this command for **manual refreshes**. Every `/research-tourOperator` run already regenerates the dashboard as its final step.
