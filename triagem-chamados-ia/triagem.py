"""Triagem de chamados de suporte com IA.

Lê chamados de um CSV, classifica categoria e prioridade e sugere a
primeira ação para o técnico. Sem chave de API, usa regras simples por
palavra-chave (modo offline), então o projeto roda em qualquer máquina.

Uso:
    python triagem.py chamados_exemplo.csv
"""
import csv
import json
import os
import sys

MODELO = os.getenv("MODELO_IA", "claude-sonnet-5-5")
CATEGORIAS = ["rede", "cftv", "hardware", "software", "acesso", "outro"]
PRIORIDADES = ["baixa", "media", "alta", "critica"]

SISTEMA = (
    "Você é um analista de service desk. Classifique o chamado e responda "
    "SOMENTE com JSON no formato "
    '{"categoria": "...", "prioridade": "...", "acao": "..."}. '
    f"categoria deve ser uma de {CATEGORIAS}. "
    f"prioridade deve ser uma de {PRIORIDADES}. "
    "acao é a primeira coisa que o técnico deve verificar, em uma frase."
)

REGRAS = [
    ("cftv", ["câmera", "camera", "dvr", "nvr", "cftv", "gravação"], "alta",
     "Verificar alimentação, cabo de rede e PoE da câmera."),
    ("rede", ["internet", "wifi", "wi-fi", "rede", "switch", "roteador", "sem conexão"], "alta",
     "Testar link do roteador/switch e o cabo do ponto afetado."),
    ("acesso", ["senha", "login", "bloqueado", "acesso", "permissão"], "media",
     "Confirmar usuário e redefinir a credencial."),
    ("hardware", ["não liga", "monitor", "teclado", "impressora", "mouse", "hd", "ssd"], "media",
     "Testar o equipamento em outra tomada e com outro cabo."),
    ("software", ["lento", "travando", "erro", "instalar", "programa", "sistema"], "baixa",
     "Reproduzir o erro e conferir logs e atualizações."),
]
PALAVRAS_CRITICAS = ["parado", "todos", "toda a empresa", "urgente", "fora do ar"]


def classificar_regras(texto):
    t = texto.lower()
    categoria, prioridade, acao = "outro", "baixa", "Entrar em contato para entender o problema."
    for cat, palavras, prio, a in REGRAS:
        if any(p in t for p in palavras):
            categoria, prioridade, acao = cat, prio, a
            break
    if any(p in t for p in PALAVRAS_CRITICAS):
        prioridade = "critica"
    return {"categoria": categoria, "prioridade": prioridade, "acao": acao}


def classificar_ia(texto):
    import anthropic  # pip install anthropic

    cliente = anthropic.Anthropic()  # lê ANTHROPIC_API_KEY do ambiente
    resposta = cliente.messages.create(
        model=MODELO,
        max_tokens=300,
        system=SISTEMA,
        messages=[{"role": "user", "content": texto}],
    )
    bruto = resposta.content[0].text.strip().strip("`")
    if bruto.startswith("json"):
        bruto = bruto[4:]
    dados = json.loads(bruto)
    if dados["categoria"] not in CATEGORIAS or dados["prioridade"] not in PRIORIDADES:
        raise ValueError("Resposta fora do formato esperado")
    return dados


def classificar(texto):
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            return classificar_ia(texto) | {"origem": "ia"}
        except Exception as erro:  # rede, cota, JSON inválido...
            print(f"Aviso: IA indisponível ({erro}). Usando regras.", file=sys.stderr)
    return classificar_regras(texto) | {"origem": "regras"}


def main():
    entrada = sys.argv[1] if len(sys.argv) > 1 else "chamados_exemplo.csv"
    saida = "triagem_resultado.csv"
    with open(entrada, newline="", encoding="utf-8") as f:
        chamados = list(csv.DictReader(f))

    resultados = []
    for c in chamados:
        r = classificar(c["descricao"])
        resultados.append({"id": c["id"], "descricao": c["descricao"], **r})
        print(f'#{c["id"]} [{r["prioridade"].upper():7}] {r["categoria"]:9} -> {r["acao"]}')

    with open(saida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "descricao", "categoria", "prioridade", "acao", "origem"])
        w.writeheader()
        w.writerows(resultados)
    print(f"\nResultado salvo em {saida}")


if __name__ == "__main__":
    main()
