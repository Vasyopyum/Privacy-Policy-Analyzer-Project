import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from google import genai


# --- 1. ДОБЫЧА ТЕКСТА ---
def get_policy_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for el in soup(["script", "style", "nav", "footer"]): el.decompose()
        return " ".join(soup.get_text().split())[:20000]
    except Exception as e:
        return f"Ошибка загрузки: {e}"


# --- 2. АНАЛИЗ ИИ (НОВЫЙ SDK) ---
def analyze_with_gemini(policy_text, api_key):
    try:
        # Инициализация нового клиента
        client = genai.Client(api_key=api_key)

        prompt = f"""
        Ты — эксперт по приватности. Проанализируй текст политики конфиденциальности.
        Найди риски и верни ответ СТРОГО в формате JSON на русском.
        Структура:
        {{
          "risk_level": "Высокий" | "Средний" | "Низкий",
          "summary": "краткое резюме",
          "red_flags": [ {{"point": "суть риска", "quote": "цитата"}} ]
        }}

        Текст для анализа: {policy_text}
        """

        # Вызов модели из твоего списка
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config={"response_mime_type": "application/json"},
            contents=prompt
        )

        # В новом SDK ответ лежит в response.text
        return json.loads(response.text)
    except Exception as e:
        return {"error": f"Ошибка ИИ: {str(e)}"}


# --- 3. ИНТЕРФЕЙС STREAMLIT ---
st.set_page_config(page_title="Privacy Scan 2026", layout="wide")

st.title("🛡️ AI Privacy Policy Analyzer")

with st.sidebar:
    api_key = st.text_input("Gemini API Key:", type="password")
    st.caption("Используется модель: gemini-2.5-flash")

url = st.text_input("Вставьте URL политики конфиденциальности:")

if st.button("Проверить", type="primary"):
    if not api_key or not url:
        st.warning("Заполните ключ и ссылку!")
    else:
        with st.status("Анализирую...") as s:
            text = get_policy_text(url)
            if "Ошибка" in text:
                st.error(text)
            else:
                s.update(label="Текст готов. ИИ выносит вердикт...")
                result = analyze_with_gemini(text, api_key)

                if "error" in result:
                    st.error(result["error"])
                else:
                    s.update(label="Готово!", state="complete")

                    # Красивый вывод результата
                    lvl = result.get("risk_level", "Низкий")
                    color = "red" if lvl == "Высокий" else "orange" if lvl == "Средний" else "green"

                    st.markdown(f"### Уровень риска: :{color}[{lvl}]")
                    st.info(result.get("summary"))

                    st.subheader("🚩 Критические пункты:")
                    for flag in result.get("red_flags", []):
                        with st.expander(f"⚠️ {flag['point']}"):
                            st.write(f"**Цитата:** _{flag['quote']}_")