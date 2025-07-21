import os
import requests

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

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

if __name__ == '__main__':
    enviar_mensagem('🤖 Teste simples diretamente pelo GitHub Actions.')
