# Bermuda - Conversational Forms

A conversational alternative to Google Forms that leverages AI to auto-generate forms from text dumps and provides human-like chat experiences for respondents.

## Features

- **AI-Powered Form Creation**: Transform any text dump into structured forms using GPT-4o-mini
- **Human-like Chat Interface**: Respondents interact through natural conversation
- **Anonymous by Default**: No registration required for form respondents
- **Real-time Data Collection**: Structured data extraction from chat transcripts
- **Responsive Design**: Works on all devices with mobile-first design

## Tech Stack

- **Frontend**: Vanilla JavaScript, Tailwind CSS, Firebase Auth
- **Backend**: Python Flask, LangChain
- **Database**: Firebase Firestore & Realtime Database
- **AI**: OpenAI GPT-4o-mini via LangChain

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js (for serving frontend)
- Firebase project with Firestore and Authentication enabled
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bermuda-01
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Install backend dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Configure Firebase**
   - Place your Firebase Admin SDK JSON file as `firebase-adminsdk.json` in the root directory
   - Update Firebase configuration in `frontend/index.html`

5. **Start the backend server**
   ```bash
   cd backend
   python run.py
   ```

6. **Serve the frontend**
   ```bash
   cd frontend
   # Using Python's built-in server
   python -m http.server 8000
   # Or using Node.js
   npx serve .
   ```

7. **Open your browser**
   ```
   http://localhost:8000
   ```

## Project Structure

```
bermuda-01/
├── frontend/
│   └── index.html          # Complete frontend application
├── backend/
│   ├── app.py              # Flask application
│   ├── run.py              # Development server
│   └── requirements.txt    # Python dependencies
├── firebase-adminsdk.json  # Firebase service account key
├── .env                    # Environment variables
└── README.md
```

## API Endpoints

### Authentication Required
- `POST /api/infer` - Generate form from text dump
- `POST /api/save-form` - Save form to database
- `GET /api/forms` - Get user's forms
- `GET /api/forms/{id}/responses` - Get form responses

### Anonymous Access
- `GET /api/forms/{id}` - Get form metadata
- `POST /api/chat-message` - Process chat messages

## Usage

### Creating a Form

1. **Sign in** with Google account
2. **Paste your content** - meeting notes, requirements, survey questions
3. **AI generates form** - questions are automatically inferred with types
4. **Edit as needed** - adjust questions, types, and demographics
5. **Save and share** - get a unique link to share with respondents

### Form Types Supported

- **Text**: Open-ended responses
- **Multiple Choice**: Predefined options
- **Yes/No**: Binary choices
- **Number**: Numeric inputs
- **Rating**: 1-5 scale ratings

### Demographics (Optional)

- Age Range
- Gender
- Location
- Education Level
- Income Bracket
- Occupation
- Ethnicity

## Development

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend can be tested manually or with browser automation
```

### Environment Variables

```bash
OPENAI_API_KEY=your_openai_api_key
FLASK_ENV=development
FLASK_DEBUG=True
FIREBASE_SERVICE_ACCOUNT_PATH=firebase-adminsdk.json
FIREBASE_PROJECT_ID=your_firebase_project_id
```

### Firebase Configuration

Update the Firebase config in `frontend/index.html`:

```javascript
const firebaseConfig = {
    apiKey: "your_api_key",
    authDomain: "your_project.firebaseapp.com",
    projectId: "your_project_id",
    storageBucket: "your_project.appspot.com",
    messagingSenderId: "your_sender_id",
    appId: "your_app_id"
};
```

## Security Features

- Firebase Authentication for creators
- Anonymous access for respondents
- Device fingerprinting for abuse prevention
- Rate limiting on API endpoints
- Secure token verification

## Deployment

### Backend (Flask)

```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Using Docker
docker build -t bermuda-backend .
docker run -p 5000:5000 bermuda-backend
```

### Frontend

Deploy static files to any CDN or hosting service:
- Netlify
- Vercel
- Firebase Hosting
- AWS S3 + CloudFront

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the documentation in YAML files
- Create an issue in the repository
- Review the CLAUDE.md for development guidance