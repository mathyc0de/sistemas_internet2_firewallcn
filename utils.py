import json
from datetime import datetime
import re

def load_data() -> tuple[list, list]:
    """
    Carrega os dados de bloqueio de domínios e palavras ofensivas dos arquivos JSON.
    """


    ## Foi feito um scrap na wikipedia dos sites bloqueados na China
    with open('data/blocked.json', 'r', encoding='utf-8') as f:
        blocked_domains = json.load(f)
        f.close()
    
    ## Lista de xingamentos, gerado com IA
    with open('data/words.json', 'r', encoding='utf-8') as f:
        blocked_words = json.load(f)
        f.close()
    
    return blocked_domains, blocked_words


def filter_domains(request: str, blocked_domains: list) -> bool:
    return any(domain in request for domain in blocked_domains)

def filter_curse_words(conteudo: str, blocked_words: list) -> str:
    """
    Substitui as palavras ofensivas pela string 'censurado'
    """
    conteudo_modificado = conteudo
    for palavra in blocked_words:
        if palavra.lower() in conteudo_modificado.lower():
            conteudo_modificado = re.sub(re.escape(palavra), "censurado", conteudo_modificado, flags=re.IGNORECASE)
    
    return conteudo_modificado
