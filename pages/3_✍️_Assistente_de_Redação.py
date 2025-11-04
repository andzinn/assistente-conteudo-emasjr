import streamlit as st
import google.generativeai as genai
import os
import re

st.set_page_config(layout="wide")
st.title("✍️ Assistente de Redação (Copywriter)")

# --- Carregando os Modelos (mesma função robusta) ---
@st.cache_resource
def load_models():
    try:
        api_key = os.environ["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except KeyError:
        st.error("Erro: A variável de ambiente GOOGLE_API_KEY não foi encontrada.")
        return None, None
    
    generation_config = {"temperature": 0.7, "max_output_tokens": 8192} # Temp um pouco mais alta para criatividade
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

# --- Função Principal: O "Super-Prompt" de Redação ---
def get_redacao_estrategica(ideia, formato, tom_de_voz, objetivo, model):
    prompt = f"""
    Você é um Copywriter Sênior e Estrategista de Conteúdo da EMAS Jr., uma empresa júnior de engenharia civil e ambiental. Sua especialidade é traduzir conceitos técnicos complexos em conteúdo de marketing engajante para Instagram.

    **TAREFA:** Gerar o conteúdo de um post completo com base nas seguintes diretrizes:

    1.  **Ideia Central / Título:** "{ideia}"
    2.  **Formato Desejado:** "{formato}"
    3.  **Tom de Voz:** "{tom_de_voz}"
    4.  **Objetivo (Funil):** "{objetivo}"

    **REGRAS DE GERAÇÃO OBRIGATÓRIAS:**

    **SE O FORMATO FOR "Reels":**
    Gere um roteiro cena a cena, otimizado para prender a atenção. Use o seguinte formato:
    **Cena 1:**
    * **Visual:** (Descrição da imagem ou vídeo)
    * **Texto na Tela (Hook):** (Texto curto e impactante)
    **Cena 2:**
    * **Visual:** ...
    * **Texto na Tela:** ...
    (Continue por 4-5 cenas)
    **CTA (Narração ou Texto Final):** (Chamada para ação alinhada ao objetivo)

    **SE O FORMATO FOR "Carrossel de Imagens":**
    Gere o texto para um carrossel de 6 a 8 slides. Use o seguinte formato:
    **Slide 1 (Capa):**
    * **Título:** (Use a ideia central como base)
    * **Subtítulo/Gancho:** (Uma frase que gera curiosidade)
    **Slide 2 (O Problema):**
    * (Texto que apresenta o problema ou contexto)
    **Slide 3 (Desenvolvimento 1):**
    * (Primeiro ponto da solução ou explicação)
    (Continue por mais 2-3 slides de desenvolvimento)
    **Slide [Final-1] (Conclusão/Solução):**
    * (Apresenta a solução ou o "pulo do gato")
    **Slide [Final] (CTA):**
    * (Chamada para ação clara e alinhada ao objetivo)

    **SE O FORMATO FOR "Post Estático":**
    Gere uma legenda (copy) completa para um post de imagem única. Use o seguinte formato:
    **[GANCHO INICIAL]**
    (Uma ou duas frases de abertura fortes para parar a rolagem.)

    **[DESENVOLVIMENTO]**
    (O corpo da legenda, explicando a ideia central. Use parágrafos curtos e emojis para facilitar a leitura.)

    **[FECHAMENTO/PERGUNTA]**
    (Uma frase de transição ou pergunta para engajar.)

    **[CTA - CHAMADA PARA AÇÃO]**
    (A chamada para ação principal, alinhada ao objetivo.)

    **[HASHTAGS]**
    (5 hashtags relevantes)

    **INSTRUÇÃO FINAL:** Comece a resposta IMEDIATAMENTE com o formato solicitado. Não use saudações, introduções ou conclusões. Apenas o conteúdo.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Erro na chamada à API: {e}")
        return ""

# --- Interface do Streamlit ---
st.info("Esta ferramenta ajuda a transformar uma ideia estratégica em um post completo (roteiro ou legenda).")

# 1. Inputs do Usuário
ideia_input = st.text_input(
    "1. Cole a ideia, título ou tema central do post:", 
    placeholder="Ex: A Armadilha do Projeto Barato"
)
formato_choice = st.selectbox(
    "2. Escolha o Formato do Post:", 
    ("Reels", "Carrossel de Imagens", "Post Estático")
)
tom_choice = st.selectbox(
    "3. Escolha o Tom de Voz:", 
    ("Profissional-Consultivo", "Técnico-Educativo", "Inspirador (Cultura da Empresa)")
)
objetivo_choice = st.selectbox(
    "4. Escolha o Objetivo Principal (Funil):", 
    ("Gerar Curiosidade (ToFu)", "Construir Confiança (MoFu)", "Gerar Ação (BoFu)")
)
model_choice = st.radio(
    "5. Escolha o Modelo de IA:",
    ("Pro (Mais Criativo e Detalhado)", "Flash (Mais Rápido e Conciso)"),
    horizontal=True,
)

if 'generated_copy' not in st.session_state:
    st.session_state.generated_copy = None

# Limpa o resultado anterior se os inputs mudarem (para evitar confusão)
if st.session_state.generated_copy and (st.session_state.get('last_ideia') != ideia_input or st.session_state.get('last_formato') != formato_choice):
    st.session_state.generated_copy = None

if st.button(f"Gerar Redação para {formato_choice}", key="generate_copy_button"):
    if ideia_input:
        selected_model_name = "Pro" if "Pro" in model_choice else "Flash"
        model_to_use = model_pro if selected_model_name == "Pro" else model_flash

        with st.spinner(f"Criando seu {formato_choice} com o Gemini {selected_model_name}..."):
            redacao = get_redacao_estrategica(ideia_input, formato_choice, tom_choice, objetivo_choice, model_to_use)
            st.session_state.generated_copy = redacao
            # Salva os inputs para verificar se mudaram
            st.session_state.last_ideia = ideia_input
            st.session_state.last_formato = formato_choice
    else:
        st.warning("Por favor, insira uma ideia ou título para começar.")

# --- Exibição do Resultado ---
if st.session_state.generated_copy:
    st.divider()
    st.subheader(f"✅ Sugestão de {formato_choice} Gerada:")
    
    # Exibe o resultado. O markdown da IA (como **Cena 1:**) será renderizado
    st.markdown(st.session_state.generated_copy)
    
    # Adiciona um botão de "Copiar" para facilitar
    st.code(st.session_state.generated_copy, language=None)
    st.caption("Você pode copiar o texto do bloco acima.")
