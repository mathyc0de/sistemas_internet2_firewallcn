from flask import Flask, render_template, request
import requests
import re
import logging
from utils import filter_domains, filter_curse_words, load_data, read_logs

logging.basicConfig(
    level=logging.INFO,
    datefmt= '%Y-%m-%d %H:%M:%S',
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('log.txt', mode='a', encoding='utf-8'),
    ]
)

logging.getLogger("werkzeug").setLevel(logging.ERROR) # Evita os logs desnecessarios do flask

app = Flask(__name__)
PORT = 4500
BLOCKED_DOMAINS, BLOCKED_WORDS = load_data()


def pagina_erro(codigo: int, titulo: str, mensagem: str, url: str | None = None):
    return render_template(
        'erro.html',
        codigo=codigo,
        titulo=titulo,
        mensagem=mensagem,
        url=url,
    ), codigo


@app.route('/logs')
def view_logs():
    return render_template('logs.html', content=read_logs())


@app.route('/')
@app.route('/<path:url>')
def proxy(url=None):
    if not url:
        url = request.args.get('url')

    if not url:
        return render_template('formulario.html')
    
    full_url = url if re.match(r'^https?://', url) else 'https://' + url      # Gerei o regex com IA, fica mais elegante do que verificando com str.startswith()
    if filter_domains(full_url, BLOCKED_DOMAINS):
        logging.info(f"BLOQUEADO: {full_url}")
        return render_template('aviso_bloqueio.html', url=full_url), 403
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(full_url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        content = response.text
        
        filtered_content = filter_curse_words(content, BLOCKED_WORDS)
        
        if filtered_content != content:
            logging.info(f"FILTRADO: {full_url}")
        else:
            logging.info(f"PERMITIDO: {full_url}")
        
        return filtered_content, response.status_code
    
    except requests.exceptions.Timeout:
        logging.info(f"TIMEOUT: {full_url}")
        return pagina_erro(
            504,
            'Tempo esgotado',
            'O site demorou demais para responder. Tente novamente mais tarde.',
            full_url,
        )
    except requests.exceptions.ConnectionError:
        logging.info(f"ERRO_CONEXAO: {full_url}")
        return pagina_erro(
            502,
            'Falha na conexão',
            'Não foi possível conectar ao endereço solicitado. Verifique a URL e sua conexão.',
            full_url,
        )
    except Exception as e:
        logging.info(f"ERRO: {full_url} — {e}")
        return pagina_erro(
            500,
            'Erro interno',
            'Ocorreu um erro inesperado ao processar a requisição.',
            full_url,
        )

if __name__ == '__main__':
    print(" PROXY INICIADO\n")
    print(f"Ouvindo em http://localhost:{PORT}\n")
    app.run(host='0.0.0.0', port=PORT)