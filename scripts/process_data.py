"""
LILA BLACK — Player Journey Data Pipeline
==========================================
Reads all .nakama-0 parquet files, applies coordinate mapping per README,
detects bots, normalizes timestamps, outputs per-map JSON for the frontend.

Usage:
    python scripts/process_data.py --input ./player_data --output ./public/data

Coordinate formula (from README):
    u = (x - origin_x) / scale
    v = (z - origin_z) / scale
    pixel_x = u * IMG_SIZE
    pixel_y = (1 - v) * IMG_SIZE   <- y-flip: image origin is top-left
"""

import pandas as pd
import glob
import os
import re
import json
import argparse

MAP_CONFIG = {
    "AmbroseValley": {"scale": 900,  "origin_x": -370, "origin_z": -473},
    "GrandRift":     {"scale": 581,  "origin_x": -290, "origin_z": -290},
    "Lockdown":      {"scale": 1000, "origin_x": -500, "origin_z": -500},
}

def is_bot(user_id):
    return bool(re.match(r"^\d+$", str(user_id).strip()))

def decode_event(val):
    if isinstance(val, bytes):
        return val.decode("utf-8")
    return str(val)

def load_all_files(input_dir):
    pattern = os.path.join(input_dir, "**", "*.nakama-0")
    files = glob.glob(pattern, recursive=True)
    print(f"Found {len(files)} files")
    frames = []
    skipped = 0
    for f in files:
        if os.path.getsize(f) == 0:
            skipped += 1
            continue
        try:
            df = pd.read_parquet(f)
            parts = f.replace("\\", "/").split("/")
            df["date"] = next((p for p in parts if p.startswith("February_")), "unknown")
            frames.append(df)
        except Exception as e:
            print(f"  Skipping {os.path.basename(f)}: {e}")
            skipped += 1
    print(f"Loaded {len(frames)} files, skipped {skipped}")
    if not frames:
        raise ValueError("No data loaded — check input path")
    return pd.concat(frames, ignore_index=True)

def process(df):
    df = df.copy()
    df["event"] = df["event"].apply(decode_event)
    df["is_bot"] = df["user_id"].apply(is_bot)
    df["ts_ms"] = df["ts"].astype("int64")
    match_min_ts = df.groupby("match_id")["ts_ms"].transform("min")
    df["ts_rel"] = df["ts_ms"] - match_min_ts
    df["u"] = None
    df["v"] = None
    for map_id, cfg in MAP_CONFIG.items():
        mask = df["map_id"] == map_id
        if mask.sum() == 0:
            continue
        df.loc[mask, "u"] = ((df.loc[mask, "x"] - cfg["origin_x"]) / cfg["scale"]).round(5)
        df.loc[mask, "v"] = ((df.loc[mask, "z"] - cfg["origin_z"]) / cfg["scale"]).round(5)
    return df

def build_match_index(df):
    matches = []
    for mid, grp in df.groupby("match_id"):
        humans = grp[~grp["is_bot"]]["user_id"].nunique()
        bots = grp[grp["is_bot"]]["user_id"].nunique()
        duration_ms = int(grp["ts_rel"].max())
        match_type = "mixed" if humans > 0 and bots > 0 else "human_only" if humans > 0 else "bot_only"
        ev = grp["event"].value_counts().to_dict()
        matches.append({
            "match_id": str(mid),
            "map_id": str(grp["map_id"].iloc[0]),
            "date": str(grp["date"].iloc[0]),
            "humans": int(humans),
            "bots": int(bots),
            "duration_ms": duration_ms,
            "match_type": match_type,
            "total_events": int(len(grp)),
            "kills": int(ev.get("BotKill", 0) + ev.get("Kill", 0)),
            "deaths": int(ev.get("BotKilled", 0) + ev.get("Killed", 0)),
            "loot": int(ev.get("Loot", 0)),
            "storm_deaths": int(ev.get("KilledByStorm", 0)),
        })
    matches.sort(key=lambda x: (x["map_id"], x["date"], x["match_id"]))
    return matches

def serialize_events(df):
    events = []
    for _, row in df.iterrows():
        u, v = row.get("u"), row.get("v")
        if u is None or v is None:
            continue
        events.append({
            "user_id": str(row["user_id"]),
            "match_id": str(row["match_id"]),
            "map_id": str(row["map_id"]),
            "u": round(float(u), 5),
            "v": round(float(v), 5),
            "y": round(float(row["y"]), 2),
            "ts_rel": int(row["ts_rel"]),
            "event": str(row["event"]),
            "is_bot": bool(row["is_bot"]),
            "date": str(row["date"]),
        })
    return events

def main(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    print("Loading parquet files...")
    df = load_all_files(input_dir)
    print(f"Total rows: {len(df)}")
    print("Processing...")
    df = process(df)
    match_index = build_match_index(df)
    with open(os.path.join(output_dir, "matches.json"), "w") as f:
        json.dump(match_index, f, separators=(",", ":"))
    print(f"Wrote matches.json ({len(match_index)} matches)")
    for map_id in df["map_id"].unique():
        events = serialize_events(df[df["map_id"] == map_id])
        filename = f"events_{map_id}.json"
        with open(os.path.join(output_dir, filename), "w") as f:
            json.dump(events, f, separators=(",", ":"))
        print(f"Wrote {filename} ({len(events)} events)")
    summary = {
        "total_events": int(len(df)),
        "total_matches": int(df["match_id"].nunique()),
        "total_human_players": int(df[~df["is_bot"]]["user_id"].nunique()),
        "total_bots": int(df[df["is_bot"]]["user_id"].nunique()),
        "maps": list(df["map_id"].unique()),
        "dates": sorted(df["date"].unique().tolist()),
        "event_types": df["event"].value_counts().to_dict(),
        "map_config": MAP_CONFIG,
    }
    with open(os.path.join(output_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="./player_data")
    parser.add_argument("--output", default="./public/data")
    args = parser.parse_args()
    main(args.input, args.output)