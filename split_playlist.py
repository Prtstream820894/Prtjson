import os
import re
import json
from urllib.parse import quote

# Configuration
INPUT_FILE = "playlist.m3u"
OUTPUT_DIR = "playlists"
JSON_OUTPUT = "playlists.json"
# Apna GitHub raw base URL yahan daal dena (repo name aur branch ke hisab se)
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Prtstream820894/NEW_REPO_NAME/main/playlists/"

def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name).strip('_')

def process_playlist():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} nahi mili!")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # M3U entries parse karna
    lines = content.splitlines()
    groups = {}
    
    current_header = ""
    for line in lines:
        if line.startswith("#EXTINF"):
            current_header = line
            # group-title dhundhna
            match = re.search(r'group-title="(.*?)"', line, re.IGNORECASE)
            if match:
                group_title = match.group(1).strip()
            else:
                group_title = "Uncategorized"
            
            if group_title not in groups:
                groups[group_title] = ["#EXTM3U\n"]
        elif current_header and not line.startswith("#"):
            # URL line
            groups[group_title].append(f"{current_header}\n{line}\n")
            current_header = ""

    json_data = []

    for group_title, entries in groups.items():
        filename = sanitize_filename(group_title) + ".m3u"
        file_path = os.path.join(OUTPUT_DIR, filename)
        
        # Alag playlist file save karna
        with open(file_path, "w", encoding="utf-8") as out_f:
            out_f.writelines(entries)
            
        raw_link = f"{GITHUB_RAW_BASE}{quote(filename)}"
        json_data.append({
            "group_title": group_title,
            "playlist_url": raw_link
        })

    # JSON index file save karna
    with open(JSON_OUTPUT, "w", encoding="utf-8") as json_f:
        json.dump(json_data, json_f, indent=4, ensure_ascii=False)
    
    print("Playlist splitting successfully complete ho gayi!")

if __name__ == "__main__":
    process_playlist()
