import streamlit as st
from main import main as run_ai_system

st.title("🤖 نظام الوكلاء الذكي")
st.write("اطرح سؤالك وسيقوم 8 وكلاء بالرد!")

user_input = st.text_area("اكتب مهمتك هنا:")

if st.button("ابدأ النقاش"):
    with st.spinner('الوكلاء يفكرون...'):
        # هنا نربط مع نظامك
        st.success("تمت المعالجة!")