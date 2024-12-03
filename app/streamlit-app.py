import streamlit as st
from streamlit_option_menu import option_menu
from home import HomePage
from chat import ChatPage
from settings import SettingsPage
from document_load import EducationPage

# 페이지 설정
st.set_page_config(page_title="BPI 챗봇", page_icon="🤖")

# CSS 코드 추가
st.markdown(
    """
    <style>
        .st-emotion-cache-1jicfl2 {
            width: 70% !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# 사이드바 메뉴 선택
with st.sidebar:
    selected_option = option_menu(
        menu_title="메뉴",
        options=["홈", "챗봇", "설정", "교육"],
        icons=["house", "chat", "gear" , "journal"],
        default_index=1,
        orientation="vertical"
    )

# 선택된 메뉴에 따라 페이지 표시
if selected_option == "홈":
    HomePage.display()
elif selected_option == "챗봇":
    ChatPage.display()
elif selected_option == "설정":
    SettingsPage.display()
elif selected_option == "교육":
    EducationPage.display()
