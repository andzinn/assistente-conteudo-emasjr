import streamlit as st
import google.generativeai as genai
import os
import re

st.set_page_config(layout="wide")
st.title("🎣 Gerador e Repositório de Ganchos")

# --- BANCO DE DADOS DE GANCHOS (O SEU REPOSITÓRIO) ---
# Eu transformei sua lista em um dicionário Python
HOOK_DATABASE = {
    "Declarações Impactantes e Provocativas": [
        "Tenho certeza de que você está cometendo esse erro agora...",
        "Se você está fazendo isso, pare imediatamente.",
        "Esqueça o que você aprendeu. Isso funciona.",
        "Isso pode ser a coisa mais importante que compartilho o ano todo.",
        "Isso mudou meus resultados da noite para o dia...",
        "A solução mais simples é geralmente a melhor.",
        "A maioria das pessoas complica isso, mas é bem simples...",
        "Parece ilegal saber disso.",
        "Eu NÃO esperava por isso...",
        "O/A ____ que eu não esperava.",
        "Você precisa disso.",
        "Isso vai mudar sua vida.",
        "Isso vai explodir sua mente.",
        "Isso não é uma piada.",
        "Isso pode te chocar, mas...",
        "Alguém tinha que dizer...",
        "Este truque vai te economizar horas.",
        "Esta dica vai explodir sua mente.",
        "Eu não sei se você está pronto(a) para ouvir isso!",
        "Isso vai mudar como você pensa sobre...",
        "Você precisa ouvir isso hoje...",
        "Isso não é um treinamento.",
        "Isso não pode ser real.",
        "A única coisa que odeio sobre [isso] mas que funciona.",
        "Não é sobre [isso], faça isso em vez disso.",
        "Você não pode esperar [isso] sem [isso]."
    ],
    "Perguntas de Curiosidade": [
        "Qual é a verdadeira razão pela qual você não está crescendo?",
        "Quer saber a estratégia que ninguém está falando sobre?",
        "Como seria finally alcançar [resultado desejado]?",
        "Por que isso sempre acontece com [público específico]?",
        "Você está sabotando seu crescimento sem perceber?",
        "Você sabia ____?",
        "Quer saber algo louco?",
        "Por que não há mais pessoas falando sobre...",
        "Já se perguntou, ____?",
        "Quem mais faz isso?",
        "Você deveria [fazer isso ou aquilo]?",
        "Isto ou aquilo?",
        "Podemos falar sobre [isso]?"
    ],
    "Resolução de Problemas e Hacks": [
        "O truque que resolveu tudo de uma vez...",
        "Finalmente – uma maneira fácil de conseguir [resultado].",
        "Diga adeus a [problema] de uma vez por todas.",
        "Isso funcionou para mim quando nada mais deu certo.",
        "Está lutando com [problema]? Faça isso no lugar.",
        "Como melhorar instantaneamente ____",
        "Como nunca ficar sem ____",
        "Truque rápido...",
        "Lutando com ____? Você vai querer salvar isso.",
        "Como ____ de graça.",
        "Economize tempo e dinheiro ao ____",
        "A melhor maneira de ____",
        "Como conseguir [isso] com meu sistema simples que [resolve isso]",
        "Como parar de [fazer isso] da maneira fácil",
        "A maneira preguiçosa de [aprender isso]",
        "A maneira simples de [fazer isso]",
        "O que fazer sobre [este problema]",
        "A maneira sem estresse de [alcançar isso]",
        "O sistema que eu uso para [resolver este problema]",
        "Como [alcançar isso]",
        "Em vez de fazer [isso], faça [isso]",
        "O que realmente importa para [resolver este problema]",
        "Como [alcançar isso] agora mesmo",
        "A estratégia que ninguém está usando para [alcançar isso]"
    ],
    "Listas e Dicas Numeradas": [
        "Esse método é 10x melhor do que [conselho comum].",
        "7 maneiras de ganhar mais ____",
        "Meus 5 ____ favoritos",
        "Top 3 ____ que vocês estão amando",
        "Minhas 5 melhores dicas para ____",
        "5 ____ indispensáveis",
        "7 coisas que você não sabia que precisava de ____",
        "3 dicas simples de ____ que mudaram meu/minha ____",
        "5 ____ que estão custando caro para você.",
        "3 dicas comprovadas para ____.",
        "Cuidado com essas três coisas...",
        "3 razões pelas quais você deveria ____",
        "7 fatos desmistificadores sobre ____",
        "5 coisas que eu faria se estivesse começando de novo.",
        "Cinco ____ que você pode fazer agora mesmo para melhorar ____",
        "Três coisas that made ____ mais fácil.",
        "3 dicas para resolver [isso]",
        "3 razões por que [isso]",
        "3 coisas para [fazer isso]",
        "Dicas essenciais para [alcançar isso] sem [isso]",
        "3 estratégias para [alcançar isso]",
        "5 coisas para [resolver isso]",
        "5 ideias para [resolver este problema]",
        "5 maneiras de [fazer isso]",
        "7 tipos de [coisas do nicho]",
        "3 dicas para [fazer isso]",
        "Truque fácil para [resolver isso] em 3 passos",
        "10 coisas que você precisa saber [sobre este tópico]",
        "7 passos para ir de [isso] para [isso]",
        "O que fazer e o que não fazer"
    ],
    "Storytelling e Experiência Pessoal": [
        "Eu estava travado até descobrir isso...",
        "O momento que mudou tudo para mim foi...",
        "Aqui está o que ninguém me contou quando comecei...",
        "Esse único erro quase me custou [resultado].",
        "Eu tentei de tudo... até encontrar o que realmente funcionou.",
        "Eu finalmente cedi...",
        "Eu estava errado(a)...",
        "Erros que cometi quando ____",
        "Eu tenho uma confissão a fazer...",
        "Algo que aprendi recentemente...",
        "Se eu pudesse voltar no tempo, esta é a única coisa que eu diria a mim mesmo(a).",
        "O que aconteceu quando eu ____",
        "Não acredito que estou compartilhando isso...",
        "Eu acabei de descobrir...",
        "Eu não sabia que você podia...",
        "A maior lição que aprendi com [meu nicho]",
        "Meu cliente obteve [este resultado] fazendo [isso]",
        "Eu gostaria que alguém tivesse me dito [isso] antes de [fazer isso]",
        "Eu fiz [isso] por [x período de tempo] e [isto] foi o que aconteceu",
        "Eu parei de fazer [isso] e [isto] foi o que aconteceu",
        "Como meu cliente parou de [ter este problema]"
    ],
    "Construção de Confiança e Relatabilidade": [
        "Eu costumava acreditar em [mito], mas aqui está o que aprendi...",
        "Você não está sozinho se sente isso...",
        "Já sentiu [frustração comum]? Você não está louco.",
        "Foi exatamente assim que superei [luta específica].",
        "Apenas ____ vão entender isso.",
        "Isso soa como você?",
        "Você não ama quando ____",
        "Ok, eu sei o que você está pensando...",
        "Abaixe um dedo se você já...",
        "“Eu odeio ter que fazer isso” [responda a esse ponto de dor na legenda]"
    ],
    "Mitos, Segredos e Revelações": [
        "Aqui está a verdade que eu gostaria que alguém tivesse me contado antes.",
        "Você nunca vai adivinhar o que fez a diferença.",
        "Aqui está o que você estava perdendo o tempo todo...",
        "Eu tenho guardado um segredo...",
        "MITO: ____",
        "O que seu/sua ____ gostaria que você soubesse.",
        "Eu não ia compartilhar isso, mas...",
        "Vou lhe contar um segredinho.",
        "Aqui está a verdade sobre ____",
        "O que seu/sua _____ não está lhe dizendo.",
        "O/A ____ que ninguém está falando sobre.",
        "Verdadeiro ou falso...",
        "A verdade sobre [este tópico]",
        "O segredo para [isso]",
        "O que não te contam sobre [este tópico]",
        "A verdade sobre [meu nicho]",
        "A verdade sobre [isso]",
        "A verdade sobre encontrar [isso]",
        "O segredo para [este tópico suculento]",
        "Como aceitar que [esta verdade] é importante",
        "A verdade sobre [não fazer isso]",
        "Ninguém mais vai te dizer [isso]"
    ],
    "Desafio e Confronto (Opinião Impopular)": [
        "Você não pode mudar minha opinião ____ (afirme uma crença forte).",
        "Você está fazendo isso tudo errado.",
        "Opinião impopular: ____",
        "Você tem feito ____ errado.",
        "Não cometa esses erros.",
        "Pare de usar...",
        "Não se deixe enganar por...",
        "Pare...",
        "A razão pela qual você não está [alcançando isso] é porque você está fazendo [isso errado]",
        "O maior erro [é este], eis o porquê",
        "Erros a evitar ao [fazer isso]",
        "A razão pela qual [isso é ruim] e como consertar",
        "Opinião impopular [sobre isso]",
        "Pare de fazer [isso errado], aqui está minha estratégia",
        "Por que focar [nisso] é errado",
        "Coisas que você não deveria fazer se quer [isso]",
        "Por que eu [não acredito nisso]",
        "Por que eu não acho que [isso] é importante"
    ],
    "Cenários e 'Ponto de Vista' (POV)": [
        "O que seu/sua ____ diz sobre você.",
        "POV: Você decidiu levar [isso] a sério e agora você tem [este resultado]",
        "POV: Você finalmente [decidiu fazer isso] e agora [você tem isso]",
        "POV: Você [está fazendo isso] e se sente [assim]",
        "POV: Você [está alcançando isso] e só levou [este processo ou período]",
        "POV: Quando você finalmente parou de acreditar [nisso] e agora você [alcançou isso]",
        "POV: Aquele momento em que você [alcançou isso] e agora você comemora [isso]",
        "POV: Você finalmente [está fazendo isso] e se sente [assim]",
        "POV: Você decidiu [fazer isso] para que possa [fazer isso no seu tempo livre]"
    ],
    "Resultados e Transformação": [
        "Uma única coisa mudou minha vida.",
        "Como eu fui de ____ para ____",
        "Como eu [consegui isso] e parei de [fazer isso]",
        "Eu consigo alcançar [isso] todo santo dia usando meu [método]",
        "Como ir de [isso] para [isso]",
        "Eu faço [isso] para conseguir [isso]",
        "Como eu alcancei [isso]",
        "Eu obtenho [este resultado] todo dia, eis como",
        "Eu descobri como [fazer isso] sem [fazer isso]",
        "Como ter [isso] de forma consistente",
        "A estratégia por trás [deste resultado]",
        "Como eu consigo isso facilmente com [este segredinho]",
        "Como [fazer isso] nos próximos 30 dias",
        "Eu obtenho [este resultado] a cada [período de tempo]",
        "Como se tornar [isso] no próximo [período de tempo]"
    ],
    "Chamadas (CTAs) e Alertas": [
        "Este é o seu sinal para ____",
        "Assista até o final!",
        "Chamando todos os ____",
        "Este é o seu lembrete para ____",
        "Pare de rolar!",
        "Notícia de última hora!",
        "Lembrete:",
        "Qual deles é você A: ____ ou B: ____",
        "Alerta de nova tendência!",
        "Marque um amigo que precisa ver isso.",
        "Dica profissional: ___",
        "PSA (Aviso de Utilidade Pública): ____",
        "Sinais de que [você precisa x]",
        "Lembrete: [isso é possível] se você focar [nisso]",
        "Lembrete: Você não precisa ser [isso] para conseguir [isso]",
        "A coisa mais importante a fazer agora é [isso] ou [na legenda]"
    ]
}

# --- CÉREBRO DA IA (CONTEÚDO DAS SUAS FÓRMULAS) ---
FORMULAS_CONTEXT = """
**Princípios da Fórmula 1 (Engajamento):**
- **Perguntas de Curiosidade:** Criar uma lacuna de conhecimento (ex: "Você sabia que...").
- **Declarações Polêmicas:** Desafiar a sabedoria convencional (ex: "Pare de usar hashtags agora!").
- **Histórias Inacabadas (Efeito Zeigarnik):** Começar uma história intrigante (ex: "Eu perdi 10 mil seguidores quando...").
- **Promessas de Benefícios Claros:** Oferecer valor imediato (ex: "Aprenda a criar posts virais em 3 passos.").
- **Gatilhos Mentais:** Usar Escassez, Autoridade, Prova Social, Urgência.
- **Interação:** Fazer perguntas diretas e CTAs claros.

**Princípios da Fórmula 2 (Psicologia e Neurociência):**
- **Dopamina (Novidade):** Prometer uma recompensa, surpresa ou informação valiosa.
- **Dissonância Cognitiva (Surpresa):** Questionar crenças existentes para forçar o cérebro a buscar uma resolução (ex: "Seu método de [X] está te impedindo de [Y]").
- **Identificação (Relatabilidade):** Usar cenários com os quais o público se identifica (ex: "Quando você tenta [ação frustrante]...").
- **Tutorial Rápido (Antes e Depois):** Mostrar o resultado desejado logo nos primeiros segundos para provar o valor.
"""

# --- CARREGAMENTO DOS MODELOS (padrão) ---
@st.cache_resource
def load_models():
    try:
        api_key = os.environ["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except KeyError:
        st.error("Erro: A variável de ambiente GOOGLE_API_KEY não foi encontrada.")
        return None, None
    generation_config = {"temperature": 0.7, "max_output_tokens": 8192}
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]
    model_pro = genai.GenerativeModel("models/gemini-2.5-pro", generation_config=generation_config, safety_settings=safety_settings)
    model_flash = genai.GenerativeModel("models/gemini-2.5-flash", generation_config=generation_config, safety_settings=safety_settings)
    return model_pro, model_flash

model_pro, model_flash = load_models()
if not model_pro or not model_flash:
    st.stop()

# --- FUNÇÕES DA IA ---

# Função para o Criador (Tab 2)
def create_new_hook(tema, principios, model):
    prompt = f"""
    **Contexto:** Você é um copywriter de elite. Seu cérebro foi treinado com os seguintes princípios de psicologia de ganchos virais:
    {FORMULAS_CONTEXT}

    **Sua Tarefa:**
    Com base **apenas** nos princípios de "{', '.join(principios)}" (e em mais nada), crie **3 ganchos (títulos) novos e originais** para um post sobre o tema: "{tema}".
    
    Seja direto. Apresente os 3 ganchos em uma lista de bullet points (•).
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Erro na chamada à API: {e}")
        return ""

# Função para o Adaptador (Tab 3)
def adapt_hook(tema, model):
    # Converte o dicionário do repositório em uma string de texto para a IA ler
    database_string = ""
    for category, hooks in HOOK_DATABASE.items():
        database_string += f"Categoria: {category}\n"
        for hook in hooks:
            database_string += f"- {hook}\n"
        database_string += "\n"

    prompt = f"""
    Você é um assistente de IA especialista em marketing. Sua tarefa é encontrar o melhor gancho em um banco de dados e adaptá-lo para um novo tema.

    **1. Tema Alvo:**
    "{tema}"

    **2. Banco de Dados de Ganchos (Repositório):**
    {database_string}

    **Sua Tarefa (em 3 passos):**
    1.  **Análise:** Leia o "Tema Alvo" e entenda sua intenção (é um problema? uma dica? uma novidade?).
    2.  **Seleção:** Vasculhe o "Banco de Dados" e escolha o **UM** gancho (hook) que melhor se encaixa na intenção do tema.
    3.  **Adaptação:** Reescreva o gancho escolhido para que ele se encaixe perfeitamente no "{tema}". Substitua placeholders como [isso] ou ____.

    **Formato da Resposta:**
    **Gancho Original (da Categoria [Nome da Categoria]):**
    [O gancho que você escolheu]

    **Gancho Adaptado para o Tema:**
    [O novo gancho reescrito]
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Erro na chamada à API: {e}")
        return ""

# --- INTERFACE DA FERRAMENTA ---

# Cria as 3 abas
tab1, tab2, tab3 = st.tabs(["🗂️ Navegador do Repositório", "🧙‍♂️ Criador de Ganchos (IA)", "🔄 Adaptador de Ganchos (IA)"])


# --- Aba 1: Navegador do Repositório ---
with tab1:
    st.subheader("Explore o Repositório de Ganchos")
    st.markdown("Navegue pelas 11 categorias de ganchos comprovados. Use-os como inspiração ou copie-os diretamente.")
    
    # Lista de categorias
    categorias = list(HOOK_DATABASE.keys())
    categoria_escolhida = st.selectbox("Escolha uma Categoria:", categorias)
    
    if categoria_escolhida:
        st.markdown("---")
        # Mostra os ganchos da categoria escolhida
        for hook in HOOK_DATABASE[categoria_escolhida]:
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.info(hook)
            with col2:
                if st.button("Copiar", key=hook):
                    st.toast(f"'{hook}' copiado!")
                    # (Note: a cópia para a área de transferência real requer bibliotecas JS,
                    # mas o st.info facilita a seleção manual e o toast dá o feedback)

# --- Aba 2: Criador de Ganchos (IA) ---
with tab2:
    st.subheader("Crie Ganchos Novos com IA")
    st.markdown("Use a IA para gerar ganchos originais com base nos princípios psicológicos das Fórmulas 1 e 2.")
    
    tema_criador = st.text_input("Qual é o tema central do seu post?", placeholder="Ex: A importância do projeto estrutural", key="tema_criador")
    
    principios_opcoes = [
        "Perguntas de Curiosidade",
        "Declarações Polêmicas",
        "Histórias Inacabadas (Efeito Zeigarnik)",
        "Promessas de Benefícios Claros",
        "Identificação (Relatabilidade)",
        "Dissonância Cognitiva (Surpresa)",
        "Tutorial Rápido (Antes e Depois)"
    ]
    principios_escolhidos = st.multiselect(
        "Escolha 1 ou 2 princípios-chave das Fórmulas:",
        principios_opcoes,
        default=principios_opcoes[0:1] # Seleciona o primeiro por padrão
    )
    
    model_choice_criador = st.radio(
        "Escolha o Modelo de IA:",
        ("Pro (Mais Criativo)", "Flash (Mais Rápido)"),
        horizontal=True,
        key="model_criador"
    )
    
    if st.button("Gerar Novos Ganchos"):
        if not tema_criador or not principios_escolhidos:
            st.warning("Por favor, preencha o tema e escolha pelo menos um princípio.")
        else:
            model_to_use = model_pro if "Pro" in model_choice_criador else model_flash
            with st.spinner(f"Gerando ganchos com base em '{', '.join(principios_escolhidos)}'..."):
                ganchos_gerados = create_new_hook(tema_criador, principios_escolhidos, model_to_use)
                st.markdown("---")
                st.subheader("Ganchos Gerados pela IA:")
                st.markdown(ganchos_gerados)

# --- Aba 3: Adaptador de Ganchos (IA) ---
with tab3:
    st.subheader("Adapte um Gancho do Repositório com IA")
    st.markdown("Não sabe qual gancho do repositório usar? Dê um tema e deixe a IA encontrar e adaptar o melhor gancho para você.")
    
    tema_adaptador = st.text_input("Qual é o tema central do seu post?", placeholder="Ex: Os riscos de uma infiltração não tratada", key="tema_adaptador")

    model_choice_adaptador = st.radio(
        "Escolha o Modelo de IA:",
        ("Pro (Mais Inteligente)", "Flash (Mais Rápido)"),
        horizontal=True,
        key="model_adaptador"
    )

    if st.button("Encontrar e Adaptar Gancho"):
        if not tema_adaptador:
            st.warning("Por favor, preencha o tema.")
        else:
            model_to_use = model_pro if "Pro" in model_choice_adaptador else model_flash
            with st.spinner(f"IA está lendo o repositório e adaptando o melhor gancho para '{tema_adaptador}'..."):
                gancho_adaptado = adapt_hook(tema_adaptador, model_to_use)
                st.markdown("---")
                st.subheader("Sugestão da IA:")
                st.markdown(gancho_adaptado)
