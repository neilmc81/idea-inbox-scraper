import requests

def fetch_reddit_ideas(subreddit="startups"):
    url = f"https://www.reddit.com/r/{subreddit}/new.json"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        posts = response.json().get('data', {}).get('children', [])
        ideas = []
        for post in posts:
            title = post['data']['title']
            link = f"https://www.reddit.com{post['data']['permalink']}"
            ideas.append({"title": title, "link": link})
        return ideas
    else:
        print("Failed to fetch data from Reddit.")
        return []

# Temporary test run
if __name__ == "__main__":
    ideas = fetch_reddit_ideas()
    print(ideas)
