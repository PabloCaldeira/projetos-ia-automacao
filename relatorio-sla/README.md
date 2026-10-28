# Relatório automático de SLA

Calcula quantos chamados foram resolvidos dentro do prazo de cada prioridade e gera o relatório da semana em Markdown, sem montar planilha à mão.

## Como funciona
- `gerar_dados.py` cria um banco SQLite com 120 chamados fictícios e a tabela de SLA (crítica 2h, alta 4h, média 8h, baixa 24h).
- `relatorio.py` roda uma consulta SQL com `JOIN` e `GROUP BY`, calcula o cumprimento por prioridade e grava `relatorio.md`.

## Como rodar
```bash
python gerar_dados.py
python relatorio.py
```
Para usar dados reais, aponte `relatorio.py` para o banco do seu sistema de chamados e ajuste os nomes das colunas.

## Tecnologias
Python (sqlite3), SQL (JOIN, GROUP BY, funções de data). Ideias de evolução: enviar o relatório por e-mail toda segunda, gerar gráficos com matplotlib, resumo em texto escrito por IA.
