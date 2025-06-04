"""
Optimized Contextual RAG Implementation - Phase 1
High-performance implementation with batch processing and persistent storage.
"""

import os
import json
import time
from typing import List, TypedDict, Optional
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm

# Document loading and processing
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Embeddings and vector store
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma

# LangGraph for workflow
from langgraph.graph import StateGraph, START, END

# Contextual enhancement
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document

# Load environment variables
load_dotenv()

# Define the state for our RAG workflow
class ContextualRAGState(TypedDict):
    question: str
    documents: List[str]
    enhanced_context: str
    answer: str

class OptimizedContextualRAGSystem:
    def __init__(self, persist_directory: str = "./chroma_db", force_rebuild: bool = False):
        """Initialize the Optimized Contextual RAG system."""
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        self.force_rebuild = force_rebuild
        
        # Metadata file for tracking processed documents
        self.metadata_file = self.persist_directory / "processed_metadata.json"
        
        # Initialize embeddings - using OpenAI's latest model for best performance
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large",
            dimensions=3072  # Full dimensions for maximum performance
        )
        
        # Initialize LLM for contextual enhancement and answer generation
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # Cost-effective choice for contextual enhancement
            temperature=0
        )
        
        # Initialize text splitter optimized for contextual retrieval
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,      # Optimal size for contextual enhancement
            chunk_overlap=200,   # Good overlap for context preservation
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Optimized contextual enhancement prompt (based on Anthropic's research)
        self.contextual_prompt = PromptTemplate(
            input_variables=["document_context", "chunk_content"],
            template="""Please provide a brief, contextual summary for this text chunk to improve search retrieval:

Document Context: {document_context}

Text Chunk: {chunk_content}

Provide only a concise context (1-2 sentences) that situates this chunk within the document."""
        )
        
        # Initialize vector store
        self.vectorstore = None
        self.retriever = None
        
        # Initialize LangGraph workflow
        self.workflow = self._build_rag_workflow()
        
        # Load existing vectorstore if it exists
        self._load_existing_vectorstore()
    
    def _load_existing_vectorstore(self):
        """Load existing vectorstore if it exists and is not being force rebuilt."""
        if not self.force_rebuild and (self.persist_directory / "chroma.sqlite3").exists():
            try:
                print("🔄 Loading existing vector store...")
                self.vectorstore = Chroma(
                    persist_directory=str(self.persist_directory),
                    embedding_function=self.embeddings,
                    collection_name="contextual_rag_collection"
                )
                
                # Create retriever with optimized settings
                self._setup_retriever()
                
                # Load metadata
                if self.metadata_file.exists():
                    with open(self.metadata_file, 'r') as f:
                        metadata = json.load(f)
                        print(f"✅ Loaded existing vector store with {metadata.get('total_chunks', 'unknown')} chunks")
                        print(f"📄 Processed documents: {', '.join(metadata.get('processed_files', []))}")
                else:
                    print("✅ Loaded existing vector store (no metadata found)")
                    
            except Exception as e:
                print(f"❌ Failed to load existing vector store: {e}")
                print("🔄 Will create new vector store...")
                self.vectorstore = None
    
    def _setup_retriever(self):
        """Setup the retriever with optimized settings."""
        if self.vectorstore:
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": 5  # Number of documents to retrieve
                }
            )
    
    def is_document_processed(self, file_path: str) -> bool:
        """Check if a document has already been processed."""
        if not self.metadata_file.exists():
            return False
            
        try:
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
                return file_path in metadata.get('processed_files', [])
        except Exception:
            return False
    
    def load_and_process_documents(self, file_path: str, skip_if_processed: bool = True):
        """
        Load and process documents with optimized batch contextual enhancement.
        Returns number of chunks processed.
        """
        print(f"📚 Loading document from: {file_path}")
        
        # Check if already processed
        if skip_if_processed and not self.force_rebuild and self.is_document_processed(file_path):
            print(f"✅ Document already processed: {file_path}")
            return 0
        
        # Load document
        loader = TextLoader(file_path, encoding="utf-8")
        documents = loader.load()
        
        print(f"📄 Loaded {len(documents)} documents")
        
        # Process each document with optimized batch contextual enhancement
        total_chunks = 0
        
        for doc in documents:
            print(f"🔄 Processing document: {doc.metadata.get('source', 'Unknown')}")
            chunks_processed = self._create_contextual_chunks_batch(doc)
            total_chunks += chunks_processed
        
        # Save metadata
        self._save_processed_metadata(file_path, total_chunks)
        
        print(f"✅ Successfully processed {total_chunks} chunks with contextual enhancement")
        return total_chunks
    
    def _create_contextual_chunks_batch(self, document: Document) -> int:
        """
        Enhanced chunking with OPTIMIZED batch contextual enhancement.
        Uses LangChain's batch processing for 10x+ speed improvement.
        """
        whole_document = document.page_content
        chunks = self.text_splitter.split_documents([document])
        
        if not chunks:
            return 0
        
        print(f"🚀 Processing {len(chunks)} chunks with contextual enhancement...")
        
        # Create abbreviated document context for efficiency
        doc_context = whole_document[:1500] + "..." if len(whole_document) > 1500 else whole_document
        
        # Prepare batch inputs for LLM
        batch_inputs = []
        for chunk in chunks:
            prompt_input = {
                "document_context": doc_context,
                "chunk_content": chunk.page_content
            }
            batch_inputs.append(self.contextual_prompt.format(**prompt_input))
        
        # BATCH PROCESS all contextual enhancements at once
        start_time = time.time()
        try:
            # Use LangChain's optimized batch processing
            batch_responses = self.llm.batch(batch_inputs)
            batch_time = time.time() - start_time
            
            print(f"⚡ Batch processing completed in {batch_time:.2f}s ({len(chunks)/batch_time:.1f} chunks/sec)")
            
            # Process responses and create enhanced documents
            enhanced_documents = []
            for i, (chunk, response) in enumerate(zip(chunks, batch_responses)):
                try:
                    context = response.content.strip()
                    
                    # Create enhanced content with contextual prefix
                    enhanced_content = f"Context: {context}\n\nContent: {chunk.page_content}"
                    
                    # Create new document with enhanced content
                    enhanced_doc = Document(
                        page_content=enhanced_content,
                        metadata={
                            **chunk.metadata,
                            'chunk_id': f"chunk_{i}",
                            'char_count': len(enhanced_content),
                            'contextually_enhanced': True,
                            'original_chunk_size': len(chunk.page_content),
                            'context_added': len(context)
                        }
                    )
                    enhanced_documents.append(enhanced_doc)
                    
                except Exception as chunk_error:
                    print(f"❌ Error processing chunk {i}: {chunk_error}")
                    # Use original chunk if enhancement fails
                    enhanced_documents.append(chunk)
        
        except Exception as e:
            print(f"❌ Batch processing failed: {e}")
            print("🔄 Falling back to sequential processing...")
            
            # Fallback to sequential processing
            enhanced_documents = []
            for i, chunk in enumerate(tqdm(chunks, desc="Processing chunks sequentially")):
                try:
                    prompt_input = {
                        "document_context": doc_context,
                        "chunk_content": chunk.page_content
                    }
                    
                    # Single LLM call for this chunk
                    context_response = self.llm.invoke(self.contextual_prompt.format(**prompt_input))
                    context = context_response.content.strip()
                    
                    # Create enhanced content
                    enhanced_content = f"Context: {context}\n\nContent: {chunk.page_content}"
                    
                    # Create enhanced document
                    enhanced_doc = Document(
                        page_content=enhanced_content,
                        metadata={
                            **chunk.metadata,
                            'chunk_id': f"chunk_{i}",
                            'char_count': len(enhanced_content),
                            'contextually_enhanced': True,
                            'original_chunk_size': len(chunk.page_content),
                            'context_added': len(context)
                        }
                    )
                    enhanced_documents.append(enhanced_doc)
                    
                except Exception as e:
                    print(f"❌ Error enhancing chunk {i}: {e}")
                    # Use original chunk if enhancement fails
                    enhanced_documents.append(chunk)
        
        # Add enhanced documents to vector store
        self._add_to_vectorstore_batch(enhanced_documents)
        
        return len(enhanced_documents)
    
    def _add_to_vectorstore_batch(self, documents: List[Document]):
        """Add documents to vector store using optimized batch operations."""
        if not documents:
            return
        
        if self.vectorstore is None:
            # Create new vector store with batch
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=str(self.persist_directory),
                collection_name="contextual_rag_collection"
            )
        else:
            # Add to existing vector store using batch upsert
            try:
                self.vectorstore.add_documents(documents)
            except Exception as e:
                print(f"❌ Batch add failed, trying individual adds: {e}")
                for i, doc in enumerate(tqdm(documents, desc="Adding documents")):
                    try:
                        self.vectorstore.add_documents([doc])
                    except Exception as doc_error:
                        print(f"❌ Failed to add document {i}: {doc_error}")
        
        # Setup retriever
        self._setup_retriever()
    
    def _save_processed_metadata(self, file_path: str, chunks_count: int):
        """Save metadata about processed documents."""
        metadata = {}
        
        # Load existing metadata
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    metadata = json.load(f)
            except Exception:
                metadata = {}
        
        # Update metadata
        if 'processed_files' not in metadata:
            metadata['processed_files'] = []
        
        if file_path not in metadata['processed_files']:
            metadata['processed_files'].append(file_path)
        
        metadata['total_chunks'] = metadata.get('total_chunks', 0) + chunks_count
        metadata['last_updated'] = time.time()
        
        # Save metadata
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            print(f"❌ Failed to save metadata: {e}")
    
    def _build_rag_workflow(self):
        """Build the LangGraph workflow for contextual RAG."""
        workflow = StateGraph(ContextualRAGState)
        
        # Add nodes
        workflow.add_node("retrieve_contextual", self._retrieve_contextual_documents)
        workflow.add_node("enhance_context", self._enhance_retrieved_context)
        workflow.add_node("generate_answer", self._generate_contextual_answer)
        
        # Define workflow edges
        workflow.add_edge(START, "retrieve_contextual")
        workflow.add_edge("retrieve_contextual", "enhance_context")
        workflow.add_edge("enhance_context", "generate_answer")
        workflow.add_edge("generate_answer", END)
        
        return workflow.compile()
    
    def _retrieve_contextual_documents(self, state: ContextualRAGState):
        """Retrieve documents using contextual enhancement."""
        if not self.retriever:
            raise ValueError("Vector store not initialized. Please load documents first.")
        
        question = state["question"]
        
        # Retrieve contextually enhanced documents
        docs = self.retriever.invoke(question)
        
        # Extract document content
        document_contents = [doc.page_content for doc in docs]
        
        print(f"🔍 Retrieved {len(document_contents)} contextually enhanced documents")
        
        return {"documents": document_contents}
    
    def _enhance_retrieved_context(self, state: ContextualRAGState):
        """Prepare context for optimal LLM processing."""
        documents = state["documents"]
        
        # Combine all retrieved documents with clear separators
        enhanced_context = "\n\n" + "="*50 + "\n\n".join(documents)
        
        return {"enhanced_context": enhanced_context}
    
    def _generate_contextual_answer(self, state: ContextualRAGState):
        """Generate answer using contextually enhanced documents."""
        question = state["question"]
        context = state["enhanced_context"]
        
        # Create optimized prompt for answer generation
        answer_prompt = f"""Based on the following contextually enhanced documents, provide a comprehensive and accurate answer to the question.

Context:
{context}

Question: {question}

Instructions:
- Use only the information provided in the context
- If the context doesn't contain enough information to answer the question, say so clearly
- Be specific and cite relevant parts of the context when possible
- Provide a clear, well-structured answer

Answer:"""
        
        # Generate answer
        answer = self.llm.invoke(answer_prompt).content
        
        return {"answer": answer}
    
    def query(self, question: str) -> str:
        """
        Query the contextual RAG system.
        
        Args:
            question: The question to ask
            
        Returns:
            The generated answer
        """
        if not self.vectorstore:
            raise ValueError("No documents loaded. Please load documents first using load_and_process_documents()")
        
        # Initialize state
        initial_state = {
            "question": question,
            "documents": [],
            "enhanced_context": "",
            "answer": ""
        }
        
        # Run the workflow
        result = self.workflow.invoke(initial_state)
        
        return result["answer"]
    
    def get_retrieval_info(self, question: str) -> dict:
        """Get information about the retrieval process for debugging."""
        if not self.retriever:
            raise ValueError("Vector store not initialized. Please load documents first.")
        
        docs = self.retriever.invoke(question)
        
        return {
            "num_retrieved": len(docs),
            "documents": [
                {
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in docs
            ]
        }
    
    def get_stats(self) -> dict:
        """Get statistics about the RAG system."""
        stats = {
            "vectorstore_exists": self.vectorstore is not None,
            "retriever_exists": self.retriever is not None,
            "persist_directory": str(self.persist_directory),
        }
        
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    metadata = json.load(f)
                    stats.update({
                        "total_chunks": metadata.get('total_chunks', 0),
                        "processed_files": metadata.get('processed_files', []),
                        "last_updated": metadata.get('last_updated', 0)
                    })
            except Exception:
                pass
        
        return stats 