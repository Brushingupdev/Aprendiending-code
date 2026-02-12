
import urllib.request
import re
import json
import socket
import sys
import io

# Forzar salida en UTF-8 para evitar errores en Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def extract_playlist_info(url):
    try:
        # User-Agent header to avoid basic scraping blocks
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            
        # Find ytInitialData variable
        match = re.search(r'var ytInitialData = ({.*?});</script>', html)
        if not match:
            # Try without the semicolon if it's different
            match = re.search(r'window\["ytInitialData"\] = ({.*?});', html)
        
        if match:
            data = json.loads(match.group(1))
            
            # Navigate the JSON to find videos
            # Typical path: contents -> twoColumnBrowseResultsRenderer -> tabs -> [0] -> tabRenderer -> content -> sectionListRenderer -> contents -> [0] -> itemSectionRenderer -> contents -> [0] -> playlistVideoListRenderer -> contents
            
            videos = []
            try:
                # This path changes sometimes, but let's try a common one
                sidebar_contents = data['sidebar']['playlistSidebarRenderer']['items']
                # Or main contents
                tabs = data['contents']['twoColumnBrowseResultsRenderer']['tabs']
                content = tabs[0]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['playlistVideoListRenderer']['contents']
                
                for item in content:
                    if 'playlistVideoRenderer' in item:
                        video_data = item['playlistVideoRenderer']
                        video_id = video_data['videoId']
                        title = video_data['title']['runs'][0]['text']
                        duration = video_data.get('lengthText', {}).get('simpleText', '0:00')
                        videos.append({
                            'id': video_id,
                            'title': title,
                            'duration': duration
                        })
            except (KeyError, IndexError) as e:
                # Fallback: simple regex for video IDs if JSON parsing fails
                # regex for videoIds in a playlist: "videoId":"([a-zA-Z0-9_-]{11})"
                matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})","thumbnail".*?"title":{"runs":\[{"text":"(.*?)"}\]', html)
                for vid, title in matches:
                    if vid not in [v['id'] for v in videos]:
                        videos.append({'id': vid, 'title': title, 'duration': 'N/A'})
            
            return videos
        else:
            print("Could not find ytInitialData")
            return []
            
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    url = "https://www.youtube.com/playlist?list=PLvq-jIkSeTUZ6QgYYO3MwG9EMqC-KoLXA"
    res = extract_playlist_info(url)
    with open("js_videos.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    print(f"Extraction complete. {len(res)} videos found.")
