# Bermuda Frontend - React + TypeScript

Modern React TypeScript frontend for the Bermuda conversational forms application.

## 🚀 **Tech Stack**

- **React 18** - Component-based UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Zustand** - Lightweight state management
- **React Router** - Client-side routing
- **Firebase v9** - Authentication and real-time database
- **Lucide React** - Beautiful icons
- **ESLint & Prettier** - Code quality and formatting

## 📁 **Project Structure**

```
frontend-react/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── ui/             # Basic UI components (Button, Toast, Loading)
│   │   ├── auth/           # Authentication components
│   │   ├── forms/          # Form builder components
│   │   ├── chat/           # Chat interface components
│   │   ├── dashboard/      # Dashboard components
│   │   └── layout/         # Layout components (Navbar, Layout)
│   ├── pages/              # Page components
│   │   ├── LandingPage.tsx
│   │   ├── CreateFormPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── ChatPage.tsx
│   │   └── NotFoundPage.tsx
│   ├── stores/             # Zustand state stores
│   │   ├── authStore.ts    # Authentication state
│   │   ├── formStore.ts    # Form builder state
│   │   └── chatStore.ts    # Chat interface state
│   ├── services/           # API and external services
│   │   ├── firebase.ts     # Firebase configuration
│   │   └── api.ts          # API service layer
│   ├── types/              # TypeScript type definitions
│   │   └── index.ts
│   ├── hooks/              # Custom React hooks (future)
│   ├── utils/              # Utility functions (future)
│   ├── App.tsx             # Main App component
│   ├── main.tsx            # Application entry point
│   └── index.css           # Global styles and Tailwind imports
├── public/                 # Static assets
├── index.html              # HTML template
├── package.json            # Dependencies and scripts
├── vite.config.ts          # Vite configuration
├── tsconfig.json           # TypeScript configuration
├── tailwind.config.js      # Tailwind CSS configuration
├── postcss.config.js       # PostCSS configuration
├── .eslintrc.cjs          # ESLint configuration
└── .prettierrc            # Prettier configuration
```

## 🛠️ **Setup & Installation**

### Prerequisites
- Node.js 16+ 
- npm or pnpm
- Backend API running on http://127.0.0.1:5000

### Install Dependencies
```bash
cd frontend-react
npm install
```

### Environment Setup
Create a `.env` file in the project root:
```bash
# Firebase Configuration (already configured in firebase.ts)
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_firebase_auth_domain
VITE_FIREBASE_PROJECT_ID=bermuda-01

# API Configuration
VITE_API_BASE_URL=http://127.0.0.1:5000/api
```

### Start Development Server
```bash
npm run dev
```

The app will be available at `http://localhost:5173` (or the next available port).

## 📜 **Available Scripts**

```bash
# Development
npm run dev          # Start dev server with hot reload
npm run build        # Build for production
npm run preview      # Preview production build locally

# Code Quality
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint errors automatically

# Type Checking
npm run type-check   # Run TypeScript compiler check
```

## 🏗️ **Key Features**

### **Authentication System**
- Google OAuth integration via Firebase Auth
- Persistent auth state with Zustand
- Protected routes for authenticated users
- Clean sign in/out experience

### **Form Builder**
- AI-powered form generation from text dumps
- Drag & drop question reordering
- 5 question types: text, multiple choice, yes/no, rating, number
- Demographics selection
- Real-time form preview
- Form validation and error handling

### **Chat Interface** 
- Real-time chat with Firebase Realtime Database
- Natural conversation flow
- Message history persistence
- Typing indicators and loading states
- Mobile-responsive design

### **Dashboard**
- Form management (create, edit, delete)
- Response analytics and statistics
- Form sharing via unique links
- Export functionality (planned)

### **Design System**
- Burnt orange primary color (#CC5500)
- Flat design aesthetic (no shadows)
- Plus Jakarta Sans for headings
- Inter Tight for body text
- Fully responsive mobile-first design

## 🔌 **API Integration**

The frontend communicates with the Flask backend via REST API:

### **API Endpoints Used:**
- `POST /api/infer` - AI form generation
- `POST /api/save-form` - Save forms
- `GET /api/forms` - List user forms  
- `GET /api/forms/{id}` - Get specific form
- `GET /api/forms/{id}/responses` - Get form responses
- `POST /api/chat-message` - Send chat messages
- `POST /api/extract` - Extract structured data

### **API Service Layer:**
The `src/services/api.ts` file provides a clean abstraction over fetch calls with:
- Automatic authentication headers
- Error handling
- Type-safe responses
- Request/response logging in development

## 🗂️ **State Management**

### **Zustand Stores:**

#### **AuthStore** (`src/stores/authStore.ts`)
- User authentication state
- Google sign-in/sign-out actions
- Firebase auth state listener

#### **FormStore** (`src/stores/formStore.ts`)
- Form builder state and actions
- Form CRUD operations
- Question management (add, edit, delete, reorder)
- AI form generation

#### **ChatStore** (`src/stores/chatStore.ts`)
- Chat session management
- Real-time message sync
- Firebase Realtime Database integration

## 🎨 **Styling**

### **Tailwind CSS Configuration**
- Custom color palette with burnt orange primary
- Typography scale with custom fonts
- Component utilities for common patterns
- Responsive breakpoints

### **CSS Architecture**
- Utility-first approach with Tailwind
- Component-scoped styles when needed
- CSS custom properties for theming
- No external CSS frameworks

## 🔧 **Development Guidelines**

### **Component Structure**
```tsx
import React from 'react';
import { SomeIcon } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useStore } from '@/stores/someStore';

interface ComponentProps {
  title: string;
  onAction: () => void;
}

export const Component: React.FC<ComponentProps> = ({ title, onAction }) => {
  const { state, action } = useStore();

  return (
    <div className="p-4 bg-white rounded-lg">
      <h2 className="text-xl font-heading font-bold">{title}</h2>
      <Button onClick={onAction}>
        <SomeIcon className="w-4 h-4 mr-2" />
        Action
      </Button>
    </div>
  );
};
```

### **Best Practices**
- Use TypeScript strict mode
- Prefer functional components with hooks
- Keep components small and focused
- Use proper TypeScript interfaces
- Handle loading and error states
- Follow the established naming conventions
- Use semantic HTML elements

### **File Naming Conventions**
- Components: `PascalCase.tsx` (e.g., `FormBuilder.tsx`)
- Hooks: `camelCase.ts` (e.g., `useFormData.ts`)
- Utils: `camelCase.ts` (e.g., `formatDate.ts`)
- Types: `camelCase.ts` (e.g., `formTypes.ts`)

## 🚀 **Deployment**

### **Build for Production**
```bash
npm run build
```

This creates a `dist/` folder with optimized production files.

### **Firebase Hosting**
The app is configured for Firebase Hosting deployment:
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Deploy
firebase deploy --only hosting
```

## 🔍 **Troubleshooting**

### **Common Issues**

1. **API Connection Errors**
   - Ensure backend is running on http://127.0.0.1:5000
   - Check CORS configuration
   - Verify API endpoints in browser network tab

2. **Firebase Auth Issues**
   - Check Firebase project configuration
   - Verify API keys in environment variables
   - Ensure domain is whitelisted in Firebase console

3. **Build Errors**
   - Run `npm run type-check` for TypeScript errors
   - Check for missing dependencies
   - Clear node_modules and reinstall if needed

### **Development Tips**
- Use browser dev tools React extension
- Check console for detailed error messages
- Use the network tab to debug API calls
- Firebase emulator for local testing

## 📝 **Future Enhancements**

- [ ] Unit testing with Vitest/Jest
- [ ] E2E testing with Playwright
- [ ] PWA capabilities
- [ ] Offline support
- [ ] Advanced form analytics
- [ ] Team collaboration features
- [ ] Custom themes
- [ ] Multi-language support

## 🤝 **Contributing**

1. Follow the established code style
2. Write TypeScript interfaces for all data
3. Add proper error handling
4. Test your changes thoroughly
5. Update documentation as needed

---

Built with ❤️ using React, TypeScript, and modern web technologies.