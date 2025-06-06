#!/usr/bin/env python3
"""
Q&A Cache System for RAG

Implements specialized caching for Q&A documents where questions are embedded
separately from answers for optimal semantic matching.
"""

import os
import json
import time
import re
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import numpy as np

try:
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain_core.documents import Document
except ImportError:
    print("⚠️ Missing dependencies for Q&A cache")
    OpenAIEmbeddings = None
    Chroma = None
    Document = None


class QACache:
    """
    Specialized cache for Q&A documents with question-based retrieval.
    
    This system:
    1. Parses Q&A documents to extract question-answer pairs
    2. Creates embeddings for questions only
    3. Stores full answers as retrievable content
    4. Maintains domain filtering and metadata
    """
    
    def __init__(self, 
                 cache_dir: str = "data/chroma_db/qa_cache",
                 collection_name: str = "qa_cache_collection",
                 similarity_threshold: float = 0.85):
        """Initialize Q&A cache system."""
        self.cache_dir = cache_dir
        self.collection_name = collection_name
        self.similarity_threshold = similarity_threshold
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize embeddings
        try:
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                show_progress_bar=False
            )
        except Exception as e:
            print(f"❌ Failed to initialize Q&A embeddings: {e}")
            self.embeddings = None
            
        # Initialize vector store
        self.vectorstore = None
        self._setup_vectorstore()
        
        # Stats tracking
        self.stats = {
            'total_qa_pairs': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_queries': 0,
            'avg_response_time': 0.0,
            'domains_loaded': set()
        }
    
    def _setup_vectorstore(self):
        """Initialize or load the Q&A vectorstore."""
        if self.embeddings is None:
            print("⚠️ Cannot initialize Q&A vectorstore without embeddings")
            return
            
        if os.path.exists(self.cache_dir):
            try:
                self.vectorstore = Chroma(
                    persist_directory=self.cache_dir,
                    embedding_function=self.embeddings,
                    collection_name=self.collection_name
                )
                count = self.vectorstore._collection.count()
                print(f"📚 Q&A Cache: {count} question-answer pairs loaded")
            except Exception as e:
                print(f"⚠️ Error loading Q&A cache: {e}")
                self.vectorstore = None
        else:
            print("📚 Q&A Cache: Creating new cache")
    
    def parse_qa_document(self, content: str, source_path: str, domain: str) -> List[Dict[str, Any]]:
        """
        Parse Q&A document to extract question-answer pairs.
        
        Args:
            content: Raw document content
            source_path: Path to source file
            domain: Domain classification
            
        Returns:
            List of question-answer pair dictionaries
        """
        qa_pairs = []
        
        # Split by major question headers (## followed by number)
        sections = re.split(r'\n## \d+\.', content)
        
        for i, section in enumerate(sections):
            if not section.strip():
                continue
                
            # Extract question from the first line after split
            lines = section.strip().split('\n')
            if not lines:
                continue
                
            # Find the question (usually the first substantial line)
            question = None
            answer_start_idx = 1
            
            for idx, line in enumerate(lines):
                if line.strip() and not line.startswith('#'):
                    question = line.strip()
                    answer_start_idx = idx + 1
                    break
            
            if not question:
                continue
                
            # Clean up question
            question = re.sub(r'^[\d\.\s]+', '', question).strip()  # Remove numbering
            question = question.rstrip('?') + '?'  # Ensure ends with ?
            
            # Extract answer (everything after the question)
            answer_lines = lines[answer_start_idx:]
            answer = '\n'.join(answer_lines).strip()
            
            # Remove separators and clean up
            answer = re.sub(r'\n---+\n', '\n\n', answer)
            answer = answer.strip()
            
            if question and answer and len(answer) > 50:  # Minimum answer length
                qa_pairs.append({
                    'question': question,
                    'answer': answer,
                    'domain': domain,
                    'source': source_path,
                    'qa_id': f"{domain}_qa_{i}",
                    'question_length': len(question),
                    'answer_length': len(answer)
                })
        
        return qa_pairs
    
    def add_qa_document(self, file_path: str, domain: str) -> bool:
        """
        Add Q&A document to cache with question-based embedding.
        
        Args:
            file_path: Path to Q&A document
            domain: Domain classification
            
        Returns:
            bool: Success status
        """
        try:
            if not os.path.exists(file_path):
                print(f"❌ Q&A file not found: {file_path}")
                return False
                
            # Read document content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse Q&A pairs
            qa_pairs = self.parse_qa_document(content, file_path, domain)
            
            if not qa_pairs:
                print(f"⚠️ No Q&A pairs found in {file_path}")
                return False
            
            # Create documents for questions only (for embedding)
            question_docs = []
            for qa_pair in qa_pairs:
                # Create document with question as content for embedding
                doc = Document(
                    page_content=qa_pair['question'],
                    metadata={
                        'qa_id': qa_pair['qa_id'],
                        'domain': qa_pair['domain'],
                        'source': qa_pair['source'],
                        'doc_type': 'qa',
                        'question': qa_pair['question'],
                        'answer': qa_pair['answer'],  # Store full answer in metadata
                        'question_length': qa_pair['question_length'],
                        'answer_length': qa_pair['answer_length']
                    }
                )
                question_docs.append(doc)
            
            # Add to vectorstore
            if self.vectorstore is None:
                # Create new vectorstore
                self.vectorstore = Chroma.from_documents(
                    documents=question_docs,
                    embedding=self.embeddings,
                    persist_directory=self.cache_dir,
                    collection_name=self.collection_name
                )
            else:
                # Add to existing vectorstore
                self.vectorstore.add_documents(question_docs)
            
            # Update stats
            self.stats['total_qa_pairs'] += len(qa_pairs)
            self.stats['domains_loaded'].add(domain)
            
            print(f"✅ Added {len(qa_pairs)} Q&A pairs from {file_path} ({domain})")
            return True
            
        except Exception as e:
            print(f"❌ Error adding Q&A document {file_path}: {e}")
            return False
    
    def search_qa(self, query: str, active_domains: List[str], k: int = 3) -> Optional[Dict[str, Any]]:
        """
        Search for Q&A answers based on question similarity.
        
        Args:
            query: User's question
            active_domains: List of active domains to filter by
            k: Number of similar questions to retrieve
            
        Returns:
            Dict with answer and metadata if found, None otherwise
        """
        start_time = time.time()
        self.stats['total_queries'] += 1
        
        try:
            if self.vectorstore is None:
                self.stats['cache_misses'] += 1
                return None
            
            # Create domain filter
            domain_filter = {"domain": {"$in": active_domains}} if active_domains else {}
            
            # Search for similar questions
            if domain_filter:
                docs = self.vectorstore.similarity_search_with_score(
                    query, 
                    k=k,
                    filter=domain_filter
                )
            else:
                docs = self.vectorstore.similarity_search_with_score(query, k=k)
            
            if not docs:
                self.stats['cache_misses'] += 1
                return None
            
            # Check if best match exceeds similarity threshold
            best_doc, best_score = docs[0]
            similarity = 1 - best_score  # Convert distance to similarity
            
            if similarity >= self.similarity_threshold:
                # Cache hit!
                self.stats['cache_hits'] += 1
                response_time = time.time() - start_time
                
                # Update average response time
                self._update_avg_response_time(response_time)
                
                return {
                    'answer': best_doc.metadata['answer'],
                    'question': best_doc.metadata['question'],
                    'domain': best_doc.metadata['domain'],
                    'source': best_doc.metadata['source'],
                    'similarity': similarity,
                    'qa_id': best_doc.metadata['qa_id'],
                    'response_time': response_time,
                    'cache_type': 'qa_hit'
                }
            else:
                self.stats['cache_misses'] += 1
                return None
                
        except Exception as e:
            print(f"❌ Q&A search error: {e}")
            self.stats['cache_misses'] += 1
            return None
    
    def _update_avg_response_time(self, response_time: float):
        """Update average response time calculation."""
        total = self.stats['total_queries']
        if total > 1:
            self.stats['avg_response_time'] = (
                (self.stats['avg_response_time'] * (total - 1) + response_time) / total
            )
        else:
            self.stats['avg_response_time'] = response_time
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Q&A cache statistics."""
        total_queries = self.stats['total_queries']
        hit_rate = (self.stats['cache_hits'] / total_queries * 100) if total_queries > 0 else 0
        
        # Get actual count from vectorstore if available
        actual_qa_pairs = 0
        if self.vectorstore:
            try:
                actual_qa_pairs = self.vectorstore._collection.count()
            except:
                actual_qa_pairs = self.stats['total_qa_pairs']
        
        return {
            'total_qa_pairs': actual_qa_pairs or self.stats['total_qa_pairs'],
            'total_queries': total_queries,
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'hit_rate': hit_rate,
            'avg_response_time': self.stats['avg_response_time'],
            'domains_loaded': list(self.stats['domains_loaded']),
            'similarity_threshold': self.similarity_threshold
        }
    
    def clear_cache(self):
        """Clear the Q&A cache."""
        try:
            if self.vectorstore:
                # Clear the collection by deleting all documents
                try:
                    # Get all document IDs and delete them
                    collection = self.vectorstore._collection
                    all_docs = collection.get()
                    if all_docs['ids']:
                        collection.delete(ids=all_docs['ids'])
                        print("✅ Cleared existing Q&A documents")
                except Exception as delete_error:
                    print(f"⚠️ Collection delete issue (continuing): {delete_error}")
                
            # Reset stats
            self.stats = {
                'total_qa_pairs': 0,
                'cache_hits': 0,
                'cache_misses': 0,
                'total_queries': 0,
                'avg_response_time': 0.0,
                'domains_loaded': set()
            }
            
            # Reinitialize
            self._setup_vectorstore()
            print("✅ Q&A cache cleared")
            return True
            
        except Exception as e:
            print(f"❌ Error clearing Q&A cache: {e}")
            return False
    
    def reload_cache(self):
        """Reload the Q&A cache from disk."""
        self._setup_vectorstore()
        print("✅ Q&A cache reloaded")
    
    def __str__(self) -> str:
        """String representation."""
        return f"QACache(pairs={self.stats['total_qa_pairs']}, domains={len(self.stats['domains_loaded'])})" 