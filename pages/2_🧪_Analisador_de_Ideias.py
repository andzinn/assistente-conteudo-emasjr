import streamlit as st
import google.generativeai as genai
import os
import re
import time # NOVO: Precisamos da biblioteca 'time' para o 'sleep'

st.set_page_config(layout="wide")
st.title("🧪 Analisador de Ideias v1.1.4")

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

# Parser Robusto (sem mudanças)
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

# NOVO: Função "segura" com Backoff Exponencial
def safe_generate_content(prompt, model, max_retries=3):
    """
    Tenta gerar conteúdo com o modelo, aplicando backoff exponencial
    em caso de erro de limite de taxa (429).
    Retorna o response.text em sucesso, ou None em falha.
    """
    wait_time = 1 # Começa esperando 1 segundo
    for i in range(max_retries):
        try:
            # Tenta a chamada de API
            response = model.generate_content(prompt)
            return response.text # Sucesso!
        except Exception as e:
            # Verifica se é um erro de limite de taxa
            # (A API do Google joga um erro genérico, mas o texto contém '429')
            if "429" in str(e):
                st.warning(f"Limite de taxa atingido para {model.model_name} (Tentativa {i+1}/{max_retries}). Esperando {wait_time}s...")
                time.sleep(wait_time)
                wait_time *= 2 # Backoff exponencial: 1s, 2s, 4s
            else:
                # Foi outro erro (ex: segurança, 500)
                st.error(f"Erro inesperado da API: {e}")
                return None # Não adianta tentar de novo
    
    # Se o loop terminar, todas as tentativas falharam
    st.error(f"Falha ao gerar conteúdo com {model.model_name} após {max_retries} tentativas.")
    return None

# O Super-Prompt v1.1 (sem mudanças)
def get_full_analysis_prompt(tema, ideia):
    return f"""
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
    (Forneça uma justificativa completa...)
    [---JUSTIFICATIVA_END---]
    [---FORMATO_START---]
    (Sugira o formato de post ideal... Justifique brevemente.)
    [---FORMATO_END---]
    [---FORMATO_TRANSFORM_START---]
    (Com base no formato... explique como adaptar...
    Use este formato EXATAMENTE:
    - **Para [Formato A]:** Título: [Seu Título para o Formato A]. Abordagem: [Sua explicação].
    - **Para [Formato B]:** Título: [Seu Título para o Formato B]. Abordagem: [Sua explicação].)
    [---FORMATO_TRANSFORM_END---]
    [---CONTEUDO_START---]
    (Sugira um título otimizado e crie uma lista detalhada...)
    [---CONTEUDO_END---]
    [---HASHTAGS_START---]
    (Liste EXATAMENTE 5 hashtags altamente relevantes...)
    [---HASHTAGS_END---]
    [---PROTIP_START---]
    (Ofereça uma 'Dica de Mestre' estratégica e elaborada...)
    [---PROTIP_END---]
    [---TRANSFORMACOES_START---]
    (Explique detalhadamente como adaptar ESTA MESMA IDEIA...)
    [---TRANSFORMACOES_END---]
    [---META_DESCRICAO_START---]
    (Este bloco é oculto. Escreva um prompt de comando para uma IA...)
    [---META_DESCRICAO_END---]
    """

# Função da "Consultoria 5 Estrelas" (sem mudanças na lógica do prompt)
def get_five_star_tips_prompt(tema, ideia, notas):
    return f"""
    **Contexto:** Uma ideia de post foi analisada com as seguintes notas:
    - Tema: "{tema}"
    - Ideia: "{ideia}"
    - Avaliação: {notas}

    **Sua Tarefa:** Agir como um consultor de conteúdo. Para CADA categoria (Criatividade, Potencial de Viralização) que NÃO recebeu 5 estrelas, forneça:
    1.  **Diagnóstico:** Explique brevemente (1 frase) por que a nota não foi máxima.
    2.  **Ação Concreta:** Sugira uma mudança específica e prática para melhorar (1 frase).

    **Após** as análises individuais, proponha UM **Título Ideal (5 Estrelas)** que incorpore as melhorias sugeridas para maximizar Criatividade e Viralização.
    **Formato da Resposta:** Use bullet points... No final, apresente o título com "**Título Ideal (5 Estrelas):**".
    """

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

# NOVO: Lógica de Botão com Redundância
if st.button(button_label, key="analyze_button"):
    if tema_geral_input and ideia_input:
        
        # 1. Define o modelo primário e de fallback
        if "Pro" in model_choice:
            primary_model = model_pro
            fallback_model = model_flash
            st.session_state.model_in_use = model_pro # Salva para o botão "5 estrelas"
        else:
            primary_model = model_flash
            fallback_model = model_pro
            st.session_state.model_in_use = model_flash
        
        st.session_state.current_tema = tema_geral_input
        st.session_state.current_ideia = ideia_input
        
        # 2. Gera o prompt
        prompt = get_full_analysis_prompt(tema_geral_input, ideia_input)

        # 3. Tenta a chamada com o modelo primário (com backoff embutido)
        with st.spinner(f"Analisando sua ideia com {primary_model.model_name}..."):
            raw_response = safe_generate_content(prompt, primary_model)
        
        # 4. Se falhar, tenta com o fallback
        if raw_response is None:
            st.warning(f"{primary_model.model_name} está sobrecarregado. Trocando automaticamente para {fallback_model.model_name}...")
            st.session_state.model_in_use = fallback_model # Atualiza o modelo em uso
            with st.spinner(f"Tentando com {fallback_model.model_name}..."):
                raw_response = safe_generate_content(prompt, fallback_model)
        
        # 5. Verifica se tudo falhou
        if raw_response is None:
            st.error("Falha crítica. Ambos os modelos (Pro e Flash) parecem estar indisponíveis ou sobrecarregados. Tente novamente mais tarde.")
            st.stop()
        
        # 6. Sucesso! Salva os resultados
        st.session_state.raw_response = raw_response
        st.session_state.show_results = True
        st.session_state.five_star_tips = None
        st.success("Análise concluída!")
    else:
        st.warning("Por favor, preencha ambos os campos.")

# NOVO: Lógica do botão "5 Estrelas" também usa o sistema de redundância
if 'show_results' in st.session_state and st.session_state.show_results:
    # (A lógica de extração 'r = {...}' e exibição do layout 'col1, col2...' continua a mesma)
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Classificação**"); st.metric(label="", value=r.get('classification') or "Não encontrado", label_visibility="collapsed")
        st.markdown("**Avaliação da Ideia**"); st.markdown(r.get('notas') or "Não encontrado.") 
        
        if 'current_notas' in st.session_state:
            if st.button("Ver dicas para 5 estrelas ★"):
                
                # Define o modelo primário e fallback para esta chamada
                primary_model = st.session_state.model_in_use
                fallback_model = model_flash if primary_model == model_pro else model_pro
                
                prompt_dicas = get_five_star_tips_prompt(
                    st.session_state.current_tema,
                    st.session_state.current_ideia,
                    st.session_state.current_notas
                )
                
                with st.spinner(f"Gerando dicas com {primary_model.model_name}..."):
                    tips = safe_generate_content(prompt_dicas, primary_model)
                
                if tips is None:
                    st.warning(f"{primary_model.model_name} está sobrecarregado. Trocando para {fallback_model.model_name}...")
                    with st.spinner(f"Tentando com {fallback_model.model_name}..."):
                        tips = safe_generate_content(prompt_dicas, fallback_model)

                if tips is None:
                    st.error("Falha ao gerar dicas. Tente novamente.")
                else:
                    st.session_state.five_star_tips = tips
        
        st.markdown("**Formato Ideal Sugerido**"); st.success(r.get('format') or "Não encontrado.", icon="🎨")
        st.markdown("**Sugestões de Hashtags**"); st.info(r.get('hashtags') or "Não encontrado.", icon="#️⃣")
        st.markdown("**Sugestões de Conteúdo**"); st.info(r.get('content') or "Não encontrado.", icon="📄")

    with col2:
        st.markdown("**Dica de Mestre**"); st.info(r.get('pro_tip') or "Não encontrado.", icon="💡")
        st.markdown("**Justificativa e Aula**"); st.success(r.get('justification') or "Não encontrado.", icon="🎯")
        
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
