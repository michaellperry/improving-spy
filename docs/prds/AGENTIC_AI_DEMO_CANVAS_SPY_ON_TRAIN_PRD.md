# Product Requirements Document (PRD): Agentic AI Demo Canvas - Spy on a Train

## Overview
The Agentic AI Demo Canvas: Spy on a Train is an interactive demonstration system designed to showcase the core capabilities of agentic AI systems. Through a narrative-driven experience of a spy traveling across Europe by train, the demo illustrates three fundamental AI agent concepts: **tool calling**, **state management**, and **problem decomposition**.

## Goals
- **Primary Objective**: Demonstrate the effectiveness of agentic AI systems in managing complex, multi-step tasks
- **Secondary Objective**: Illustrate the importance of proper tool design and problem decomposition in AI agent reliability
- **Educational Objective**: Provide a concrete, engaging example for understanding AI agent architecture and best practices

## User Roles
- **AI Researchers**: Understanding agentic AI system design and implementation
- **Software Engineers**: Learning tool integration and state management patterns
- **Product Managers**: Seeing the value of proper problem decomposition in AI systems
- **Students**: Learning AI agent concepts through interactive demonstration

## Information Architecture

### Core State Model
The demo extends the existing spy data structure with travel-specific state information:

```json
{
  "spy": {
    "id": "uuid-string",
    "name": "Agent Name",
    "codename": "CODENAME",
    "biography": "Agent background",
    "specialty": "Agent specialty",
    "travel_state": {
      "city_id": "vienna",
      "time_utc": "2025-08-30T08:00:00Z",
      "inventory": {
        "tickets": [],
        "passports": ["Austrian", "French"],
        "items": ["camera", "notebook"]
      }
    }
  }
}
```

**State Properties**:
- **Core Spy Properties**: Inherited from existing `Spy` model (id, name, codename, biography, specialty)
- **travel_state.city_id**: Current location identifier (string)
- **travel_state.time_utc**: Current timestamp in UTC (ISO 8601 format)
- **travel_state.inventory**: Collection of items including tickets, passports, and mission equipment (object)

### Data Store Expansion

The demo requires expanding the existing data store to include cities and train schedules while maintaining compatibility with the current spy system:

#### Cities Data Store
```json
{
  "cities": [
    {
      "id": "vienna",
      "name": "Vienna",
      "country": "Austria",
      "timezone": "+02:00",
      "coordinates": {"lat": 48.2082, "lng": 16.3738}
    },
    {
      "id": "munich",
      "name": "Munich", 
      "country": "Germany",
      "timezone": "+01:00",
      "coordinates": {"lat": 48.1351, "lng": 11.5820}
    },
    {
      "id": "paris",
      "name": "Paris",
      "country": "France", 
      "timezone": "+01:00",
      "coordinates": {"lat": 48.8566, "lng": 2.3522}
    },
    {
      "id": "zurich",
      "name": "Zurich",
      "country": "Switzerland",
      "timezone": "+01:00", 
      "coordinates": {"lat": 47.3769, "lng": 8.5417}
    }
  ]
}
```

#### Train Schedules Data Store
```json
{
  "train_schedules": [
    {
      "service_id": "S1",
      "origin": "vienna",
      "destination": "munich",
      "departure_local": "09:00",
      "arrival_local": "13:20",
      "duration_minutes": 260,
      "frequency": "daily",
      "operator": "ÖBB"
    },
    {
      "service_id": "S2", 
      "origin": "vienna",
      "destination": "zurich",
      "departure_local": "09:15",
      "arrival_local": "15:15",
      "duration_minutes": 360,
      "frequency": "daily",
      "operator": "ÖBB"
    },
    {
      "service_id": "S3",
      "origin": "munich",
      "destination": "paris", 
      "departure_local": "13:40",
      "arrival_local": "20:20",
      "duration_minutes": 400,
      "frequency": "daily",
      "operator": "DB"
    },
    {
      "service_id": "S4",
      "origin": "zurich",
      "destination": "paris",
      "departure_local": "15:10", 
      "arrival_local": "20:10",
      "duration_minutes": 300,
      "frequency": "daily",
      "operator": "SBB"
    }
  ]
}
```

### Tool Interface
**Purpose**: Provides the complete transportation network graph
**Input**: None
**Output**: 
```json
{
  "cities": [
    { "id": "vienna", "tz": "+2" },
    { "id": "munich", "tz": "+1" },
    { "id": "paris", "tz": "+1" },
    { "id": "zurich", "tz": "+1" }
  ],
  "edges": [
    { "from": "vienna", "to": "munich", "min_minutes": 260 },
    { "from": "munich", "to": "paris", "min_minutes": 400 },
    { "from": "vienna", "to": "zurich", "min_minutes": 360 },
    { "from": "zurich", "to": "paris", "min_minutes": 300 }
  ]
}
```

#### 2. get_schedule(origin_id, date_range, destination_id?)
**Purpose**: Retrieves available train services between cities
**Input**:
- **origin_id**: Starting city identifier (string)
- **date_range**: Time window for search (string)
- **destination_id**: Optional target city filter (string)
**Output**:
```json
{
  "services": [
    { "id": "S1", "origin": "vienna", "destination": "munich", "dep_local": "09:00", "arr_local": "13:20" },
    { "id": "S2", "origin": "vienna", "destination": "zurich", "dep_local": "09:15", "arr_local": "15:15" },
    { "id": "S3", "origin": "munich", "destination": "paris", "dep_local": "13:40", "arr_local": "20:20" },
    { "id": "S4", "origin": "zurich", "destination": "paris", "dep_local": "15:10", "arr_local": "20:10" }
  ]
}
```

#### 3. travel(service_id)
**Purpose**: Executes travel on a specific service, updating spy state
**Input**: **service_id**: Service identifier to travel on (string)
**Output**: 
- **Success**: Updated spy state with new location and time
- **Failure**: Error codes including `MISSED_DEPARTURE`, `MISSED_CONNECTION`

#### 4. plan_route(origin_id, dest_id, depart_after, prefs)
**Purpose**: Generates guaranteed valid travel itineraries (Future Implementation)
**Input**:
- **origin_id**: Starting city (string)
- **dest_id**: Destination city (string)
- **depart_after**: Earliest departure time (ISO 8601)
- **prefs**: Travel preferences including min_transfer time (object)

## User Experience

### Demo Flow Structure

#### Phase 1: Basic State Management and Direct Travel
**User Experience**: 
- System displays spy's initial state in Vienna at 08:00 UTC
- Agent demonstrates basic tool calling by retrieving available services
- Single-leg travel from Vienna to Munich shows state updates
- **Learning Outcome**: Understanding how AI agents maintain and update state

**Expected Behavior**:
- Agent calls `get_schedule("vienna")` to see available options
- Agent selects service S1 (Vienna→Munich) and calls `travel("S1")`
- Spy state updates: city_id becomes "munich", time_utc advances by 260 minutes

#### Phase 2: Multi-Leg Journey Challenges
**User Experience**:
- Agent attempts complex route Vienna→Zurich→Paris without planning tools
- System demonstrates connection failures and scheduling conflicts
- **Learning Outcome**: Understanding the limitations of ad-hoc problem solving

**Expected Behavior**:
- Agent tries Vienna→Zurich→Paris route
- Connection failure due to arrival time exceeding departure time
- Agent retries Vienna→Munich→Paris with potential missed connection scenarios
- Multiple tool calls and error handling demonstrate inefficiency

#### Phase 3: Problem Decomposition Concepts
**User Experience**:
- System explains how complex goals break down into sub-tasks
- **Learning Outcome**: Understanding the importance of structured problem solving

**Expected Behavior**:
- Demo explains goal decomposition: "reach Paris by midnight"
- Sub-goals identified: find valid path, book individual legs, update state
- Limitations of ad-hoc graph search without planning tools highlighted

#### Phase 4: Planning Tool Introduction
**User Experience**:
- Agent uses `plan_route` tool for efficient itinerary generation
- **Learning Outcome**: Seeing the power of proper decomposition tools

**Expected Behavior**:
- Agent calls `plan_route("vienna", "paris", depart_after="2025-08-30T08:00Z", prefs={"min_transfer": 10})`
- Tool returns optimized itinerary: Vienna→Munich (S1), Munich→Paris (S3)
- Agent executes plan with minimal tool calls and no failures

#### Phase 5: Comparative Analysis and Reflection
**User Experience**:
- System compares performance metrics between approaches
- **Learning Outcome**: Quantifying the value of proper tool design

**Expected Behavior**:
- Metrics comparison: tool calls, time taken, error rates
- Clear demonstration of improved reliability and efficiency
- Key insight: right decomposition tools make agentic systems more effective

## Integration Requirements

### Existing System Compatibility
- **Spy Model Extension**: The demo extends the existing `Spy` model without breaking current functionality
- **Database Schema**: New tables for cities and train schedules will be added alongside existing spy tables
- **API Compatibility**: All existing spy endpoints remain unchanged; new travel-related endpoints are additive
- **Repository Pattern**: New repositories for cities and train schedules follow the established repository pattern

### State Management Integration
- **Travel State**: Travel-specific state is encapsulated within the existing spy structure
- **Session Persistence**: Travel state persists across chat sessions and can be saved/restored
- **Multi-Agent Support**: Multiple spies can have independent travel states
- **State Validation**: Travel state changes are validated against the existing spy profile

### Tool Integration
- **Existing Tools**: Current mission tools continue to work alongside new travel tools
- **Tool Registry**: New travel tools are registered in the existing tool system
- **Error Handling**: Consistent error handling patterns across all tools
- **Logging**: Travel tool usage follows established logging patterns

## Non-Functional Requirements

### Performance Requirements
- **Response Time**: Tool calls must respond within 2 seconds
- **State Updates**: State transitions must be atomic and immediate
- **Error Handling**: Failed operations must provide clear, actionable error messages

### Reliability Requirements
- **State Consistency**: Spy state must remain consistent across all operations
- **Tool Availability**: All tools must be available 99.9% of the time
- **Data Integrity**: Schedule and map data must be accurate and up-to-date

### Usability Requirements
- **Demo Duration**: Complete demonstration should take 10-15 minutes
- **Learning Curve**: New users should understand the demo within 5 minutes
- **Visual Feedback**: State changes and tool calls must be clearly visible

### Technical Requirements
- **API Compatibility**: Must integrate with existing AI agent frameworks and FastAPI structure
- **State Persistence**: Travel state must persist across chat sessions and be stored in database
- **Database Integration**: New data stores must follow existing SQLAlchemy patterns
- **Extensibility**: Tool interface must support future additions like `plan_route`
- **Backward Compatibility**: All existing spy functionality must remain unchanged

## Success Criteria

### Functional Requirements
- [ ] **State Management**: Spy location, time, and inventory update correctly after each action
- [ ] **Tool Integration**: All four tools respond with expected data formats
- [ ] **Error Handling**: System gracefully handles missed connections and invalid operations
- [ ] **Multi-Leg Travel**: Agent can successfully complete complex routes with proper planning

### Educational Requirements
- [ ] **Concept Clarity**: Users understand tool calling, state management, and problem decomposition
- [ ] **Comparative Learning**: Users can see the difference between ad-hoc and planned approaches
- [ ] **Practical Application**: Users can apply learned concepts to other AI agent scenarios

### Technical Requirements
- [ ] **Performance**: All operations complete within specified time limits
- [ ] **Reliability**: System maintains consistent state across all operations
- [ ] **Extensibility**: New tools can be added without breaking existing functionality

## Implementation Phases

### Phase 1: Core Infrastructure and Integration (Week 1-2)
- [ ] Extend existing Spy model with travel_state field
- [ ] Create database migration for new cities and train_schedules tables
- [ ] Implement travel state management system
- [ ] Create tool interface framework
- [ ] Build basic demo flow structure

### Phase 2: Tool Implementation and Data Integration (Week 3-4)
- [ ] Implement `get_map` tool using cities data store
- [ ] Implement `get_schedule` tool using train_schedules data store
- [ ] Implement `travel` tool with state validation
- [ ] Create error handling system consistent with existing patterns
- [ ] Integrate new tools with existing tool registry

### Phase 3: Demo Scenarios (Week 5-6)
- [ ] Build Phase 1 demo flow (basic travel)
- [ ] Build Phase 2 demo flow (multi-leg challenges)
- [ ] Build Phase 3 demo flow (problem decomposition)

### Phase 4: Advanced Features (Week 7-8)
- [ ] Implement `plan_route` tool
- [ ] Build Phase 4 demo flow (planning tool)
- [ ] Build Phase 5 demo flow (comparative analysis)

### Phase 5: Testing and Refinement (Week 9-10)
- [ ] Comprehensive testing of all demo scenarios
- [ ] Performance optimization
- [ ] User experience refinement

## Data Validation and Consistency

### State Validation Rules
- **Location Consistency**: Spy cannot be in multiple cities simultaneously
- **Time Continuity**: Travel time must advance logically (no time travel backwards)
- **Inventory Validation**: Tickets must correspond to valid train services
- **Geographic Constraints**: Travel must follow valid train routes

### Data Integrity Requirements
- **Referential Integrity**: All city_id references must exist in cities table
- **Schedule Consistency**: Train schedules must have valid origin/destination cities
- **Timezone Handling**: All time calculations must respect city timezone differences
- **State Atomicity**: Travel state updates must be atomic operations

## Risk Assessment

### Technical Risks
- **Tool Integration Complexity**: Risk of tools not working together seamlessly
- **State Management Bugs**: Risk of state becoming inconsistent during operations
- **Performance Issues**: Risk of demo becoming too slow for effective learning

### Mitigation Strategies
- **Comprehensive Testing**: Extensive testing of tool interactions and state transitions
- **State Validation**: Built-in state validation at each operation
- **Performance Monitoring**: Continuous monitoring and optimization of response times

## Future Enhancements

### Additional Tools
- **Weather Tool**: Consider weather conditions in travel planning
- **Cost Tool**: Include ticket pricing and budget management
- **Security Tool**: Add passport and visa requirements

### Enhanced Scenarios
- **Dynamic Events**: Add unexpected delays and route changes
- **Multiple Spies**: Demonstrate multi-agent coordination
- **Real-time Updates**: Live schedule updates and disruption handling

## Conclusion

The Agentic AI Demo Canvas: Spy on a Train provides a compelling, narrative-driven approach to demonstrating AI agent capabilities. By focusing on three core concepts—tool calling, state management, and problem decomposition—the demo offers both educational value and practical insights into building effective AI agent systems.

The implementation approach prioritizes seamless integration with the existing spy system, extending current functionality without disruption. By following established patterns for database design, tool implementation, and state management, the demo demonstrates how new AI agent capabilities can be added incrementally to existing systems.

The phased implementation ensures that core functionality is delivered early while maintaining backward compatibility. The comparative analysis between ad-hoc and planned approaches will clearly demonstrate the value of proper tool design and problem decomposition in AI agent systems, while showcasing the benefits of a well-architected, extensible platform.
