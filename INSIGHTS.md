# INSIGHTS.md

Three things I found in the data by using the tool.

---

## 1. AmbroseValley has a kill funnel — 52% of kills happen in one zone

**What I saw**

When I turned on the kill heatmap for AmbroseValley across all matches, one zone in the center-left of the map was clearly dominant. Not a gradual hotspot — a single concentrated cluster. I enabled the zone coverage grid to confirm: the same area had the highest movement density on the entire map.

**The data**

Dividing AmbroseValley into an 8×8 grid, the top kill zone accounts for **52% of all kills** across all matches. The next three zones combined account for 30%. The remaining 60 cells share 18%.

The loot centroid sits at approximately (−12, +56) world units. The kill centroid is at (−6, +13). They're **43 world units apart** — players loot in one area then consistently travel south to fight.

**What it means for level design**

Players aren't choosing to fight there. They're being directed there — by the road layout, terrain, or the only viable path between two high-loot areas. This is either a deliberate choke point that's working, or an unintentional bottleneck making matches feel repetitive.

**Action items**
- Cross-reference kill cluster coordinates (~−6, +13) with the level design doc. Is there a named feature there?
- If unintentional: open an alternate route through center-right to distribute combat across the map
- **Metric to watch:** No single 8×8 zone should account for more than 30% of kills on a balanced map

---

## 2. Lockdown's southern half has zero player traffic across all matches

**What I saw**

I selected Lockdown and enabled the zone coverage grid. The entire bottom half of the map was red — zero visits across all 4 matches. The top half was active. I looked at the minimap: the unvisited bottom half contains two named zones with clear level design work — **Gas Station** and **Engineer's Quarters**.

**The data**

- Top half of map: **97% of all position events**
- Bottom half: **3%** (edge cases, not deliberate exploration)
- Kill events in bottom half: **0**
- Loot pickups in bottom half: **0**

All 33 loot pickups on Lockdown cluster in a 3-cell band in the upper center. Players never have a reason to go south.

**What it means for level design**

Two fully built named zones contributing zero gameplay. Either the storm is consistently pushing players away from those areas before they can reach them, or there's no loot or objective south of center to make the journey worth the risk.

**Action items**
- Check storm direction on Lockdown — if it always pushes north, players will avoid going south late in the match
- Add high-value loot spawns at Gas Station and Engineer's Quarters
- **Metric to watch:** Zone visit rate — % of matches where at least one player enters each named zone. Target: above 60%. Current rate for Gas Station and Engineer's Quarters: ~0%

---

## 3. Bots and humans explore completely different parts of the map — bot sessions can't be used for design testing

**What I saw**

I filtered to bot-only matches on AmbroseValley and turned on the death heatmap. Bot deaths clustered in a tight zone around (0–50, −100–0) — the same coordinates in every bot match. I then switched to human-only matches. Human deaths were spread across four different quadrants. The tool's live insights panel flagged a high centroid gap between bot and human movement patterns.

**The data**

- **Bot-only match (9 bots, 6.3 min):** 9 deaths — a rate of 1.4 deaths per minute
- **Human-only matches (avg across 9 sessions):** 0.4 deaths per match — roughly 0.05 per minute
- **Death rate ratio:** Bots die ~28× more often than humans, in the same locations every time

Bot deaths cluster within a ~50 unit radius. Human deaths are distributed: (33, +8), (87, −78), (55, +226), (−111, −39) across different parts of the map.

**What it means for level design**

The bot AI has a pathfinding trap somewhere in the center band — a wall, cliff, or narrow corridor where bots consistently make bad routing decisions. This means two things:

1. **Bot matches are not reliable proxies for human behavior.** If the team is using bot sessions to test map balance before real players arrive, the results are misleading. Bots cluster where humans don't and avoid areas humans actively use.

2. **The geometry causing bot deaths may also affect human players** — it's just that humans adapt faster and the issue is harder to see. Worth investigating even if human players haven't flagged it yet.

**Action items**
- Separate bot and human data in all design analysis — never aggregate them
- Investigate geometry at approximately (10, −30) on AmbroseValley: is there a dead-end or visibility disadvantage there?
- **Metric to watch:** Bot/human spatial divergence — mean distance between bot and human movement centroids. Above 100 world units = bots are not simulating real players. Exclude those sessions from design telemetry.
