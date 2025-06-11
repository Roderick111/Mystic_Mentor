# Single Domain Mode - Temporary Changes

## Overview
Multiple knowledge domains have been temporarily disabled to simplify the backend workflow. Only one domain can be active at a time.

## 🔧 Changes Made

### 1. Core Domain Manager (`src/core/domain_manager.py`)
- **Changed**: `MAX_ACTIVE_DOMAINS = 2` → `MAX_ACTIVE_DOMAINS = 1`
- **Location**: Line ~29
- **Restoration**: Change back to `MAX_ACTIVE_DOMAINS = 2` (or higher)

### 2. Unit Tests (`tests/unit/test_domain_manager.py`)
- **Changed**: Multiple test assertions updated for single domain mode
- **Restoration**: Search for `TODO: TEMPORARY` comments and revert changes
- **Key tests affected**:
  - `test_enable_valid_domain`
  - `test_fifo_replacement` 
  - `test_get_status_content`
  - `test_chroma_filter_multiple_domains`
  - `test_is_domain_active`
  - `test_get_active_domains_sorted`
  - `test_concurrent_operations`
  - `test_custom_initialization_*`
  - `test_validate_domains_method`

## 🔄 How to Re-enable Multiple Domains

### Step 1: Update Domain Manager
```python
# In src/core/domain_manager.py, line ~29
MAX_ACTIVE_DOMAINS = 2  # Or whatever number you prefer
```

### Step 2: Restore Unit Tests
```bash
# Search for all temporary changes
grep -n "TODO: TEMPORARY" tests/unit/test_domain_manager.py

# Revert each test based on the original expected behavior
# Most tests need to go back to expecting 2 active domains
```

### Step 3: Test Everything
```bash
# Run unit tests to ensure everything works
python -m unittest tests.unit.test_domain_manager -v

# Test the web interface
curl http://localhost:8000/domains
```

## 📝 Current Behavior
- ✅ Only one domain can be active at any time
- ✅ FIFO replacement works (switching domains replaces the current one)
- ✅ Web interface correctly shows single domain limitation  
- ✅ All tests pass with single domain constraints
- ✅ Backend API endpoints work correctly

## 📋 Files Modified
1. `src/core/domain_manager.py` - Core logic change
2. `tests/unit/test_domain_manager.py` - Test updates for single domain mode

## 🏷️ Search Tags for Easy Restoration
- Search for: `TODO: TEMPORARY` 
- Search for: `MAX_ACTIVE_DOMAINS = 1`
- Search for: `single domain mode`

---
**Created**: $(date)  
**Reason**: Backend workflow simplification  
**Impact**: Multiple domains disabled, single domain enforced  
**Reversal**: Simple constant change + test restoration 