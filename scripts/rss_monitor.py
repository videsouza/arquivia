import os
import feedparser
from supabase import create_client
from dateutil import parser

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

rss_url = "https://revista.ibict.br/ciinf/gateway/plugin/WebFeedGatewayPlugin/rss2"

feed = feedparser.parse(rss_url)

for entry in feed.entries[:5]:

    titulo = entry.title
    link = entry.link

    publicado = None

    if hasattr(entry, "published"):
        publicado = parser.parse(entry.published).isoformat()

    artigo = {
        "titulo": titulo,
        "link": link,
        "revista": "Ciência da Informação",
        "publicado_em": publicado
    }

    response = supabase.table("articles").upsert(
        artigo,
        on_conflict="link"
    ).execute()

    print(f"Salvo: {titulo}")
