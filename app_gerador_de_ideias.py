import streamlit as st

st.set_page_config(
    page_title="Assistente de Conteúdo",
    page_icon="🧠"
)

st.title("🧠 Bem-vindo ao seu Assistente de Conteúdo!")

st.sidebar.success("Selecione uma ferramenta acima.")

st.markdown(
    """
    Este é o seu centro de comando para criação e análise de conteúdo para redes sociais.

    **Selecione uma das ferramentas na barra lateral à esquerda para começar:**

    - **💡 Criador de Ideias:** Não sabe o que postar? Dê um tema e a IA criará 5 ideias de posts estruturadas em um funil de vendas.
    - **🧪 Analisador de Ideias:** Já tem uma ideia? A IA vai classificar o nível de funil, sugerir melhorias e mostrar como adaptar a ideia para outros estágios do funil.

    Aproveite!
    """
)