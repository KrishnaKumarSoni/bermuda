# Bermuda - Conversational Forms

A conversational alternative to Google Forms that leverages AI to auto-generate forms from text dumps and provides human-like chat experiences for respondents.

## Features

- **AI-Powered Form Creation**: Transform any text dump into structured forms using GPT-4o-mini
- **Human-like Chat Interface**: Respondents interact through natural conversation
- **Five Question Types**: text, multiple_choice, yes_no, number, rating
- **Real-time AI Inference**: Chain-of-thought prompting with few-shot examples
- **Firebase Integration**: Secure data storage and user authentication
- **Vercel Deployment**: Serverless deployment with global CDN

## Architecture

### Backend (Python Flask)
- **Form Inference API**: `/api/infer` - AI-powered form generation
- **Form Management**: Save, retrieve, and manage forms
- **OpenAI Integration**: GPT-4o-mini with optimized prompting
- **Firebase Integration**: Firestore for data persistence

### Frontend (React TypeScript)
- **Form Creator Interface**: Text-to-form conversion
- **Form Editor**: Drag-and-drop form customization
- **Respondent Chat**: Conversational form completion
- **Real-time Validation**: Instant feedback and error handling

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key
- Firebase project

### Local Development

1. **Clone and Setup**
```bash
git clone <repository>
cd bermuda
pip install -r requirements.txt
npm install
```

2. **Environment Variables**
```bash
# .env
OPENAI_API_KEY=your_openai_api_key
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_CLIENT_EMAIL=your_service_account_email
FIREBASE_PRIVATE_KEY=your_private_key
```

3. **Start Services**
```bash
# Backend
python backend/app_no_auth.py

# Frontend  
npm run dev
```

### API Testing

Test form inference:
```bash
curl -X POST http://localhost:5000/api/infer \
  -H "Content-Type: application/json" \
  -d '{"dump": "Customer survey about pizza preferences, delivery speed ratings, and recommendations"}'
```

## Deployment

### Vercel (Recommended)

1. **Install Vercel CLI**
```bash
npm i -g vercel
```

2. **Deploy**
```bash
vercel --prod
```

3. **Configure Environment Variables**
- Go to Vercel Dashboard → Project Settings → Environment Variables
- Add all required environment variables
- Set Function Max Duration to 60 seconds

## Technical Details

### AI Inference Pipeline
1. **Input Validation**: 20-5000 character text dumps
2. **Prompt Engineering**: Chain-of-thought with few-shot examples
3. **Response Processing**: JSON extraction and validation
4. **Question Enhancement**: Auto-complete options for choice questions

### Question Types
- **text**: Open-ended text input
- **multiple_choice**: Predefined options (2-7 choices)
- **yes_no**: Binary choice ["Yes", "No"]
- **number**: Numeric input validation
- **rating**: 1-5 scale ["1", "2", "3", "4", "5"]

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Current Status

✅ **System Deployed**: Full Flask API + React frontend deployed to Vercel  
✅ **GitHub Integration**: Automatic deployments configured  
✅ **Local Testing**: Form generation working perfectly (8 questions in 3 seconds)  
⏰ **Production Issue**: OpenAI API timeout in Vercel environment (investigating)

## Support

For issues and questions:
- Check the documentation in YAML files
- Create an issue in the repository
- Review the CLAUDE.md for development guidance