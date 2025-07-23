// Firebase Configuration
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
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const db = firebase.firestore();
const rtdb = firebase.database();

// Global variables
let currentUser = null;