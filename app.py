import streamlit as st
import requests

st.set_page_config(page_title="B.O. Zastosowanie sztucznych sieci neuronowych", layout="centered")
st.title("Asystent AI – powered by OpenRouter")

# 🔐 Klucz API z secrets (działa lokalnie z secrets.toml i w Streamlit Cloud)
api_key = st.secrets["OPENROUTER_API_KEY"]

# 📦 Lista modeli OpenRouter
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

# 🧠 Klucz sesji dla danego modelu
klucz_historia = f"messages_{model_alias}"

# 📥 Inicjalizacja historii dla tego modelu
if klucz_historia not in st.session_state:
    st.session_state[klucz_historia] = [
        {"role": "system", "content": prompt_systemowy}
    ]

# 📝 Pole tekstowe na zapytanie
prompt = st.text_area("Wprowadź swoje polecenie:", "")

# 🚀 Przycisk wysyłania zapytania
if st.button("Wyślij"):
    if prompt.strip():
        headers = {
            "Authorization": f"Bearer {api_key}",
        }

        # ➕ Dodaj wiadomość użytkownika do historii
        st.session_state[klucz_historia].append({"role": "user", "content": prompt})

        data = {
            "model": model_alias,
            "messages": st.session_state[klucz_historia],
            "max_tokens": 1024
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )

        response_data = response.json()

        if "choices" in response_data and "message" in response_data["choices"][0]:
            reply = response_data["choices"][0]["message"]["content"]
            st.session_state[klucz_historia].append({"role": "assistant", "content": reply})
        elif "choices" in response_data and "text" in response_data["choices"][0]:
            reply = response_data["choices"][0]["text"]
            st.session_state[klucz_historia].append({"role": "assistant", "content": reply})
        else:
            st.error("Nieoczekiwana odpowiedź od modelu:")
            st.code(response_data)

# 📚 Wyświetlenie historii rozmowy dla wybranego modelu
st.markdown("---")
st.subheader("Historia rozmowy")

for msg in st.session_state[klucz_historia]:
    if msg["role"] == "user":
        st.markdown(f"**Ty:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**Asystent:** {msg['content']}")
