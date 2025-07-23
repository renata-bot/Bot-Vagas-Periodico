import os
import requests

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
ARQUIVO_ESTADO = 'ultimo_estado.txt'

# URLs para consultar, com paginação de offset 0 e 100 para exemplo
URLS_BASE = [
    'https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=vaga&limit=100&offset={offset}&workplaceType=remote',
    'https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=analista&limit=100&offset={offset}&workplaceType=remote',
    'https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=pessoa&limit=100&offset={offset}&workplaceType=remote',
    'https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=especialista&limit=100&offset={offset}&workplaceType=remote',
    'https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=specialist&limit=100&offset={offset}&workplaceType=remote',
    'https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=product&limit=100&offset={offset}&workplaceType=remote',
    'https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=marketing&limit=100&offset={offset}&workplaceType=remote',
    'https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=gerente&limit=100&offset={offset}&workplaceType=remote',
    'https://portal.api.gupy.io/api/v1/jobs?careerPageName=Grupo%20Botic%C3%A1rio&jobName=coordenadora&limit=100&offset={offset}&workplaceType=remote',
]

def enviar_mensagem(texto):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': texto,
        'parse_mode': 'HTML'
    }
    response = requests.post(url, data=payload)
    print(f'Mensagem enviada com status {response.status_code}')
    print(response.text)

def carregar_estado_anterior():
    try:
        with open(ARQUIVO_ESTADO, 'r') as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()

def salvar_estado_atual(lista_vagas):
    with open(ARQUIVO_ESTADO, 'w') as f:
        f.write('\n'.join(lista_vagas))

def buscar_vagas_remotas():
    vagas_encontradas = set()

    # Para cada URL base, tentamos offset 0 e offset 100 (pode expandir para mais paginações se quiser)
    offsets = [0, 100]

    for base_url in URLS_BASE:
        for offset in offsets:
            url = base_url.format(offset=offset)
            print(f'🔎 Consultando: {url}')
            try:
                resposta = requests.get(url)
                resposta.raise_for_status()
                dados = resposta.json()

                vagas_na_url = 0
                for vaga in dados.get('data', []):
                    titulo = vaga.get('title', '').strip()
                    link = vaga.get('jobUrl', '').strip()
                    if titulo and link:
                        vaga_formatada = f'{titulo} | {link}'
                        vagas_encontradas.add(vaga_formatada)
                        vagas_na_url += 1
                print(f'📌 {vagas_na_url} vagas encontradas nesta URL')

                # Se achou menos que limit, provavelmente última página
                if vagas_na_url < 100:
                    break

            except Exception as e:
                print(f'❌ Erro ao buscar vagas em {url}: {e}')

    return sorted(vagas_encontradas)

def verificar_novas_vagas():
    vagas_atuais = buscar_vagas_remotas()
    print(f'Vagas atuais ({len(vagas_atuais)}): {vagas_atuais}')

    vagas_anteriores = carregar_estado_anterior()
    print(f'Vagas anteriores ({len(vagas_anteriores)}): {vagas_anteriores}')

    novas_vagas = [vaga for vaga in vagas_atuais if vaga not in vagas_anteriores]

    print(f'✅ Total de vagas únicas encontradas: {len(vagas_atuais)}')
    print(f'✅ Novas vagas detectadas: {len(novas_vagas)}')

    if novas_vagas:
        mensagem = '🚀 <b>Novas vagas remotas detectadas no Boticário:</b>\n\n'
        for vaga in novas_vagas:
            mensagem += f'👉 {vaga}\n\n'
        enviar_mensagem(mensagem)
    else:
        mensagem = 'ℹ️ Nenhuma nova vaga remota detectada no Boticário.'
        enviar_mensagem(mensagem)

    salvar_estado_atual(vagas_atuais)

if __name__ == '__main__':
    enviar_mensagem('🤖 Bot iniciado e verificando novas vagas...')
    try:
        verificar_novas_vagas()
    except Exception as e:
        enviar_mensagem(f'⚠️ Erro no bot: {e}')
