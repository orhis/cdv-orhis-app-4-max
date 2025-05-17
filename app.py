import streamlit as st
import requests

st.set_page_config(page_title="B.O. Zastosowanie sztucznych sieci neuronowych", layout="centered")
st.title("B.O. Zastosowanie sztucznych sieci neuronowych")

# 🔐 Klucz API z secrets
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

# 🧠 Klucz do historii i suwaka tokenów dla danego modelu
klucz_historia = f"messages_{model_alias}"
klucz_tokeny = f"max_tokens_{model_alias}"

# 📥 Inicjalizacja historii i tokenów dla danego modelu
if klucz_historia not in st.session_state:
    st.session_state[klucz_historia] = [{"role": "system", "content": prompt_systemowy}]

if klucz_tokeny not in st.session_state:
    st.session_state[klucz_tokeny] = 1024  # domyślny limit tokenów

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
            "max_tokens": st.session_state[klucz_tokeny]
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

        # 📊 Licznik tokenów i kosztów
        if "usage" in response_data:
            tokens = response_data["usage"]["total_tokens"]

            ceny = {
                "openai/gpt-3.5-turbo": 0.001,
                "openai/gpt-4-turbo": 0.01,
                "anthropic/claude-3-sonnet": 0.003,
                "anthropic/claude-3-opus": 0.015,
                "mistralai/mistral-7b-instruct": 0.0005,
                "meta-llama/llama-3-8b-instruct": 0.0005
            }

            cena_tokena = ceny.get(model_alias, 0.001)
            koszt = tokens * cena_tokena / 1000
            st.info(f"Zużyto {tokens} tokenów. Szacowany koszt: ${koszt:.4f}")

# 🧼 Suwak max_tokens dla danego modelu (nad historią)
st.markdown("---")
st.subheader("Historia rozmowy")

st.session_state[klucz_tokeny] = st.slider(
    "Maksymalna długość odpowiedzi (tokeny):",
    min_value=128,
    max_value=4096,
    value=st.session_state[klucz_tokeny],
    step=64,
    key=klucz_tokeny
)

# 📚 Wyświetlenie historii rozmowy
for msg in st.session_state[klucz_historia]:
    if msg["role"] == "user":
        st.markdown(f"**Ty:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**Asystent:** {msg['content']}")

# 🔘 Przycisk czyszczenia historii dla danego modelu
if st.button("🧹 Wyczyść historię tego modelu"):
    st.session_state[klucz_historia] = [{"role": "system", "content": prompt_systemowy}]
    st.success("Historia została wyczyszczona.")
