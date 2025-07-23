import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    wait = WebDriverWait(driver, 10)

    vagas_encontradas = []

    while True:
        # Espera os cards das vagas carregarem
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[class*="job-link"]')))

        links = driver.find_elements(By.CSS_SELECTOR, 'a[class*="job-link"]')

        for link in links:
            titulo = link.text.strip()
            url = link.get_attribute('href')
            if 'remoto' in titulo.lower() or 'home office' in titulo.lower():
                vaga_formatada = f'{titulo} | {url}'
                if vaga_formatada not in vagas_encontradas:
                    vagas_encontradas.append(vaga_formatada)

        # Tenta clicar no botão ">" para próxima página
        try:
            btn_proximo = driver.find_element(By.XPATH, '//button[contains(@aria-label,"Next")]')
            if btn_proximo.is_enabled():
                btn_proximo.click()
                time.sleep(3)  # espera a próxima página carregar
            else:
                break
        except Exception:
            # botão próximo não encontrado ou não clicável -> fim das páginas
            break

    driver.quit()
    return vagas_encontradas

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
