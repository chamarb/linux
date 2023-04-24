const loginForm = document.querySelector("#login-form");
const emailInput = document.querySelector("#email");
const passwordInput = document.querySelector("#password");
const loginBtn = document.querySelector("#login-btn");
const forgotPasswordLink = document.querySelector("#forgot-password");
const createAccountLink = document.querySelector("#create-account");

loginForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const email = emailInput.value;
  const password = passwordInput.value;
  // Perform authentication logic here
});

forgotPasswordLink
