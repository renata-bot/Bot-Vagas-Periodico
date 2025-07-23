import requests
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

def pegar_titulo_vaga(url):
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        h1 = soup.find('h1', class_='jumbotron__title')
        if h1:
            return h1.text.strip()
        else:
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
                if link:
                    titulo = pegar_titulo_vaga(link)
                    if titulo:
                        vagas_encontradas.add(f"{titulo} | {link}")
        except Exception as e:
            print(f"❌ Erro ao buscar vagas em {url}: {e}")
    return vagas_encontradas

def enviar_mensagem(mensagem):
    bot = Bot(token=TOKEN)
    resposta = bot.send_message(chat_id=CHAT_ID, text=mensagem)
    if resposta:
        print("✅ Mensagem enviada com status 200")

def main():
    enviar_mensagem("🤖 Bot iniciado e listando vagas remotas do Grupo Boticário...")

    vagas_atuais = buscar_vagas_remotas()

    print(f"\n📋 Total de vagas encontradas: {len(vagas_atuais)}")
    for vaga in sorted(vagas_atuais):
        print(f"🔹 {vaga}")

    if vagas_atuais:
        mensagem = f"📢 Vagas remotas no Grupo Boticário ({datetime.now().strftime('%d/%m %H:%M')}):\n\n"
        for vaga in sorted(vagas_atuais):
            mensagem += f"🔹 {vaga}\n"
        enviar_mensagem(mensagem)
    else:
        enviar_mensagem("ℹ️ Nenhuma vaga remota encontrada no momento.")

if __name__ == "__main__":
    main()
