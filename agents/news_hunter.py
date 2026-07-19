"""
NovaPress AI
News Hunter Module
Day 7
"""

from agents.collector import collect_news


def run_news_hunter():
    print("🚀 NovaPress AI - News Hunter Started")

    news = collect_news()

    if not news:
        print("❌ No news found.")
        return []

    print(f"✅ {len(news)} news collected.")
    return news


if __name__ == "__main__":
    run_news_hunter()