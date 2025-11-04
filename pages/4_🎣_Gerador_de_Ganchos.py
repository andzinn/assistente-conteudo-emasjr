import streamlit as st
import google.generativeai as genai
import os
import re

st.set_page_config(layout="wide")
st.title("🎣 Gerador e Repositório de Ganchos v1.3")

# --- BANCO DE DADOS DE GANCHOS (v1.3 - sem mudanças) ---
HOOK_DATABASE = {
    "Declarações Impactantes e Provocativas": [
        {"text": "Tenho certeza de que você está cometendo esse erro agora...", "format": "Reels / Carrossel"},
        {"text": "Se você está fazendo isso, pare imediatamente.", "format": "Reels"},
        # ... (Todo o resto do seu banco de dados de ganchos) ...
        {"text": "Salve este post para mais tarde.", "format": "Qualquer Formato"},
    ]
}

# --- CÉREBRO DA IA (sem mudanças) ---
FORMULAS_CONTEXT = """
**Princípios da Fórmula 1 (Engajamento):**
- **Perguntas de Curiosidade:** Criar uma lacuna de conhecimento (ex: "Você sabia que...").
... (resto das fórmulas) ...
- **Tutorial Rápido (Antes e Depois):** Mostrar o resultado desejado logo nos primeiros segundos para provar o valor.
"""

# --- CARREGAMENTO DOS MODELOS (sem mudanças) ---
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

# NOVO: Copiamos o Parser Robusto do Analisador para este arquivo
def extrair_bloco_robusto(texto_completo, bloco_atual, proximo_bloco=None):
    if texto_completo is None: return None
    start_tag = f"[---{bloco_atual}_START---]"
    if proximo_bloco:
        end_tag_pattern = f"[---{proximo_bloco}_START---]"
    else:
        # Se for o último bloco, procuramos seu próprio _END
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

# --- FUNÇÕES DA IA ---

# MUDANÇA: Prompt do Criador (Tab 2) agora usa as tags [---BLOCO---]
def create_new_hook(tema, principios, model):
    prompt = f"""
    **Contexto:** Você é um copywriter de elite. Seu cérebro foi treinado com os seguintes princípios de psicologia de ganchos virais:
    {FORMULAS_CONTEXT}

    **Sua Tarefa:**
    Com base **apenas** nos princípios de "{', '.join(principios)}", crie **3 ganchos (títulos) novos e originais** para um post sobre o tema: "{tema}".

    **Para cada gancho gerado,** explique brevemente a **"Proposta de Conteúdo"** (o que desenvolver no post para que o gancho faça sentido).

    **Formato de Resposta (OBRIGATÓRIO):**
    Use este formato de bloco com tags OBRIGATORIAMENTE para CADA gancho:

    [---GANCHO_1_START---]
    **Gancho:** [Seu primeiro gancho]
    **Proposta de Conteúdo:** [Explicação breve do que abordar no post, qual o ângulo]
    [---GANCHO_1_END---]

    [---GANCHO_2_START---]
    **Gancho:** [Seu segundo gancho]
    **Proposta de Conteúdo:** [Explicação breve...]
    [---GANCHO_2_END---]

    [---GANCHO_3_START---]
    **Gancho:** [Seu terceiro gancho]
    **Proposta de Conteúdo:** [Explicação breve...]
    [---GANCHO_3_END---]
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Erro na chamada à API: {e}")
        return ""

# Função do Adaptador (Tab 3) - sem mudanças, já era robusta
def adapt_hook(tema, model):
    database_string = ""
    for category, hooks in HOOK_DATABASE.items():
        database_string += f"Categoria: {category}\n"
        for hook_obj in hooks:
            database_string += f"- {hook_obj['text']}\n"
        database_string += "\n"
    prompt = f"""
    ... (prompt do adaptador, sem mudanças) ...
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Erro na chamada à API: {e}")
        return ""

# --- INTERFACE DA FERRAMENTA ---

tab1, tab2, tab3 = st.tabs(["🗂️ Navegador do Repositório", "🧙‍♂️ Criador de Ganchos (IA)", "🔄 Adaptador de Ganchos (IA)"])

# --- Aba 1: Navegador do Repositório (sem mudanças) ---
with tab1:
    st.subheader("Explore o Repositório de Ganchos")
    st.markdown("Navegue pelas 11 categorias de ganchos comprovados. Use-os como inspiração ou copie-os diretamente.")
    
    categorias = list(HOOK_DATABASE.keys())
    categoria_escolhida = st.selectbox("Escolha uma Categoria:", categorias)
    
    if categoria_escolhida:
        st.markdown("---")
        for hook in HOOK_DATABASE[categoria_escolhida]:
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.info(hook['text'])
                st.caption(f"Formato Ideal Sugerido: {hook['format']}")
            with col2:
                if st.button("Copiar", key=hook['text']):
                    st.toast(f"'{hook['text']}' copiado!")

# --- Aba 2: Criador de Ganchos (IA) (INTERFACE ATUALIZADA) ---
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
        default=principios_opcoes[0:1]
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
                ganchos_gerados_raw = create_new_hook(tema_criador, principios_escolhidos, model_to_use)
                st.session_state.ganchos_gerados_raw = ganchos_gerados_raw # Salva para o debug

    # MUDANÇA: Lógica de exibição agora usa o parser
    if 'ganchos_gerados_raw' in st.session_state and st.session_state.ganchos_gerados_raw:
        raw_text = st.session_state.ganchos_gerados_raw
        
        gancho_1 = extrair_bloco_robusto(raw_text, 'GANCHO_1', 'GANCHO_2')
        gancho_2 = extrair_bloco_robusto(raw_text, 'GANCHO_2', 'GANCHO_3')
        gancho_3 = extrair_bloco_robusto(raw_text, 'GANCHO_3')

        st.markdown("---")
        st.subheader("Ganchos e Propostas de Conteúdo Gerados:")
        
        if gancho_1:
            st.markdown(gancho_1)
            st.divider()
        if gancho_2:
            st.markdown(gancho_2)
            st.divider()
        if gancho_3:
            st.markdown(gancho_3)

        # Debugger opcional
        if st.checkbox("Mostrar resposta bruta (Criador)", key="debug_criador"):
            st.text(raw_text or "Nenhuma resposta foi gravada.")

# --- Aba 3: Adaptador de Ganchos (IA) (sem mudanças) ---
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
