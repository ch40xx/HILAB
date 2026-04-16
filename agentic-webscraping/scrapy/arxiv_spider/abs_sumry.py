import os
import sqlite3
from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter
from langchain_community.docstore.document import Document
from langchain_classic.chains.summarize import load_summarize_chain
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

class PaperAgent:
    def __init__(self):
        self.llm = ChatOpenRouter(
            model=os.getenv('MODEL_NAME'),
            api_key=os.getenv('OPENROUTER_API_KEY_ONE'),
            temperature=0.2
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000, 
            chunk_overlap=300
        )

    def fetch_paper_from_db(self, paper_title=None):
        try:
            conn = sqlite3.connect(os.getenv('DB_PATH'))
            cursor = conn.cursor()
            
            if paper_title:
                cursor.execute("SELECT abstract FROM paper_queue WHERE title LIKE ?", (f'%{paper_title}%',))
            else:
                cursor.execute("SELECT abstract FROM paper_queue LIMIT 1")
                
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else None
        except Exception as e:
            print(f"Database error: {e}")
            return None

    def summarize(self, raw_text):
        """Processes text through the LangChain summarization chain."""
        if not raw_text:
            return "No text provided for summarization."

        docs = self.text_splitter.create_documents([raw_text])
        
        print(f"Paper split into {len(docs)} chunks. Starting summarization...")

        chain = load_summarize_chain(self.llm, chain_type="stuff")
        
        result = chain.invoke(docs)
        return result["output_text"]

if __name__ == "__main__":
    agent = PaperAgent()
    
    print("*** Research Paper Abstract Agent ***")
    search_query = input("Enter paper title to summarize (or press Enter for latest): ")
    
    paper_content = agent.fetch_paper_from_db(search_query)
    
    if paper_content:
        summary = agent.summarize(paper_content)
        print("\n=== FINAL SUMMARY ===\n")
        print(summary)
    else:
        print("Could not find that paper in the database.")
