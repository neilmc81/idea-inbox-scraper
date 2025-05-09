import json
from datetime import datetime

FILE_PATH = "app/data/idea_vault.json"

def save_ideas(platform, ideas):
    try:
        with open(FILE_PATH, "r") as file:
            data = json.load(file)

        if platform not in data:
            data[platform] = []

        # Add a timestamp
        for idea in ideas:
            idea["timestamp"] = datetime.now().isoformat()

        data[platform].extend(ideas)

        with open(FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)

        print(f"{len(ideas)} ideas saved to {platform} in idea_vault.json")
    except Exception as e:
        print("Failed to save ideas:", e)