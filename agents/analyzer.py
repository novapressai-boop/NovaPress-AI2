import os
import json
from datetime import datetime


class NewsAnalyzer:

    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.input_file = os.path.join(
            self.base_dir,
            "data",
            "output",
            "news_output.json"
        )

        self.output_dir = os.path.join(
            self.base_dir,
            "data",
            "output"
        )

        os.makedirs(self.output_dir, exist_ok=True)

        self.output_file = os.path.join(
            self.output_dir,
            "analyzed_news.json"
        )

        self.news = []
        self.analyzed_news = []


    def load_news(self):

        if not os.path.exists(self.input_file):
            raise FileNotFoundError(
                f"Input file not found: {self.input_file}"
            )

        with open(
            self.input_file,
            "r",
            encoding="utf-8"
        ) as f:

            self.news = json.load(f)

        print(f"Loaded {len(self.news)} news articles.")
    def calculate_score(self, article):
        score = 0

        title = article.get("title", "").lower()
        summary = article.get("summary", "").lower()
        category = article.get("category", "").lower()
        source = article.get("source", "").lower()

        # ---------- Title ----------
        if len(title) >= 60:
            score += 20
        elif len(title) >= 30:
            score += 15
        elif len(title) >= 15:
            score += 10

        # ---------- Summary ----------
        if len(summary) >= 200:
            score += 20
        elif len(summary) >= 100:
            score += 15
        elif len(summary) >= 50:
            score += 10

        # ---------- Breaking / Trending ----------
        keywords = [
            "breaking",
            "latest",
            "update",
            "viral",
            "exclusive",
            "live",
            "developing",
            "alert"
        ]

        for word in keywords:
            if word in title:
                score += 10

        # ---------- Category ----------
        if category == "bangladesh":
            score += 10
        elif category == "international":
            score += 10
        elif category == "sports":
            score += 10
        elif category == "technology":
            score += 10
        elif category == "women":
            score += 10

        # ---------- Trusted Sources ----------
        trusted_sources = [
            "bbc",
            "reuters",
            "associated press",
            "ap",
            "cnn",
            "al jazeera",
            "the guardian",
            "techcrunch",
            "the verge",
            "cricbuzz",
            "icc"
        ]

        for trusted in trusted_sources:
            if trusted in source:
                score += 10
                break

        if score > 100:
            score = 100

        return score


    def analyze_news(self):

        for article in self.news:

            score = self.calculate_score(article)

            article["score"] = score

            if score >= 80:
                article["status"] = "premium"
            elif score >= 60:
                article["status"] = "good"
            elif score >= 40:
                article["status"] = "review"
            else:
                article["status"] = "reject"

            article["analyzed_at"] = datetime.now().isoformat()

            self.analyzed_news.append(article)

        print(f"Analyzed {len(self.analyzed_news)} articles.")
    def save_news(self):
        # Score অনুযায়ী সাজানো
        self.analyzed_news.sort(
            key=lambda x: x.get("score", 0),
            reverse=True
        )

        with open(
            self.output_file,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                self.analyzed_news,
                f,
                ensure_ascii=False,
                indent=4
            )

        premium = len([
            x for x in self.analyzed_news
            if x["status"] == "premium"
        ])

        good = len([
            x for x in self.analyzed_news
            if x["status"] == "good"
        ])

        review = len([
            x for x in self.analyzed_news
            if x["status"] == "review"
        ])

        reject = len([
            x for x in self.analyzed_news
            if x["status"] == "reject"
        ])

        print("\n====================================")
        print("NovaPress AI Analyzer Report")
        print("====================================")
        print(f"Total News : {len(self.analyzed_news)}")
        print(f"Premium    : {premium}")
        print(f"Good       : {good}")
        print(f"Review     : {review}")
        print(f"Reject     : {reject}")
        print(f"Saved File : {self.output_file}")
        print("====================================\n")


    def run(self):
        print("\n====================================")
        print("NovaPress AI News Analyzer")
        print("====================================\n")

        self.load_news()
        self.analyze_news()
        self.save_news()

        print("✅ News Analysis Completed Successfully!")


if __name__ == "__main__":
    analyzer = NewsAnalyzer()
    analyzer.run()