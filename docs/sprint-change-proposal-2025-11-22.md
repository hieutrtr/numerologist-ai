# Sprint Change Proposal - User Observations Consolidation Feature

**Date:** 2025-11-22
**Project:** Numerologist AI
**Change Type:** Feature Addition
**Scope:** Moderate

---

## Section 1: Issue Summary

### Problem Statement
During the implementation phase, a new requirement has emerged to enhance the AI agent's capability to observe and persist user behavioral patterns during conversations. The system needs to track user intents, wishes, struggles, issues, and goals to provide more personalized guidance and build deeper user relationships over time.

### Discovery Context
- **When Identified:** During Sprint execution, post Epic 4 completion
- **Requested By:** Product stakeholder (Hieu)
- **Current State:** System captures conversation history but doesn't extract or persist behavioral observations

### Evidence Supporting Change
- Enhances personalization capabilities significantly
- Enables data-driven insights about user concerns
- Supports long-term relationship building between AI and users
- Aligns with existing FR-3.4 (Context Retention) requirements
- Improves engagement metrics through better understanding of user needs

---

## Section 2: Impact Analysis

### Epic Impact

**Epic 5: Conversation History & Context Management**
- **Status:** Can accommodate this feature within current scope
- **Changes Required:** Add 4 new stories for observations functionality
- **Timeline Impact:** Adds ~2-3 days to epic completion
- **Dependencies:** Builds on existing conversation infrastructure

**Future Epics:**
- Epic 6 (Performance & Polish): May need optimization for observation processing
- Epic 7 (Deployment & Launch): No significant impact

### Artifact Conflicts

**PRD Document:**
- ✅ No conflicts - Feature enhances existing requirements
- Supports FR-3.4: "System shall remember previous conversations in AI context"
- Aligns with success criteria for engagement depth

**Architecture Document:**
- Database: New table required (user_observation)
- API: New endpoints needed (/api/v1/observations)
- Voice Pipeline: Minor modification to extract observations
- ✅ No architectural pattern violations

**UI/UX Specifications:**
- No immediate UI changes required for MVP
- Optional future UI for displaying user insights

### Technical Impact

**Database Changes:**
- New table: user_observation
- New relationships: User → Observations, Conversation → Observations
- New indexes for efficient querying
- Migration required

**Backend Services:**
- New service: ObservationService
- Modified: Voice pipeline (pipecat_bot.py)
- New API router: observations.py

**Performance Considerations:**
- Async observation extraction (non-blocking)
- Indexed queries for fast retrieval
- Redis caching potential for frequent access patterns

---

## Section 3: Recommended Approach

### Selected Path: Direct Adjustment

**Rationale:**
- Feature is purely additive, no breaking changes
- Aligns perfectly with project goals and vision
- Moderate complexity with low risk
- Enhances user value significantly
- Can be implemented within current sprint structure

**Effort Estimate:** MEDIUM (2-3 days)
**Risk Assessment:** LOW
**Timeline Impact:** Minimal, can be absorbed within Epic 5

### Implementation Strategy

1. **Database Setup (0.5 day)**
   - Create user_observation model
   - Run migration
   - Update relationships

2. **Backend Services (1.5 days)**
   - Implement ObservationService
   - Add extraction logic to voice pipeline
   - Create API endpoints
   - Write extraction prompts

3. **Testing & Integration (1 day)**
   - Unit tests for observation service
   - API endpoint tests
   - End-to-end conversation test with observations

---

## Section 4: Detailed Change Proposals

### Database Schema Addition

```python
# New model: backend/src/models/user_observation.py
class UserObservation(SQLModel, table=True):
    id: UUID (primary key)
    user_id: UUID (foreign key → user)
    conversation_id: UUID (foreign key → conversation)
    observation_type: str ("intent"|"wish"|"struggle"|"issue"|"goal")
    content: str (observation text)
    confidence: float (0.0-1.0)
    extracted_at: datetime
    metadata: JSON (optional)
```

### New API Endpoints

```
GET  /api/v1/observations
     Query params: ?type={type}&limit={limit}
     Returns: User's observations

GET  /api/v1/observations/summary
     Returns: Aggregated insights about user
```

### Service Architecture

```python
ObservationService:
  - extract_observations(conversation_id, user_id, messages)
  - get_user_observations(user_id, type, limit)
  - get_observation_summary(user_id)
  - _call_gpt_for_extraction(prompt)
  - _save_observations(observations, conversation_id, user_id)
```

### Voice Pipeline Integration

- Non-blocking async task during conversation
- Extracts observations after each meaningful exchange
- No impact on voice latency

### New Stories for Epic 5

1. **5-5: User observations database schema**
   - Create model, migration, relationships
   - Acceptance: Database ready for observations

2. **5-6: Observation extraction service**
   - Implement ObservationService with GPT integration
   - Acceptance: Service extracts observations from text

3. **5-7: Observations API endpoints**
   - Create endpoints for retrieval and summary
   - Acceptance: API returns user observations

4. **5-8: GPT observation extraction prompts**
   - Design prompts for accurate extraction
   - Acceptance: 80%+ accuracy in observation categorization

---

## Section 5: Implementation Handoff

### Change Scope Classification: MODERATE

Requires backlog reorganization and technical implementation but doesn't fundamentally alter project direction.

### Handoff Recipients & Responsibilities

**Development Team (Primary)**
- Implement database schema and migration
- Create ObservationService
- Add API endpoints
- Integrate with voice pipeline
- Write tests

**Scrum Master**
- Add new stories to Epic 5
- Update sprint backlog
- Track implementation progress

**Product Owner**
- Validate observation categories meet business needs
- Review extraction accuracy
- Approve API response formats

### Success Criteria

1. ✅ Observations extracted during conversations
2. ✅ Data persisted to database
3. ✅ API endpoints return user observations
4. ✅ No impact on voice latency (<3s maintained)
5. ✅ 80%+ accuracy in observation categorization
6. ✅ All tests passing

### Implementation Timeline

- **Day 1:** Database schema, migration, models
- **Day 2:** ObservationService and GPT integration
- **Day 3:** API endpoints, voice pipeline integration, testing

---

## Approval & Next Steps

### Approval Status
**Awaiting approval to proceed with implementation**

### Immediate Actions Upon Approval

1. Create database migration file
2. Implement UserObservation model
3. Start ObservationService development
4. Update Epic 5 in sprint backlog

### Risk Mitigation

- **Risk:** GPT extraction accuracy
  - **Mitigation:** Iterative prompt refinement, confidence scoring

- **Risk:** Performance impact
  - **Mitigation:** Async processing, database indexing

- **Risk:** Data privacy concerns
  - **Mitigation:** User consent, data anonymization options

---

## Summary

This change adds significant value by enabling the AI to build deeper understanding of users over time through observation consolidation. The feature is architecturally sound, aligns with project goals, and can be implemented within the current sprint structure with moderate effort and low risk.

**Recommendation:** Proceed with implementation via Direct Adjustment approach.

---

_Generated by Correct Course Workflow_
_Date: 2025-11-22_
_For: Hieu_