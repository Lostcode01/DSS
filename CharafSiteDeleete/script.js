import { createClient }
from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm'

const supabase = createClient(
    'https://sximqxiirjfchbpzhrof.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN4aW1xeGlpcmpmY2hicHpocm9mIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA0MDcyODQsImV4cCI6MjA5NTk4MzI4NH0.t5pHCLrfCmwgtJWAh3AdOcpr_l0BjehJxyN0tpjnD7Y'
)

// -------------------- AUTH --------------------

window.register = async function () {

    const email = document.getElementById("email").value
    const password = document.getElementById("password").value

    const { error } = await supabase.auth.signUp({
        email,
        password
    })

    document.getElementById("message").textContent =
        error ? error.message : translations[currentLang].registered
}

window.login = async function () {

    const email = document.getElementById("email").value
    const password = document.getElementById("password").value

    const { error } = await supabase.auth.signInWithPassword({
        email,
        password
    })

    document.getElementById("message").textContent =
        error ? error.message : translations[currentLang].loggedIn
}

// -------------------- LANGUAGE --------------------

let currentLang = "en"

const translations = {
    en: {
        login: "Login",
        register: "Register",
        email: "Email",
        password: "Password",
        registered: "Account created successfully!",
        loggedIn: "Login successful!"
    },
    ru: {
        login: "Войти",
        register: "Регистрация",
        email: "Эл. почта",
        password: "Пароль",
        registered: "Аккаунт создан!",
        loggedIn: "Успешный вход!"
    }
}

window.toggleLanguage = function () {

    currentLang = currentLang === "en" ? "ru" : "en"

    document.getElementById("title").textContent =
        translations[currentLang].login

    document.getElementById("registerBtn").textContent =
        translations[currentLang].register

    document.getElementById("loginBtn").textContent =
        translations[currentLang].login

    document.getElementById("email").placeholder =
        translations[currentLang].email

    document.getElementById("password").placeholder =
        translations[currentLang].password
}