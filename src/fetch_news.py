import feedparser as feed


class FetchNews:
    def the_hacker_news(self):
        rss_url = "https://feeds.feedburner.com/TheHackersNews"
        rss_data = feed.parse(rss_url)

        if rss_data.bozo == 1:
            print("Gagal mengambil data!")
            print("Detail Error:", rss_data.bozo_exception)
            return []

        news_data = []

        for news in rss_data["entries"]:
            item_data = {
                "title": news.title,
                "summary": news.summary,
                "link": news.link,
                "published": news.published,
                "authors": news.authors
            }

            news_data.append(item_data)

        return news_data


# Testing Class
# if __name__=="__main__":
#     data = FetchNews()
#     thn = data.the_hacker_news()
#     print(thn)
