#!/usr/bin/env python3
"""
Stats Collector for Esoteric Vectors

Clean statistics collection with:
- Query performance tracking
- Vectorstore health monitoring
- Resilience metrics integration
- Clean logging
"""

import time
from typing import Dict, Any, Optional
from collections import defaultdict, deque
from datetime import datetime

from utils.logger import logger


class StatsCollector:
    """
    Clean statistics collector for system performance monitoring.
    
    Tracks:
    - Query performance and response times
    - Vectorstore health and document counts
    - System resilience metrics
    - Cache hit rates and efficiency
    """
    
    def __init__(self, max_recent_queries: int = 100):
        """Initialize stats collector."""
        self.max_recent_queries = max_recent_queries
        
        # Query performance tracking
        self.query_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'recent_times': deque(maxlen=max_recent_queries)
        })
        
        # System start time
        self.start_time = datetime.now()
        
        logger.debug("Stats collector initialized")
    
    def record_query(self, query_type: str, response_time: float):
        """Record a query execution."""
        stats = self.query_stats[query_type]
        stats['count'] += 1
        stats['total_time'] += response_time
        stats['recent_times'].append(response_time)
        
        logger.debug(f"Recorded {query_type} query: {response_time:.3f}s")
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get comprehensive query performance statistics."""
        if not self.query_stats:
            return {
                'total_queries': 0,
                'avg_response_time': 0.0,
                'by_type': {}
            }
        
        total_queries = sum(stats['count'] for stats in self.query_stats.values())
        total_time = sum(stats['total_time'] for stats in self.query_stats.values())
        avg_response_time = total_time / total_queries if total_queries > 0 else 0.0
        
        by_type = {}
        for query_type, stats in self.query_stats.items():
            avg_time = stats['total_time'] / stats['count'] if stats['count'] > 0 else 0.0
            recent_avg = sum(stats['recent_times']) / len(stats['recent_times']) if stats['recent_times'] else 0.0
            
            by_type[query_type] = {
                'count': stats['count'],
                'avg_response_time': avg_time,
                'recent_avg_response_time': recent_avg,
                'total_time': stats['total_time']
            }
        
        return {
            'total_queries': total_queries,
            'avg_response_time': avg_response_time,
            'total_time': total_time,
            'by_type': by_type
        }
    
    def get_vectorstore_stats(self, vectorstore) -> Dict[str, Any]:
        """Get vectorstore statistics."""
        stats = {}
        
        try:
            if vectorstore and hasattr(vectorstore, '_collection'):
                collection = vectorstore._collection
                if collection:
                    stats['vectorstore_docs'] = collection.count()
                    stats['collection_name'] = collection.name
                    
                    # Collection metadata
                    metadata = getattr(collection, 'metadata', {})
                    if metadata:
                        stats['collection_metadata'] = {
                            'version': metadata.get('version', 'unknown'),
                            'created': metadata.get('created', 'unknown'),
                            'embedding_model': metadata.get('embedding_model', 'unknown'),
                            'last_updated': metadata.get('last_updated', 'unknown')
                        }
                    
                    # Health metrics
                    health_metrics = self._get_collection_health(collection)
                    stats['collection_health'] = health_metrics
                else:
                    stats['vectorstore_docs'] = 0
                    stats['error'] = 'Collection not available'
            else:
                stats['vectorstore_docs'] = 0
                stats['error'] = 'Vectorstore not available'
                
        except Exception as e:
            logger.debug(f"Error getting vectorstore stats: {e}")
            stats['vectorstore_docs'] = 0
            stats['error'] = str(e)
        
        return stats
    
    def _get_collection_health(self, collection) -> Dict[str, Any]:
        """Get collection health metrics."""
        try:
            # Basic health check
            doc_count = collection.count()
            
            health = {
                'status': 'healthy' if doc_count > 0 else 'empty',
                'document_count': doc_count,
                'last_checked': datetime.now().isoformat()
            }
            
            # Check if collection has metadata
            metadata = getattr(collection, 'metadata', {})
            if metadata:
                health['has_metadata'] = True
                health['version'] = metadata.get('version', 'unknown')
            else:
                health['has_metadata'] = False
            
            return health
            
        except Exception as e:
            logger.debug(f"Collection health check failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'last_checked': datetime.now().isoformat()
            }
    
    def get_system_uptime(self) -> Dict[str, Any]:
        """Get system uptime information."""
        uptime = datetime.now() - self.start_time
        
        return {
            'start_time': self.start_time.isoformat(),
            'uptime_seconds': uptime.total_seconds(),
            'uptime_formatted': str(uptime).split('.')[0]  # Remove microseconds
        }
    
    def reset_query_stats(self):
        """Reset all query statistics."""
        self.query_stats.clear()
        logger.debug("Query statistics reset")
    
    def get_performance_summary(self) -> str:
        """Get formatted performance summary."""
        try:
            query_stats = self.get_query_stats()
            uptime = self.get_system_uptime()
            
            if query_stats['total_queries'] == 0:
                return f"📊 System uptime: {uptime['uptime_formatted']} | No queries processed yet"
            
            summary_parts = [
                f"📊 Uptime: {uptime['uptime_formatted']}",
                f"Queries: {query_stats['total_queries']}",
                f"Avg: {query_stats['avg_response_time']:.3f}s"
            ]
            
            # Add breakdown by type if multiple types
            if len(query_stats['by_type']) > 1:
                type_breakdown = []
                for query_type, stats in query_stats['by_type'].items():
                    type_breakdown.append(f"{query_type}: {stats['count']}")
                summary_parts.append(f"({', '.join(type_breakdown)})")
            
            return " | ".join(summary_parts)
            
        except Exception as e:
            logger.debug(f"Performance summary error: {e}")
            return "📊 Performance data unavailable"
    
    def get_comprehensive_stats(self, **kwargs) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        stats = {}
        
        # Core performance stats
        stats['query_performance'] = self.get_query_stats()
        stats['system_uptime'] = self.get_system_uptime()
        
        # Vectorstore stats
        vectorstore = kwargs.get('vectorstore')
        if vectorstore:
            vectorstore_stats = self.get_vectorstore_stats(vectorstore)
            stats.update(vectorstore_stats)
        
        # Domain manager stats
        domain_manager = kwargs.get('domain_manager')
        if domain_manager:
            try:
                stats['domain_config'] = domain_manager.get_status()
            except Exception as e:
                logger.debug(f"Domain manager stats error: {e}")
                stats['domain_config'] = {'error': str(e)}
        
        # Add resilience stats if available
        try:
            from core.resilience_manager import resilience_manager
            resilience_stats = resilience_manager.get_health_summary()
            stats.update(resilience_stats)
        except Exception as e:
            logger.debug(f"Resilience stats error: {e}")
            stats['resilience_health'] = {'error': str(e)}
        
        return stats 