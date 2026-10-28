"""Cria um banco SQLite (chamados.db) com chamados fictícios para testar o relatório."""
import random
import sqlite3
from datetime import datetime, timedelta

random.seed(42)
SLA = {"critica": 2, "alta": 4, "media": 8, "baixa": 24}

con = sqlite3.connect("chamados.db")
con.executescript("""
DROP TABLE IF EXISTS chamados;
DROP TABLE IF EXISTS sla;
CREATE TABLE sla (prioridade TEXT PRIMARY KEY, horas_limite INTEGER NOT NULL);
CREATE TABLE chamados (
    id INTEGER PRIMARY KEY,
    prioridade TEXT NOT NULL REFERENCES sla(prioridade),
    aberto_em TEXT NOT NULL,
    resolvido_em TEXT
);
""")
con.executemany("INSERT INTO sla VALUES (?, ?)", SLA.items())

inicio = datetime(2026, 10, 19, 8, 0)
for i in range(1, 121):
    prio = random.choices(list(SLA), weights=[1, 3, 4, 3])[0]
    aberto = inicio + timedelta(minutes=random.randint(0, 5 * 24 * 60))
    duracao = SLA[prio] * random.uniform(0.3, 1.5)  # alguns estouram o prazo
    resolvido = None if random.random() < 0.05 else aberto + timedelta(hours=duracao)
    con.execute(
        "INSERT INTO chamados VALUES (?, ?, ?, ?)",
        (i, prio, aberto.isoformat(" ", "seconds"),
         resolvido.isoformat(" ", "seconds") if resolvido else None),
    )
con.commit()
print("chamados.db criado com 120 chamados.")
