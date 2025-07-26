# 📁 Bermuda Project Structure

Clean, organized project structure with separate frontend implementations and Python backend.

## 🏗️ **Root Directory Overview**

```
bermuda/
├── 📄 Project Documentation
│   ├── CLAUDE.md                   # AI assistant instructions
│   ├── README.md                   # Main project documentation
│   ├── PROJECT_STRUCTURE.md        # This file
│   └── TEST_CASES.md               # Test cases and scenarios
│
├── 🐍 Python Backend
│   ├── api/                        # Main API implementation
│   │   ├── main.py                 # Firebase Functions entry point
│   │   ├── respondent.py           # Chat & form response API
│   │   ├── creator.py              # Form creation API
│   │   ├── firebase_integration.py # Firebase services
│   │   ├── langchain_manager.py    # LLM integrations
│   │   ├── agentic_conversation.py # AI conversation logic
│   │   ├── modern_chat_agents.py   # Advanced chat agents
│   │   ├── natural_conversation_manager.py # NLP processing
│   │   ├── requirements.txt        # Python dependencies
│   │   └── venv/                   # Python virtual environment
│   │
│   ├── simple_backend.py           # Simplified development server
│   ├── run_local_backend.py        # Local development runner
│   └── modularize.py               # Code organization utility
│
├── ⚛️ React Frontend (New)
│   └── frontend-react/             # Modern React + TypeScript implementation
│       ├── src/                    # Source code
│       │   ├── components/         # React components
│       │   ├── pages/             # Page components
│       │   ├── stores/            # State management (Zustand)
│       │   ├── services/          # API & Firebase services
│       │   └── types/             # TypeScript definitions
│       ├── package.json           # Node.js dependencies
│       ├── vite.config.ts         # Build configuration
│       ├── README.md              # React frontend docs
│       ├── QUICKSTART.md          # Quick setup guide
│       └── OVERVIEW.md            # Technical deep dive
│
├── 🌐 Vanilla JS Frontend (Legacy)
│   └── frontend/                   # Original vanilla JavaScript implementation
│       ├── js/                     # JavaScript modules
│       ├── css/                    # Stylesheets
│       ├── pages/                  # HTML pages
│       └── index.html              # Main entry point
│
├── 📚 Archive & Documentation
│   └── archive/                    # Historical files and documentation
│       ├── spec-files/             # YAML specifications
│       ├── test-files/             # Test scripts and reports
│       ├── debug-files/            # Debug utilities and screenshots
│       ├── legacy-html/            # Old HTML prototypes
│       └── build-files/            # Build artifacts
│
├── ⚙️ Configuration
│   ├── .env                        # Environment variables
│   ├── firebase.json               # Firebase hosting config
│   └── image.png                   # Project logo/image
```

## 🎯 **How to Use Each Part**

### **🐍 Python Backend**
```bash
# Start the simplified development server
python3 simple_backend.py

# Or use the full API implementation
cd api && python3 respondent.py
```

### **⚛️ React Frontend** (Recommended)
```bash
cd frontend-react
npm install
npm run dev
```

### **🌐 Vanilla JS Frontend** (Legacy)
```bash
# Serve the frontend directory with any static server
cd frontend
python3 -m http.server 8000
```

## 📋 **Key Files Explained**

### **Backend Files**
- `simple_backend.py` - **Simplified Flask server for development**
- `api/respondent.py` - **Main chat and response handling API**
- `api/creator.py` - **Form creation and management API**
- `api/firebase_integration.py` - **Firebase services wrapper**
- `api/langchain_manager.py` - **LLM and AI conversation logic**

### **Frontend Files**
- `frontend-react/` - **Modern React TypeScript implementation** ✨
- `frontend/` - **Original vanilla JavaScript implementation**

### **Configuration Files**
- `.env` - **Environment variables (API keys, configs)**
- `firebase.json` - **Firebase hosting and functions config**
- `CLAUDE.md` - **Instructions for AI assistant**

### **Documentation Files**
- `README.md` - **Main project overview**
- `frontend-react/README.md` - **React frontend documentation**
- `archive/spec-files/` - **Detailed YAML specifications**

## 🚀 **Recommended Development Workflow**

### **1. Backend Development**
```bash
# Start the backend server
python3 simple_backend.py
# Server runs on http://127.0.0.1:5000
```

### **2. Frontend Development** (Choose one)

#### **Option A: React Frontend** (Recommended)
```bash
cd frontend-react
npm install
npm run dev
# App runs on http://localhost:5173
```

#### **Option B: Vanilla JS Frontend** (Legacy)
```bash
cd frontend
# Serve with any static server
python3 -m http.server 8000
# App runs on http://localhost:8000
```

### **3. Full Stack Development**
```bash
# Terminal 1: Backend
python3 simple_backend.py

# Terminal 2: Frontend
cd frontend-react && npm run dev

# Access app at http://localhost:5173
```

## 🧹 **What Was Cleaned Up**

### **Removed from Root Directory:**
- ❌ `src/` - Duplicate React source code
- ❌ `node_modules/` - Node.js dependencies
- ❌ `package.json` / `package-lock.json` - Node.js configs
- ❌ `tsconfig*.json` - TypeScript configs
- ❌ `vite.config.ts` - Vite build config
- ❌ `tailwind.config.js` - Tailwind CSS config
- ❌ `postcss.config.js` - PostCSS config
- ❌ `.eslintrc.cjs` / `.prettierrc` - Code quality configs
- ❌ `index.html` - Duplicate HTML file
- ❌ `test_api.html` - Temporary test file

### **Kept in Root Directory:**
- ✅ All Python backend files
- ✅ Environment configuration (`.env`)
- ✅ Project documentation
- ✅ Firebase configuration
- ✅ Archive and historical files
- ✅ Organized frontend implementations

## 📈 **Project Benefits**

### **Clean Separation**
- **Backend** - Pure Python with Flask and Firebase
- **React Frontend** - Modern TypeScript with proper tooling
- **Legacy Frontend** - Original vanilla JS preserved
- **Documentation** - Comprehensive guides and specs

### **Development Experience**
- **No conflicts** between different tech stacks
- **Clear file organization** for easy navigation
- **Separate dependencies** for frontend and backend
- **Multiple frontend options** for different needs

### **Maintainability**
- **Focused directories** - each serves a specific purpose
- **Proper separation of concerns**
- **Easy to add new features** or remove unused code
- **Clear documentation** for onboarding

## 💡 **Next Steps**

1. **Use the React frontend** for new development
2. **Keep the Python backend** as the API layer
3. **Archive legacy code** when no longer needed
4. **Add testing** to both frontend and backend
5. **Set up CI/CD** for automated deployments

---

**Clean, organized, and ready for development! 🎉**