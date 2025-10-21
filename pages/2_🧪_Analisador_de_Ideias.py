import streamlit as st
import google.generativeai as genai
import os
import re

st.set_page_config(layout="wide")
st.title("🧪 Analisador de Ideias v1.1.3") # Incrementando a versão

@st.cache_resource
def load_models():
    try:
        api_key = os.environ["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except KeyError:
        st.error("Erro: A variável de ambiente GOOGLE_API_KEY não foi encontrada.")
        return None, None
    
    generation_config = {"temperature": 0.5, "max_output_tokens": 8192}
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

# O Parser Robusto (sem mudanças)
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

# O Super-Prompt v1.1 (sem mudanças)
def get_full_analysis(tema, ideia, model):
    prompt = f"""
    Sua tarefa é fazer uma análise completa e contextual da 'Ideia de Post' fornecida. A sua resposta DEVE ser uma única string contendo 10 blocos. Siga as instruções de CADA bloco com precisão absoluta. Não improvise formatos.

    **Tema Geral:** {tema}
    **Ideia de Post para Análise:** {ideia}

    [---CLASSIFICACAO_START---]
    (Responda APENAS com: Topo de Funil, Meio de Funil, ou Fundo de Funil)
    [---CLASSIFICACAO_END---]

    [---NOTAS_START---]
    (Avalie a ideia em 3 categorias, de 0 a 5. Use estrelas (★) para a nota e (☆) para o que falta. Siga este formato EXATAMENTE:
    - **Criatividade:** [estrelas, ex: ★★★☆☆]
    - **Potencial de Viralização:** [estrelas, ex: ★★★★★]
    - **Coesão com o Tema:** [estrelas, ex: ★★★★★])
    [---NOTAS_END---]

    [---JUSTIFICATIVA_START---]
    (Forneça uma justificativa completa, explicando o objetivo deste estágio do funil e como a ideia se alinha perfeitamente a ele.)
    [---JUSTIFICATIVA_END---]

    [---FORMATO_START---]
    (Sugira o formato de post ideal, escolhendo UMA das seguintes três opções: Reels, Carrossel de Imagens, ou Post Estático. Justifique brevemente.)
    [---FORMATO_END---]

    [---FORMATO_TRANSFORM_START---]
    (Com base no formato que você sugeriu no bloco 'FORMATO', explique como adaptar a ideia para os outros dois formatos. Para cada formato, sugira um novo Título de Post otimizado.
    Use este formato EXATAMENTE:
    - **Para [Formato A]:** Título: [Seu Título para o Formato A]. Abordagem: [Sua explicação].
    - **Para [Formato B]:** Título: [Seu Título para o Formato B]. Abordagem: [Sua explicação].)
    [---FORMATO_TRANSFORM_END---]

    [---CONTEUDO_START---]
    (Sugira um título otimizado e crie uma lista detalhada de tópicos e sugestões para o conteúdo do post.)
    [---CONTEUDO_END---]

    [---HASHTAGS_START---]
    (Liste EXATAMENTE 5 hashtags altamente relevantes para o tema e a ideia. Coloque cada hashtag em uma nova linha.)
    [---HASHTAGS_END---]

    [---PROTIP_START---]
    (Ofereça uma 'Dica de Mestre' estratégica e elaborada sobre uma tática ou perspectiva única para maximizar o impacto do post.)
    [---PROTIP_END---]

    [---TRANSFORMACOES_START---]
    (Explique detalhadamente como adaptar ESTA MESMA IDEIA para os outros dois estágios do funil, com exemplos claros.)
    [---TRANSFORMACOES_END---]

    [---META_DESCRICAO_START---]
    (Este bloco é oculto. Escreva um prompt de comando para uma IA, instruindo-a a "Gerar 5 ideias de post (2 ToFu, 2 MoFu, 1 BoFu) inspiradas na seguinte ideia analisada: [resumo da ideia, tema, funil e formato sugerido].")
    [---META_DESCRICAO_END---]
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Erro na chamada à API: {e}")
        return ""

# MUDANÇA: Prompt das dicas de 5 estrelas atualizado para "Título Ideal"
def get_five_star_tips(tema, ideia, notas, model):
    prompt = f"""
    **Contexto:** Uma ideia de post foi analisada com as seguintes notas:
    - Tema: "{tema}"
    - Ideia: "{ideia}"
    - Avaliação: {notas}

    **Sua Tarefa:** Agir como um consultor de conteúdo. Para CADA categoria (Criatividade, Potencial de Viralização) que NÃO recebeu 5 estrelas, forneça:
    1.  **Diagnóstico:** Explique brevemente (1 frase) por que a nota não foi máxima.
    2.  **Ação Concreta:** Sugira uma mudança específica e prática para melhorar (1 frase).

    **Após** as análises individuais, proponha UM **Título Ideal (5 Estrelas)** que incorpore as melhorias sugeridas para maximizar Criatividade e Viralização.

    **Formato da Resposta:** Use bullet points para cada categoria a ser melhorada (com Diagnóstico e Ação). No final, apresente o título com o marcador "**Título Ideal (5 Estrelas):**". Seja direto e acionável. Não use saudações.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Erro ao gerar dicas: {e}")
        return ""

# --- INTERFACE E LÓGICA PRINCIPAL ---

def clear_results():
    if 'show_results' in st.session_state:
        st.session_state.show_results = False
    if 'prompt_mae_gerado' in st.session_state:
        st.session_state.prompt_mae_gerado = None
    if 'five_star_tips' in st.session_state:
        st.session_state.five_star_tips = None

tema_geral_input = st.text_input("Qual o tema geral ou área de atuação?", placeholder="Construção Civil", on_change=clear_results)
ideia_input = st.text_input("Cole aqui o título ou a ideia de post que você quer analisar:", placeholder="Tendências na construção civil", on_change=clear_results)
model_choice = st.radio(
    "Escolha o Modelo de IA para a Análise:",
    ("Pro (Mais Detalhado)", "Flash (Mais Rápido)"),
    horizontal=True,
    index=0,
    on_change=clear_results
)
button_label = "Reanalisar Ideia" if 'show_results' in st.session_state and st.session_state.show_results else "Analisar Ideia"

if st.button(button_label, key="analyze_button"):
    if tema_geral_input and ideia_input:
        
        selected_model_name = "Pro" if "Pro" in model_choice else "Flash"
        model_to_use = model_pro if selected_model_name == "Pro" else model_flash
        
        st.session_state.current_tema = tema_geral_input
        st.session_state.current_ideia = ideia_input
        st.session_state.model_in_use = model_to_use

        with st.spinner(f"Analisando sua ideia com o Gemini {selected_model_name}..."):
            raw_response = get_full_analysis(tema_geral_input, ideia_input, model_to_use)
            st.session_state.raw_response = raw_response
        
        st.session_state.show_results = True
        st.session_state.five_star_tips = None 
    else:
        st.warning("Por favor, preencha ambos os campos.")

if 'show_results' in st.session_state and st.session_state.show_results:
    response_text = st.session_state.get('raw_response', "")

    r = {
        'classification': extrair_bloco_robusto(response_text, 'CLASSIFICACAO', 'NOTAS'),
        'notas': extrair_bloco_robusto(response_text, 'NOTAS', 'JUSTIFICATIVA'),
        'justification': extrair_bloco_robusto(response_text, 'JUSTIFICATIVA', 'FORMATO'),
        'format': extrair_bloco_robusto(response_text, 'FORMATO', 'FORMATO_TRANSFORM'),
        'format_transform': extrair_bloco_robusto(response_text, 'FORMATO_TRANSFORM', 'CONTEUDO'),
        'content': extrair_bloco_robusto(response_text, 'CONTEUDO', 'HASHTAGS'),
        'hashtags': extrair_bloco_robusto(response_text, 'HASHTAGS', 'PROTIP'),
        'pro_tip': extrair_bloco_robusto(response_text, 'PROTIP', 'TRANSFORMACOES'),
        'transformations': extrair_bloco_robusto(response_text, 'TRANSFORMACOES', 'META_DESCRICAO'),
        'meta_descricao': extrair_bloco_robusto(response_text, 'META_DESCRICAO')
    }
    
    if r.get('meta_descricao'):
        st.session_state.prompt_mae_gerado = r['meta_descricao']
    if r.get('notas'):
        st.session_state.current_notas = r['notas'] 

    st.subheader("🔬 Análise Estratégica da sua Ideia:")
    st.divider()
    
    # MUDANÇA: Rebalanceamento do Layout
    col1, col2 = st.columns(2) # Todas as linhas agora são 50/50
    
    with col1:
        st.markdown("**Classificação**"); st.metric(label="", value=r.get('classification') or "Não encontrado", label_visibility="collapsed")
        st.markdown("**Avaliação da Ideia**"); st.markdown(r.get('notas') or "Não encontrado.") 
        
        if 'current_notas' in st.session_state:
            if st.button("Ver dicas para 5 estrelas ★"):
                with st.spinner("Gerando dicas de melhoria..."):
                    model_to_use = st.session_state.model_in_use
                    tips = get_five_star_tips(
                        st.session_state.current_tema,
                        st.session_state.current_ideia,
                        st.session_state.current_notas,
                        model_to_use
                    )
                    st.session_state.five_star_tips = tips
        
        st.markdown("**Formato Ideal Sugerido**"); st.success(r.get('format') or "Não encontrado.", icon="🎨")
        st.markdown("**Sugestões de Hashtags**"); st.info(r.get('hashtags') or "Não encontrado.", icon="#️⃣")
        
        # MUDANÇA: "Sugestões de Conteúdo" movido para col1
        st.markdown("**Sugestões de Conteúdo**"); st.info(r.get('content') or "Não encontrado.", icon="📄")


    with col2:
        st.markdown("**Dica de Mestre**"); st.info(r.get('pro_tip') or "Não encontrado.", icon="💡")
        st.markdown("**Justificativa e Aula**"); st.success(r.get('justification') or "Não encontrado.", icon="🎯")
        
        # MUDANÇA: "Consultoria 5 Estrelas" agora na col2
        if 'five_star_tips' in st.session_state and st.session_state.five_star_tips:
            st.markdown("**Consultoria 5 Estrelas**")
            st.info(st.session_state.five_star_tips, icon="✨") 

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**Reaproveitamento (Outros Formatos)**"); st.info(r.get('format_transform') or "Não encontrado.", icon="♻️")
    with col4:
        st.markdown("**Reaproveitamento (Outros Níveis de Funil)**"); st.warning(r.get('transformations') or "Não encontrado.", icon="🔄")

    st.divider()
    if st.checkbox("Mostrar resposta bruta da IA para depuração"):
        st.subheader("Resposta Bruta da IA")
        st.text(st.session_state.get('raw_response', 'Nenhuma resposta foi gravada.'))