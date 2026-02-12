import json

def format_lessons():
    try:
        with open('js_videos.json', 'r', encoding='utf-8') as f:
            videos = json.load(f)
        
        formatted = []
        for i, v in enumerate(videos, 1):
            # Basic duration estimation if not present or just placeholder
            duration = "15:00" # default
            
            lesson = {
                "id": i,
                "title": v['title'],
                "duration": v['duration'],
                "videoId": v['id'],
                "image": f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg",
                "description": f"En esta lección {i} profundizamos en los conceptos de JavaScript."
            }
            formatted.append(lesson)
            
        with open('formatted_js.txt', 'w', encoding='utf-8') as f:
            f.write(json.dumps(formatted, indent=4, ensure_ascii=False))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    format_lessons()
