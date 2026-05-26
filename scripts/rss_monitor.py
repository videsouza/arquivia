import os
import feedparser
from supabase import create_client
from dateutil import parser

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

rss_url = "https://periodicos.ufmg.br/index.php/pci/gateway/plugin/WebFeedGatewayPlugin/rss2"

feed = feedparser.parse(rss_url)

print(f"Entradas encontradas: {len(feed.entries)}")

for entry in feed.entries[:5]:

    titulo = entry.title
    link = entry.link

    publicado = entry.get("published", None)

    artigo = {
        "titulo": titulo,
        "link": link,
        "revista": "Ciência da Informação",
        "publicado_em": None
    }

    response = supabase.table("articles").upsert(
        artigo,
        on_conflict="link"
    ).execute()

    print(f"Salvo: {titulo}")

print("Finalizado.")
