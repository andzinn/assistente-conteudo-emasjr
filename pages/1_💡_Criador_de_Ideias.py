import streamlit as st
import google.generativeai as genai
import os
import re

st.set_page_config(layout="wide") 
st.title("💡 Criador de Ideias Estratégicas") 

@st.cache_resource
def load_models():
    try:
        api_key = os.environ["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except KeyError:
        st.error("Erro: GOOGLE_API_KEY não encontrada.")
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

def extrair_bloco_robusto(texto_completo, bloco_atual, proximo_bloco=None):
    if texto_completo is None: return None
    start_tag = f"[---{bloco_atual}_START---]"
    if proximo_bloco:
        end_tag_pattern = f"[---{proximo_bloco}_START---]"
    else:
        end_tag_pattern = f"[---{bloco_atual}_END---]"
    try:
        start_index = texto_completo.index(start_tag) + len(start_tag)
        captured_text = ""
        try:
            end_index = texto_completo.index(end_tag_pattern, start_index)
            captured_text = texto_completo[start_index:end_index]
        except ValueError:
            captured_text = texto_completo[start_index:]
        cleaned_text = re.sub(r'\[---.*?_END---\]', '', captured_text, flags=re.DOTALL)
        return cleaned_text.strip()
    except ValueError:
        return None

def gerar_ideias_detalhadas(tema, model):
    prompt = f"""
    Sua tarefa é gerar 5 ideias ESTRATÉGICAS de posts para Instagram sobre o tema "{tema}".
    Organize as ideias por funil: 2 para Topo (ToFu), 2 para Meio (MoFu), 1 para Fundo (BoFu).
    Para CADA uma das 5 ideias, você DEVE fornecer 4 informações, usando o seguinte formato de bloco com tags de início e fim:

    [---IDEIA_X_START---]
    **Título:** (Um título criativo e chamativo para o post)
    **Descrição:** (Uma breve descrição do conteúdo e da abordagem do post)
    **Formato Sugerido:** (Escolha UM: Reels, Carrossel de Imagens, ou Post Estático, com uma breve justificativa)
    **CTA (Chamada para Ação):** (Uma sugestão de CTA apropriada para o estágio do funil)
    [---IDEIA_X_END---]

    Substitua 'X' pelo número da ideia (1 a 5). Gere os blocos na ordem: IDEIA_1 (ToFu), IDEIA_2 (ToFu), IDEIA_3 (MoFu), IDEIA_4 (MoFu), IDEIA_5 (BoFu).
    Siga a formatação com precisão absoluta. Não adicione texto fora dos blocos.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Erro na chamada à API: {e}")
        return ""

# --- Interface Gráfica ---

def clear_ideas():
    if 'generated_ideas_raw' in st.session_state:
        st.session_state.generated_ideas_raw = None

tema_input = st.text_input(
    "Digite o tema principal para as ideias de post:",
    placeholder="Ex: Marketing para engenharia",
    on_change=clear_ideas
)

model_choice = st.radio(
    "Escolha o Modelo de IA para a Geração:",
    ("Pro (Mais Criativo)", "Flash (Mais Rápido)"),
    horizontal=True,
    on_change=clear_ideas
)

button_label = "Gerar Novas Ideias" if 'generated_ideas_raw' in st.session_state and st.session_state.generated_ideas_raw else "Gerar Ideias"

if st.button(button_label):
    if tema_input:
        selected_model_name = "Pro" if "Pro" in model_choice else "Flash"
        model_to_use = model_pro if selected_model_name == "Pro" else model_flash
        
        with st.spinner(f"Gerando ideias estratégicas com o Gemini {selected_model_name}..."):
            st.session_state.generated_ideas_raw = gerar_ideias_detalhadas(tema_input, model_to_use)
    else:
        st.warning("Por favor, digite um tema.")

# MUDANÇA: Lógica de Exibição com formatação aprimorada
if 'generated_ideas_raw' in st.session_state and st.session_state.generated_ideas_raw:
    raw_text = st.session_state.generated_ideas_raw
    
    ideias = [
        extrair_bloco_robusto(raw_text, f'IDEIA_{i}', f'IDEIA_{i+1}' if i < 5 else None)
        for i in range(1, 6)
    ]
    
    st.subheader("💡 Ideias Geradas:")
    
    tab_tofu, tab_mofu, tab_bofu = st.tabs(["🎯 Topo de Funil (ToFu)", "🤔 Meio de Funil (MoFu)", "💰 Fundo de Funil (BoFu)"])

    # Função auxiliar para extrair e formatar
    def display_ideia(ideia_content, default_title):
        if not ideia_content:
            st.warning(f"Não foi possível extrair {default_title}.")
            return

        titulo = re.search(r"\*\*Título:\*\*\s*(.*)", ideia_content)
        descricao = re.search(r"\*\*Descrição:\*\*\s*(.*)", ideia_content, re.DOTALL)
        formato = re.search(r"\*\*Formato Sugerido:\*\*\s*(.*)", ideia_content, re.DOTALL)
        cta = re.search(r"\*\*CTA \(Chamada para Ação\):\*\*\s*(.*)", ideia_content, re.DOTALL)

        expander_title = titulo.group(1).strip() if titulo else default_title

        with st.expander(f"**{expander_title}**", expanded=False):
            if descricao:
                st.markdown(f"**Descrição:**\n{descricao.group(1).strip()}")
            if formato:
                st.markdown(f"**Formato Sugerido:**\n_{formato.group(1).strip()}_") # Justificativa em itálico
            if cta:
                st.markdown(f"**CTA:**\n`{cta.group(1).strip()}`") # CTA em formato de código

    with tab_tofu:
        display_ideia(ideias[0], "Ideia ToFu 1")
        display_ideia(ideias[1], "Ideia ToFu 2")

    with tab_mofu:
        display_ideia(ideias[2], "Ideia MoFu 1")
        display_ideia(ideias[3], "Ideia MoFu 2")

    with tab_bofu:
        display_ideia(ideias[4], "Ideia BoFu")


    st.divider()
    if st.checkbox("Mostrar resposta bruta da IA para depuração"):
        st.subheader("Resposta Bruta da IA")
        st.text(raw_text or "Nenhuma resposta foi gravada.")