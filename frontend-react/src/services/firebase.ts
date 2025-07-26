import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getDatabase } from 'firebase/database';

const firebaseConfig = {
  apiKey: "AIzaSyAoWt0HAUvLzMD5OX43URZlbLFimA0wnmA",
  authDomain: "bermuda-01.firebaseapp.com",
  projectId: "bermuda-01",
  storageBucket: "bermuda-01.firebasestorage.app",
  messagingSenderId: "212698241186",
  appId: "1:212698241186:web:dfe2ec1c46dd5a4e9c1ffb",
  measurementId: "G-ZQGF5RB992",
  databaseURL: "https://bermuda-01-default-rtdb.firebaseio.com"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase services
export const auth = getAuth(app);
export const db = getFirestore(app);
export const rtdb = getDatabase(app);

export default app;