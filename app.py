import streamlit as st
import requests

# Tytuł aplikacji
st.title("Asystent AI – powered by OpenRouter")

# 🔐 Klucz API z sekcji secrets (działa w Streamlit Cloud i lokalnie z secrets.toml)
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

# 🎭 Styl odpowiedzi
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

        response_data = response.json()

        # ✅ Obsługa różnych formatów odpowiedzi (GPT/Claude/Mistral)
        if "choices" in response_data and "message" in response_data["choices"][0]:
            reply = response_data["choices"][0]["message"]["content"]
            st.success(reply)

        elif "choices" in response_data and "text" in response_data["choices"][0]:
            reply = response_data["choices"][0]["text"]
            st.success(reply)

        else:
            st.error("Nieoczekiwana odpowiedź od modelu:")
            st.code(response_data)
