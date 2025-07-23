function signInWithGoogle() {
    const provider = new firebase.auth.GoogleAuthProvider();
    auth.signInWithPopup(provider).catch((error) => {
        showToast('Sign in failed: ' + error.message, 'error');
    });
}