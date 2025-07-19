# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bermuda is a conversational alternative to Google Forms that leverages AI to auto-generate forms from text dumps and provides human-like chat experiences for respondents. The project uses Flask for the backend, vanilla JavaScript with Shadcn/Tailwind for the frontend, and Firebase for data storage.

## Architecture

### Tech Stack
- **Backend**: Python Flask with CORS enabled
- **Frontend**: Vanilla JavaScript with Shadcn components and Tailwind CSS
- **Database**: Firebase (Firestore for persistent data, Realtime Database for chat sync)
- **AI/ML**: LangChain with GPT-4o-mini for all LLM operations
- **Authentication**: Firebase Auth with Google OAuth

### Key Components

#### Backend API Structure
- **Base URL**: `/api`
- **Authentication**: Firebase token verification for creator endpoints, anonymous for respondent endpoints
- **Rate Limiting**: 100 requests/min per IP

#### Core API Endpoints
- `POST /api/infer` - Infers form structure from text dump using LangChain
- `POST /api/save-form` - Saves form to Firebase with UUID generation
- `GET /api/forms` - Lists creator's forms
- `GET /api/forms/{form_id}/responses` - Fetches form responses
- `GET /api/forms/{form_id}` - Anonymous form metadata access
- `POST /api/chat-message` - Processes chat messages via ConversationChain
- `POST /api/extract` - Extracts structured data from chat transcripts

#### Data Models
- **Forms**: Stored in Firestore `/forms` collection with questions, demographics, and metadata
- **Responses**: Stored in `/forms/{form_id}/responses` subcollection with structured data and transcripts
- **Chats**: Real-time sync in Firebase Realtime Database `/chats/{session_id}`

#### LLM Implementation
- **Inference Chain**: LLMChain for form creation with CoT and few-shot examples
- **Conversation Chain**: ConversationChain with BufferMemory (last 10 messages) for natural chat experience
- **Extraction Chain**: LLMChain for transforming chat transcripts to structured JSON

### Frontend Structure
- **Design System**: Burnt orange (#CC5500) primary with flat design (no shadows)
- **Typography**: Plus Jakarta Sans for headings, Inter Tight for body text
- **Form Builder**: Editable UI with toggles, type dropdowns, and demographics presets
- **Chat Interface**: Full-screen chat with bot/user message bubbles and real-time sync

## Development Commands

Since this is a specification-only repository with YAML files, there are no build commands. The project is designed to be implemented from these specifications.

## Key Features

### Form Creation Flow
1. Text dump inference using GPT-4o-mini with engineered prompts
2. Editable form builder with 5 question types: text, multiple_choice, yes_no, number, rating
3. Predefined demographics (age, gender, location, education, income, occupation, ethnicity)
4. Preview and share functionality with unique links

### Chat Experience
- Anonymous respondent access via shared links
- Natural conversation flow with human-like bot responses
- Silent security collection (device_id, location) for anti-abuse
- Type-specific data bucketizing and transformation
- Partial saves every 5 messages for data preservation

### Data Handling
- Extraction of structured responses from chat transcripts
- Bucketizing for multiple choice questions without bias
- Conflict resolution prioritizing latest responses
- CSV export functionality for responses

## Security Considerations

- Anonymous by default for respondents
- Device fingerprinting and location collection for security (internal use only)
- Firebase security rules restrict direct client writes to responses
- Rate limiting and anti-abuse measures
- No PII collection unless explicitly in demographics

## Implementation Notes

- All LLM operations use GPT-4o-mini for cost-effectiveness
- ConversationChain uses BufferMemory with 10-message limit
- Forms are immutable after first save (MVP limitation)
- Mobile-responsive design with desktop-optimized form creation
- Error handling with inline validation and user-friendly messages

## MVP Limitations

- No advanced analytics or multi-user collaboration
- No custom themes or email sharing
- No persistent chat resume capability
- No complex conditionals or form logic
- Maximum 50 questions per form, 20 options per multiple choice