# 🚀 Bermuda React Frontend - Quick Start Guide

Get the React TypeScript frontend up and running in minutes!

## ⚡ **Quick Setup**

1. **Navigate to the React frontend directory:**
   ```bash
   cd /Users/spider/Desktop/bermuda/frontend-react
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   ```
   http://localhost:5173
   ```

That's it! The React app should now be running.

## 🔧 **Prerequisites**

Make sure you have the backend running:

1. **Start the backend** (in a separate terminal):
   ```bash
   cd /Users/spider/Desktop/bermuda
   python3 simple_backend.py
   ```

2. **Verify backend is running:**
   ```
   Backend should be available at: http://127.0.0.1:5000
   ```

## 📁 **What You Get**

- ✅ **Modern React 18** with TypeScript
- ✅ **Vite** for lightning-fast development
- ✅ **Tailwind CSS** for styling
- ✅ **Firebase Auth** integration
- ✅ **State management** with Zustand
- ✅ **React Router** for navigation
- ✅ **ESLint & Prettier** for code quality

## 🎯 **Key Features Ready to Use**

### **Landing Page** (`/`)
- Marketing page with feature highlights
- Call-to-action buttons
- Responsive design

### **Create Form** (`/create`)
- AI-powered form generation
- Manual form builder
- Question types: text, multiple choice, yes/no, rating, number
- Demographics selection

### **Dashboard** (`/dashboard`)
- Form management
- Response analytics
- Form sharing
- CRUD operations

### **Chat Interface** (`/form/:id`)
- Real-time conversational forms
- Natural chat experience
- Message persistence

## 🛠️ **Development Commands**

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check

# Linting
npm run lint
npm run lint:fix

# Preview production build
npm run preview
```

## 🔍 **Troubleshooting**

### **Port Already in Use**
If port 5173 is busy, Vite will automatically use the next available port.

### **API Connection Issues**
- Ensure backend is running on `http://127.0.0.1:5000`
- Check browser console for CORS errors
- Verify API endpoints in Network tab

### **Firebase Auth Issues**
- Firebase is configured in `src/services/firebase.ts`
- Auth should work out of the box for development

## 📦 **Project Structure**

```
frontend-react/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/         # Page components
│   ├── stores/        # Zustand state management
│   ├── services/      # API and Firebase services
│   ├── types/         # TypeScript definitions
│   └── App.tsx        # Main app component
├── package.json       # Dependencies and scripts
├── vite.config.ts     # Vite configuration
└── README.md          # Detailed documentation
```

## 🎨 **Customization**

### **Colors**
Edit `tailwind.config.js` to change the color scheme:
```js
colors: {
  primary: {
    500: '#CC5500', // Burnt orange
    // ... other shades
  }
}
```

### **Typography**
Fonts are configured in `tailwind.config.js`:
- Headings: Plus Jakarta Sans
- Body: Inter Tight

### **API Endpoint**
Update API URL in `src/services/api.ts`:
```ts
const API_BASE_URL = 'http://127.0.0.1:5000/api';
```

## 🚀 **Deployment**

### **Build for Production**
```bash
npm run build
```

### **Deploy to Firebase Hosting**
```bash
# Install Firebase CLI (if not already installed)
npm install -g firebase-tools

# Login to Firebase
firebase login

# Deploy
firebase deploy --only hosting
```

## 💡 **Next Steps**

1. **Customize the design** to match your brand
2. **Add new features** or modify existing ones
3. **Set up testing** with Jest/Vitest
4. **Configure CI/CD** for automated deployments
5. **Add analytics** for user behavior tracking

## 🆘 **Need Help?**

- Check the detailed [README.md](./README.md) for comprehensive documentation
- Review component files in `src/components/` for examples
- Look at the store files in `src/stores/` for state management patterns
- Check browser console for error messages and debugging info

---

**Happy coding! 🎉**