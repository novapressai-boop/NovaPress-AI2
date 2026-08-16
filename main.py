"""
NovaPress AI
Main Pipeline
Version: 2.0
"""

from agents.collector import collect_news
from agents.analyzer import analyze_all_news
from agents.writer import main as writer_main


def main():
    print("=" * 60)
    print("NovaPress AI - Main Pipeline")
    print("=" * 60)

    # Step 1: Collect News
    print("\n[1/3] Collecting news...")
    collect_news()

    # Step 2: Analyze News
    print("\n[2/3] Analyzing news...")
    analyze_all_news()

    # Step 3: Write SEO Articles
    print("\n[3/3] Generating SEO articles...")
    writer_main()

    print("\n" + "=" * 60)
    print("NovaPress AI Pipeline Completed")
    print("=" * 60)
    print("Articles are ready for approval.")
    print("Publishing is NOT automatic.")
    print("=" * 60)


if __name__ == "__main__":
    main()