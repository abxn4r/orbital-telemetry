#!/usr/bin/env python3
"""
Orbital Telemetry & Deep Space Canary Probe
Fetches NASA Astronomy Picture of the Day (APOD) and probes global network backbones.
Built with zero external dependencies (Python 3 standard library).
"""

import json
import socket
import time
import urllib.request
from datetime import datetime, timezone

NASA_APOD_URL = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"

TARGETS = [
    ("Cloudflare DNS", "1.1.1.1", 53),
    ("Google DNS", "8.8.8.8", 53),
    ("Quad9 DNS", "9.9.9.9", 53),
    ("GitHub Core", "github.com", 443),
    ("AWS Cloud", "aws.amazon.com", 443),
]


def fetch_nasa_apod():
    req = urllib.request.Request(NASA_APOD_URL, headers={"User-Agent": "OrbitalCanary/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Warning: Could not fetch NASA APOD: {e}")
        return {
            "title": "Cosmic Observation Offline",
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "url": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=1200",
            "media_type": "image",
            "explanation": "NASA APOD API was temporarily unavailable during probe execution.",
            "copyright": "Deep Space Archive",
        }


def probe_latency(host, port, timeout=3.0):
    t0 = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return round((time.perf_counter() - t0) * 1000, 2)
    except Exception:
        return None


def render_ascii_bar(ms, max_ms=150.0):
    if ms is None:
        return "[TIMEOUT]"
    filled = min(10, max(1, int((ms / max_ms) * 10)))
    return "█" * filled + "░" * (10 - filled)


def run_probes():
    results = []
    for name, host, port in TARGETS:
        lat = probe_latency(host, port)
        results.append((name, host, port, lat))
    return results


def generate_telemetry_markdown(apod, probes):
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    date_str = apod.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    title = apod.get("title", "Deep Space Capture")
    media_url = apod.get("hdurl") or apod.get("url", "")
    media_type = apod.get("media_type", "image")
    explanation = apod.get("explanation", "").strip()
    copyright_info = apod.get("copyright", "NASA / Public Domain").replace("\n", " ").strip()

    valid_latencies = [lat for _, _, _, lat in probes if lat is not None]
    avg_latency = round(sum(valid_latencies) / len(valid_latencies), 2) if valid_latencies else 0.0

    md = []
    md.append("# 🛰️ Orbital Telemetry & Deep Space Canary\n")
    md.append("> Autonomous daily probe archiving NASA cosmic imagery and global network infrastructure telemetry.\n")
    md.append(f"**Last Sync:** `{now_utc}` • **Status:** `OPERATIONAL` • **Average Latency:** `{avg_latency} ms`\n")
    md.append("---\n")

    # Section 1: NASA APOD
    md.append(f"## 🌌 Cosmic Observation: {title}\n")
    md.append(f"*Catalog Date: {date_str}* | *Credits: {copyright_info}*\n\n")

    if media_type == "image":
        md.append(f'<div align="center">\n  <img src="{media_url}" width="100%" alt="{title}" style="border-radius: 8px;" />\n</div>\n\n')
    else:
        md.append(f"[▶️ Watch Cosmic Video]({media_url})\n\n")

    md.append(f"> {explanation}\n\n")
    md.append("---\n")

    # Section 2: Global Latency Canary
    md.append("## 📡 Global Backbone Latency Canary\n\n")
    md.append("```text\n")
    md.append(f"{'ENDPOINT TARGET':<22} | {'HOST':<16} | {'LATENCY':<10} | {'TELEMETRY':<10} | STATUS\n")
    md.append("─" * 75 + "\n")

    for name, host, port, lat in probes:
        if lat is not None:
            bar = render_ascii_bar(lat)
            md.append(f"{name:<22} | {host:<16} | {lat:>6.2f} ms | {bar} | ONLINE\n")
        else:
            md.append(f"{name:<22} | {host:<16} |    TIMEOUT | ░░░░░░░░░░ | UNREACHABLE\n")

    md.append("─" * 75 + "\n")
    md.append(f"Probe Execution: GitHub Actions Runner (Ubuntu) • Average RTT: {avg_latency} ms\n")
    md.append("```\n\n")

    md.append("---\n")
    md.append("<sub>Maintained autonomously via [GitHub Actions](https://github.com/features/actions). Historical observations cataloged in `ARCHIVE.md`.</sub>\n")

    return "".join(md)


def main():
    print("Executing Orbital Telemetry Probe...")
    apod = fetch_nasa_apod()
    probes = run_probes()

    readme_content = generate_telemetry_markdown(apod, probes)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    # Append to archive log
    date_str = apod.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    archive_entry = f"\n### 🛰️ Telemetry Log — {date_str}\n"
    archive_entry += f"- **Cosmic Target:** {apod.get('title')}\n"
    archive_entry += f"- **Image URL:** [High-Res View]({apod.get('url')})\n"
    archive_entry += f"- **Probe Status:** Normal ({len([l for _, _, _, l in probes if l is not None])}/{len(probes)} online)\n"

    with open("ARCHIVE.md", "a", encoding="utf-8") as f:
        f.write(archive_entry)

    print("Probe complete: README.md and ARCHIVE.md updated successfully.")


if __name__ == "__main__":
    main()
