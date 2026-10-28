# Monitor de rede com alertas

Script que verifica se equipamentos de rede e câmeras IP estão respondendo e avisa quando algum cai ou volta. Nasceu da rotina de suporte e CFTV.

## Como funciona
- Cada equipamento do `hosts.json` recebe uma tentativa de conexão TCP na porta indicada (80 para painel web, 554 para vídeo RTSP, 53 para DNS).
- O alerta só dispara quando o **estado muda**, para não gerar spam.
- Tudo é registrado em `monitor.log`. Com `TELEGRAM_TOKEN` e `TELEGRAM_CHAT_ID`, o alerta também chega no celular.

## Como rodar
```bash
python monitor.py --uma-vez
python monitor.py --intervalo 30
```
Edite o `hosts.json` com os IPs da sua rede. Não precisa instalar nada.

## Tecnologias
Python (socket, logging, urllib), redes, automação de alertas. Ideias de evolução: painel web simples, histórico de quedas em SQLite, resposta automática com IA sugerindo a causa provável.
