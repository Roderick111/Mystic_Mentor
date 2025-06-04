#!/usr/bin/env python3
"""
Test script for Esoteric Agent RAG activation system and Embedding Cache Performance
"""

from main import classify_and_decide_rag
from contextual_rag import OptimizedContextualRAGSystem
import time

def test_esoteric_agent_rag():
    print('🔮 Testing Esoteric Agent RAG Activation System')
    print('=' * 60)
    
    # Test queries organized by expected behavior
    test_cases = {
        "Emotional + RAG Expected": [
            "I feel anxious and don't know why",
            "I'm feeling really restless lately",
            "it is a Waxing Gibbous today, may be it affected my mood? i feel sad",
            "I feel disconnected from myself",
            "I always feel different during full moons"
        ],
        
        "Logical + RAG Expected": [
            "What should I know about spiritual practices?",
            "Explain lunar phases and their meanings",
            "How do moon cycles affect daily life?",
            "What is the significance of new moon rituals?",
            "Tell me about moon gardening practices"
        ],
        
        "Emotional + No RAG Expected": [
            "I'm stressed about work deadlines",
            "My relationship is having problems",
            "I'm worried about my finances",
            "I had a fight with my friend",
            "I'm feeling overwhelmed with responsibilities"
        ],
        
        "Logical + No RAG Expected": [
            "What's the weather like today?",
            "How do I cook pasta?",
            "What's the capital of France?",
            "Explain basic math concepts",
            "Tell me about car maintenance"
        ],
        
        "Mixed Scenarios": [
            "Hello there!",
            "Thanks for your help",
            "I need some guidance on my spiritual journey"
        ]
    }
    
    correct_classifications = 0
    correct_rag_decisions = 0
    total_tests = 0
    
    for category, queries in test_cases.items():
        print(f"\n📂 {category}")
        print("-" * 40)
        
        for query in queries:
            total_tests += 1
            
            # Test our combined classifier
            decision = classify_and_decide_rag({"messages": [type('obj', (object,), {'content': query})]})
            message_type = decision["message_type"]
            should_use_rag = decision["should_use_rag"]
            
            # Expected behavior based on category
            expected_emotional = "Emotional" in category
            expected_rag = "RAG Expected" in category
            
            # Check classification accuracy
            is_classification_correct = (
                (expected_emotional and message_type == "emotional") or
                (not expected_emotional and message_type == "logical")
            )
            
            # Check RAG decision accuracy  
            is_rag_correct = (should_use_rag == expected_rag)
            
            if is_classification_correct:
                correct_classifications += 1
            if is_rag_correct:
                correct_rag_decisions += 1
            
            # Visual indicators
            class_icon = "✅" if is_classification_correct else "❌"
            rag_icon = "✅" if is_rag_correct else "❌"
            
            print(f"  {class_icon} {rag_icon} [{message_type[:4]}|RAG:{should_use_rag}] \"{query[:45]}{'...' if len(query) > 45 else ''}\"")
    
    # Calculate accuracy
    classification_accuracy = (correct_classifications / total_tests) * 100
    rag_accuracy = (correct_rag_decisions / total_tests) * 100
    overall_accuracy = ((correct_classifications + correct_rag_decisions) / (total_tests * 2)) * 100
    
    print(f"\n📊 Test Results Summary:")
    print(f"Classification Accuracy: {correct_classifications}/{total_tests} ({classification_accuracy:.1f}%)")
    print(f"RAG Decision Accuracy: {correct_rag_decisions}/{total_tests} ({rag_accuracy:.1f}%)")
    print(f"Overall System Accuracy: {overall_accuracy:.1f}%")

def test_embedding_cache_performance():
    print('\n\n🚀 Testing Embedding Cache Performance')
    print('=' * 60)
    
    # Initialize RAG system
    print("Initializing RAG system with embedding cache...")
    rag = OptimizedContextualRAGSystem()
    
    # Test queries - some repeats to demonstrate cache hits
    test_queries = [
        "I feel anxious and restless today",
        "What does the new moon symbolize?", 
        "I'm feeling disconnected from my spiritual self",
        "I feel anxious and restless today",  # Repeat - should hit cache
        "How do lunar phases affect emotions?",
        "What does the new moon symbolize?",  # Repeat - should hit cache
        "I feel drawn to start something new during this moon phase",
        "I feel anxious and restless today",  # Another repeat
    ]
    
    print(f"\n⏱️  Testing {len(test_queries)} queries (including repeats)...")
    print("-" * 50)
    
    total_time = 0
    for i, query in enumerate(test_queries, 1):
        start_time = time.time()
        
        try:
            # Test RAG query
            result = rag.query(query)
            elapsed = time.time() - start_time
            total_time += elapsed
            
            # Identify if this was likely a cache hit (very fast)
            cache_indicator = "🎯" if elapsed < 0.5 else "🔍"
            
            print(f"  {i:2d}. {cache_indicator} {elapsed:.3f}s - \"{query[:40]}{'...' if len(query) > 40 else ''}\"")
            
        except Exception as e:
            print(f"  {i:2d}. ❌ Error: {str(e)[:50]}...")
    
    # Show cache statistics
    print(f"\n📊 Performance Summary:")
    print(f"Total time: {total_time:.3f}s")
    print(f"Average per query: {total_time/len(test_queries):.3f}s")
    
    print(f"\n💾 Embedding Cache Statistics:")
    cache_stats = rag.get_embedding_cache_stats()
    embedding_cache = cache_stats.get('embedding_cache', {})
    print(f"  Cached embeddings: {embedding_cache.get('cached_embeddings', 'unknown')}")
    print(f"  Cache size: {embedding_cache.get('cache_size_mb', 'unknown')} MB")
    print(f"  Status: {embedding_cache.get('status', 'unknown')}")
    
    print(f"\n🎯 Cache Performance Notes:")
    print("  🔍 = Fresh embedding computation (slower)")
    print("  🎯 = Cache hit (much faster)")

if __name__ == "__main__":
    test_esoteric_agent_rag()
    test_embedding_cache_performance() 