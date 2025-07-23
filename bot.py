import requests
import json
import os
from datetime import datetime
from telegram import Bot
from bs4 import BeautifulSoup

# === CONFIGURAÇÕES ===
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
ARQUIVO_HISTORICO = 'historico_vagas.json'

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
    if os.path.exists(ARQUIVO_HISTORICO):
        with open(ARQUIVO_HISTORICO, 'r', encoding='utf-8') as f:
            try:
                return set(json.load(f))
            except json.JSONDecodeError:
                print("⚠️ Erro ao carregar o histórico (formato inválido). Começando do zero.")
                return set()
    return set()

def salvar_historico(vagas):
    with open(ARQUIVO_HISTORICO, 'w', encoding='utf-8') as f:
        json.dump(sorted(list(vagas)), f, indent=2, ensure_ascii=False)

def enviar_mensagem(mensagem):
    bot = Bot(token=TOKEN)
    resposta = bot.send_message(chat_id=CHAT_ID, text=mensagem)
    if resposta:
        print("✅ Mensagem enviada com status 200")

def main():
    print("🚀 Iniciando busca de vagas remotas do Grupo Boticário...")

    vagas_atuais = buscar_vagas_remotas()
    historico = carregar_historico()

    novas_vagas = vagas_atuais - historico
    vagas_removidas = historico - vagas_atuais  # só para controle, não notifica

    print(f"\n📋 Vagas atuais: {len(vagas_atuais)}")
    print(f"🕘 Vagas no histórico: {len(historico)}")
    print(f"✨ Novas vagas detectadas: {len(novas_vagas)}")
    print(f"❌ Vagas removidas: {len(vagas_removidas)}")

    if novas_vagas:
        mensagem = f"📢 Novas vagas remotas no Grupo Boticário ({datetime.now().strftime('%d/%m %H:%M')}):\n\n"
        for vaga in sorted(novas_vagas):
            mensagem += f"🔹 {vaga}\n"
        enviar_mensagem(mensagem)
    else:
        print("✅ Nenhuma vaga nova detectada. Nenhuma mensagem enviada.")

    salvar_historico(vagas_atuais)

if __name__ == "__main__":
    main()
