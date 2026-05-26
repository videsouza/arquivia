import feedparser

rss_url = "https://revista.ibict.br/ciinf/gateway/plugin/WebFeedGatewayPlugin/rss2"

feed = feedparser.parse(rss_url)

for entry in feed.entries[:5]:
    print(entry.title)
