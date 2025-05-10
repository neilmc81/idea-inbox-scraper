import cloudscraper
import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client
import logging
import sys
import traceback
import requests
from bs4 import BeautifulSoup

# Direct file write test - at the very start
try:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    log_file = os.path.join(project_root, 'scraper.log')
    with open(log_file, 'a') as f:
        f.write(f"\n--- INDIE HACKERS SCRAPER DIRECT WRITE TEST at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
except Exception as e:
    print(f"ERROR WITH DIRECT WRITE: {e}")

# === LOGGING CONFIGURATION ===
try:
    # Dynamically find the project root (two levels up from this script)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    log_file = os.path.join(project_root, 'scraper.log')
    
    # Remove all handlers associated with the root logger object (prevents duplicate logs)
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Create file handler with immediate flush
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Set up the root logger
    logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler], force=True)
    
    # Explicitly log and flush to verify logging is working
    logging.info("=== Logging system initialized successfully ===")
    for handler in logging.getLogger().handlers:
        handler.flush()

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

# 🚀 **Fetch Ideas from Indie Hackers**
def fetch_ih_ideas():
    logging.info("=== Step 1: Fetching Latest Indie Hackers Posts ===")
    for handler in logging.getLogger().handlers:
        handler.flush()
    
    url = "https://www.indiehackers.com/post"
    
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            posts = soup.find_all('a', class_='title-link')

            ideas = []
            for post in posts:
                title = post.get_text(strip=True)
                link = f"https://www.indiehackers.com{post['href']}"
                
                idea = {
                    "title": title,
                    "description": title,
                    "link": link,
                    "votes": 0,  # Indie Hackers does not provide vote count in the listing
                    "source": "Indie Hackers",
                    "user_id": user_id
                }
                ideas.append(idea)

            logging.info("=== Step 2: Batch Saving Ideas ===")
            for handler in logging.getLogger().handlers:
                handler.flush()
                
            batch_save_to_supabase(ideas)
            logging.info("✅ All ideas processed.")
            for handler in logging.getLogger().handlers:
                handler.flush()
        else:
            logging.error(f"❌ Failed to fetch stories from Indie Hackers. Status Code: {response.status_code}")
            for handler in logging.getLogger().handlers:
                handler.flush()
    except Exception as e:
        logging.error(f"❌ Exception occurred during Indie Hackers Fetch: {e}")
        for handler in logging.getLogger().handlers:
            handler.flush()

# === Test run ===
if __name__ == "__main__":
    logging.info("=== Testing Indie Hackers Scraper ===")
    try:
        fetch_ih_ideas()
    except Exception as e:
        logging.error(f"Error in main execution: {e}")
        traceback.print_exc()

# Force flush all log handlers at the end
for handler in logging.getLogger().handlers:
    handler.flush()

# Final direct write test
try:
    with open(log_file, 'a') as f:
        f.write(f"--- INDIE HACKERS SCRAPER COMPLETED at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n\n")
except Exception as e:
    print(f"ERROR WITH FINAL DIRECT WRITE: {e}")
