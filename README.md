# Proxy de Censura — Firewall CN

Aplicação web em **Flask** que funciona como proxy HTTP com duas camadas de filtro:

1. **Bloqueio de domínios** — sites da lista retornam HTTP 403 com página de aviso.
2. **Censura de palavras** — termos ofensivos no conteúdo das páginas permitidas são substituídos por `censurado`.

A interface inicial simula um portal de busca; o usuário informa a URL e navega pelo proxy.

---

## Requisitos

- Python 3.10 ou superior
- Conexão com a internet (para buscar sites externos)

---

## Instalação

### 1. Clone ou baixe o projeto

```bash
cd sistemas_internet2_firewallcn
```

### 2. Crie e ative o ambiente virtual

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

Pacotes principais: `flask`, `requests`. `gunicorn`

---

## Configuração das listas

As regras de bloqueio ficam em `data/` em formato JSON. **Reinicie o servidor** após alterar os arquivos (eles são carregados na inicialização).

### `data/blocked.json` — domínios bloqueados

Lista de strings com domínios ou partes de URL. Se algum item aparecer na URL solicitada, o acesso é negado.

```json
[
  "youtube.com",
  "facebook.com",
  "twitter.com"
]
```

**Como funciona:** o proxy verifica se cada entrada da lista está **contida** na URL (ex.: `youtube.com` bloqueia `https://www.youtube.com/watch?v=...`).

**Lista atual:** domínios extraídos da [Wikipedia — Websites bloqueados na China continental](https://pt.wikipedia.org/wiki/Websites_bloqueados_na_China_continental) (sites mais conhecidos da tabela principal).

### `data/words.json` — palavras censuradas

Lista de termos substituídos no HTML/texto das páginas permitidas.

```json
[
  "caralho",
  "porra",
  "vai tomar no cu"
]
```

**Como funciona:** busca case-insensitive; cada ocorrência vira `censurado`.

---

## Executar o proxy

Com o ambiente virtual ativo:

```bash
python app.py
```

Saída esperada:

```
 PROXY INICIADO

Ouvindo em http://localhost:4500
```

Acesse no navegador: **http://localhost:4500**

---

## Como usar

### Página inicial

Abra `http://localhost:4500/` e digite a URL no campo de busca (ex.: `https://www.python.org`), depois clique em **Acessar**.

### Formas de acesso direto

| Formato | Exemplo |
|---------|---------|
| Query string | `http://localhost:4500/?url=https://www.python.org` |
| Caminho | `http://localhost:4500/https://www.python.org` |
| Logs | `http://localhost:4500/logs` |

Se a URL não tiver `http://` ou `https://`, o proxy adiciona `https://` automaticamente.

### Site bloqueado

URLs que coincidem com `data/blocked.json` exibem a página `aviso_bloqueio.html` (HTTP 403) com o endereço bloqueado.

### Erros de conexão

Falhas ao buscar o site destino exibem a página `erro.html` com código HTTP correspondente:

| Código | Situação |
|--------|----------|
| 504 | Timeout (site demorou mais de 10 s) |
| 502 | Falha de conexão com o destino |
| 500 | Erro inesperado no proxy |

Todas incluem o botão **Voltar ao início** (`/`).

### Logs

Ações são registradas em `log.txt` e no terminal:

- `BLOQUEADO` — domínio na lista negra
- `FILTRADO` — página acessada, mas com palavras censuradas
- `PERMITIDO` — acesso sem alterações

**Visualização no navegador:** acesse **http://localhost:4500/logs** para ver o conteúdo bruto de `log.txt`. Também há um link “Ver logs” no rodapé da página inicial.

---

## Estrutura do projeto

```
Proxy/
├── app.py                 # Rotas Flask e lógica do proxy
├── utils.py               # Carregamento JSON, filtros de domínio e palavras
├── requirements.txt
├── data/
│   ├── blocked.json       # Domínios bloqueados
│   └── words.json         # Palavras censuradas
├── templates/
│   ├── formulario.html    # Página inicial (portal de busca)
│   ├── aviso_bloqueio.html
│   ├── erro.html          # Timeout, conexão e erros internos
│   └── logs.html          # Visualização do log de acessos
├── static/
│   ├── style.css
│   ├── china_flag.svg
│   ├── blocked.gif
│   ├── xi_jinping.jpg
│   └── emoji.png
└── log.txt                # Gerado em runtime (ignorado pelo Git)
```

---

## Uso de Inteligência Artificial

Este projeto utilizou IA (Cursor / assistente de código) nas etapas abaixo. A lógica de proxy foi revisada e corrigida manualmente quando necessário.

| Área | O que a IA fez | O que ficou manual |
|------|----------------|-------------------|
| **Interface (UI/UX)** | Redesign completo de `formulario.html` e `aviso_bloqueio.html`; criação de `static/style.css`; layout responsivo estilo portal de busca; página de bloqueio com GIF local | Ajustes de opacidade, posição das imagens decorativas e centralização do card |
| **`data/words.json`** | Geração da lista inicial de xingamentos em pt-BR | Revisão e manutenção da lista pelo grupo |
| **`data/blocked.json`** | Script de extração a partir da tabela da Wikipedia (página em português) | Validação dos domínios; remoção de duplicatas e entradas inválidas |
| **`app.py`** | Sugestão de regex para normalizar URL (`^https?://`) |
| **Assets visuais** | Posicionamento inicial aleatório de imagens na home | Correção de sobreposição (cantos fixos) e contraste do texto |

### Transparência

- A IA **não alterou** a regra de negócio principal: GET com `name="url"`, bloqueio por substring de domínio e substituição de palavras.
- Conteúdo sensível (listas de bloqueio e palavras) deve ser **revisado pelo grupo** antes de uso em ambiente real.
- Memes e imagens decorativas (`blocked.gif`, `xi_jinping.jpg`, `emoji.png`) foram escolhidos/adicionados no contexto do trabalho acadêmico sobre censura.

---

## Solução de problemas

| Problema | Possível causa |
|----------|----------------|
| Formulário não abre o site | Servidor precisa estar rodando; confira se a URL inclui o protocolo ou deixe o proxy adicionar `https://` |
| Todo site retorna bloqueio | Verifique se `filter_domains` está correto em `utils.py` e se a URL não contém acidentalmente um domínio da lista |
| Lista não atualiza | Reinicie `python app.py` após editar os JSON |
| Erro 502 / 504 | Site destino indisponível ou timeout (10 s); a página de erro oferece retorno à home |

---

## Licença / contexto acadêmico

Projeto desenvolvido para demonstração de proxy HTTP com filtros de conteúdo. Uso responsável e apenas em ambientes autorizados.
