import requests

def fetch_hn_ideas():
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    response = requests.get(url)

    if response.status_code == 200:
        story_ids = response.json()[:10]  # Get the top 10 stories
        ideas = []

        for story_id in story_ids:
            item_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            item_response = requests.get(item_url)

            if item_response.status_code == 200:
                story_data = item_response.json()
                if "title" in story_data and "url" in story_data:
                    ideas.append({
                        "title": story_data.get("title", "No Title"),
                        "link": story_data.get("url", "No URL"),
                        "source": "Hacker News"
                    })

        return ideas
    else:
        print("Failed to fetch data from Hacker News.")
        return []
