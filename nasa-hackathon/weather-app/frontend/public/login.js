document.addEventListener('DOMContentLoaded', () => { // This can stay as is
    const togglePassword = document.getElementById('toggle-password');
    const passwordInput = document.getElementById('password');
    const loginForm = document.querySelector('.login-form');
    const emailInput = document.getElementById('email');

    const signinContainer = document.getElementById('signin-container');
    const signupContainer = document.getElementById('signup-container');
    const toggleToSignup = document.getElementById('toggle-to-signup');
    const toggleToSignin = document.getElementById('toggle-to-signin');

    const signupForm = document.querySelector('.signup-form');

    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', () => {
            // Toggle the type attribute
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);

            // Toggle the icon
            if (type === 'password') {
                togglePassword.setAttribute('data-feather', 'eye');
            } else {
                togglePassword.setAttribute('data-feather', 'eye-off');
            }
            feather.replace(); // Redraw icons
        });
    }

    // Handle form submission for login
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault(); // Prevent default form submission

            const email = emailInput.value;
            const password = passwordInput.value;

            try {
                // The backend team should provide this URL
                const response = await fetch('http://127.0.0.1:8000/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password }),
                });

                if (response.ok) {
                    // Login successful, redirect to the main weather app
                    window.location.href = 'index.html';
                } else {
                    // Login failed, show an error message from the backend
                    const errorData = await response.json();
                    alert(errorData.detail || 'Invalid email or password.');
                }
            } catch (error) {
                console.error('Login error:', error);
                alert('Could not connect to the server. Please try again later.');
            }
        });
    }

    // Handle form submission for sign-up
    if (signupForm) {
        signupForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const name = document.getElementById('signup-name').value;
            const dob = document.getElementById('signup-dob').value;
            const email = document.getElementById('signup-email').value;
            const password = document.getElementById('signup-password').value;
            const confirmPassword = document.getElementById('confirm-password').value;

            if (password !== confirmPassword) {
                alert("Passwords do not match. Please try again.");
                return;
            }

            try {
                // The backend team should provide this URL for registration
                const response = await fetch('http://127.0.0.1:8000/api/signup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, dob, email, password }),
                });

                if (response.ok) {
                    alert("Account created successfully! Please sign in.");
                    // Switch back to the sign-in form
                    signupContainer.classList.add('hidden');
                    signinContainer.classList.remove('hidden');
                    toggleToSignup.classList.remove('hidden');
                    toggleToSignin.classList.add('hidden');
                } else {
                    const errorData = await response.json();
                    alert(errorData.detail || "Could not create account. The email might already be in use.");
                }
            } catch (error) {
                console.error('Signup error:', error);
                alert('Could not connect to the server. Please try again later.');
            }
        });
    }

    // --- Form Toggling ---
    if (toggleToSignup) {
        toggleToSignup.addEventListener('click', (e) => {
            e.preventDefault();
            signinContainer.classList.add('hidden');
            signupContainer.classList.remove('hidden');
            toggleToSignup.classList.add('hidden');
            toggleToSignin.classList.remove('hidden');
        });
    }
    if (toggleToSignin) {
        toggleToSignin.addEventListener('click', (e) => {
            e.preventDefault();
            signupContainer.classList.add('hidden');
            signinContainer.classList.remove('hidden');
            toggleToSignup.classList.remove('hidden');
            toggleToSignin.classList.add('hidden');
        });
    }

    // Also apply theme from localStorage if it exists
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.dataset.theme = 'dark';
    } else {
        document.body.dataset.theme = 'light';
    }
});