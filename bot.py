import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
VAGAS_URL = 'https://grupoboticario.gupy.io/'
ARQUIVO_ESTADO = 'ultimo_estado.txt'

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
            return f.read().splitlines()
    except FileNotFoundError:
        return []

def salvar_estado_atual(lista_vagas):
    with open(ARQUIVO_ESTADO, 'w') as f:
        f.write('\n'.join(lista_vagas))

def buscar_vagas_remotas():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    driver.get(VAGAS_URL)
    time.sleep(3)

    vagas = []

    while True:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        for link in soup.find_all('a'):
            href = link.get('href', '')
            titulo = link.get_text(strip=True)
            if ('remoto' in titulo.lower() or 'home office' in titulo.lower()) and '/jobs/' in href:
                vaga = f'{titulo} | https://grupoboticario.gupy.io{href}'
                if vaga not in vagas:
                    vagas.append(vaga)

        try:
            botao_proxima = driver.find_element(By.XPATH, "//button[text()='>']")
            if not botao_proxima.is_enabled():
                break
            botao_proxima.click()
            time.sleep(2)
        except:
            break

    driver.quit()
    return vagas

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
        mensagem = 'ℹ️ Nenhuma nova vaga remota detectada no Boticário.'
        enviar_mensagem(mensagem)
        print('Nenhuma nova vaga encontrada.')

if __name__ == '__main__':
    enviar_mensagem('🤖 Bot iniciado e verificando novas vagas...')
    try:
        verificar_novas_vagas()
    except Exception as e:
        enviar_mensagem(f'⚠️ Erro no bot: {e}')
