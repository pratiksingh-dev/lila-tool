# Architecture

## What I built

A static web tool that lets level designers explore player behavior on LILA BLACK maps — no server, no setup, just open a URL and the data is there.

---

## Tech stack

| Layer | Technology | Why |
|---|---|---|
| Data pipeline | Python · pandas · pyarrow | Parquet files can't be read in a browser. One script converts all files to JSON once — moving that cost to deploy time, not user time. |
| Frontend | Vanilla HTML + JavaScript | No build step, no framework, no dependencies to break. Opens by dragging into a browser. Zero setup for whoever evaluates it. |
| Rendering | HTML5 Canvas API | 89,000 events as SVG DOM nodes would freeze the browser. Canvas draws pixels directly and renders the full dataset in under 100ms. |
| Heatmaps | heatmap.js v2.0.5 via cdnjs | Loaded from CDN at runtime — not bundled in the repo. One script tag, zero config. Requires internet for heatmap overlay. |
| Hosting | Vercel (static) | Connected to GitHub repo. Every push auto-deploys. No server runtime, no downtime, global CDN. |

---

## How data flows

```
.nakama-0 parquet files  (one file = one player in one match)
        ↓
scripts/process_data.py  — run once locally
  1.  Glob all .nakama-0 files recursively across all date folders
  2.  Skip 0-byte files  (one exists in the dataset — pyarrow crashes on empty files)
  3.  Read with pyarrow, decode event bytes  →  UTF-8 string
  4.  Detect bots: /^\d+$/ on user_id  (numeric = bot, UUID = human)
  5.  Normalize timestamps per match: ts_rel = ts − min(ts)
  6.  Apply coordinate formula  →  store u, v as normalized 0–1 floats
  7.  Output per-map JSON files + match index
        ↓
public/data/
  matches.json                  796 matches, metadata only
  events_AmbroseValley.json     61,013 events
  events_GrandRift.json          6,853 events
  events_Lockdown.json          21,238 events
        ↓
Vercel CDN  →  browser
  - Fetches matches.json on load  →  populates all dropdowns
  - Lazy-fetches map JSON only when that map is selected
  - All filtering runs in memory — no re-fetch on filter change
  - Canvas re-renders on every interaction: filter, scrub, resize
  - heatmap.js fetched from cdnjs for density overlay
```

---

## Coordinate mapping

The README provides exact per-map configuration:

| Map | Scale | Origin X | Origin Z |
|---|---|---|---|
| AmbroseValley | 900 | −370 | −473 |
| GrandRift | 581 | −290 | −290 |
| Lockdown | 1000 | −500 | −500 |

```python
# Python pipeline — computed once, stored in JSON as u, v
u = (x - origin_x) / scale          # normalized 0–1 horizontal
v = (z - origin_z) / scale          # normalized 0–1 vertical

# JavaScript frontend — applied at render time
pixel_x = u * canvas_width
pixel_y = (1 - v) * canvas_height   # y-flip: image origin is top-left
```

**Why store u, v and not pixels?** The frontend multiplies by the current canvas size at render time — so the map renders correctly at any screen resolution without recalculation.

**Why the y-flip?** Game world coordinates increase upward (3D convention). Screen coordinates increase downward. Without inverting `v`, every event renders on the wrong half of the map.

**Validation:** Sampled 200 events per map and checked each computed pixel against the minimap image. 100% of events land on actual map terrain — zero in the black border region.

**Image size note:** The README documents minimaps as 1024×1024px. Actual files are 2000×2000px. Because the formula outputs normalized UV coordinates, image dimensions have zero effect on accuracy — the dot lands at the same relative position regardless of size.

---

## Assumptions

| What I found | How I handled it |
|---|---|
| `event` column stored as bytes: `b'Position'` | Decoded with `.decode('utf-8')` in pipeline |
| Timestamps are match-relative ms, not wall-clock | Normalized per match: `ts_rel = ts − min(ts)`. Sort by ts_rel to reconstruct timeline. |
| One 0-byte file in the dataset | `os.path.getsize()` check before read — skip and continue |
| Only Feb 14 provided (not all 5 days) | Pipeline handles any date range dynamically. Other days load automatically when present. |
| `Kill` / `Killed` events absent from Feb 14 | All 8 event types handled in code. Render automatically with the full dataset. |
| Minimap images are 2000px, README says 1024px | UV normalization is size-independent. Documented and confirmed with validation. |

---

## Trade-offs

| Decision | What I chose | What I gave up |
|---|---|---|
| Static JSON vs. live API | Static — no runtime cost, instant loads, no downtime | Must re-run pipeline manually when new match data arrives |
| Per-map files vs. one combined | Per-map lazy loading — only fetch what's needed | Three separate files to manage; each new map needs a new file |
| Canvas vs. SVG | Canvas — 89k events with no DOM freeze | Tooltip hit-testing built manually; no native interactivity |
| Vanilla JS vs. React | No build step, opens anywhere, zero setup | Less structured state management |
| CDN for heatmap.js | Zero config, not bundled in repo | Heatmap overlay requires internet — won't render offline |
| Aggregate timeline | Shows cross-match density patterns | Events from different matches appear simultaneously — not a perfect per-match replay |

---

## What I'd do with more time

- **Named zone overlays** — Lockdown's minimap has labeled zones (Mine Pit, Gas Station, etc.). Clickable polygon boundaries with per-zone K/D/loot stats would let designers answer design questions directly on the map.
- **Day-over-day trend chart** — a chart showing kill density or zone coverage shifting across Feb 10–14. Lets designers spot the impact of a balance change the day after it shipped.
- **Bot divergence score** — a single metric: mean distance between bot and human movement centroids per map. Above threshold → automatically flag bot sessions as unreliable for design testing.
- **Bundle heatmap.js locally** — remove the CDN dependency so the tool works fully offline.
- **Automated pipeline** — GitHub Action running `process_data.py` on a schedule, committing updated JSON, triggering Vercel redeploy. Currently requires a manual step.
