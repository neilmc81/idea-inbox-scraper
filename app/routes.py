from fastapi import APIRouter
from app.scrapers.reddit_spider import fetch_reddit_ideas
from app.scrapers.hn_spider import fetch_hn_ideas
from app.scrapers.ph_spider import fetch_ph_ideas
from app.storage import save_ideas

router = APIRouter()

@router.get("/reddit")
def get_reddit_ideas():
    ideas = fetch_reddit_ideas()
    save_ideas("reddit", ideas)
    return {"ideas": ideas}

@router.get("/hackernews")
def get_hn_ideas():
    ideas = fetch_hn_ideas()
    save_ideas("hackernews", ideas)
    return {"ideas": ideas}

@router.get("/producthunt")
def get_ph_ideas():
    print("=== /producthunt endpoint hit ===")
    ideas = fetch_ph_ideas()
    print("=== Ideas fetched from scraper ===")
    print(ideas)

    if ideas:
        print("✅ Data fetched, saving to JSON")
        save_ideas("producthunt", ideas)
    else:
        print("❌ No data fetched from Product Hunt.")

    return {"ideas": ideas}
