import os
import json
import feedparser

from supabase import create_client
from openai import OpenAI

print("Iniciando ArquivIA...")

# =========================
# SUPABASE
# =========================

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

print("Supabase conectado.")

# =========================
# OPENAI
# =========================

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

print("OpenAI conectada.")

# =========================
# RSS
# =========================

rss_url = (
    "https://periodicos.ufmg.br/index.php/pci/"
    "gateway/plugin/WebFeedGatewayPlugin/rss2"
)

print("Lendo RSS...")

feed = feedparser.parse(rss_url)

print(f"Entradas encontradas: {len(feed.entries)}")

# =========================
# PROCESSAMENTO
# =========================

for entry in feed.entries[:5]:

    print("\n-------------------")
    print("Processando artigo")

    titulo = entry.title
    link = entry.link

    print(f"Título: {titulo}")

    # =========================
    # IA
    # =========================

    prompt = f"""
Você é um especialista em Ciência da Informação,
Arquivologia e Biblioteconomia.

Analise o título abaixo e responda APENAS
em JSON válido.

Título:
{titulo}

Formato obrigatório:

{{
  "descricao_curta": "...",
  "resumo_ia": "...",
  "categoria": "...",
  "tags_ia": ["...", "...", "..."]
}}
"""

    try:

        resposta = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        conteudo = (
            resposta
            .choices[0]
            .message
            .content
        )

        ia = json.loads(conteudo)

        print("IA processada.")

    except Exception as erro:

        print("Erro IA:")
        print(erro)

        ia = {
            "descricao_curta": None,
            "resumo_ia": None,
            "categoria": None,
            "tags_ia": []
        }

    # =========================
    # ARTIGO
    # =========================

    artigo = {

        "titulo": titulo,

        "link": link,

        "revista":
            "Perspectivas em Ciência da Informação",

        "descricao_curta":
            ia["descricao_curta"],

        "resumo_ia":
            ia["resumo_ia"],

        "categoria":
            ia["categoria"],

        "tags_ia":
            ia["tags_ia"],

        "publicado_em":
            None
    }

    # =========================
    # SUPABASE INSERT
    # =========================

    try:

        supabase.table("articles").upsert(
            artigo,
            on_conflict="link"
        ).execute()

        print("Artigo salvo.")

    except Exception as erro:

        print("Erro Supabase:")
        print(erro)

print("\nArquivIA finalizado.")
