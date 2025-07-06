# 🐛 Bug Report - AI Agent Education Platform

## Critical Issues

### 1. **JWT Authentication Issue** (HIGH PRIORITY)
**File:** `backend/utilities/auth.py`
**Line:** 45
**Issue:** JWT token payload expects `user_id` as string but attempts to parse as int
```python
user_id: int = payload.get("sub")  # This will fail if sub is a string
```
**Impact:** Authentication will fail, users cannot login
**Fix:** Convert to int safely or update token creation to store as int

### 2. **Database Connection Security** (HIGH PRIORITY)
**File:** `backend/database/connection.py`
**Line:** 17
**Issue:** Default secret key is hardcoded and insecure
```python
secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
```
**Impact:** Major security vulnerability
**Fix:** Generate a secure random secret key and require it in production

### 3. **Missing API Endpoints** (HIGH PRIORITY)
**File:** `frontend/src/services/api.ts`
**Issue:** Frontend API service calls endpoints that don't exist in backend:
- `/scenarios/{id}/agents` - Not implemented in backend
- `/process-pdf` - Not implemented in backend
- `/simulations/{id}` - Different endpoint name than backend
**Impact:** Frontend will crash when trying to use these features
**Fix:** Implement missing endpoints or update frontend to use correct endpoints

## Data Model Issues

### 4. **Schema Mismatch** (MEDIUM PRIORITY)
**Files:** `backend/database/models.py` vs `frontend/src/services/api.ts`
**Issue:** BusinessScenario interface doesn't match database schema
- Frontend expects `source_data` field, backend has `pdf_content`
- Frontend expects `source_type` as union type, backend uses string
**Impact:** Data serialization errors
**Fix:** Align schema definitions between frontend and backend

### 5. **Missing Foreign Key Constraints** (MEDIUM PRIORITY)
**File:** `backend/database/models.py`
**Issue:** Some relationships allow NULL created_by but don't handle orphaned records
**Impact:** Data integrity issues
**Fix:** Add proper cascading deletes or restrict NULL values

## Authentication & Security Issues

### 6. **Password Verification Import** (MEDIUM PRIORITY)
**File:** `backend/main.py`
**Line:** 384
**Issue:** `verify_password` is imported inside function, should be at module level
```python
from utilities.auth import verify_password  # Should be at top
```
**Impact:** Performance hit, potential import errors
**Fix:** Move import to top of file

### 7. **Hardcoded User ID** (MEDIUM PRIORITY)
**File:** `frontend/src/components/ScenarioBuilder.tsx`
**Line:** 64
**Issue:** Hardcoded user ID in custom scenario creation
```typescript
created_by: 1 // Placeholder user ID
```
**Impact:** All scenarios attributed to same user
**Fix:** Implement proper user authentication context

## Frontend Issues

### 8. **Missing Error Handling** (MEDIUM PRIORITY)
**File:** `frontend/src/components/ScenarioBuilder.tsx`
**Issue:** API calls don't properly handle all error cases
- Network errors
- Authentication failures
- Server errors
**Impact:** App crashes or hangs on errors
**Fix:** Add comprehensive error handling

### 9. **React Router Version Mismatch** (LOW PRIORITY)
**File:** `frontend/package.json`
**Issue:** Using React Router v7 with v5 types
```json
"react-router-dom": "^7.6.3",
"@types/react-router-dom": "^5.3.3"
```
**Impact:** TypeScript errors, potential runtime issues
**Fix:** Update types to match router version

### 10. **Missing CORS Configuration** (LOW PRIORITY)
**File:** `backend/main.py`
**Issue:** CORS allows all methods and headers, but only specific origins
**Impact:** Potential security risk
**Fix:** Restrict allowed methods and headers

## Database Issues

### 11. **Database URL Default** (MEDIUM PRIORITY)
**File:** `backend/database/connection.py`
**Line:** 12
**Issue:** Defaults to SQLite in production, should require PostgreSQL
**Impact:** Performance and scalability issues
**Fix:** Require proper database URL in production

### 12. **Missing Database Migrations** (LOW PRIORITY)
**Issue:** No Alembic migrations setup despite importing it
**Impact:** Database schema changes not versioned
**Fix:** Initialize Alembic and create initial migration

## API Design Issues

### 13. **Inconsistent Response Models** (LOW PRIORITY)
**File:** `backend/main.py`
**Issue:** Some endpoints return models, others return dictionaries
**Impact:** Inconsistent API responses
**Fix:** Standardize all responses to use Pydantic models

### 14. **Missing Input Validation** (MEDIUM PRIORITY)
**File:** `backend/main.py`
**Issue:** File upload endpoints don't validate file types or sizes
**Impact:** Security and storage issues
**Fix:** Add proper file validation

## Performance Issues

### 15. **Debug Print Statements** (LOW PRIORITY)
**File:** `backend/database/connection.py`
**Lines:** 26-30
**Issue:** Debug prints in production code
**Impact:** Performance and log noise
**Fix:** Remove or make conditional on environment

### 16. **Missing Database Indexes** (LOW PRIORITY)
**File:** `backend/database/models.py`
**Issue:** Missing indexes on frequently queried fields
**Impact:** Slow database queries
**Fix:** Add indexes for search and filter operations

## Recommendations

1. **Immediate:** Fix authentication issues (#1, #6)
2. **Priority:** Implement missing API endpoints (#3)
3. **Security:** Update default secret key (#2)
4. **Data:** Align schemas between frontend and backend (#4)
5. **Testing:** Add comprehensive error handling (#8)

## Testing Suggestions

1. Test authentication flow end-to-end
2. Test all API endpoints with invalid data
3. Test file upload functionality
4. Test database operations with various user roles
5. Test error scenarios and recovery

This report covers the major issues I found. Would you like me to help fix any of these specific bugs?