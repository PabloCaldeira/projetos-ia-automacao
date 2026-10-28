# Triagem de chamados com IA

Classifica chamados de suporte por **categoria** e **prioridade** e sugere a primeira ação ao técnico.

## Como funciona
1. Lê os chamados de um CSV (`id,descricao`).
2. Com `ANTHROPIC_API_KEY` definida, envia cada texto a um modelo de IA que devolve JSON.
3. Sem chave, ou se a IA falhar, usa regras por palavra-chave (modo offline).
4. Grava `triagem_resultado.csv`.

## Como rodar
```bash
python triagem.py                      # modo offline, só Python
pip install -r requirements.txt        # para usar IA
export ANTHROPIC_API_KEY="sua-chave"   # Windows: set ANTHROPIC_API_KEY=sua-chave
python triagem.py chamados_exemplo.csv
```
Use `MODELO_IA` para trocar o modelo. Para outro provedor (OpenAI, Gemini), só a função `classificar_ia` muda.

## Tecnologias
Python, API de LLM, CSV. Ideias de evolução: ler chamados de um sistema real via API, validar a saída com Pydantic, medir acerto contra classificação manual.
