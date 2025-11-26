import streamlit as st
import requests

st.set_page_config(page_title="CaloriFit", page_icon="🔥")

st.title("🔥 CaloriFit – Cálculo de Ingestão Alimentar")
st.write("Baseado na API oficial **USDA FoodData Central**")

with st.form("form"):
    alimento = st.text_input("Nome do alimento:", placeholder="ex: banana, arroz, frango grelhado")
    quantidade = st.number_input("Quantidade (em gramas):", min_value=1, value=100)
    
    submitted = st.form_submit_button("Calcular")

if submitted:
    if alimento.strip() == "":
        st.error("Digite o nome do alimento!")
    else:
        FUNCTION_URL = "https://NOME-DA-SUA-FUNCTION.azurewebsites.net/api/NOME-DA-FUNCTION"

        params = {
            "alimento": alimento,
            "quantidade": quantidade
        }

        response = requests.get(FUNCTION_URL, params=params)

        if response.status_code == 200:
            result = response.json()

            st.success("Resultado encontrado!")
            st.json(result)

            st.metric(
                label=f"Calorias totais ingeridas ({quantidade}g de {alimento})",
                value=f"{result['calorias_totais']:.2f} kcal"
            )
        else:
            st.error(f"Erro da API: {response.text}")
