# Insights

Three things I found in the data by using the tool.

---

## Insight 1 — AmbroseValley has a kill funnel: 52% of kills happen in one zone

### What caught my eye

When I turned on the kill heatmap for AmbroseValley across all matches, one zone in the center-left of the map dominated. Not a gradual hotspot — a single concentrated cluster. I enabled the zone coverage grid to confirm: the same area had the highest movement density on the entire map.

### The data

Dividing AmbroseValley into an 8×8 grid, the top kill zone accounts for **52% of all kills** across all matches. The next three zones combined account for 30%. The remaining 60 cells share 18%.

The loot centroid sits at approximately (−12, +56) world units. The kill centroid is at (−6, +13). They're **43 world units apart** — players loot in one area then consistently travel south to fight. The tool makes this visible instantly by toggling between the loot heatmap and the kill heatmap.

### Can I draw something actionable?

Yes. This pattern tells us players aren't *choosing* to fight in that zone — something in the map's geometry is routing them there. Either a deliberate choke point that's working, or an unintentional bottleneck making matches feel repetitive.

**Metrics affected:** Kill dispersion index (standard deviation of kill coordinates), match-to-match combat predictability.

**Actionable items:**
- Cross-reference kill cluster coordinates (~−6, +13) with the level design doc. Is there a named feature — a bridge, road junction, or building entrance — at those coordinates?
- If intentional: no action needed. The choke is working.
- If unintentional: open an alternate route through center-right to distribute combat.
- Target: no single 8×8 zone should account for more than 30% of kills on a balanced map.

### Why a level designer should care

A 52% kill concentration is a structural signal. It means matches on this map are becoming predictable — players know where fights happen before they land. That predictability reduces replayability. The tool surfaces this in seconds; without it you'd need to manually aggregate hundreds of match files.

---

## Insight 2 — Lockdown's southern half has zero player traffic across all matches

### What caught my eye

I selected Lockdown and enabled the zone coverage grid. The entire bottom half of the map was red — zero visits across all 4 matches in the dataset. The top half was active. The Lockdown minimap has named zones: the unvisited bottom half contains **Gas Station** and **Engineer's Quarters** — both with visible level design work that no player is reaching.

### The data

- Top half of map: **97% of all position events**
- Bottom half: **3%** — edge cases, not deliberate exploration
- Kill events in bottom half: **0**
- Loot pickups in bottom half: **0**

All 33 loot pickups on Lockdown cluster in a 3-cell horizontal band in the upper center. Players never have a reason to move south.

### Can I draw something actionable?

Yes. Two named zones with fully built level design contributing zero gameplay value. The cause is likely one of two things: the storm consistently pushes north forcing players to extract before reaching the south, or there's no loot or objective south of center worth the risk of going there.

**Metrics affected:** Zone visit rate per named area, player extraction distribution.

**Actionable items:**
- Check storm direction on Lockdown. If it always pushes north, players will avoid the south late-game. Make storm direction variable, or place an extraction point in the south to create a reason to go there.
- Add high-value loot spawns at Gas Station and Engineer's Quarters.
- Target: zone visit rate above 60% for all named zones. Current rate for Gas Station and Engineer's Quarters: approximately 0%.

### Why a level designer should care

Two fully built areas that don't contribute to gameplay represent wasted development effort and a smaller effective playspace than the map was designed to have. Without the coverage grid overlay, this dead zone is invisible in raw telemetry — it's absence of data, which is hard to spot in a spreadsheet.

---

## Insight 3 — Bot sessions are not reliable proxies for human behavior

### What caught my eye

I filtered to bot-only matches on AmbroseValley and turned on the death heatmap. Bot deaths clustered in a tight ~50 unit radius around (0–50, −100–0) — the same coordinates in every bot match. I then switched to human-only matches. Human deaths were distributed across four different quadrants. The Live Insights panel flagged a high centroid gap between bot and human movement patterns automatically.

### The data

- **Bot-only match (9 bots, 6.3 min):** 9 deaths — a rate of **1.4 deaths per minute**
- **Human-only matches (avg across 9 sessions):** 0.4 deaths per match — approximately **0.05 per minute**
- **Death rate ratio:** Bots die ~28× more often than humans, in the same map locations every time

Bot deaths cluster within a ~50 unit radius: approximately (8, −14), (−3, −24), (36, −94), (11, −13). Human deaths distribute across the map: (33, +8), (87, −78), (55, +226), (−111, −39).

### Can I draw something actionable?

Yes. Two separate problems are visible here.

**Problem 1 — Bot AI pathfinding trap:** The bot death cluster points to a specific feature of the level geometry where the AI consistently makes poor routing decisions — likely a wall, cliff, or narrow corridor creating a dead end. This is a fixable AI bug with a specific spatial location.

**Problem 2 — Invalid design testing data:** If the team is using bot match sessions to test map balance before real players arrive, those results are misleading. Bots cluster where humans don't and avoid areas humans actively use.

**Metrics affected:** Bot/human spatial divergence score, design testing validity, pathfinding error rate.

**Actionable items:**
- Separate bot and human data in all design analysis pipelines. Never aggregate them — bot behavior will skew the human signal and produce false conclusions about player routing.
- Investigate level geometry at approximately (10, −30) on AmbroseValley. Is there a dead-end, visibility disadvantage, or narrow passage that creates a pathfinding trap?
- Define a bot/human divergence threshold: if the mean distance between bot and human movement centroids exceeds 100 world units on any map, automatically flag those bot sessions as excluded from design telemetry.

### Why a level designer should care

Designers relying on bot sessions for early-stage map testing are making decisions on data that doesn't reflect how real players navigate the space. The tool makes the divergence visible in one toggle — switching between human-only and bot-only views shows the difference immediately. Without that comparison, the problem is completely hidden.
# Insights

Three things I found in the data by using the tool.

---

## Insight 1 — AmbroseValley has a kill funnel: 52% of kills happen in one zone

### What caught my eye

When I turned on the kill heatmap for AmbroseValley across all matches, one zone in the center-left of the map dominated. Not a gradual hotspot — a single concentrated cluster. I enabled the zone coverage grid to confirm: the same area had the highest movement density on the entire map.

### The data

Dividing AmbroseValley into an 8×8 grid, the top kill zone accounts for **52% of all kills** across all matches. The next three zones combined account for 30%. The remaining 60 cells share 18%.

The loot centroid sits at approximately (−12, +56) world units. The kill centroid is at (−6, +13). They're **43 world units apart** — players loot in one area then consistently travel south to fight. The tool makes this visible instantly by toggling between the loot heatmap and the kill heatmap.

### Can I draw something actionable?

Yes. This pattern tells us players aren't *choosing* to fight in that zone — something in the map's geometry is routing them there. Either a deliberate choke point that's working, or an unintentional bottleneck making matches feel repetitive.

**Metrics affected:** Kill dispersion index (standard deviation of kill coordinates), match-to-match combat predictability.

**Actionable items:**
- Cross-reference kill cluster coordinates (~−6, +13) with the level design doc. Is there a named feature — a bridge, road junction, or building entrance — at those coordinates?
- If intentional: no action needed. The choke is working.
- If unintentional: open an alternate route through center-right to distribute combat.
- Target: no single 8×8 zone should account for more than 30% of kills on a balanced map.

### Why a level designer should care

A 52% kill concentration is a structural signal. It means matches on this map are becoming predictable — players know where fights happen before they land. That predictability reduces replayability. The tool surfaces this in seconds; without it you'd need to manually aggregate hundreds of match files.

---

## Insight 2 — Lockdown's southern half has zero player traffic across all matches

### What caught my eye

I selected Lockdown and enabled the zone coverage grid. The entire bottom half of the map was red — zero visits across all 4 matches in the dataset. The top half was active. The Lockdown minimap has named zones: the unvisited bottom half contains **Gas Station** and **Engineer's Quarters** — both with visible level design work that no player is reaching.

### The data

- Top half of map: **97% of all position events**
- Bottom half: **3%** — edge cases, not deliberate exploration
- Kill events in bottom half: **0**
- Loot pickups in bottom half: **0**

All 33 loot pickups on Lockdown cluster in a 3-cell horizontal band in the upper center. Players never have a reason to move south.

### Can I draw something actionable?

Yes. Two named zones with fully built level design contributing zero gameplay value. The cause is likely one of two things: the storm consistently pushes north forcing players to extract before reaching the south, or there's no loot or objective south of center worth the risk of going there.

**Metrics affected:** Zone visit rate per named area, player extraction distribution.

**Actionable items:**
- Check storm direction on Lockdown. If it always pushes north, players will avoid the south late-game. Make storm direction variable, or place an extraction point in the south to create a reason to go there.
- Add high-value loot spawns at Gas Station and Engineer's Quarters.
- Target: zone visit rate above 60% for all named zones. Current rate for Gas Station and Engineer's Quarters: approximately 0%.

### Why a level designer should care

Two fully built areas that don't contribute to gameplay represent wasted development effort and a smaller effective playspace than the map was designed to have. Without the coverage grid overlay, this dead zone is invisible in raw telemetry — it's absence of data, which is hard to spot in a spreadsheet.

---

## Insight 3 — Bot sessions are not reliable proxies for human behavior

### What caught my eye

I filtered to bot-only matches on AmbroseValley and turned on the death heatmap. Bot deaths clustered in a tight ~50 unit radius around (0–50, −100–0) — the same coordinates in every bot match. I then switched to human-only matches. Human deaths were distributed across four different quadrants. The Live Insights panel flagged a high centroid gap between bot and human movement patterns automatically.

### The data

- **Bot-only match (9 bots, 6.3 min):** 9 deaths — a rate of **1.4 deaths per minute**
- **Human-only matches (avg across 9 sessions):** 0.4 deaths per match — approximately **0.05 per minute**
- **Death rate ratio:** Bots die ~28× more often than humans, in the same map locations every time

Bot deaths cluster within a ~50 unit radius: approximately (8, −14), (−3, −24), (36, −94), (11, −13). Human deaths distribute across the map: (33, +8), (87, −78), (55, +226), (−111, −39).

### Can I draw something actionable?

Yes. Two separate problems are visible here.

**Problem 1 — Bot AI pathfinding trap:** The bot death cluster points to a specific feature of the level geometry where the AI consistently makes poor routing decisions — likely a wall, cliff, or narrow corridor creating a dead end. This is a fixable AI bug with a specific spatial location.

**Problem 2 — Invalid design testing data:** If the team is using bot match sessions to test map balance before real players arrive, those results are misleading. Bots cluster where humans don't and avoid areas humans actively use.

**Metrics affected:** Bot/human spatial divergence score, design testing validity, pathfinding error rate.

**Actionable items:**
- Separate bot and human data in all design analysis pipelines. Never aggregate them — bot behavior will skew the human signal and produce false conclusions about player routing.
- Investigate level geometry at approximately (10, −30) on AmbroseValley. Is there a dead-end, visibility disadvantage, or narrow passage that creates a pathfinding trap?
- Define a bot/human divergence threshold: if the mean distance between bot and human movement centroids exceeds 100 world units on any map, automatically flag those bot sessions as excluded from design telemetry.

### Why a level designer should care

Designers relying on bot sessions for early-stage map testing are making decisions on data that doesn't reflect how real players navigate the space. The tool makes the divergence visible in one toggle — switching between human-only and bot-only views shows the difference immediately. Without that comparison, the problem is completely hidden.
