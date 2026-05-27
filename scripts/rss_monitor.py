import os
import json
import feedparser

from supabase import create_client
from openai import OpenAI
from sources import FONTES

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
# IA LOCAL GRATUITA
# =========================

def analisar_artigo(titulo):

    texto = titulo.lower()

    tags = []

    categoria = "Ciência da Informação"

    # ====================
    # TAGS
    # ====================

    if "memória" in texto:
        tags.append("Memória")

    if "algoritmo" in texto:
        tags.append("Algoritmos")

    if "ia" in texto:
        tags.append("Inteligência Artificial")

    if "preservação" in texto:
        tags.append("Preservação Digital")

    if "desinformação" in texto:
        tags.append("Desinformação")

    if "tesauro" in texto:
        tags.append("Tesauros")

    if "arquivo" in texto:
        tags.append("Arquivos")

    if "biblioteca" in texto:
        tags.append("Bibliotecas")

    # ====================
    # CATEGORIAS
    # ====================

    if "algoritmo" in texto or "ia" in texto:
        categoria = "Tecnologias da Informação"

    elif "preservação" in texto:
        categoria = "Preservação Digital"

    elif "tesauro" in texto:
        categoria = "Representação da Informação"

    elif "desinformação" in texto:
        categoria = "Políticas de Informação"

    resumo = (
        "Artigo monitorado automaticamente "
        "pelo ArquivIA."
    )

    descricao = (
        "Pesquisa em "
        + categoria
    )

    return {

        "descricao_curta":
            descricao,

        "resumo_ia":
            resumo,

        "categoria":
            categoria,

        "tags_ia":
            tags
    }

# =========================
# RSS
# =========================

for fonte in FONTES:

    print("\n======================")
    print(f"Fonte: {fonte['revista']}")

    print("Lendo RSS...")

    feed = feedparser.parse(
        fonte["rss"]
    )

    print(
        f"Entradas encontradas: "
        f"{len(feed.entries)}"
    )

    # =========================
    # PROCESSAMENTO
    # =========================

    for entry in feed.entries[:5]:

        print("\n-------------------")
        print("Processando artigo")

        titulo = entry.title
        link = entry.link

        print(f"Título: {titulo}")

        ia = analisar_artigo(titulo)

        artigo = {

            "titulo": titulo,

            "link": link,

            "revista":
                fonte["revista"],

            "categoria":
                fonte["area"],

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

        try:

            supabase.table("articles").upsert(
                artigo,
                on_conflict="link"
            ).execute()

            print("Artigo salvo.")

        except Exception as erro:

            print("Erro Supabase:")
            print(erro)

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
            fonte["revista"],

        "categoria":
            fonte["area"],

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
