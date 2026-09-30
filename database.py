from langchain_community.vectorstores import FAISS

def create_vectorstore(chunks, embedding_model):

    vectorstore = FAISS.from_documents(
        chunks,
        embedding_model
    )

    vectorstore.save_local("vectorstore")

    return vectorstore
