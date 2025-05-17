import streamlit as st
import requests

# Tytuł aplikacji
st.title("Asystent AI – powered by OpenRouter")

# 📌 Klucz API z bezpiecznego magazynu Streamlit Cloud (lub lokalnie przez st.secrets.toml)
api_key = st.secrets["OPENROUTER_API_KEY"]

# 📦 Lista modeli dostępnych w OpenRouter
MODELE = {
    "GPT-3.5 Turbo": "openai/gpt-3.5-turbo",
    "GPT-4 Turbo": "openai/gpt-4-turbo",
    "Claude 3 Opus": "anthropic/claude-3-opus",
    "Claude 3 Sonnet": "anthropic/claude-3-sonnet",
    "Mistral 7B": "mistralai/mistral-7b-instruct",
    "LLaMA 3 8B": "meta-llama/llama-3-8b-instruct"
}

# 🔽 Wybór modelu
nazwa_modelu = st.selectbox("Wybierz model:", list(MODELE.keys()))
model_alias = MODELE[nazwa_modelu]

# 🎭 Wybór stylu odpowiedzi
styl = st.radio("Styl odpowiedzi:", ["Precyzyjny", "Kreatywny"])

# 🧠 Prompt systemowy zależny od stylu
if styl == "Precyzyjny":
    prompt_systemowy = "Odpowiadasz rzeczowo i konkretnie, jak profesjonalny asystent AI."
else:
    prompt_systemowy = "Odpowiadasz kreatywnie, z humorem i wyobraźnią – jak inspirujący doradca."

# 📝 Pole tekstowe na zapytanie
prompt = st.text_area("Wprowadź swoje polecenie:", "")

# 🚀 Przycisk wysyłania zapytania
if st.button("Wyślij"):
    if prompt.strip():
        headers = {
            "Authorization": f"Bearer {api_key}",
        }

        data = {
            "model": model_alias,
            "messages": [
                {"role": "system", "content": prompt_systemowy},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )

        if response.ok:
            reply = response.json()["choices"][0]["message"]["content"]
            st.success(reply)
        else:
            st.error(f"Błąd: {response.status_code} - {response.text}")
