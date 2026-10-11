import streamlit as st
import requests
import json
import time

st.title("AlejandraCalderonVazquez_AIBot")

def ai_ask(prompt, data=None, temperature=0.5,
           max_tokens=250, model="open-mistral-nemo",
           api_key=None,
           api_url="https://api.mistral.ai/v1/chat/completions"):
    if not api_key:
        return "API key is not configured yet."
    message = prompt
    if data is not None:
        message += "\n\nData to analyze:\n"
        message += json.dumps(data, indent=2)
    payload = {
        "messages": [{"role": "user", "content": message}],
        "temperature": temperature,
        "model": model,
        "max_tokens": max_tokens
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(
            api_url, headers=headers,
            json=payload, timeout=45
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"API connection error: {str(e)}"
    except (KeyError, IndexError, ValueError):
        return "Unable to read the AI response."
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
def response_generator():
    try:
        api_key = st.secrets["apikey"]
    except Exception:
        api_key = None
    response = ai_ask(
        "Pretend you are a very friendly and helpful "
        "person. Respond to the conversation using "
        "the provided context. Give only your response.",
        data=st.session_state.messages,
        api_key=api_key
    )
    for word in response.split():
        yield word + " "
        time.sleep(0.05)
if prompt := st.chat_input("Ask me anything!"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator())
    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )
