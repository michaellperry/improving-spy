# Agentic AI Demo Canvas - Phase 1 Implementation Plan

## Overview
Phase 1 focuses on establishing the core infrastructure and integration foundation for the Agentic AI Demo Canvas: Spy on a Train project. This phase extends the existing spy system with travel capabilities while maintaining full backward compatibility.

## Progress Summary
- ✅ **Phase 1: Core Infrastructure and Integration** - IN PROGRESS
- ❌ **Phase 2: Tool Implementation and Data Integration** - PENDING
- ❌ **Phase 3: Demo Scenarios** - PENDING
- ❌ **Phase 4: Advanced Features** - PENDING
- ❌ **Phase 5: Testing and Refinement** - PENDING

**Current Status**: Starting Phase 1 implementation - Core infrastructure development

## Prerequisites
- [x] Existing spy system running and functional
- [x] FastAPI backend with SQLAlchemy database
- [x] Pydantic AI integration with Ollama backend
- [x] Textual CLI frontend operational
- [x] UV package manager and Python 3.13+ environment

## Phase 1: Core Infrastructure and Integration 🔄

### 1.1 Extend Existing Spy Model with Travel State
**Location**: `src/backend/models/__init__.py`

**Required Steps**:
- [ ] Add `TravelState` Pydantic model with city_id, time_utc, and inventory fields
- [ ] Extend existing `Spy` model to include optional `travel_state` field
- [ ] Create `SpyUpdate` model for travel state modifications
- [ ] Add validation rules for travel state consistency

**Acceptance Criteria**:
- [ ] `TravelState` model validates city_id, time_utc (ISO 8601), and inventory structure
- [ ] Extended `Spy` model maintains backward compatibility with existing endpoints
- [ ] `SpyUpdate` model allows partial updates to travel state
- [ ] All existing spy functionality continues to work unchanged

**Testing Approach**:
- [ ] Unit tests for `TravelState` validation (city_id format, time_utc parsing, inventory structure)
- [ ] Integration tests ensuring existing spy endpoints remain functional
- [ ] Model serialization/deserialization tests with and without travel state
- [ ] Backward compatibility tests with existing spy data

### 1.2 Create Database Migration for New Tables
**Location**: `src/backend/core/database.py` and new migration files

**Required Steps**:
- [ ] Design cities table schema with id, name, country, timezone, coordinates
- [ ] Design train_schedules table with service_id, origin, destination, timing fields
- [ ] Create SQLAlchemy ORM models for Cities and TrainSchedules
- [ ] Implement database migration scripts
- [ ] Add sample data for Vienna, Munich, Paris, and Zurich

**Acceptance Criteria**:
- [ ] Cities table stores European city data with proper timezone and coordinate information
- [ ] Train_schedules table contains realistic train service data between major cities
- [ ] Database migration runs without errors on existing spy_chat.db
- [ ] Sample data populates tables with Vienna as starting point (08:00 UTC)

**Testing Approach**:
- [ ] Database migration tests on fresh and existing databases
- [ ] ORM model CRUD operations for cities and train schedules
- [ ] Data integrity tests ensuring referential consistency
- [ ] Sample data validation against PRD specifications

### 1.3 Implement Travel State Management System
**Location**: `src/backend/services/travel_service.py` (new file)

**Required Steps**:
- [ ] Create TravelService class for managing spy travel state
- [ ] Implement state validation methods (location consistency, time continuity)
- [ ] Add inventory management for tickets, passports, and items
- [ ] Create state persistence and retrieval methods
- [ ] Integrate with existing spy repository pattern

**Acceptance Criteria**:
- [ ] TravelService validates all state transitions before applying changes
- [ ] State updates are atomic and consistent across all operations
- [ ] Inventory management handles tickets, passports, and mission items
- [ ] State persistence integrates with existing spy database operations
- [ ] Error handling provides clear messages for invalid state changes

**Testing Approach**:
- [ ] Unit tests for all TravelService methods and validation logic
- [ ] Integration tests with spy repository and database operations
- [ ] State consistency tests across multiple operations
- [ ] Error handling tests for invalid state transitions
- [ ] Performance tests ensuring state updates complete within 2 seconds

### 1.4 Create Tool Interface Framework
**Location**: `src/backend/tools/travel_tools.py` (new file)

**Required Steps**:
- [ ] Define base tool interface structure following existing tool patterns
- [ ] Create tool registration system compatible with Pydantic AI
- [ ] Implement tool input/output validation using Pydantic models
- [ ] Add tool logging and error handling consistent with existing patterns
- [ ] Create tool response models for consistent API structure

**Acceptance Criteria**:
- [ ] Tool interface follows established patterns from existing mission tools
- [ ] Tool registration integrates seamlessly with Pydantic AI tool system
- [ ] All tools provide consistent error handling and response formats
- [ ] Tool usage is logged for debugging and monitoring purposes
- [ ] Tool responses include proper status codes and error messages

**Testing Approach**:
- [ ] Tool interface integration tests with Pydantic AI framework
- [ ] Tool registration and discovery tests
- [ ] Input/output validation tests for all tool parameters
- [ ] Error handling tests for malformed tool requests
- [ ] Logging verification tests for tool usage tracking

### 1.5 Build Basic Demo Flow Structure
**Location**: `src/backend/services/demo_service.py` (new file)

**Required Steps**:
- [ ] Create DemoService class for orchestrating demo scenarios
- [ ] Implement Phase 1 demo flow (basic travel demonstration)
- [ ] Add demo state tracking and progress management
- [ ] Create demo response models for frontend integration
- [ ] Integrate with existing chat system for demo interactions

**Acceptance Criteria**:
- [ ] DemoService can execute Phase 1 demo flow without errors
- [ ] Demo state tracks progress through basic travel scenario
- [ ] Demo responses provide clear feedback on agent actions
- [ ] Demo integrates with existing chat system seamlessly
- [ ] Demo can be started, paused, and reset as needed

**Testing Approach**:
- [ ] Unit tests for DemoService methods and demo flow logic
- [ ] Integration tests with chat system and travel tools
- [ ] Demo flow execution tests for Phase 1 scenario
- [ ] State management tests for demo progress tracking
- [ ] Frontend integration tests for demo response handling

## Success Criteria for Phase 1

### Functional Requirements
- [ ] **Spy Model Extension**: Travel state field added without breaking existing functionality
- [ ] **Database Schema**: Cities and train_schedules tables created with sample data
- [ ] **State Management**: Travel state updates work correctly and consistently
- [ ] **Tool Framework**: Tool interface system ready for Phase 2 implementation
- [ ] **Demo Structure**: Basic demo flow can execute Phase 1 scenario

### Technical Requirements
- [ ] **Backward Compatibility**: All existing spy functionality remains unchanged
- [ ] **Performance**: State updates complete within 2 seconds
- [ ] **Data Integrity**: Database maintains referential consistency
- [ ] **Error Handling**: Clear error messages for invalid operations
- [ ] **Integration**: New components integrate seamlessly with existing system

### Testing Requirements
- [ ] **Unit Test Coverage**: 90%+ coverage for new components
- [ ] **Integration Tests**: All new services integrate with existing system
- [ ] **Database Tests**: Migration and data integrity tests pass
- [ ] **Performance Tests**: State operations meet timing requirements
- [ ] **Compatibility Tests**: Existing functionality remains unchanged

## Dependencies and Blockers

### Internal Dependencies
- [ ] Existing spy system must be fully functional
- [ ] Database migration system must be in place
- [ ] Tool registration system must be accessible
- [ ] Chat system must support demo integration

### External Dependencies
- [ ] Pydantic AI framework compatibility
- [ ] SQLAlchemy database operations
- [ ] FastAPI endpoint integration
- [ ] Textual frontend integration

## Risk Mitigation

### Technical Risks
- **Database Migration Complexity**: Risk of breaking existing data
  - Mitigation: Comprehensive testing on copy of production database
- **State Management Bugs**: Risk of inconsistent spy state
  - Mitigation: Extensive validation and atomic operation patterns
- **Tool Integration Issues**: Risk of tools not working together
  - Mitigation: Following established patterns and comprehensive testing

### Timeline Risks
- **Scope Creep**: Risk of adding features beyond Phase 1
  - Mitigation: Strict adherence to Phase 1 requirements
- **Integration Complexity**: Risk of unexpected integration issues
  - Mitigation: Early integration testing and incremental development

## Next Steps After Phase 1

### Phase 2 Preparation
- [ ] Tool interface framework ready for travel tool implementation
- [ ] Database schema established for cities and train schedules
- [ ] State management system ready for complex travel scenarios
- [ ] Demo structure ready for Phase 2 scenario development

### Documentation Updates
- [ ] Update API documentation with new travel endpoints
- [ ] Create developer guide for travel state management
- [ ] Document tool interface patterns for future development
- [ ] Update database schema documentation

## Notes

- **Priority**: Focus on core infrastructure and backward compatibility
- **Testing**: Emphasize integration testing with existing system
- **Performance**: Monitor state update timing throughout development
- **Documentation**: Maintain clear documentation for Phase 2 developers
- **Code Quality**: Follow established patterns from existing codebase
