import cloudscraper
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
user_id = os.getenv("USER_ID")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_to_supabase(idea):
    try:
        print(f"💾 Attempting to save: {idea['title']}")
        response = supabase.table('ideas').insert(idea).execute()
        
        # === New Logging ===
        if response.status_code == 201 or response.status_code == 200:
            print(f"✅ Successfully saved: {idea['title']}")
        else:
            print(f"❌ Failed to save: {idea['title']}")
            print(f"🛑 Response: {response}")
            print(f"🛑 Data Sent: {idea}")
    except Exception as e:
        print(f"🚨 Error saving to Supabase: {e}")
