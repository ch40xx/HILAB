import os
from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter
from langchain_community.document_loaders import PyPDFLoader
from langchain_classic.chains.summarize import load_summarize_chain
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

class LocalPDFAgent:
    def __init__(self):
        self.llm = ChatOpenRouter(
            model=os.getenv('MODEL_NAME'),
            api_key=os.getenv('OPENROUTER_API_KEY_TWO'),
            temperature=0
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000, 
            chunk_overlap=200
        )

    def summarize_pdf(self, file_path):
        """Loads a local PDF and runs map_reduce summarization."""
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"

        print(f"Loading PDF: {file_path}...")
        
        loader = PyPDFLoader(file_path)

        pages = loader.load()
        
        docs = self.text_splitter.split_documents(pages)
        
        print(f"Processing {len(docs)} document chunks via Map-Reduce...")

        chain = load_summarize_chain(self.llm, chain_type="map_reduce", verbose=False)
        
        result = chain.invoke(docs)
        return result["output_text"]

if __name__ == "__main__":
    agent = LocalPDFAgent()
    
    print("*** Local PDF Summarizer ***")

    path = input("Enter the full path to your PDF file: ").strip()
    #path = "~/Projects/HILAB/HILAB/agentic-webscraping/scrapy/arxiv_spider/downloads/arxiv_pdfs/2064short.pdf"
    
    full_path = os.path.expanduser(path)
    
    summary = agent.summarize_pdf(full_path)
    
    print("\n=== RESEARCH PAPER [PDF] SUMMARY ===\n")
    print(summary)
