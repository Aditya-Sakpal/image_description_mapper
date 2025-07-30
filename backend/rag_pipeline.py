from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, PointStruct, Distance, VectorParams
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

class VectorSearch:
    def __init__(self, collection_name: str = "oracle_docs_data"):
        """
        Initialize Qdrant client and OpenAI embeddings
        
        Args:
            collection_name: Name of the Qdrant collection
        """
        # Initialize Qdrant client
        self.client = QdrantClient(
            url=os.getenv("QDRANT_CLOUD_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
            prefer_grpc=True
        )
        
        # Initialize OpenAI embeddings
        self.embedding_model = OpenAIEmbeddings(
            model="text-embedding-3-large",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.collection_name = collection_name

    def text_to_embedding(self, text: str) -> List[float]:
        """
        Convert text to embedding vector
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        return self.embedding_model.embed_query(text)

    def search_similar_chunks(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar text chunks in Qdrant
        
        Args:
            query_text: Text to search similar chunks for
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries containing:
            - text: The similar text chunk
            - score: Similarity score
            - metadata: Original metadata
        """
        # Convert query text to embedding
        query_embedding = self.text_to_embedding(query_text)
        
        # Search Qdrant for similar vectors
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            with_payload=True,
            with_vectors=False
        )
        
        # Format results
        results = []
        for result in search_results:
            results.append({
                "text": result.payload.get("text", ""),
                "score": result.score,
                "metadata": {
                    "link": result.payload.get("link", ""),
                    "original_text": result.payload.get("original_text", ""),
                    "chunk_index": result.payload.get("chunk_index", -1),
                    "document_id": result.payload.get("document_id", -1)
                }
            })
        
        return results

# Example usage
if __name__ == "__main__":
    # Initialize the search system
    search = VectorSearch(collection_name="oracle_docs_data")
    
    # Example query
    query = "What are the security best practices for Oracle databases?"
    
    # Get top 5 similar chunks
    results = search.search_similar_chunks(query)
    
    # Print results
    print(f"Top {len(results)} results for query: '{query}'\n")
    for i, result in enumerate(results, 1):
        print(f"Result #{i} (Score: {result['score']:.3f})")
        print(f"Text: {result['text']}...")  # Print first 200 chars
        print(f"Source: {result['metadata']['link']}")
        print(f"Document ID: {result['metadata']['document_id']}")
        print(f"Chunk Index: {result['metadata']['chunk_index']}")
        print("-" * 80)