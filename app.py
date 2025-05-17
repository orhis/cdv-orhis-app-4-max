import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Wczytanie zmiennych środowiskowych
load_dotenv()

# Interfejs aplikacji
st.title("Asystent AI – powered by OpenRouter")

prompt = st.text_area("Wprowadź swoje polecenie:", "")

if st.button("Wyślij"):
    if prompt.strip():
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        }
        data = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}]
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