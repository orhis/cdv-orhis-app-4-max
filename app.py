# === 1. USTAWIENIA I IMPORTY ===
import streamlit as st
import requests

st.set_page_config(page_title="B.O. Zastosowanie sztucznych sieci neuronowych", layout="centered")
st.title("B.O. Zastosowanie sztucznych sieci neuronowych")

# === 2. KONFIGURACJA MODELI I STANÓW SESJI ===
api_key = st.secrets["OPENROUTER_API_KEY"]

MODELE = {
    "GPT-3.5 Turbo": "openai/gpt-3.5-turbo",
    "GPT-4 Turbo": "openai/gpt-4-turbo",
    "Claude 3 Opus": "anthropic/claude-3-opus",
    "Claude 3 Sonnet": "anthropic/claude-3-sonnet",
    "Mistral 7B": "mistralai/mistral-7b-instruct",
    "LLaMA 3 8B": "meta-llama/llama-3-8b-instruct"
}

nazwa_modelu = st.selectbox("Wybierz model:", list(MODELE.keys()))
model_alias = MODELE[nazwa_modelu]

klucz_historia = f"messages_{model_alias}"
klucz_tokeny = f"max_tokens_{model_alias}"

if klucz_historia not in st.session_state:
    st.session_state[klucz_historia] = [{"role": "system", "content": "Jesteś pomocnym asystentem AI, który mówi po polsku."}]
if klucz_tokeny not in st.session_state:
    st.session_state[klucz_tokeny] = 1024

# === 3. PANEL KONTROLNY (STYL / TOKENY / NOWA SESJA) ===
col1, col2, col3, col4 = st.columns([2, 2, 4, 2])

with col1:
    styl = st.radio("Styl odpowiedzi:", ["Precyzyjny", "Kreatywny"])

if styl == "Precyzyjny":
    prompt_systemowy = "Odpowiadasz rzeczowo i konkretnie, jak profesjonalny asystent AI."
else:
    prompt_systemowy = "Odpowiadasz kreatywnie, z humorem i wyobraźnią – jak inspirujący doradca."

with col2:
    st.markdown("**Max tokens**")
    st.caption(f"🎯 Aktualnie: {st.session_state[klucz_tokeny]}")

with col3:
    nowa_liczba = st.slider(
        "Ukryty suwak (dla dostępności)",
        128, 4096,
        st.session_state[klucz_tokeny],
        64,
        key="temp_token_slider",
        label_visibility="collapsed"
    )

with col4:
    if st.button("🔄 Nowa sesja"):
        st.session_state[klucz_tokeny] = nowa_liczba
        st.session_state[klucz_historia] = [{"role": "system", "content": prompt_systemowy}]
        st.success(f"Nowa sesja rozpoczęta z max_tokens = {nowa_liczba}")

# === 4. FORMULARZ ZAPYTANIA I OBSŁUGA API ===
col_prompt, col_send = st.columns([5, 1])

with col_prompt:
    prompt = st.text_area(
        "Ukryte pole tekstowe (dla dostępności)",
        "",
        label_visibility="collapsed"
    )

with col_send:
    if st.button("Wyślij"):
        if prompt.strip():
            headers = {"Authorization": f"Bearer {api_key}"}
            st.session_state[klucz_historia].append({"role": "user", "content": prompt})

            data = {
                "model": model_alias,
                "messages": st.session_state[klucz_historia],
                "max_tokens": st.session_state[klucz_tokeny]
            }

            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
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
                st.session_state["koszt"] = f"Zużyto {tokens} tokenów • Koszt: ${koszt:.4f}"

# === 5. WIDOK HISTORII ROZMOWY ===
st.markdown("---")
col_hist, col_btn = st.columns([1, 1])
with col_hist:
    st.subheader("Historia rozmowy")
with col_btn:
    if st.button("🧹 Wyczyść historię"):
        st.session_state[klucz_historia] = [{"role": "system", "content": prompt_systemowy}]
        st.success("Historia została wyczyszczona.")

for msg in st.session_state[klucz_historia]:
    if msg["role"] == "user":
        st.markdown(f"**Ty:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**Asystent:** {msg['content']}")

# === 6. OVERLAY KOSZTOWY (PRAWY GÓRNY RÓG) ===
if "koszt" in st.session_state:
    st.markdown(
        f"<div style='position:fixed; top:1.5rem; right:2rem; color:#999; font-size:0.85rem;'>💲 {st.session_state['koszt']}</div>",
        unsafe_allow_html=True
    )
