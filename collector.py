"""
NovaPress AI - News Collector
Version: 1.0
"""

import json
import feedparser

SOURCE_FILE = "data/sources/bangladesh.json"

def load_sources():
    with open(SOURCE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

def collect_news():
    sources = load_sources()

    for source in sources:
        print(f"Collecting news from: {source['name']}")

        feed = feedparser.parse(source["rss"])

        for news in feed.entries[:5]:
            print("-" * 50)
            print("Title :", news.title)
            print("Link  :", news.link)

if __name__ == "__main__":
    collect_news()