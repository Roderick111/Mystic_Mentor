#!/usr/bin/env python3
"""
Unit tests for DomainManager component.

Tests all domain management functionality including:
- Domain validation and initialization
- FIFO replacement logic
- ChromaDB filter generation
- Status reporting
- Edge cases and error handling
"""

import unittest
import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_dir))

from src.core.domain_manager import DomainManager


class TestDomainManager(unittest.TestCase):
    """Test suite for DomainManager class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.dm = DomainManager()
    
    def test_default_initialization(self):
        """Test default initialization with lunar domain."""
        self.assertEqual(self.dm.active_domains, ["lunar"])
        self.assertEqual(len(self.dm.active_domains), 1)
        self.assertTrue(self.dm.is_domain_active("lunar"))
    
    def test_custom_initialization_valid_domains(self):
        """Test initialization with custom valid domains."""
        custom_domains = {"astrology", "crystals"}
        dm = DomainManager(custom_domains)
        self.assertEqual(set(dm.active_domains), custom_domains)
        self.assertEqual(len(dm.active_domains), 2)
    
    def test_custom_initialization_invalid_domains(self):
        """Test initialization with invalid domains (should be filtered out)."""
        mixed_domains = {"lunar", "invalid_domain", "astrology"}
        dm = DomainManager(mixed_domains)
        expected = {"lunar", "astrology"}
        self.assertEqual(set(dm.active_domains), expected)
    
    def test_custom_initialization_too_many_domains(self):
        """Test initialization with more than max allowed domains."""
        too_many_domains = {"lunar", "astrology", "crystals", "numerology"}
        dm = DomainManager(too_many_domains)
        self.assertEqual(len(dm.active_domains), DomainManager.MAX_ACTIVE_DOMAINS)
        self.assertTrue(set(dm.active_domains).issubset(DomainManager.AVAILABLE_DOMAINS))
    
    def test_enable_valid_domain(self):
        """Test enabling a valid domain."""
        result = self.dm.enable_domain("astrology")
        self.assertTrue(result)
        self.assertIn("astrology", self.dm.active_domains)
        self.assertEqual(len(self.dm.active_domains), 2)
    
    def test_enable_invalid_domain(self):
        """Test enabling an invalid domain."""
        result = self.dm.enable_domain("invalid_domain")
        self.assertFalse(result)
        self.assertNotIn("invalid_domain", self.dm.active_domains)
        self.assertEqual(len(self.dm.active_domains), 1)  # Should remain unchanged
    
    def test_enable_already_active_domain(self):
        """Test enabling a domain that's already active."""
        result = self.dm.enable_domain("lunar")
        self.assertTrue(result)
        self.assertEqual(len(self.dm.active_domains), 1)  # Should not duplicate
    
    def test_fifo_replacement(self):
        """Test FIFO replacement when adding domains beyond capacity."""
        # Fill to capacity
        self.dm.enable_domain("astrology")
        self.assertEqual(len(self.dm.active_domains), 2)
        
        # Add third domain - should trigger FIFO
        self.dm.enable_domain("crystals")
        
        # Should still have max domains
        self.assertEqual(len(self.dm.active_domains), DomainManager.MAX_ACTIVE_DOMAINS)
        
        # Should contain the new domain
        self.assertIn("crystals", self.dm.active_domains)
        
        # Should have removed the oldest domain (lunar was first)
        self.assertNotIn("lunar", self.dm.active_domains)
        
        # Should contain astrology and crystals
        self.assertEqual(set(self.dm.active_domains), {"astrology", "crystals"})
    
    def test_disable_active_domain(self):
        """Test disabling an active domain."""
        self.dm.enable_domain("astrology")
        result = self.dm.disable_domain("astrology")
        self.assertTrue(result)
        self.assertNotIn("astrology", self.dm.active_domains)
    
    def test_disable_inactive_domain(self):
        """Test disabling a domain that's not active."""
        result = self.dm.disable_domain("astrology")
        self.assertFalse(result)
        # Active domains should remain unchanged
        self.assertEqual(self.dm.active_domains, ["lunar"])
    
    def test_get_status_structure(self):
        """Test that get_status returns correct structure."""
        status = self.dm.get_status()
        required_keys = {"active_domains", "available_domains", "max_active_domains", "inactive_domains"}
        self.assertTrue(all(key in status for key in required_keys))
    
    def test_get_status_content(self):
        """Test that get_status returns correct content."""
        self.dm.enable_domain("astrology")
        status = self.dm.get_status()
        
        self.assertEqual(set(status["active_domains"]), {"astrology", "lunar"})
        self.assertEqual(set(status["available_domains"]), DomainManager.AVAILABLE_DOMAINS)
        self.assertEqual(status["max_active_domains"], DomainManager.MAX_ACTIVE_DOMAINS)
        
        expected_inactive = DomainManager.AVAILABLE_DOMAINS - {"astrology", "lunar"}
        self.assertEqual(set(status["inactive_domains"]), expected_inactive)
    
    def test_chroma_filter_single_domain(self):
        """Test ChromaDB filter generation for single domain."""
        filter_dict = self.dm.get_chroma_filter()
        expected = {"domain": {"$in": ["lunar"]}}
        self.assertEqual(filter_dict, expected)
    
    def test_chroma_filter_multiple_domains(self):
        """Test ChromaDB filter generation for multiple domains."""
        self.dm.enable_domain("astrology")
        filter_dict = self.dm.get_chroma_filter()
        
        self.assertIn("domain", filter_dict)
        self.assertIn("$in", filter_dict["domain"])
        
        # Check that both domains are included
        domains_in_filter = set(filter_dict["domain"]["$in"])
        self.assertEqual(domains_in_filter, {"lunar", "astrology"})
    
    def test_chroma_filter_empty_domains(self):
        """Test ChromaDB filter generation when no domains are active."""
        self.dm.active_domains.clear()
        filter_dict = self.dm.get_chroma_filter()
        self.assertEqual(filter_dict, {})
    
    def test_is_domain_active(self):
        """Test domain activity checking."""
        self.assertTrue(self.dm.is_domain_active("lunar"))
        self.assertFalse(self.dm.is_domain_active("astrology"))
        
        self.dm.enable_domain("astrology")
        self.assertTrue(self.dm.is_domain_active("astrology"))
    
    def test_get_active_domains_sorted(self):
        """Test that active domains are returned in sorted order."""
        self.dm.enable_domain("astrology")
        active = self.dm.get_active_domains()
        self.assertEqual(active, ["astrology", "lunar"])  # Should be sorted
    
    def test_get_inactive_domains_sorted(self):
        """Test that inactive domains are returned in sorted order."""
        inactive = self.dm.get_inactive_domains()
        expected = sorted(DomainManager.AVAILABLE_DOMAINS - {"lunar"})
        self.assertEqual(inactive, expected)
    
    def test_reset_to_default(self):
        """Test resetting to default configuration."""
        self.dm.enable_domain("astrology")
        self.dm.enable_domain("crystals")
        
        self.dm.reset_to_default()
        self.assertEqual(self.dm.active_domains, ["lunar"])
    
    def test_string_representation(self):
        """Test string representation methods."""
        str_repr = str(self.dm)
        self.assertIn("DomainManager", str_repr)
        self.assertIn("lunar", str_repr)
        
        repr_str = repr(self.dm)
        self.assertIn("DomainManager", repr_str)
        self.assertIn("active_domains", repr_str)
    
    def test_domain_constants(self):
        """Test that domain constants are properly defined."""
        self.assertIsInstance(DomainManager.AVAILABLE_DOMAINS, set)
        self.assertGreater(len(DomainManager.AVAILABLE_DOMAINS), 0)
        self.assertIsInstance(DomainManager.MAX_ACTIVE_DOMAINS, int)
        self.assertGreater(DomainManager.MAX_ACTIVE_DOMAINS, 0)
        
        # Test that expected domains are available
        expected_domains = {"lunar", "numerology", "ifs", "astrology", "crystals", "tarot"}
        self.assertEqual(DomainManager.AVAILABLE_DOMAINS, expected_domains)
    
    def test_validate_domains_method(self):
        """Test the _validate_domains private method."""
        # Test with valid domains
        valid_domains = {"lunar", "astrology"}
        result = self.dm._validate_domains(valid_domains)
        self.assertEqual(result, valid_domains)
        
        # Test with mixed valid/invalid domains
        mixed_domains = {"lunar", "invalid", "astrology"}
        result = self.dm._validate_domains(mixed_domains)
        self.assertEqual(result, {"lunar", "astrology"})
        
        # Test with too many domains
        too_many = {"lunar", "astrology", "crystals", "numerology"}
        result = self.dm._validate_domains(too_many)
        self.assertEqual(len(result), DomainManager.MAX_ACTIVE_DOMAINS)
    
    def test_concurrent_operations(self):
        """Test multiple operations in sequence."""
        # Enable multiple domains
        self.dm.enable_domain("astrology")
        self.dm.enable_domain("crystals")  # Should trigger FIFO
        
        # Check state
        self.assertEqual(len(self.dm.active_domains), 2)
        self.assertNotIn("lunar", self.dm.active_domains)  # Should be removed
        self.assertEqual(set(self.dm.active_domains), {"astrology", "crystals"})
        
        # Disable one domain
        self.dm.disable_domain("astrology")
        self.assertEqual(len(self.dm.active_domains), 1)
        self.assertIn("crystals", self.dm.active_domains)
        
        # Re-enable lunar
        self.dm.enable_domain("lunar")
        self.assertEqual(len(self.dm.active_domains), 2)
        self.assertIn("lunar", self.dm.active_domains)
        self.assertIn("crystals", self.dm.active_domains)


if __name__ == "__main__":
    unittest.main() 