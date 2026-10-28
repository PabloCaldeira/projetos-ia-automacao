"""Gera o relatório semanal de SLA a partir do banco chamados.db.

Uso:
    python gerar_dados.py     # só para criar dados de teste
    python relatorio.py
"""
import sqlite3
from datetime import date

CONSULTA = """
SELECT c.prioridade,
       COUNT(*) AS total,
       SUM(CASE WHEN (julianday(c.resolvido_em) - julianday(c.aberto_em)) * 24
                     <= s.horas_limite THEN 1 ELSE 0 END) AS no_prazo,
       ROUND(AVG((julianday(c.resolvido_em) - julianday(c.aberto_em)) * 24), 1) AS media_horas,
       s.horas_limite
FROM chamados c
JOIN sla s ON s.prioridade = c.prioridade
WHERE c.resolvido_em IS NOT NULL
GROUP BY c.prioridade
ORDER BY s.horas_limite
"""


def main():
    con = sqlite3.connect("chamados.db")
    linhas = con.execute(CONSULTA).fetchall()
    abertos = con.execute("SELECT COUNT(*) FROM chamados WHERE resolvido_em IS NULL").fetchone()[0]

    total = sum(l[1] for l in linhas)
    no_prazo = sum(l[2] for l in linhas)
    geral = 100 * no_prazo / total if total else 0

    md = [f"# Relatório de SLA — {date.today():%d/%m/%Y}", ""]
    md.append(f"**Cumprimento geral:** {geral:.1f}% ({no_prazo} de {total} chamados resolvidos no prazo)")
    md.append(f"**Chamados ainda abertos:** {abertos}")
    md += ["", "| Prioridade | Limite (h) | Resolvidos | No prazo | Cumprimento | Média (h) |",
           "|---|---|---|---|---|---|"]
    for prio, tot, ok, media, limite in linhas:
        md.append(f"| {prio} | {limite} | {tot} | {ok} | {100 * ok / tot:.1f}% | {media} |")

    texto = "\n".join(md)
    with open("relatorio.md", "w", encoding="utf-8") as f:
        f.write(texto + "\n")
    print(texto)


if __name__ == "__main__":
    main()
