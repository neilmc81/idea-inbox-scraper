import requests
import os

def fetch_ph_ideas():
    try:
        # Use Product Hunt API (needs API key)
        api_key = os.getenv("PH_API_KEY")

        if not api_key:
            print("⚠️  PH_API_KEY is missing! Make sure you added it to Replit Secrets.")
            return []

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
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

        response = requests.post(url, json={"query": query}, headers=headers)

        # === ADD THIS LOGGING ===
        print("✅ Response Status:", response.status_code)
        print("✅ Response Content:", response.text)

        if response.status_code == 200:
            posts = response.json()["data"]["posts"]["edges"]
            ideas = []
            for post in posts:
                node = post["node"]
                ideas.append({
                    "title": node["name"],
                    "description": node["description"],
                    "link": node["url"],
                    "votes": node["votesCount"],
                    "source": "Product Hunt"
                })
            return ideas
        else:
            print(f"❌ Failed to fetch data from Product Hunt. Status Code: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []