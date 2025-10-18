import chromadb
from datetime import datetime


class VectorMemory:
    """
    A class to manage agent memory using a ChromaDB vector database.
    """

    def __init__(self, db_path: str = "src/memory/chroma_db"):
        """
        Initializes the VectorMemory, setting up the ChromaDB client and collection.

        Args:
            db_path: The directory path to store the ChromaDB database files.
        """
        print(f"[Memory]: Initializing ChromaDB at {db_path}")
        self.client = chromadb.PersistentClient(path=db_path)
        # The sentence-transformer model is downloaded automatically by ChromaDB the first time.
        self.collection = self.client.get_or_create_collection(
            name="quant_apprentice_memory"
        )

    def add_analysis(self, ticker: str, report_text: str):
        """
        Adds a new analysis report to the vector memory.

        Args:
            ticker: The stock ticker the report is about (e.g., 'NVDA').
            report_text: The full text of the final, refined analysis.
        """
        print(f"[Memory]: Adding analysis for {ticker} to vector memory...")
        try:
            current_date = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
            unique_id = f"{ticker}_{current_date}"

            self.collection.add(
                documents=[report_text],
                metadatas=[{"ticker": ticker, "date": current_date}],
                ids=[unique_id]
            )
            print(f"[Memory]: Successfully added document with ID: {unique_id}")
        except Exception as e:
            print(f"[Memory Error]: Failed to add analysis for {ticker}. Details: {e}")

    def query_memory(self, query_text: str, n_results: int = 2) -> list:
        """
        Queries the memory for analyses semantically related to the query text.

        Args:
            query_text: The question or topic to search for.
            n_results: The maximum number of relevant results to return.

        Returns:
            A list of the most relevant documents found in memory.
        """
        print(f"[Memory]: Querying memory with: '{query_text}'")
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results.get('documents', [[]])[0]
        except Exception as e:
            print(f"[Memory Error]: Failed to query memory. Details: {e}")
            return []