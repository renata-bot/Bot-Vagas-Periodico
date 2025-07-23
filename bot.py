import os
import requests

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
ARQUIVO_ESTADO = 'ultimo_estado.txt'

URLS = [
    "https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=vaga&limit=100&offset=0&workplaceType=remote",
    "https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=analista&limit=100&offset=0&workplaceType=remote",
    "https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=pessoa&limit=100&offset=0&workplaceType=remote",
    "https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=especialista&limit=100&offset=0&workplaceType=remote",
    "https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=specialist&limit=100&offset=0&workplaceType=remote",
    "https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=product&limit=100&offset=0&workplaceType=remote",
    "https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=marketing&limit=100&offset=0&workplaceType=remote",
    "https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=gerente&limit=100&offset=0&workplaceType=remote",
    "https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=coordenadora&limit=100&offset=0&workplaceType=remote",
]

def enviar_mensagem(texto):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': texto, 'parse_mode': 'HTML'}
    response = requests.post(url, data=payload)
    print(f'Mensagem enviada com status {response.status_code}')
    print(response.text)

def carregar_estado_anterior():
    try:
        with open(ARQUIVO_ESTADO, 'r') as f:
            return f.read().splitlines()
    except FileNotFoundError:
        return []

def salvar_estado_atual(lista_vagas):
    with open(ARQUIVO_ESTADO, 'w') as f:
        f.write('\n'.join(lista_vagas))

def buscar_vagas_remotas():
    vagas_encontradas = set()

    for url in URLS:
        try:
            resposta = requests.get(url)
            resposta.raise_for_status()
            dados = resposta.json()
            for vaga in dados.get('data', []):
                titulo = vaga.get('title', '').strip()
                link = vaga.get('jobUrl', '').strip()
                if titulo and link:
                    vagas_encontradas.add(f'{titulo} | {link}')
        except Exception as e:
            print(f"Erro ao buscar vagas em {url}: {e}")

    return sorted(vagas_encontradas)

def verificar_novas_vagas():
    vagas_atuais = buscar_vagas_remotas()
    vagas_anteriores = carregar_estado_anterior()
    novas_vagas = [vaga for vaga in vagas_atuais if vaga not in vagas_anteriores]

    if novas_vagas:
        mensagem = '🚀 <b>Novas vagas remotas detectadas no Boticário:</b>\n\n'
        for vaga in novas_vagas:
            mensagem += f'👉 {vaga}\n\n'
        enviar_mensagem(mensagem)
        salvar_estado_atual(vagas_atuais)
    else:
        print('Nenhuma nova vaga encontrada.')

if __name__ == '__main__':
    enviar_mensagem('🤖 Bot iniciado e verificando novas vagas...')
    try:
        verificar_novas_vagas()
    except Exception as e:
        enviar_mensagem(f'⚠️ Erro no bot: {e}')
