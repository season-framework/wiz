import os
from langchain_openai import ChatOpenAI
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

Assistant = wiz.ide.plugin.model("assistant")
guide = wiz.server.config.ide.assistant_guide
assistant_path = wiz.server.config.ide.assistant_path
if assistant_path is None:
    assistant_path = "src/reference"

def reset():
    assistant = Assistant(path=assistant_path)
    retriever = assistant.retriever()
    wiz.server.app.wizideretriever = retriever
    wiz.response.status(200)

def request():
    openai_key = wiz.server.config.ide.openai_key
    openai_model = wiz.server.config.ide.openai_model
    query = wiz.request.query("query", True)

    output_parser = StrOutputParser()
    llm = ChatOpenAI(
        model=openai_model,
        temperature=0,
        max_tokens=4096,
        api_key=openai_key)

    if wiz.server.app.wizideretriever is None:
        assistant = Assistant(path=assistant_path)
        retriever = assistant.retriever()
        wiz.server.app.wizideretriever = retriever
    else:
        retriever = wiz.server.app.wizideretriever
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", guide + "\ncontext is below:\n{context}"),
        ("human", query)
    ])

    if retriever is None:
        chain = prompt | llm | output_parser
    else:
        setup_and_retrieval = RunnableParallel({"context": retriever, "question": RunnablePassthrough()})
        chain = setup_and_retrieval | prompt | llm | output_parser

    result = chain.invoke(query)
    wiz.response.status(200, result)