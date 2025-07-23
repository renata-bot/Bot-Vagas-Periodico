import requests
import json
import os
from datetime import datetime
from telegram import Bot
from bs4 import BeautifulSoup

# === CONFIGURAÇÕES ===
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
HISTORICO_PATH = "historico_vagas.json"

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
        except Exception as e:
            print(f"❌ Erro ao buscar vagas em {url}: {e}")
    return vagas_encontradas

def carregar_historico():
    if os.path.exists(HISTORICO_PATH):
        try:
            with open(HISTORICO_PATH, "r", encoding="utf-8") as f:
                data = f.read().strip()
                if not data:
                    return set()
                return set(json.loads(data))
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️ Erro ao ler histórico. Ignorando conteúdo inválido: {e}")
            return set()
    return set()

def salvar_historico(vagas):
    with open(HISTORICO_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(list(vagas)), f, ensure_ascii=False, indent=2)

def enviar_mensagem(texto):
    bot = Bot(token=TOKEN)
    max_len = 4000  # Limite seguro (máx é 4096)
    partes = [texto[i:i+max_len] for i in range(0, len(texto), max_len)]
    for parte in partes:
        bot.send_message(chat_id=CHAT_ID, text=parte)
    print("✅ Mensagem enviada")

def main():
    print("🚀 Iniciando busca de vagas remotas do Grupo Boticário...")

    vagas_atuais = buscar_vagas_remotas()
    historico = carregar_historico()

    novas_vagas = vagas_atuais - historico
    vagas_removidas = historico - vagas_atuais

    print(f"\n📋 Vagas atuais: {len(vagas_atuais)}")
    print(f"🕘 Vagas no histórico: {len(historico)}")
    print(f"✨ Novas vagas detectadas: {len(novas_vagas)}")
    print(f"❌ Vagas removidas: {len(vagas_removidas)}")

    if novas_vagas:
        mensagem = f"📢 Novas vagas remotas no Grupo Boticário ({datetime.now().strftime('%d/%m %H:%M')}):\n\n"
        for vaga in sorted(novas_vagas):
            mensagem += f"🔹 {vaga}\n"
        enviar_mensagem(mensagem)

    salvar_historico(vagas_atuais)

if __name__ == "__main__":
    main()
