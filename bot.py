import os
import json
import requests
from datetime import datetime

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
ESTADO_PATH = "ultimo_estado.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

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

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=payload)
    print("Mensagem enviada com status", response.status_code)
    print(response.text)

def buscar_vagas():
    todas_vagas = []

    for url in URLS:
        print(f"🔎 Consultando: {url}")
        try:
            resposta = requests.get(url, headers=HEADERS)
            resposta.raise_for_status()
            dados = resposta.json()
            vagas = dados.get("data", [])
            print(f"📌 {len(vagas)} vagas encontradas nesta URL")
            for vaga in vagas:
                titulo = vaga.get("title", "").strip()
                url_vaga = vaga.get("jobUrl", "").strip()
                if titulo and url_vaga:
                    todas_vagas.append((titulo, url_vaga))
        except Exception as e:
            print(f"❌ Erro ao consultar {url}: {e}")
    return todas_vagas

def carregar_estado_anterior():
    if os.path.exists(ESTADO_PATH):
        with open(ESTADO_PATH, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def salvar_estado_atual(vagas):
    with open(ESTADO_PATH, "w", encoding="utf-8") as f:
        json.dump(list(vagas), f, ensure_ascii=False, indent=2)

def main():
    enviar_telegram("🤖 Bot iniciado e verificando novas vagas...")

    vagas_atuais = buscar_vagas()
    vagas_atuais_set = set(f"{titulo} - {url}" for titulo, url in vagas_atuais)

    vagas_anteriores = carregar_estado_anterior()

    print(f"Vagas atuais ({len(vagas_atuais_set)}): {list(vagas_atuais_set)[:2]}...")
    print(f"Vagas anteriores ({len(vagas_anteriores)}): {list(vagas_anteriores)[:2]}...")

    novas_vagas = vagas_atuais_set - vagas_anteriores

    print(f"✅ Total de vagas únicas encontradas: {len(vagas_atuais_set)}")
    print(f"✅ Novas vagas detectadas: {len(novas_vagas)}")

    if novas_vagas:
        mensagem = f"🚨 <b>{len(novas_vagas)} nova(s) vaga(s) remota(s) encontrada(s) no Boticário</b>:\n\n"
        for vaga in novas_vagas:
            mensagem += f"🔹 {vaga}\n"
        enviar_telegram(mensagem)
    else:
        enviar_telegram("ℹ️ Nenhuma nova vaga remota detectada no Boticário.")

    salvar_estado_atual(vagas_atuais_set)

if __name__ == "__main__":
    main()
