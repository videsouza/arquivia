import os
import re
import feedparser

from email.utils import parsedate_to_datetime

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
# IA LOCAL
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

    if "arquivo" in texto or "arquiv" in texto:
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
    # CATEGORIA
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
# EXTRAÇÃO DE EDIÇÃO
# =========================================

def extrair_edicao(texto):

    volume = None
    numero = None
    ano = None
    edicao = None

    if not texto:

        return {

            "volume": None,
            "numero": None,
            "ano": None,
            "edicao": None

        }

    texto = texto.lower()

    # =====================================
    # PADRÕES MAIS CONFIÁVEIS
    # =====================================

    padroes = [

        r'v\.?\s*(\d+)\s*[,.-]?\s*n\.?\s*(\d+)\s*[,.-]?\s*(20\d{2})',

        r'volume\s*(\d+)\s*[,.-]?\s*n[uú]mero\s*(\d+)\s*[,.-]?\s*(20\d{2})',

        r'v\.?\s*(\d+)\s*n\.?\s*(\d+)'

    ]

    for padrao in padroes:

        match = re.search(
            padrao,
            texto
        )

        if match:

            volume = match.group(1)

            numero = match.group(2)

            if len(match.groups()) >= 3:

                ano = match.group(3)

            break

    # =====================================
    # PEGAR ANO APENAS SE EXISTIR VOLUME
    # =====================================

    if volume and not ano:

        ano_match = re.search(
            r'(20\d{2})',
            texto
        )

        if ano_match:

            ano = ano_match.group(1)

    # =====================================
    # GERAR EDIÇÃO
    # =====================================

    partes = []

    if volume:

        partes.append(
            f"v.{volume}"
        )

    if numero:

        partes.append(
            f"n.{numero}"
        )

    if ano:

        partes.append(
            f"({ano})"
        )

    if partes:

        edicao = " ".join(partes)

    return {

        "volume": volume,

        "numero": numero,

        "ano": ano,

        "edicao": edicao

    }

# =========================================
# FILTROS
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

    for entry in feed.entries[:15]:

        print("\n-------------------")
        print("Processando artigo")

        titulo = entry.title.strip()

        titulo_lower = titulo.lower()

        # =================================
        # FILTRO
        # =================================

        ignorar = any(
            palavra in titulo_lower
            for palavra in PALAVRAS_BLOQUEADAS
        )

        if ignorar:

            print(f"Ignorado: {titulo}")

            continue

        print(f"Título: {titulo}")

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
        # RESUMO
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

            try:

                publicado_em = (
                    parsedate_to_datetime(
                        entry.published
                    ).isoformat()
                )

            except:

                publicado_em = None

        # =================================
        # TEXTO DA EDIÇÃO
        # =================================

        texto_edicao = ""

        if "tags" in entry:

            for tag in entry.tags:

                if hasattr(tag, "term"):

                    texto_edicao += (
                        " "
                        + tag.term
                    )

        if "summary" in entry:

            texto_edicao += (
                " "
                + entry.summary
            )

        # =================================
        # EXTRAIR EDIÇÃO
        # =================================

        dados_edicao = extrair_edicao(
            texto_edicao
        )

        # =================================
        # IA LOCAL
        # =================================

        ia = analisar_artigo(titulo)

        # =================================
        # OBJETO
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
                publicado_em,

            "volume":
                dados_edicao["volume"],

            "numero":
                dados_edicao["numero"],

            "ano":
                dados_edicao["ano"],

            "edicao":
                dados_edicao["edicao"]
        }

        # =================================
        # SALVAR
        # =================================

        try:

            supabase.table(
                "articles"
            ).upsert(
                artigo,
                on_conflict="link"
            ).execute()

            print("Artigo salvo:")

            print(
                f"Edição: "
                f"{dados_edicao['edicao']}"
            )

        except Exception as erro:

            print("Erro Supabase:")
            print(erro)

print("\nArquivIA finalizado.")
```
