from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
    CSVLoader
)
from langchain.text_splitter import (
    MarkdownHeaderTextSplitter,
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter
)
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

import streamlit as st
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# 확장자별 로더 매핑
loader_map = {
    ".csv": CSVLoader,
    ".pdf": PyPDFLoader,
    ".txt": TextLoader,
    ".docx": UnstructuredWordDocumentLoader,
    ".doc": UnstructuredWordDocumentLoader,
    ".md": TextLoader
}

# 확장자별 스플리터 매핑
splitter_map = {
    ".csv": RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200),
    ".pdf": RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200),
    ".txt": CharacterTextSplitter(chunk_size=1000, chunk_overlap=200),
    ".docx": RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200),
    ".doc": RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200),
    ".md": MarkdownHeaderTextSplitter(headers_to_split_on=["#", "##", "###"])
}

def load_document(file_path: str):
    """
    파일 확장자에 따라 적절한 로더를 반환합니다.
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    loader_class = loader_map.get(file_extension)
    if not loader_class:
        raise ValueError(f"지원하지 않는 파일 확장자: {file_extension}")
    
    # 로더 초기화
    loader = loader_class(file_path)
    return loader, file_extension


def get_splitter(file_extension: str):
    """
    파일 확장자에 따라 적절한 스플리터를 반환합니다.
    """
    return splitter_map.get(file_extension, RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100))


class EducationPage:
    @staticmethod
    def display():
        st.title("📚 교육")
        st.caption("문서를 업로드하여 교육 데이터를 생성하세요.")
        #st.write("문서를 업로드하여 교육 데이터를 생성하세요.")

        # 파일 업로드 위젯
        uploaded_file = st.file_uploader("문서 파일 업로드", type=["pdf", "txt", "csv", "docx", "doc", "md"])
        
        if uploaded_file:
            try:
                # 파일을 임시 경로에 저장
                temp_path = f"./tmp/{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # 문서 로드 및 분할
                st.info("문서를 로드하는 중입니다...")
                loader, file_extension = load_document(temp_path)
                splitter = get_splitter(file_extension)
                document_list = loader.load_and_split(text_splitter=splitter)

                # 데이터베이스 생성
                embedding = OpenAIEmbeddings(model='text-embedding-3-large', openai_api_key=api_key)
                
                # 데이터베이스 저장
                database = Chroma.from_documents(
                    documents=document_list,
                    embedding=embedding,
                    collection_name='chroma-tax',
                    persist_directory="./tmp"
                )

                st.success("문서가 성공적으로 처리되었습니다!")

            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
