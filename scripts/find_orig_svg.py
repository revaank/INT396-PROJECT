import json
from pathlib import Path

transcript_path = Path(r"C:\Users\LENOVO\.gemini\antigravity\brain\70acda02-c1f8-4dcf-a143-049af112194d\.system_generated\logs\transcript_full.jsonl")
if transcript_path.exists():
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            if "india-map" in line and "state-shape" in line:
                obj = json.loads(line)
                content = str(obj.get("content", ""))
                idx = content.find('<svg class="india-map"')
                if idx != -1:
                    print("Found original SVG:")
                    print(content[idx:idx+1200])
                    break
