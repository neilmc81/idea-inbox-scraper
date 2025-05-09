import requests
import os

def fetch_ph_ideas():
    print("=== Step 1: Fetching API Key ===")
    api_key = os.getenv("PH_API_KEY")
    print(f"PH_API_KEY: {api_key}")

    if not api_key:
        print("⚠️  PH_API_KEY is missing! Please set it in your environment variables.")
        return []

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    url = "https://api.producthunt.com/v2/api/graphql"
    query = """
    {
      posts(order: VOTES, first: 10) {
        edges {
          node {
            name
            description
            url
            votesCount
          }
        }
      }
    }
    """

    try:
        print("=== Step 2: Sending POST request to Product Hunt API ===")
        response = requests.post(url, json={"query": query}, headers=headers)

        print("=== Step 3: Response Received ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        if response.status_code == 200:
            print("=== Step 4: Parsing Response ===")
            data = response.json()
            print("Data Fetched:", data)
            posts = data.get("data", {}).get("posts", {}).get("edges", [])
            ideas = []
            for post in posts:
                node = post.get("node", {})
                print(f"Node: {node}")
                ideas.append({
                    "title": node.get("name"),
                    "description": node.get("description", "No description provided."),
                    "link": node.get("url"),
                    "votes": node.get("votesCount"),
                    "source": "Product Hunt"
                })
            print("=== Step 5: Ideas Fetched ===")
            print(ideas)
            return ideas
        else:
            print(f"❌ Failed to fetch data from Product Hunt. Status Code: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return []

# === Test run ===
if __name__ == "__main__":
    print("=== Testing Product Hunt Scraper ===")
    result = fetch_ph_ideas()
    print("=== Final Result ===")
    print(result)
