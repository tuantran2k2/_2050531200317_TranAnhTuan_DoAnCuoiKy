from dotenv import load_dotenv

from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import FlashrankRerank

from models import _environments
from controllers.vector_databases import _qdrant

load_dotenv()


# Helper function for printing docs
def pretty_print_docs(docs):
    print(
        f"\n\n{'-' * 100}\n\n".join(
            [f"Document {i + 1}:\n\n" + d.page_content for i, d in enumerate(docs)]
        )
    )


collection_name = "pvbang_prompts_10"
# db = save_datavector("../../files/Prompt Engineering.pdf", collection_name)
db = _qdrant.load_vector_db(collection_name)

# retriever = db.as_retriever(search_kwargs={"k": 20, "score_threshold": 0.5}, search_type="similarity_score_threshold")
retriever = db.as_retriever(search_kwargs={"k": 10}, search_type="similarity")
query = "PROMPT ENGINEERING"
ans = retriever.invoke(query)

pretty_print_docs(ans)

compressor = FlashrankRerank()
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=retriever
)

compressed_docs = compression_retriever.invoke(query)
print("\n\nCompressed documents:\n")
pretty_print_docs(compressed_docs)
