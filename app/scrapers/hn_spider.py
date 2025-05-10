print("SCRIPT STARTING - BEFORE IMPORTS")

import cloudscraper
import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client
import logging
import sys
import traceback
import requests

print("IMPORTS COMPLETE")

# === DIRECT FILE WRITE TEST ===
try:
    print("TRYING DIRECT FILE WRITE")
    # Dynamically find the project root (two levels up from this script)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    log_file = os.path.join(project_root, 'scraper.log')
    print(f"Log file will be at: {log_file}")
    
    # Try direct write to verify file is writeable
    with open(log_file, 'a') as f:
        f.write(f"\n--- HACKER NEWS SCRAPER INIT at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        f.write("If you can see this, the file is writable directly.\n")
    print("DIRECT FILE WRITE SUCCEEDED")
except Exception as e:
    print(f"ERROR WRITING TO LOG FILE DIRECTLY: {e}")
    traceback.print_exc()

# === LOGGING CONFIGURATION ===
try:
    # Remove all handlers associated with the root logger object (prevents duplicate logs)
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, mode='a', encoding='utf-8'),
            logging.StreamHandler()
        ],
        force=True
    )

    logging.info("=== Logging system initialized successfully ===")
    
    # Verify handlers are attached
    print(f"Current logging handlers: {[h.__class__.__name__ for h in logging.getLogger().handlers]}")

except Exception as e:
    print(f"ERROR SETTING UP LOGGING: {e}")
    traceback.print_exc()

# === ENVIRONMENT CONFIGURATION ===
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
logging.info(f"Loading .env from: {dotenv_path}")
logging.info(f"Does .env exist? {os.path.exists(dotenv_path)}")
load_dotenv(dotenv_path=dotenv_path, override=True)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
user_id = os.getenv("USER_ID")

logging.info("Environment variables loaded.")

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logging.info("✅ Supabase client initialized successfully.")
except Exception as e:
    logging.error(f"❌ Error initializing Supabase client: {e}")
    exit(1)

# 🚀 **Normalize Links**
def normalize_link(link):
    return link.rstrip('/').lower()

# 🚀 **Batch Duplicate Check**
def get_existing_links(links):
    """
    Fetch all existing links from Supabase that match the provided list.
    """
    if not links:
        return set()
    try:
        response = supabase.table('ideas').select('link').in_('link', links).execute()
        existing_links = {item['link'] for item in response.data} if response.data else set()
        logging.info(f"🔍 Found {len(existing_links)} existing links in Supabase.")
        return existing_links
    except Exception as e:
        logging.error(f"❌ Error fetching existing links: {e}")
        return set()

# 🚀 **Batch Save to Supabase**
def batch_save_to_supabase(ideas, max_retries=3):
    """
    Batch insert ideas to Supabase, skipping those with duplicate links.
    """
    if not ideas:
        logging.warning("⚠️  No new ideas to insert.")
        return

    # Normalize links for comparison
    for idea in ideas:
        idea['link'] = normalize_link(idea['link'])

    links = [idea['link'] for idea in ideas]
    existing_links = get_existing_links(links)
    new_ideas = [idea for idea in ideas if idea['link'] not in existing_links]

    if not new_ideas:
        logging.warning("⚠️  All ideas are duplicates. Nothing to insert.")
        return

    logging.info(f"📝 Attempting to batch insert {len(new_ideas)} new ideas into Supabase...")

    for attempt in range(max_retries):
        try:
            response = supabase.table('ideas').insert(new_ideas).execute()
            if response.data:
                logging.info(f"✅ Successfully inserted {len(response.data)} ideas.")
                logging.info("Inserted ideas: %s", [idea.get('title') for idea in response.data])
                return True
            else:
                logging.error(f"❌ Batch insert failed. Retrying... ({attempt + 1}/{max_retries})")
        except Exception as e:
            logging.error(f"🚨 Error during batch insert attempt {attempt + 1}: {e}")
    logging.error("❌ Max retries reached. Some ideas were not inserted.")
    return False

# 🚀 **Fetch Ideas from Hacker News**
def fetch_hn_ideas():
    logging.info("=== Step 1: Fetching Top Stories IDs ===")
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            story_ids = response.json()[:30]  # Get the top 30 stories
            ideas = []
            
            for story_id in story_ids:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story_data = requests.get(story_url).json()
                
                if story_data and 'url' in story_data:
                    idea = {
                        "title": story_data.get("title"),
                        "description": story_data.get("title"),
                        "link": story_data.get("url"),
                        "votes": story_data.get("score", 0),
                        "source": "Hacker News",
                        "user_id": user_id
                    }
                    ideas.append(idea)

            logging.info("=== Step 2: Batch Saving Ideas ===")
            batch_save_to_supabase(ideas)
            logging.info("✅ All ideas processed.")
        else:
            logging.error(f"❌ Failed to fetch stories from Hacker News. Status Code: {response.status_code}")
    except Exception as e:
        logging.error(f"❌ Exception occurred during Hacker News Fetch: {e}")

# === Test run ===
if __name__ == "__main__":
    print("MAIN EXECUTION BLOCK REACHED")
    try:
        logging.info("=== Testing Hacker News Scraper ===")
        print("CALLING fetch_hn_ideas()")
        fetch_hn_ideas()
        print("fetch_hn_ideas() COMPLETED")
    except Exception as e:
        print(f"ERROR IN MAIN EXECUTION: {e}")
        traceback.print_exc()
    finally:
        print("SCRIPT EXECUTION COMPLETE")

print("END OF SCRIPT FILE REACHED")

# Force flush all log handlers at the end
for handler in logging.getLogger().handlers:
    try:
        handler.flush()
        print(f"Flushed handler: {handler}")
    except Exception as e:
        print(f"Error flushing handler: {e}")
