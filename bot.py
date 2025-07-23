import requests
import json
import os
from datetime import datetime
from telegram import Bot
from bs4 import BeautifulSoup

# === CONFIGURAÇÕES ===
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

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

HISTORICO_PATH = "historico_vagas.json"  # arquivo para armazenar histórico

def pegar_titulo_vaga(url):
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        h1 = soup.find('h1')
        if h1 and h1.text.strip():
            return h1.text.strip()
        
        title_tag = soup.find('title')
        if title_tag and title_tag.text.strip():
            return title_tag.text.strip().split('|')[0].strip()

        print(f"⚠️ Título não encontrado na página: {url}")
        return None
    except Exception as e:
        print(f"❌ Erro ao buscar título da vaga {url}: {e}")
        return None

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
                link = vaga.get('jobUrl', '').strip()
                if not link:
                    continue
                titulo = pegar_titulo_vaga(link)
                if titulo:
                    vagas_encontradas.add(f"{titulo} | {link}")
                else:
                    print(f"⚠️ Título não encontrado na página: {link}")
        except Exception as e:
            print(f"❌ Erro ao buscar vagas em {url}: {e}")
    return vagas_encontradas

def carregar_historico():
    if os.path.exists(HISTORICO_PATH):
        with open(HISTORICO_PATH, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def salvar_historico(vagas):
    with open(HISTORICO_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(list(vagas)), f, ensure_ascii=False, indent=2)

def enviar_mensagem(mensagem):
    bot = Bot(token=TOKEN)
    MAX_LENGTH = 4000
    for i in range(0, len(mensagem), MAX_LENGTH):
        parte = mensagem[i:i+MAX_LENGTH]
        bot.send_message(chat_id=CHAT_ID, text=parte)
    print("✅ Mensagem enviada com status 200")

def main():
    enviar_mensagem("🤖 Bot iniciado e listando vagas remotas do Grupo Boticário...")

    vagas_atuais = buscar_vagas_remotas()
    historico = carregar_historico()

    print(f"\n📋 Total de vagas encontradas agora: {len(vagas_atuais)}")
    print(f"📂 Vagas no histórico: {len(historico)}")

    # Vagas novas: no atual mas não no histórico
    vagas_novas = vagas_atuais - historico

    # Atualizar histórico: remove vagas que sumiram e adiciona as novas
    historico_atualizado = (historico - (historico - vagas_atuais)) | vagas_novas
    # ou simplesmente: historico_atualizado = vagas_atuais

    salvar_historico(historico_atualizado)

    if vagas_novas:
        mensagem = f"📢 Novas vagas remotas no Grupo Boticário ({datetime.now().strftime('%d/%m %H:%M')}):\n\n"
        for vaga in sorted(vagas_novas):
            mensagem += f"🔹 {vaga}\n"
        enviar_mensagem(mensagem)
    else:
        print("ℹ️ Nenhuma vaga nova encontrada. Nada será enviado.")

if __name__ == "__main__":
    main()
