"""Monitor de rede com alertas.

Testa a conexão TCP de equipamentos (câmeras IP, DVR/NVR, switches, servidores)
listados em hosts.json e avisa quando algum muda de estado (caiu ou voltou).
Usa só a biblioteca padrão do Python.

Uso:
    python monitor.py --uma-vez            # testa todos e sai
    python monitor.py --intervalo 30       # repete a cada 30 segundos
Alerta opcional no Telegram: defina TELEGRAM_TOKEN e TELEGRAM_CHAT_ID.
"""
import argparse
import json
import logging
import os
import socket
import time
import urllib.parse
import urllib.request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler("monitor.log", encoding="utf-8"), logging.StreamHandler()],
)


def esta_online(host, porta, timeout=3):
    try:
        with socket.create_connection((host, porta), timeout=timeout):
            return True
    except OSError:
        return False


def enviar_alerta(mensagem):
    logging.warning("ALERTA: %s", mensagem)
    token, chat = os.getenv("TELEGRAM_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    if not (token and chat):
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    dados = urllib.parse.urlencode({"chat_id": chat, "text": mensagem}).encode()
    try:
        urllib.request.urlopen(url, dados, timeout=10)
    except OSError as erro:
        logging.error("Falha ao enviar para o Telegram: %s", erro)


def verificar(equipamentos, estado):
    for e in equipamentos:
        online = esta_online(e["host"], e["porta"])
        antes = estado.get(e["nome"])
        if antes is None:
            logging.info("%s: %s", e["nome"], "online" if online else "OFFLINE")
        elif antes and not online:
            enviar_alerta(f'🔴 {e["nome"]} ({e["host"]}:{e["porta"]}) caiu')
        elif not antes and online:
            enviar_alerta(f'🟢 {e["nome"]} voltou a responder')
        estado[e["nome"]] = online
    return estado


def main():
    p = argparse.ArgumentParser(description="Monitor de rede com alertas")
    p.add_argument("--hosts", default="hosts.json")
    p.add_argument("--intervalo", type=int, default=30, help="segundos entre testes")
    p.add_argument("--uma-vez", action="store_true", help="testa uma vez e sai")
    args = p.parse_args()

    with open(args.hosts, encoding="utf-8") as f:
        equipamentos = json.load(f)

    estado = {}
    while True:
        estado = verificar(equipamentos, estado)
        if args.uma_vez:
            break
        time.sleep(args.intervalo)


if __name__ == "__main__":
    main()
