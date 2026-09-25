import os
import re
import json
import urllib.request
from urllib.parse import quote

# Configuration (Ab isme saari chaaron playlists ki list hai)
PLAYLIST_URLS = [
    "https://raw.githubusercontent.com/Prtstream820894/Prmovies/refs/heads/main/playlist.m3u",
    "https://divine-moon-058f.poonamchouhan076.workers.dev/",
    "",
    "https://raw.githubusercontent.com/Prtstream820894/Bazeradult/refs/heads/main/playlist.m3u"
]

OUTPUT_DIR = "playlists"
JSON_OUTPUT = "playlists.json"

GITHUB_REPO = os.getenv("GITHUB_REPOSITORY", "Prtstream820894/Prtjson")
GITHUB_REF_NAME = os.getenv("GITHUB_REF_NAME", "main")
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_REF_NAME}/{OUTPUT_DIR}/"

def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name).strip('_')

def process_playlist():
    combined_content = ""
    
    # Saari playlists ko ek-ek karke download karke combine karenge
    for url in PLAYLIST_URLS:
        print(f"Downloading: {url}")
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req) as response:
                content = response.read().decode('utf-8', errors='ignore')
                combined_content += "\n" + content
        except Exception as e:
            print(f"Error downloading {url}: {e}")

    if not combined_content.strip():
        print("Koi bhi playlist data download nahi ho paya!")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    lines = combined_content.splitlines()
    groups = {}
    
    current_header = ""
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#EXTM3U"):
            continue
            
        if line.startswith("#EXTINF"):
            current_header = line
            match = re.search(r'group-title="(.*?)"', line, re.IGNORECASE)
            if match:
                group_title = match.group(1).strip()
            else:
                group_title = "Uncategorized"
            
            if group_title not in groups:
                groups[group_title] = ["#EXTM3U\n"]
        elif current_header and not line.startswith("#"):
            groups[group_title].append(f"{current_header}\n{line}\n")
            current_header = ""

    json_data = []

    for group_title, entries in groups.items():
        filename = sanitize_filename(group_title) + ".m3u"
        file_path = os.path.join(OUTPUT_DIR, filename)
        
        with open(file_path, "w", encoding="utf-8") as out_f:
            out_f.writelines(entries)
            
        raw_link = f"{GITHUB_RAW_BASE}{quote(filename)}"
        json_data.append({
            "group_title": group_title,
            "playlist_url": raw_link
        })

    with open(JSON_OUTPUT, "w", encoding="utf-8") as json_f:
        json.dump(json_data, json_f, indent=4, ensure_ascii=False)
    
    print("Saari playlists combine, split aur JSON generation successfully complete ho gaya!")

if __name__ == "__main__":
    process_playlist()
