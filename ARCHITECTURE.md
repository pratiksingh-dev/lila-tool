# ARCHITECTURE.md

## What I built

A static web tool that lets level designers explore player behavior on LILA BLACK maps — no server, no setup, just open a URL and the data is there.

---

## Tech stack

| Layer | What | Why |
|---|---|---|
| Data pipeline | Python + pandas + pyarrow | Parquet files can't be read in a browser. One Python script converts them to JSON once, so the browser never has to wait for processing. |
| Frontend | Vanilla HTML + JavaScript | No build step, no framework, no dependencies to break. Opens by dragging into a browser. |
| Rendering | HTML5 Canvas | 89,000 events as SVG nodes would freeze the browser. Canvas draws pixels directly — renders the full dataset in under 100ms. |
| Heatmaps | heatmap.js (CDN) | One script tag, zero config, identical output to building it manually at 10% of the effort. |
| Hosting | Netlify (static) | No server to maintain, no downtime, loads fast from a CDN anywhere in the world. |

---

## How data flows

```
.nakama-0 parquet files (one per player per match)
        ↓
process_data.py  (run once locally)
  - reads all files with pyarrow
  - skips 0-byte files
  - decodes event bytes → UTF-8
  - detects bots: numeric user_id = bot, UUID = human
  - normalizes timestamps per match (ts_rel = ts − match_start)
  - applies coordinate formula → stores u, v (0–1 normalized)
  - outputs per-map JSON files + match index
        ↓
public/data/
  matches.json               (796 matches, metadata)
  events_AmbroseValley.json  (61k events)
  events_GrandRift.json      (7k events)
  events_Lockdown.json       (21k events)
        ↓
Netlify CDN → browser
  - loads matches.json on startup
  - lazy-fetches map JSON only when that map is selected
  - all filtering runs in memory — no re-fetching on filter changes
  - canvas re-renders on every interaction
```

---

## Coordinate mapping

The README gives exact values per map:

| Map | Scale | Origin X | Origin Z |
|---|---|---|---|
| AmbroseValley | 900 | −370 | −473 |
| GrandRift | 581 | −290 | −290 |
| Lockdown | 1000 | −500 | −500 |

```python
# Convert world (x, z) → normalized UV (0 to 1)
u = (x - origin_x) / scale
v = (z - origin_z) / scale

# Convert UV → pixel position on canvas (any size)
pixel_x = u * canvas_width
pixel_y = (1 - v) * canvas_height   # y-flip: image origin is top-left
```

The u, v values are computed once in Python and stored in the JSON. The frontend just multiplies by canvas size — so the map renders correctly at any screen resolution without any recalculation.

The y-flip on line 2 is essential. Game coordinates increase upward, screen coordinates increase downward. Without this, every event plots on the wrong half of the map.

**Validation:** I sampled 200 events per map and checked each computed pixel against the minimap image. 100% of events land on actual map terrain, not the black border.

**Note on image size:** The README says 1024×1024. The actual files are 2000×2000. Because the formula uses normalized UV coordinates, this makes no difference — the dot lands at the same relative position regardless of image dimensions.

---

## Assumptions

| Ambiguity | What I found | How I handled it |
|---|---|---|
| event column type | Stored as bytes: `b'Position'` | Decoded with `.decode('utf-8')` in the pipeline |
| Timestamps | `datetime64[ms]` but represent match-relative time, not wall-clock | Normalized per match: `ts_rel = ts − min(ts)` |
| 0-byte file | One empty file exists in the dataset | Skipped with a file size check before reading |
| Missing data | Only Feb 14 was in the provided zip | Pipeline handles any date range — other days load automatically when present |
| Missing event types | Kill/Killed (human-vs-human) absent from Feb 14 | All 8 event types handled in code; they appear automatically with the full dataset |
| Image size mismatch | README says 1024px, actual files are 2000px | UV coordinates are resolution-independent; no impact on accuracy |

---

## Trade-offs

| Decision | What I chose | What I gave up |
|---|---|---|
| Static JSON vs. live server | Static — faster, simpler, zero downtime | Can't query on demand; need to re-run pipeline for new data |
| Per-map files vs. one combined file | Per-map — only fetch the map you need | Slightly more files to manage |
| Canvas vs. SVG | Canvas — handles 89k events without freezing | Tooltip hit-testing has to be built manually |
| Vanilla JS vs. React | Vanilla — no build step, opens anywhere | Less structured state management for complex interactions |

---

## What I'd do with more time

- **Named zone overlays** — Lockdown's minimap has labeled areas (Mine Pit, Gas Station, etc.). I'd make those clickable with per-zone stats.
- **Day-over-day trend chart** — a small chart showing how kill density or zone coverage changes across Feb 10–14. Lets designers spot the impact of balance changes.
- **Bot divergence score** — a single number measuring how differently bots move compared to humans. If it's high, bot sessions shouldn't be used for design testing.
- **Automated pipeline** — a GitHub Action that runs `process_data.py` on a schedule and redeploys automatically. Currently it's a manual step.
