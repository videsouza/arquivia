import os
import feedparser

from supabase import create_client
from sources import FONTES

print("Iniciando ArquivIA...")

# =========================================
# SUPABASE
# =========================================

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

print("Supabase conectado.")

# =========================================
# IA LOCAL GRATUITA
# =========================================

def analisar_artigo(titulo):

    texto = titulo.lower()

    tags = []

    categoria = "Ciência da Informação"

    # =====================================
    # TAGS
    # =====================================

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

    if "arquiv" in texto:
        tags.append("Arquivologia")

    if "biblioteca" in texto:
        tags.append("Bibliotecas")

    if "bibliometr" in texto:
        tags.append("Bibliometria")

    if "digital" in texto:
        tags.append("Transformação Digital")

    if "gestão documental" in texto:
        tags.append("Gestão Documental")

    # =====================================
    # CATEGORIAS
    # =====================================

    if (
        "algoritmo" in texto
        or "ia" in texto
        or "digital" in texto
    ):
        categoria = "Tecnologias da Informação"

    elif "preservação" in texto:
        categoria = "Preservação Digital"

    elif "tesauro" in texto:
        categoria = "Representação da Informação"

    elif "desinformação" in texto:
        categoria = "Políticas de Informação"

    elif "arquiv" in texto:
        categoria = "Arquivologia"

    elif "biblioteca" in texto:
        categoria = "Biblioteconomia"

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

# =========================================
# FILTROS DE LIMPEZA
# =========================================

PALAVRAS_BLOQUEADAS = [

    "expediente",
    "editorial",
    "sumário",
    "sumario",
    "apresentação",
    "apresentacao",
    "errata",
    "prefácio",
    "prefacio"

]

# =========================================
# RSS
# =========================================

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

    # =====================================
    # PROCESSAMENTO
    # =====================================

    for entry in feed.entries[:10]:

        print("\n-------------------")
        print("Processando artigo")

        titulo = entry.title.strip()

        # =================================
        # FILTRO DE LIMPEZA
        # =================================

        titulo_lower = titulo.lower()

        ignorar = any(
            palavra in titulo_lower
            for palavra in PALAVRAS_BLOQUEADAS
        )

        if ignorar:

            print(
                f"Ignorado: {titulo}"
            )

            continue

        # =================================
        # LINK
        # =================================

        link = entry.link

        # =================================
        # AUTORES
        # =================================

        autores = None

        if "authors" in entry:

            autores = ", ".join(
                autor.name
                for autor in entry.authors
            )

        # =================================
        # RESUMO RSS
        # =================================

        resumo = None

        if "summary" in entry:

            resumo = (
                entry.summary
                .replace("\n", " ")
                .replace("\r", " ")
            )

        # =================================
        # DATA
        # =================================

        publicado_em = None

        if "published" in entry:

            publicado_em = entry.published

        # =================================
        # IA LOCAL
        # =================================

        ia = analisar_artigo(titulo)

        # =================================
        # ARTIGO
        # =================================

        artigo = {

            "titulo":
                titulo,

            "autores":
                autores,

            "resumo":
                resumo,

            "link":
                link,

            "revista":
                fonte["revista"],

            "descricao_curta":
                ia["descricao_curta"],

            "resumo_ia":
                ia["resumo_ia"],

            "categoria":
                ia["categoria"],

            "tags_ia":
                ia["tags_ia"],

            "publicado_em":
                publicado_em
        }

        # =================================
        # UPSERT
        # =================================

        try:

            supabase.table(
                "articles"
            ).upsert(
                artigo,
                on_conflict="link"
            ).execute()

            print(
                f"Artigo salvo: {titulo}"
            )

        except Exception as erro:

            print(
                "Erro Supabase:"
            )

            print(erro)

print("\nArquivIA finalizado.")
