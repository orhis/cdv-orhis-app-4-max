import streamlit as st
import requests

st.title("Zastosowanie sztucznych sieci neuronowych, Laboratoria, grupa 1")

# Pobierz klucz API z bezpiecznego magazynu Streamlit (Secrets)
api_key = st.secrets["OPENROUTER_API_KEY"]

prompt = st.text_area("Wprowadź swoje polecenie:", "")

if st.button("Wyślij"):
    if prompt.strip():
        headers = {
            "Authorization": f"Bearer {api_key}",
        }
        data = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "Jesteś pomocnym asystentem AI, który mówi po polsku."},
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
