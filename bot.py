import requests
import json
import os
from datetime import datetime
from telegram import Bot

# === CONFIGURAÇÕES ===
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
ESTADO_PATH = 'ultimo_estado.txt'

URLS = [
    "https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=vaga&limit=100&offset=0&workplaceType=remote",
    "https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=analista&limit=100&offset=0&workplaceType=remote",
    "https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=pessoa&limit=100&offset=0&workplaceType=remote",
    "https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=especialista&limit=100&offset=0&workplaceType=remote",
    "https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=specialist&limit=100&offset=0&workplaceType=remote",
    "https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=product&limit=100&offset=0&workplaceType=remote",
    "https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=marketing&limit=100&offset=0&workplaceType=remote",
    "https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=gerente&limit=100&offset=0&workplaceType=remote",
    "https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=coordenadora&limit=100&offset=0&workplaceType=remote"
]

# === FUNÇÕES ===

def buscar_vagas_remotas():
    vagas_encontradas = set()
    for url in URLS:
        print(f"🔎 Consultando: {url}")
        try:
            resposta = requests.get(url)
            resposta.raise_for_status()
            dados = resposta.json()
            vagas = dados.get('data', [])
            print(f"📌 {len(vagas)} vagas encontradas nesta URL")
            for vaga in vagas:
                titulo = vaga.get('title', '').strip()
                link = vaga.get('jobUrl', '').strip()
                if titulo and link:
                    vagas_encontradas.add(f"{titulo} | {link}")
        except Exception as e:
            print(f"❌ Erro ao buscar vagas em {url}: {e}")
    return vagas_encontradas

def salvar_estado_atual(vagas_atuais):
    with open(ESTADO_PATH, 'w') as f:
        json.dump(list(vagas_atuais), f)

def carregar_estado_anterior():
    if not os.path.exists(ESTADO_PATH):
        print("⚠️ Arquivo de estado não encontrado. Criando novo histórico...")
        return set()
    try:
        with open(ESTADO_PATH, 'r') as f:
            conteudo = f.read().strip()
            if not conteudo:
                print("⚠️ Arquivo de estado está vazio.")
                return set()
            return set(json.loads(conteudo))
    except Exception as e:
        print(f"⚠️ Erro ao carregar estado anterior: {e}")
        return set()

def enviar_mensagem(mensagem):
    bot = Bot(token=TOKEN)
    resposta = bot.send_message(chat_id=CHAT_ID, text=mensagem)
    if resposta:
        print("✅ Mensagem enviada com status 200")

def main():
    enviar_mensagem("🤖 Bot iniciado e verificando novas vagas...")

    vagas_atuais = buscar_vagas_remotas()
    vagas_anteriores = carregar_estado_anterior()

    novas_vagas = vagas_atuais - vagas_anteriores

    print(f"\n📋 Vagas atuais ({len(vagas_atuais)}): {sorted(vagas_atuais)}")
    print(f"📂 Vagas anteriores ({len(vagas_anteriores)}): {sorted(vagas_anteriores)}")
    print(f"✅ Total de vagas únicas encontradas: {len(vagas_atuais)}")
    print(f"✅ Novas vagas detectadas: {len(novas_vagas)}\n")

    if novas_vagas:
        mensagem = f"📢 Novas vagas remotas no Grupo Boticário ({datetime.now().strftime('%d/%m %H:%M')}):\n\n"
        for vaga in sorted(novas_vagas):
            mensagem += f"🔹 {vaga}\n"
        enviar_mensagem(mensagem)

    salvar_estado_atual(vagas_atuais)

# === EXECUÇÃO ===
if __name__ == "__main__":
    main()
