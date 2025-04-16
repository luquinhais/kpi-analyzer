import streamlit as st
import pandas as pd
import os
import openai
from dotenv import load_dotenv

# Carrega variável de ambiente do .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Configura chave no cliente da OpenAI
openai.api_key = api_key

# Interface
st.set_page_config(page_title="Analisador com IA", layout="wide")
st.title("🔍 Analisador de Planilhas com OpenAI")

# Mostrar parte da chave carregada
if api_key:
    st.write("🔐 Chave carregada:", api_key[:10] + "...")
else:
    st.error("❌ Chave da OpenAI não encontrada! Verifique seu arquivo `.env`.")

# Teste de conexão
st.subheader("🧪 Testar conexão com a OpenAI")
if st.button("Testar chave da OpenAI"):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": "Diga 'ok' se você está funcionando."}
            ],
            max_tokens=5
        )
        reply = response.choices[0].message.content
        st.success(f"✅ Conexão OK! Resposta: {reply}")
    except Exception as e:
        st.error(f"❌ Erro ao conectar: {e}")

# Upload e análise de planilha
if api_key:
    st.subheader("📤 Upload da Planilha")
    uploaded_file = st.file_uploader("Faça upload de uma planilha (.csv ou .xlsx)", type=["csv", "xlsx"])

    if uploaded_file:
        try:
            # Leitura da planilha
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.subheader("📊 Visualização dos Dados")
            st.dataframe(df)

            # Pergunta livre
            user_question = st.text_input("❓ Pergunte algo sobre os dados:")

            if user_question:
                resumo = df.describe(include='all').to_string()

                prompt = f"""
Você é um analista de dados experiente. Baseando-se nas estatísticas da planilha abaixo:

{resumo}

Responda de forma clara e objetiva à seguinte pergunta: {user_question}
"""

                with st.spinner("Consultando a IA..."):
                    response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Você é um especialista em análise de dados."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=500,
                        temperature=0.7,
                    )
                    answer = response.choices[0].message.content
                    st.success("✅ Resposta:")
                    st.write(answer)

            # Análise qualitativa de atendimento ao cliente
            st.subheader("📚 Análise Qualitativa de Conversas de Atendimento")
            if all(col in df.columns for col in ["session_id", "sender_type", "create_time", "text"]):
                num_chats = df["session_id"].nunique()
                st.info(f"📈 O arquivo contém **{num_chats} chats únicos**.")

                if st.button("Iniciar análise qualitativa"):
                    # Amostra dos dados para não enviar tudo (ajuste conforme necessário)
                    amostra = df.head(100).to_string(index=False)

                    prompt_qualitativo = f"""
Você é um especialista em análise de conversas de atendimento ao consumidor. Seu papel é auxiliar gerentes de experiência do cliente a entenderem profundamente as interações entre clientes e agentes de atendimento.

Análise qualitativa. Objetivos principais (Envie a análise separando em cada um desses tópicos):

1.1 Dados gerais do atendimento (Tema do atendimento, duração total do atendimento, sentimento final do cliente)

1.2 Fornecer um resumo estruturado de toda a interação entre o cliente e agente. Identifique todos possíveis comportamentos graves que podem sinalizar algum tipo de falha de processo, golpe, comportamento inadequado

1.3 Identificar problemas relatados, sentimentos do cliente e a conduta do agente.

1.4 Sugerir melhorias comportamentais, processuais e comunicacionais.

Formato de entrada esperado:
Arquivo com colunas "session_id", "sender_type", "create_time" e "text".

session_id = cada sessão é um chat diferente  
sender_type = pessoa que envia mensagem ( agent = agente do atendimento ao consumidor, user = cliente, bot = chatbot, other = mensagem automática do sistema)  
create_time = data e hora de envio de cada mensagem  
text = mensagem enviada

Em alguns momentos o cliente vai enviar uma imagem em anexo, para que você consiga identificar isso a palavra “image” vai aparecer no final da mensagem, ou seja não é o cliente enviando a palavra “image” na interação. Ex: 1906662759710343168 | User | 2025-03-31 08:00:27 | image

Amostra dos dados:

{amostra}

Estilo de resposta:
Cordial, amigável, direto e profissional.  
Organize as respostas com títulos, listas e destaques sempre que possível.  
Evite termos técnicos complexos sem necessidade.  
Use linguagem acessível e assertiva.
"""

                    with st.spinner("Consultando a IA para análise qualitativa..."):
                        response = openai.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "Você é um especialista em análise de atendimento ao cliente."},
                                {"role": "user", "content": prompt_qualitativo}
                            ],
                            max_tokens=1500,
                            temperature=0.7,
                        )
                        st.success("✅ Análise concluída!")
                        st.write(response.choices[0].message.content)
            else:
                st.warning("⚠️ Para a análise qualitativa, o arquivo deve conter as colunas: session_id, sender_type, create_time e text.")

        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")
