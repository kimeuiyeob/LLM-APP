from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
import os

# 환경변수를 불러옴
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

# 텍스트를 1500자 길이의 청크로 나누되, 각 청크가 200자씩 겹치도록 설정
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=200,
)

# 텍스트 로딩
#loader = TextLoader('/mnt/c/Users/rladm/Downloads/llm-app/document/hello.txt')
#loader = Docx2txtLoader('/mnt/c/Users/rladm/Downloads/llm-app/document/hello.txt')
#document_list = loader.load_and_split(text_splitter=text_splitter)

# OpenAI에서 제공하는 Embedding Model을 활용해서 `chunk`를 vector화
embedding = OpenAIEmbeddings(model='text-embedding-3-large', openai_api_key=api_key)

# 데이터를 처음 저장할 때 
#database = Chroma.from_documents(documents=document_list, embedding=embedding, collection_name='chroma-tax', persist_directory="/tmp")
# 이미 저장된 데이터를 사용할 때 
database = Chroma(collection_name='chroma-tax', persist_directory="/tmp", embedding_function=embedding)

# 질문
query = '이걸 누가 개발했나요?'

# `k` 값을 조절해서 얼마나 많은 데이터를 불러올지 결정
# retrieved_docs = database.similarity_search(query, k=3) <- 유사도 검색
retriever = database.as_retriever(search_kwargs={"k": 1},)

# LLM 설정
llm = ChatOpenAI(model='gpt-4o-mini', openai_api_key=api_key)

# 미리 정의된 프롬프트 가져오기
retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")

# 문서 체인 생성
combine_docs_chain = create_stuff_documents_chain(
    llm, retrieval_qa_chat_prompt
)

# 검색 체인 생성
retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

# 질문 응답 처리
ai_message = retrieval_chain.invoke({"input": query})

# 결과 출력
print(ai_message['answer'])