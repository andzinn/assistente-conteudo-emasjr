import streamlit as st
import google.generativeai as genai
import os
import re

st.set_page_config(layout="wide")
st.title("🎣 Gerador e Repositório de Ganchos v1.3.6")

# --- BANCO DE DADOS DE GANCHOS (v1.3 - completo) ---
HOOK_DATABASE = {
    "Declarações Impactantes e Provocativas": [
        {"text": "Tenho certeza de que você está cometendo esse erro agora...", "format": "Reels / Carrossel"},
        {"text": "Se você está fazendo isso, pare imediatamente.", "format": "Reels"},
        {"text": "Esqueça o que você aprendeu. Isso funciona.", "format": "Carrossel"},
        {"text": "Isso pode ser a coisa mais importante que compartilho o ano todo.", "format": "Post Estático / Reels"},
        {"text": "Isso mudou meus resultados da noite para o dia...", "format": "Reels (Storytelling)"},
        {"text": "A solução mais simples é geralmente a melhor.", "format": "Carrossel"},
        {"text": "A maioria das pessoas complica isso, mas é bem simples...", "format": "Carrossel"},
        {"text": "Parece ilegal saber disso.", "format": "Reels"},
        {"text": "Eu NÃO esperava por isso...", "format": "Reels / Post Estático"},
        {"text": "O/A ____ que eu não esperava.", "format": "Post Estático"},
        {"text": "Você precisa disso.", "format": "Post Estático"},
        {"text": "Isso vai mudar sua vida.", "format": "Reels"},
        {"text": "Isso vai explodir sua mente.", "format": "Reels"},
        {"text": "Isso não é uma piada.", "format": "Post Estático"},
        {"text": "Isso pode te chocar, mas...", "format": "Carrossel"},
        {"text": "Alguém tinha que dizer...", "format": "Reels (Opinião)"},
        {"text": "Este truque vai te economizar horas.", "format": "Reels (Hack)"},
        {"text": "Esta dica vai explodir sua mente.", "format": "Reels"},
        {"text": "Eu não sei se você está pronto(a) para ouvir isso!", "format": "Post Estático / Reels"},
        {"text": "Isso vai mudar como você pensa sobre...", "format": "Carrossel"},
        {"text": "Você precisa ouvir isso hoje...", "format": "Post Estático"},
        {"text": "Isso não é um treinamento.", "format": "Reels"},
        {"text": "Isso não pode ser real.", "format": "Reels"},
        {"text": "A única coisa que odeio sobre [isso] mas que funciona.", "format": "Carrossel"},
        {"text": "Não é sobre [isso], faça isso em vez disso.", "format": "Carrossel"},
        {"text": "Você não pode esperar [isso] sem [isso].", "format": "Post Estático"},
        {"text": "Eu pensei que [crença comum] estava certo, até que eu descobri [a verdade].", "format": "Carrossel"},
        {"text": "Sua [área de atuação] está prestes a ser interrompida.", "format": "Reels / Post Estático"},
        {"text": "Por que o [método tradicional] não funciona mais (e o que fazer).", "format": "Carrossel"},
    ],
    "Perguntas de Curiosidade": [
        {"text": "Qual é a verdadeira razão pela qual você não está crescendo?", "format": "Carrossel"},
        {"text": "Quer saber a estratégia que ninguém está falando sobre?", "format": "Reels"},
        {"text": "Como seria finally alcançar [resultado desejado]?", "format": "Post Estático / Reels"},
        {"text": "Por que isso sempre acontece com [público específico]?", "format": "Reels (Relatabilidade)"},
        {"text": "Você está sabotando seu crescimento sem perceber?", "format": "Carrossel"},
        {"text": "Você sabia ____?", "format": "Carrossel / Reels"},
        {"text": "Quer saber algo louco?", "format": "Reels"},
        {"text": "Por que não há mais pessoas falando sobre...", "format": "Carrossel"},
        {"text": "Já se perguntou, ____?", "format": "Post Estático"},
        {"text": "Quem mais faz isso?", "format": "Reels"},
        {"text": "Você deveria [fazer isso ou aquilo]?", "format": "Carrossel (Comparativo)"},
        {"text": "Isto ou aquilo?", "format": "Carrossel / Post Estático"},
        {"text": "Podemos falar sobre [isso]?", "format": "Post Estático"},
        {"text": "O que [seu nicho] e [algo aleatório] têm em comum?", "format": "Reels / Carrossel"},
        {"text": "Você realmente precisa de [coisa cara] para [resultado]?", "format": "Carrossel"},
    ],
    "Resolução de Problemas e Hacks": [
        {"text": "O truque que resolveu tudo de uma vez...", "format": "Reels"},
        {"text": "Finalmente – uma maneira fácil de conseguir [resultado].", "format": "Carrossel"},
        {"text": "Diga adeus a [problema] de uma vez por todas.", "format": "Reels"},
        {"text": "Isso funcionou para mim quando nada mais deu certo.", "format": "Reels (Storytelling)"},
        {"text": "Está lutando com [problema]? Faça isso no lugar.", "format": "Carrossel"},
        {"text": "Como melhorar instantaneamente ____", "format": "Reels"},
        {"text": "Como nunca ficar sem ____", "format": "Carrossel"},
        {"text": "Truque rápido...", "format": "Reels"},
        {"text": "Lutando com ____? Você vai querer salvar isso.", "format": "Carrossel / Post Estático"},
        {"text": "Como ____ de graça.", "format": "Reels"},
        {"text": "Economize tempo e dinheiro ao ____", "format": "Carrossel"},
        {"text": "A melhor maneira de ____", "format": "Carrossel"},
        {"text": "Como conseguir [isso] com meu sistema simples que [resolve isso]", "format": "Carrossel"},
        {"text": "Como parar de [fazer isso] da maneira fácil", "format": "Reels"},
        {"text": "A maneira preguiçosa de [aprender isso]", "format": "Reels"},
        {"text": "A maneira simples de [fazer isso]", "format": "Carrossel"},
        {"text": "O que fazer sobre [este problema]", "format": "Carrossel"},
        {"text": "A maneira sem estresse de [alcançar isso]", "format": "Carrossel"},
        {"text": "O sistema que eu uso para [resolver este problema]", "format": "Carrossel (Tutorial)"},
        {"text": "Como [alcançar isso]", "format": "Carrossel / Reels"},
        {"text": "Em vez de fazer [isso], faça [isso]", "format": "Reels (Comparativo)"},
        {"text": "O que realmente importa para [resolver este problema]", "format": "Post Estático"},
        {"text": "Como [alcançar isso] agora mesmo", "format": "Reels"},
        {"text": "A estratégia que ninguém está usando para [alcançar isso]", "format": "Carrossel"},
        {"text": "O guia de 1 minuto para [problema complexo].", "format": "Reels"},
        {"text": "Não tem [ferramenta]? Use [alternativa grátis] no lugar.", "format": "Reels"},
    ],
    "Listas e Dicas Numeradas": [
        {"text": "Esse método é 10x melhor do que [conselho comum].", "format": "Carrossel"},
        {"text": "7 maneiras de ganhar mais ____", "format": "Carrossel"},
        {"text": "Meus 5 ____ favoritos", "format": "Carrossel / Reels"},
        {"text": "Top 3 ____ que vocês estão amando", "format": "Carrossel"},
        {"text": "Minhas 5 melhores dicas para ____", "format": "Carrossel"},
        {"text": "5 ____ indispensáveis", "format": "Carrossel"},
        {"text": "7 coisas que você não sabia que precisava de ____", "format": "Carrossel"},
        {"text": "3 dicas simples de ____ que mudaram meu/minha ____", "format": "Reels"},
        {"text": "5 ____ que estão custando caro para você.", "format": "Carrossel"},
        {"text": "3 dicas comprovadas para ____.", "format": "Carrossel"},
        {"text": "Cuidado com essas três coisas...", "format": "Reels / Carrossel"},
        {"text": "3 razões pelas quais você deveria ____", "format": "Carrossel"},
        {"text": "7 fatos desmistificadores sobre ____", "format": "Carrossel"},
        {"text": "5 coisas que eu faria se estivesse começando de novo.", "format": "Carrossel (Storytelling)"},
        {"text": "Cinco ____ que você pode fazer agora mesmo para melhorar ____", "format": "Carrossel"},
        {"text": "Três coisas that made ____ mais fácil.", "format": "Reels"},
        {"text": "3 dicas para resolver [isso]", "format": "Carrossel"},
        {"text": "3 razões por que [isso]", "format": "Carrossel"},
        {"text": "3 coisas para [fazer isso]", "format": "Carrossel / Reels"},
        {"text": "Dicas essenciais para [alcançar isso] sem [isso]", "format": "Carrossel"},
        {"text": "3 estratégias para [alcançar isso]", "format": "Carrossel"},
        {"text": "5 coisas para [resolver isso]", "format": "Carrossel"},
        {"text": "5 ideias para [resolver este problema]", "format": "Carrossel"},
        {"text": "5 maneiras de [fazer isso]", "format": "Carrossel"},
        {"text": "7 tipos de [coisas do nicho]", "format": "Carrossel"},
        {"text": "3 dicas para [fazer isso]", "format": "Carrossel"},
        {"text": "Truque fácil para [resolver isso] em 3 passos", "format": "Reels / Carrossel"},
        {"text": "10 coisas que você precisa saber [sobre este tópico]", "format": "Carrossel"},
        {"text": "7 passos para ir de [isso] para [isso]", "format": "Carrossel"},
        {"text": "O que fazer e o que não fazer", "format": "Carrossel (Comparativo)"},
        {"text": "Os 4 piores ____ (e 4 alternativas melhores).", "format": "Carrossel"},
    ],
    "Storytelling e Experiência Pessoal": [
        {"text": "Eu estava travado até descobrir isso...", "format": "Reels (Voz sobreposta)"},
        {"text": "O momento que mudou tudo para mim foi...", "format": "Reels (Voz sobreposta)"},
        {"text": "Aqui está o que ninguém me contou quando comecei...", "format": "Carrossel"},
        {"text": "Esse único erro quase me custou [resultado].", "format": "Reels (Storytelling)"},
        {"text": "Eu tentei de tudo... até encontrar o que realmente funcionou.", "format": "Reels"},
        {"text": "Eu finally cedi...", "format": "Post Estático (Texto)"},
        {"text": "Eu estava errado(a)...", "format": "Post Estático (Texto)"},
        {"text": "Erros que cometi quando ____", "format": "Carrossel"},
        {"text": "Eu tenho uma confissão a fazer...", "format": "Post Estático / Reels"},
        {"text": "Algo que aprendi recentemente...", "format": "Carrossel"},
        {"text": "Se eu pudesse voltar no tempo, esta é a única coisa que eu diria a mim mesmo(a).", "format": "Reels"},
        {"text": "O que aconteceu quando eu ____", "format": "Reels (Storytelling)"},
        {"text": "Não acredito que estou compartilhando isso...", "format": "Reels"},
        {"text": "Eu acabei de descobrir...", "format": "Reels"},
        {"text": "Eu não sabia que você podia...", "format": "Reels"},
        {"text": "A maior lição que aprendi com [meu nicho]", "format": "Carrossel / Post Estático"},
        {"text": "Meu cliente obteve [este resultado] fazendo [isso]", "format": "Carrossel (Case)"},
        {"text": "Eu gostaria que alguém tivesse me dito [isso] antes de [fazer isso]", "format": "Carrossel"},
        {"text": "Eu fiz [isso] por [x período de tempo] e [isto] foi o que aconteceu", "format": "Reels / Carrossel"},
        {"text": "Eu parei de fazer [isso] e [isto] foi o que aconteceu", "format": "Reels / Carrossel"},
        {"text": "Como meu cliente parou de [ter este problema]", "format": "Carrossel (Case)"},
        {"text": "O dia em que eu [falhei] me ensinou [lição].", "format": "Reels / Post Estático"},
        {"text": "Minha jornada de [ponto A] para [ponto B] não foi fácil.", "format": "Carrossel / Reels"},
    ],
    "Construção de Confiança e Relatabilidade": [
        {"text": "Eu costumava acreditar em [mito], mas here está o que aprendi...", "format": "Carrossel"},
        {"text": "Você não está sozinho se sente isso...", "format": "Post Estático"},
        {"text": "Já sentiu [frustração comum]? Você não está louco.", "format": "Post Estático"},
        {"text": "Foi exatamente assim que superei [luta específica].", "format": "Reels"},
        {"text": "Apenas ____ vão entender isso.", "format": "Reels (POV)"},
        {"text": "Isso soa como você?", "format": "Post Estático / Carrossel"},
        {"text": "Você não ama quando ____", "format": "Reels"},
        {"text": "Ok, eu sei o que você está pensando...", "format": "Reels (Falando p/ câmera)"},
        {"text": "Abaixe um dedo se você já...", "format": "Reels (Trend)"},
        {"text": "“Eu odeio ter que fazer isso” [responda a esse ponto de dor na legenda]", "format": "Post Estático"},
        {"text": "Um lembrete gentil para quem está [sentindo X].", "format": "Post Estático"},
        {"text": "Sua timeline vs. a minha timeline.", "format": "Reels (Humor)"},
    ],
    "Mitos, Segredos e Revelações": [
        {"text": "Aqui está a verdade que eu gostaria que alguém tivesse me contado antes.", "format": "Reels"},
        {"text": "Você nunca vai adivinhar o que fez a diferença.", "format": "Reels"},
        {"text": "Aqui está o que você estava perdendo o tempo todo...", "format": "Carrossel"},
        {"text": "Eu tenho guardado um segredo...", "format": "Reels"},
        {"text": "MITO: ____", "format": "Carrossel (Mito vs. Fato)"},
        {"text": "O que seu/sua ____ gostaria que você soubesse.", "format": "Carrossel"},
        {"text": "Eu não ia compartilhar isso, mas...", "format": "Reels"},
        {"text": "Vou lhe contar um segredinho.", "format": "Reels"},
        {"text": "Aqui está a verdade sobre ____", "format": "Carrossel"},
        {"text": "O que seu/sua _____ não está lhe dizendo.", "format": "Reels / Carrossel"},
        {"text": "O/A ____ que ninguém está falando sobre.", "format": "Carrossel"},
        {"text": "Verdadeiro ou falso...", "format": "Carrossel"},
        {"text": "A verdade sobre [este tópico]", "format": "Carrossel"},
        {"text": "O segredo para [isso]", "format": "Reels"},
        {"text": "O que não te contam sobre [este tópico]", "format": "Carrossel"},
        {"text": "A verdade sobre [meu nicho]", "format": "Post Estático"},
        {"text": "A verdade sobre [isso]", "format": "Carrossel"},
        {"text": "A verdade sobre encontrar [isso]", "format": "Post Estático"},
        {"text": "O segredo para [este tópico suculento]", "format": "Reels"},
        {"text": "Como aceitar que [esta verdade] é importante", "format": "Post Estático"},
        {"text": "A verdade sobre [não fazer isso]", "format": "Carrossel"},
        {"text": "Ninguém mais vai te dizer [isso]", "format": "Reels"},
        {"text": "A [ferramenta/método] que 99% das pessoas ignora.", "format": "Reels"},
        {"text": "O hack nº 1 de [nicho] que parece bom, mas é ruim.", "format": "Carrossel"},
    ],
    "Desafio e Confronto (Opinião Impopular)": [
        {"text": "Você não pode mudar minha opinião ____ (afirme uma crença forte).", "format": "Post Estático"},
        {"text": "Você está fazendo isso tudo errado.", "format": "Reels (Confronto)"},
        {"text": "Opinião impopular: ____", "format": "Post Estático / Reels"},
        {"text": "Você tem feito ____ errado.", "format": "Reels / Carrossel"},
        {"text": "Não cometa esses erros.", "format": "Carrossel"},
        {"text": "Pare de usar...", "format": "Reels"},
        {"text": "Não se deixe enganar por...", "format": "Carrossel"},
        {"text": "Pare...", "format": "Reels"},
        {"text": "A razão pela qual você não está [alcançando isso] é porque você está fazendo [isso errado]", "format": "Carrossel"},
        {"text": "O maior erro [é este], eis o porquê", "format": "Reels"},
        {"text": "Erros a evitar ao [fazer isso]", "format": "Carrossel"},
        {"text": "A razão pela qual [isso é ruim] e como consertar", "format": "Carrossel"},
        {"text": "Opinião impopular [sobre isso]", "format": "Post Estático"},
        {"text": "Pare de fazer [isso errado], here está minha estratégia", "format": "Carrossel"},
        {"text": "Por que focar [nisso] é errado", "format": "Post Estático"},
        {"text": "Coisas que você não deveria fazer se quer [isso]", "format": "Carrossel"},
        {"text": "Por que eu [não acredito nisso]", "format": "Post Estático"},
        {"text": "Por que eu não acho que [isso] é importante", "format": "Post Estático"},
        {"text": "O [conselho popular] é um lixo. Faça isso no lugar.", "format": "Reels"},
        {"text": "Estou cansado de ver pessoas fazendo [erro comum].", "format": "Reels"},
    ],
    "Cenários e 'Ponto de Vista' (POV)": [
        {"text": "O que seu/sua ____ diz sobre você.", "format": "Carrossel"},
        {"text": "POV: Você decidiu levar [isso] a sério e agora você tem [este resultado]", "format": "Reels"},
        {"text": "POV: Você finally [decidiu fazer isso] e agora [você tem isso]", "format": "Reels"},
        {"text": "POV: Você [está fazendo isso] e se sente [assim]", "format": "Reels"},
        {"text": "POV: Você [está alcançando isso] e só levou [este processo ou período]", "format": "Reels"},
        {"text": "POV: Quando você finally parou de acreditar [nisso] e agora você [alcançou isso]", "format": "Reels"},
        {"text": "POV: Aquele momento em que você [alcançou isso] e agora você comemora [isso]", "format": "Reels"},
        {"text": "POV: Você finally [está fazendo isso] e se sente [assim]", "format": "Reels"},
        {"text": "POV: Você decidiu [fazer isso] para que possa [fazer isso no seu tempo livre]", "format": "Reels"},
        {"text": "POV: Você não contratou [serviço] e agora [resultado ruim].", "format": "Reels (Humor/Alerta)"},
        {"text": "POV: Você contratou [serviço] e agora [resultado bom].", "format": "Reels (Desejo)"},
    ],
    "Resultados e Transformação": [
        {"text": "Uma única coisa mudou minha vida.", "format": "Reels (Storytelling)"},
        {"text": "Como eu fui de ____ para ____", "format": "Reels / Carrossel"},
        {"text": "Como eu [consegui isso] e parei de [fazer isso]", "format": "Carrossel"},
        {"text": "Eu consigo alcançar [isso] todo santo dia usando meu [método]", "format": "Reels"},
        {"text": "Como ir de [isso] para [isso]", "format": "Carrossel (Tutorial)"},
        {"text": "Eu faço [isso] para conseguir [isso]", "format": "Reels"},
        {"text": "Como eu alcancei [isso]", "format": "Carrossel"},
        {"text": "Eu obtenho [este resultado] todo dia, eis como", "format": "Reels"},
        {"text": "Eu descobri como [fazer isso] sem [fazer isso]", "format": "Carrossel"},
        {"text": "Como ter [isso] de forma consistente", "format": "Carrossel"},
        {"text": "A estratégia por trás [deste resultado]", "format": "Carrossel"},
        {"text": "Como eu consigo isso facilmente com [este segredinho]", "format": "Reels"},
        {"text": "Como [fazer isso] nos próximos 30 dias", "format": "Carrossel"},
        {"text": "Eu obtenho [este resultado] a cada [período de tempo]", "format": "Reels"},
        {"text": "Como se tornar [isso] no próximo [período de tempo]", "format": "Carrossel"},
        {"text": "O antes e depois de [aplicar o método].", "format": "Reels / Carrossel"},
        {"text": "De [problema] a [solução] em X dias.", "format": "Reels"},
    ],
    "Chamadas (CTAs) e Alertas": [
        {"text": "Este é o seu sinal para ____", "format": "Post Estático / Reels"},
        {"text": "Assista até o final!", "format": "Reels"},
        {"text": "Chamando todos os ____", "format": "Post Estático"},
        {"text": "Este é o seu lembrete para ____", "format": "Post Estático"},
        {"text": "Pare de rolar!", "format": "Reels"},
        {"text": "Notícia de última hora!", "format": "Post Estático"},
        {"text": "Lembrete:", "format": "Post Estático"},
        {"text": "Qual deles é você A: ____ ou B: ____", "format": "Carrossel (Interativo)"},
        {"text": "Alerta de nova tendência!", "format": "Reels / Post Estático"},
        {"text": "Marque um amigo que precisa ver isso.", "format": "Qualquer Formato"},
        {"text": "Dica profissional: ___", "format": "Post Estático"},
        {"text": "PSA (Aviso de Utilidade Pública): ____", "format": "Post Estático / Reels"},
        {"text": "Sinais de que [você precisa x]", "format": "Carrossel / Reels"},
        {"text": "Lembrete: [isso é possível] se você focar [nisso]", "format": "Post Estático"},
        {"text": "Lembrete: Você não precisa ser [isso] para conseguir [isso]", "format": "Post Estático"},
        {"text": "A coisa mais importante a fazer agora é [isso] ou [na legenda]", "format": "Post Estático"},
        {"text": "Não faça mais nada até ver isso.", "format": "Reels"},
        {"text": "Salve este post para mais tarde.", "format": "Qualquer Formato"},
    ]
}

# --- CÉREBRO DA IA (sem mudanças) ---
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

# --- Parser Robusto (sem mudanças) ---
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

# --- FUNÇÕES DA IA ---

# MUDANÇA: Separando as duas lógicas de criação de gancho
def create_new_hook_guided(tema, principios, model):
    """Gera ganchos com base nos princípios que o usuário escolheu."""
    prompt = f"""
    **Contexto:** Você é um copywriter de elite...
    {FORMULAS_CONTEXT}
    **Definição de "Gancho":** Um "gancho" (hook) NÃO é um título. É a **primeira frase curta e impactante**... (máx. 10-12 palavras).
    * Exemplo Ruim (Título): "A Importância dos Laudos Técnicos na Engenharia"
    * Exemplo Bom (Gancho): "Seu laudo técnico é inútil por causa disso."

    **Sua Tarefa:**
    Com base **apenas** nos princípios de "{', '.join(principios)}", crie **3 GANCHOS curtos e impactantes** para o tema: "{tema}".

    **Para cada gancho,** explique a **"Proposta de Conteúdo"** (o que desenvolver no post para que o gancho faça sentido).
    **Formato de Resposta (OBRIGATÓRIO):**
    [---GANCHO_1_START---]
    **Gancho:** [Seu primeiro gancho]
    **Proposta de Conteúdo:** [Explicação...]
    [---GANCHO_1_END---]
    [---GANCHO_2_START---] ... [---GANCHO_2_END---]
    [---GANCHO_3_START---] ... [---GANCHO_3_END---]
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Erro na chamada à API: {e}")
        return ""

def create_new_hook_auto(tema, model):
    """IA escolhe os princípios E gera os ganchos."""
    prompt = f"""
    **Contexto:** Você é um copywriter de elite...
    {FORMULAS_CONTEXT}
    **Definição de "Gancho":** Um "gancho" (hook) NÃO é um título. É a **primeira frase curta e impactante**... (máx. 10-12 palavras).
    * Exemplo Ruim (Título): "A Importância dos Laudos Técnicos na Engenharia"
    * Exemplo Bom (Gancho): "Seu laudo técnico é inútil por causa disso."

    **Sua Tarefa:**
    1.  Analise o **Tema:** "{tema}".
    2.  Escolha os **2 princípios psicológicos** do CONTEXTO que você acha mais potentes para este tema.
    3.  Crie **3 GANCHOS curtos e impactantes** para o tema, baseando-se nesses princípios.
    4.  Para cada gancho, explique a **"Proposta de Conteúdo"**.

    **Formato de Resposta (OBRIGATÓRIO):**
    Primeiro, anuncie os princípios escolhidos. Depois, liste os 3 ganchos em seus blocos de formato.

    **Princípios Escolhidos:** [Princípio 1], [Princípio 2]

    [---GANCHO_1_START---]
    **Gancho:** [Seu primeiro gancho]
    **Proposta de Conteúdo:** [Explicação...]
    [---GANCHO_1_END---]
    [---GANCHO_2_START---] ... [---GANCHO_2_END---]
    [---GANCHO_3_START---] ... [---GANCHO_3_END---]
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Erro na chamada à API: {e}")
        return ""

# Adaptador (Tab 3) - (sem mudanças)
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

# Avaliador (Tab 4) - (sem mudanças)
def evaluate_hook(gancho, tema, model):
    prompt = f"""
    **Contexto:** Você é um editor-chefe de marketing viral.
    - **Tema do Post:** "{tema}"
    - **Gancho para Avaliar:** "{gancho}"
    **Definição de "Gancho":** ... (definição completa) ...
    **Sua Tarefa:** ... (avaliação e gancho aprimorado) ...
    **Formato de Resposta (OBRIGATÓRIO):**
    [---AVALIACAO_START---] ... [---AVALIACAO_END---]
    [---GANCHO_APRIMORADO_START---] ... [---GANCHO_APRIMORADO_END---]
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Erro na chamada à API: {e}")
        return ""


# --- INTERFACE DA FERRAMENTA ---

tab1, tab2, tab3, tab4 = st.tabs([
    "🗂️ Navegador do Repositório", 
    "🧙‍♂️ Criador de Ganchos (IA)", 
    "🔄 Adaptador de Ganchos (IA)",
    "⚖️ Avaliador de Ganchos (IA)"
])

# --- Aba 1: Navegador (sem mudanças) ---
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

# --- Aba 2: Criador (LÓGICA ATUALIZADA) ---
with tab2:
    st.subheader("Crie Ganchos Novos com IA")
    st.markdown("Use a IA para gerar ganchos originais com base nos princípios psicológicos das Fórmulas 1 e 2.")
    
    tema_criador = st.text_input("Qual é o tema central do seu post?", placeholder="Ex: A importância do projeto estrutural", key="tema_criador")
    
    principios_opcoes = [
        "Perguntas de Curiosidade", "Declarações Polêmicas", "Histórias Inacabadas (Efeito Zeigarnik)",
        "Promessas de Benefícios Claros", "Identificação (Relatabilidade)", "Dissonância Cognitiva (Surpresa)",
        "Tutorial Rápido (Antes e Depois)"
    ]
    
    principios_escolhidos = st.multiselect(
        "Escolha 1 ou 2 princípios (ou deixe em branco para a IA sugerir):",
        principios_opcoes,
        default=[] 
    )
    
    model_choice_criador = st.radio(
        "Escolha o Modelo de IA:",
        ("Pro (Mais Criativo)", "Flash (Mais Rápido)"),
        horizontal=True,
        key="model_criador"
    )
    
    if 'ganchos_gerados_raw' in st.session_state:
        if st.session_state.get('last_tema_criador') != tema_criador:
            st.session_state.ganchos_gerados_raw = None
    
    if st.button("Gerar Novos Ganchos"):
        if not tema_criador:
            st.warning("Por favor, preencha o tema.")
        else:
            model_to_use = model_pro if "Pro" in model_choice_criador else model_flash
            
            # MUDANÇA: Lógica de chamada dividida
            if not principios_escolhidos:
                # Caso 1: Usuário não escolheu, IA decide
                with st.spinner("IA está escolhendo os melhores princípios e gerando ganchos..."):
                    ganchos_gerados_raw = create_new_hook_auto(tema_criador, model_to_use)
            else:
                # Caso 2: Usuário escolheu
                with st.spinner(f"Gerando ganchos com base em '{', '.join(principios_escolhidos)}'..."):
                    ganchos_gerados_raw = create_new_hook_guided(tema_criador, principios_escolhidos, model_to_use)
            
            st.session_state.ganchos_gerados_raw = ganchos_gerados_raw
            st.session_state.last_tema_criador = tema_criador

    if 'ganchos_gerados_raw' in st.session_state and st.session_state.ganchos_gerados_raw:
        raw_text = st.session_state.ganchos_gerados_raw
        
        # MUDANÇA: O parser agora procura por "Princípios Escolhidos"
        principios = re.search(r"^\*\*Princípios Escolhidos:\*\*\s*(.*)", raw_text, re.MULTILINE)
        
        gancho_1 = extrair_bloco_robusto(raw_text, 'GANCHO_1', 'GANCHO_2')
        gancho_2 = extrair_bloco_robusto(raw_text, 'GANCHO_2', 'GANCHO_3')
        gancho_3 = extrair_bloco_robusto(raw_text, 'GANCHO_3')

        st.markdown("---")
        st.subheader("Ganchos e Propostas de Conteúdo Gerados:")
        
        # Se a IA escolheu, mostra quais ela escolheu
        if principios:
            st.info(f"**Princípios Recomendados pela IA:** {principios.group(1).strip()}")
        
        if gancho_1: st.markdown(gancho_1); st.divider()
        if gancho_2: st.markdown(gancho_2); st.divider()
        if gancho_3: st.markdown(gancho_3)

        if st.checkbox("Mostrar resposta bruta (Criador)", key="debug_criador"):
            st.text(raw_text or "Nenhuma resposta foi gravada.")

# --- Aba 3: Adaptador (sem mudanças) ---
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

# --- Aba 4: Avaliador (sem mudanças) ---
with tab4:
    st.subheader("Avalie a Força do seu Gancho")
    st.markdown("Cole um gancho que você criou (ou pegou do repositório) e veja a análise da IA sobre seu potencial.")
    
    gancho_avaliar = st.text_input(
        "1. Cole o gancho que você quer avaliar:",
        placeholder="Ex: Pare de usar cimento comum agora mesmo.",
        key="gancho_avaliar"
    )
    tema_avaliar = st.text_input(
        "2. Qual o tema/contexto deste gancho?",
        placeholder="Ex: A vantagens do concreto auto-regenerativo",
        key="tema_avaliar"
    )
    
    model_choice_avaliar = st.radio(
        "Escolha o Modelo de IA:",
        ("Pro (Análise Crítica)", "Flash (Análise Rápida)"),
        horizontal=True,
        key="model_avaliar"
    )
    
    if 'raw_avaliacao' in st.session_state:
        if st.session_state.get('last_gancho_avaliar') != gancho_avaliar:
            st.session_state.raw_avaliacao = None
    
    if st.button("Avaliar Gancho"):
        if not gancho_avaliar or not tema_avaliar:
            st.warning("Por favor, preencha o gancho e seu tema/contexto.")
        else:
            model_to_use = model_pro if "Pro" in model_choice_avaliar else model_flash
            with st.spinner("IA está avaliando seu gancho..."):
                raw_avaliacao = evaluate_hook(gancho_avaliar, tema_avaliar, model_to_use)
                st.session_state.raw_avaliacao = raw_avaliacao
                st.session_state.last_gancho_avaliar = gancho_avaliar

    if 'raw_avaliacao' in st.session_state and st.session_state.raw_avaliacao:
        raw_text = st.session_state.raw_avaliacao
        
        avaliacao = extrair_bloco_robusto(raw_text, 'AVALIACAO', 'GANCHO_APRIMORADO')
        aprimorado = extrair_bloco_robusto(raw_text, 'GANCHO_APRIMORADO')
        
        st.markdown("---")
        st.subheader("Resultado da Avaliação:")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Notas da IA:**")
            st.info(avaliacao or "Não foi possível extrair a avaliação.")
        with col2:
            st.markdown("**Sugestão 5 Estrelas:**")
            st.success(aprimorado or "Não foi possível extrair a sugestão.")
            
        if st.checkbox("Mostrar resposta bruta (Avaliador)", key="debug_avaliador"):
            st.text(raw_text or "Nenhuma resposta foi gravada.")
