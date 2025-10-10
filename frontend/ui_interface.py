# -*- coding: utf-8 -*-
import streamlit as st
import requests
import time

# FastAPI endpoints
API_CHAT_URL = "http://localhost:5000/api/v1/nlp/chat_recieve"
API_SESSION_URL = "http://localhost:5000/api/v1/nlp/session/"

st.set_page_config(page_title="RAG Chatbot", page_icon="🤖")
st.title("🤖 RAG Chatbot for Industrial Machines")

st.markdown("""
اسأل أي سؤال عن صيانة أو تشغيل ماكينات CNC أو Fiber Laser وسيتم الرد عليك باللهجة المصرية مع شرح عملي خطوة بخطوة.
""")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        # عرض النصوص من اليمين لليسار
        st.markdown(f"<div style='direction: rtl; text-align: right;'>{msg['content']}</div>", unsafe_allow_html=True)

# User input
if user_input := st.chat_input("اكتب سؤالك هنا..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(f"<div style='direction: rtl; text-align: right;'>{user_input}</div>", unsafe_allow_html=True)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("<div style='direction: rtl; text-align: right;'>جارٍ توليد الإجابة... ⏳</div>", unsafe_allow_html=True)

        # Send query to FastAPI to create session
        session_id = None
        try:
            resp = requests.post(API_CHAT_URL, json={"Query": user_input})
            if resp.status_code == 200:
                session_id = resp.json().get("session_id")
            else:
                error_msg = f"❌ حدث خطأ في السيرفر: {resp.status_code}"
                message_placeholder.markdown(f"<div style='direction: rtl; text-align: right;'>{error_msg}</div>", unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                st.stop()
        except Exception as e:
            error_msg = f"❌ فشل الاتصال بالخادم: {e}"
            message_placeholder.markdown(f"<div style='direction: rtl; text-align: right;'>{error_msg}</div>", unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            st.stop()

        # Poll for answer
        final_answer = ""
        dots = ["",  "..", "..."]
        dot_index = 0

        for attempt in range(30):  # ~30 seconds timeout
            try:
                session_resp = requests.get(f"{API_SESSION_URL}{session_id}")
                if session_resp.status_code == 200:
                    data = session_resp.json()
                    raw_text = "\n".join(data.get("session", []))
                    # تنسيق النص: RTL وإضافة سطر بعد كل نقطة أو :
                    formatted_text = raw_text
                    final_answer = f"<div style='direction: rtl; text-align: right;'>{formatted_text}</div>"
                    break
                elif session_resp.status_code == 404:
                    message_placeholder.markdown(f"<div style='direction: rtl; text-align: right;'>جارٍ توليد الإجابة{dots[dot_index % 4]}</div>", unsafe_allow_html=True)
                    dot_index += 1
                    time.sleep(1)
                else:
                    final_answer = f"<div style='direction: rtl; text-align: right;'>❌ خطأ أثناء جلب الإجابة: {session_resp.status_code}</div>"
                    break
            except Exception as e:
                final_answer = f"<div style='direction: rtl; text-align: right;'>❌ فشل الاتصال بالخادم أثناء جلب الإجابة: {e}</div>"
                break
        else:
            final_answer = "<div style='direction: rtl; text-align: right;'>⏰ انتهى الوقت ولم يتم توليد إجابة بعد. حاول مرة أخرى لاحقًا.</div>"

        # Show final answer
        message_placeholder.markdown(final_answer, unsafe_allow_html=True)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": formatted_text})
