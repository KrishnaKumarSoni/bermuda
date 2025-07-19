# Bermuda Form Creation Test Cases

Based on: `product-overview.yaml`, `form-creator-xp.yaml`, `ui-components.yaml`, `llm-prompts-and-chains.yaml`, `api-endpoints.yaml`

## Backend API Test Cases

### 1. Health Check
**Test**: Server health and configuration  
**Command**: `curl -X GET http://localhost:5000/health`  
**Expected**: `{"status": "healthy", "firebase": "connected", "openai": "configured"}`

### 2. Text Dump Inference - Simple
**Test**: Basic LLM inference with short text dump  
**Command**: `curl -X POST http://localhost:5000/api/infer -H "Content-Type: application/json" -d '{"dump": "Customer feedback survey about pizza preferences and delivery speed"}'`  
**Expected**: JSON with title, questions array with text/multiple_choice/rating types

### 3. Text Dump Inference - Complex
**Test**: Complex text dump with multiple question types  
**Command**: `curl -X POST http://localhost:5000/api/infer -H "Content-Type: application/json" -d '{"dump": "Employee satisfaction survey. Ask about work-life balance (1-5 scale), salary satisfaction (yes/no), years of experience (number), department (text), and would they recommend company to friends (yes/no)"}'`  
**Expected**: JSON with 5 questions, correct types (rating, yes_no, number, text, yes_no)

### 4. Text Dump Validation - Too Short
**Test**: Minimum 20 characters validation  
**Command**: `curl -X POST http://localhost:5000/api/infer -H "Content-Type: application/json" -d '{"dump": "short text"}'`  
**Expected**: `400 {"error": "Invalid dump - too short"}`

### 5. Text Dump Validation - Too Long
**Test**: Maximum 5000 characters validation  
**Command**: `curl -X POST http://localhost:5000/api/infer -H "Content-Type: application/json" -d '{"dump": "'$(printf 'a%.0s' {1..5001})'"}'`  
**Expected**: `400 {"error": "Invalid dump - too long"}`

### 6. Save Form - Valid Data
**Test**: Save form with proper structure  
**Command**: `curl -X POST http://localhost:5000/api/save-form -H "Content-Type: application/json" -d '{"title": "Test Survey", "questions": [{"text": "Favorite color?", "type": "multiple_choice", "options": ["Red", "Blue", "Green"], "enabled": true}], "demographics": []}'`  
**Expected**: `200 {"form_id": "uuid", "message": "Form saved"}`

### 7. Save Form - No Enabled Questions
**Test**: Validation for at least one enabled question  
**Command**: `curl -X POST http://localhost:5000/api/save-form -H "Content-Type: application/json" -d '{"title": "Test Survey", "questions": [{"text": "Question?", "type": "text", "enabled": false}], "demographics": []}'`  
**Expected**: `400 {"error": "No enabled questions"}`

### 8. Save Form - Missing Title
**Test**: Title validation  
**Command**: `curl -X POST http://localhost:5000/api/save-form -H "Content-Type: application/json" -d '{"title": "", "questions": [{"text": "Question?", "type": "text", "enabled": true}], "demographics": []}'`  
**Expected**: `400 {"error": "No enabled questions"}` (fails validation)

### 9. Get Forms List
**Test**: Retrieve user's forms  
**Command**: `curl -X GET http://localhost:5000/api/forms`  
**Expected**: `200 [{"id": "uuid", "title": "form title", "created_at": "timestamp", "response_count": 0}]`

### 10. Get Form Metadata - Valid ID
**Test**: Anonymous form metadata retrieval  
**Command**: `curl -X GET http://localhost:5000/api/forms/{FORM_ID}` (use saved form ID)  
**Expected**: `200 {"title": "form title", "questions": [...], "demographics": [...]}`

### 11. Get Form Metadata - Invalid ID
**Test**: Non-existent form ID  
**Command**: `curl -X GET http://localhost:5000/api/forms/invalid-id`  
**Expected**: `404 {"error": "Form not found"}`

## Frontend UI Test Cases

### 12. Frontend Accessibility
**Test**: Frontend server is running and serving HTML  
**Command**: `curl -I http://localhost:8000`  
**Expected**: `200 OK`, `Content-type: text/html`

### 13. Frontend Main Page Structure
**Test**: HTML contains required elements  
**Command**: `curl -s http://localhost:8000 | grep -E "(Sign in with Google|Create New Form|Paste your form context)"` 
**Expected**: All three strings found

### 14. Frontend CSS Loading
**Test**: Tailwind CSS classes and custom styles present  
**Command**: `curl -s http://localhost:8000 | grep -E "(tailwind|btn-primary|burnt orange|#CC5500)"`  
**Expected**: Style definitions found

### 15. Frontend JavaScript Integration
**Test**: Firebase and core JavaScript functions present  
**Command**: `curl -s http://localhost:8000 | grep -E "(firebase|showDashboard|inference_chain|ChatOpenAI)"`  
**Expected**: JavaScript functions and Firebase integration found

## Integration Test Cases

### 16. End-to-End Form Creation Flow
**Test**: Complete flow from text dump to saved form  
**Commands**:
1. `curl -X POST http://localhost:5000/api/infer -H "Content-Type: application/json" -d '{"dump": "Customer feedback: favorite food, rating 1-5, would recommend yes/no"}'`
2. Extract response and save form with returned data
3. Verify form saved correctly

### 17. Question Type Inference Accuracy
**Test**: LLM correctly identifies all 5 question types  
**Command**: `curl -X POST http://localhost:5000/api/infer -H "Content-Type: application/json" -d '{"dump": "Survey: name (text), age (number), favorite color (red/blue/green), satisfaction 1-5 scale, recommend yes/no"}'`  
**Expected**: 5 questions with types: text, number, multiple_choice, rating, yes_no

### 18. Firebase Data Persistence
**Test**: Saved forms persist in Firestore  
**Commands**:
1. Save a form via API
2. Retrieve forms list
3. Verify saved form appears in list

### 19. Error Handling and Recovery
**Test**: Graceful error handling for invalid requests  
**Commands**:
1. `curl -X POST http://localhost:5000/api/infer -H "Content-Type: application/json" -d '{"invalid": "json"}'`
2. `curl -X POST http://localhost:5000/api/save-form -H "Content-Type: application/json" -d '{}'`
3. Verify proper error responses

### 20. Performance and Response Time
**Test**: API response times under 10 seconds (as per YAML spec)  
**Command**: `time curl -X POST http://localhost:5000/api/infer -H "Content-Type: application/json" -d '{"dump": "Complex survey with multiple questions about customer satisfaction, product feedback, demographics, and recommendations"}'`  
**Expected**: Response within 10 seconds, valid JSON output

## Success Criteria

- All backend endpoints return correct HTTP status codes
- LLM inference generates proper JSON with all 5 question types
- Form validation catches all edge cases
- Frontend serves properly formatted HTML/CSS/JS
- Firebase integration works for data persistence
- Error handling is graceful and informative
- Performance meets specified requirements (inference < 10s)