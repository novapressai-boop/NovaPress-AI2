from collector import collect_news

def main():
    print("=" * 50)
    print("NovaPress AI - News Hunter")
    print("=" * 50)

    news = collect_news()

    print(f"\nTotal News Collected: {len(news)}")

if __name__ == "__main__":
    main()