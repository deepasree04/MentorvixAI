 document.addEventListener("DOMContentLoaded", () => {

  /* ================= SLIDE UI LOGIC ================= */
  const loginFormUI = document.querySelector("form.login");
  const signupFormUI = document.querySelector("form.signup");
  const loginText = document.querySelector(".title-text .login");
  const loginBtn = document.querySelector("label.login");
  const signupBtn = document.querySelector("label.signup");
  const signupLink = document.querySelector(".signup-link a");

  if (signupBtn) {
    signupBtn.onclick = () => {
      loginFormUI.style.marginLeft = "-50%";
      loginText.style.marginLeft = "-50%";
    };
  }

  if (loginBtn) {
    loginBtn.onclick = () => {
      loginFormUI.style.marginLeft = "0%";
      loginText.style.marginLeft = "0%";
    };
  }

  if (signupLink) {
    signupLink.onclick = (e) => {
      e.preventDefault();
      signupBtn.click();
    };
  }

  /* ================= LOGIN ================= */
  const loginForm = document.getElementById("loginForm");

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const username = document.getElementById("loginEmail").value.trim();
      const password = document.getElementById("loginPassword").value.trim();

      try {
        const res = await fetch("http://127.0.0.1:8000/api/auth/login/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password })
        });

        const data = await res.json();

        if (!res.ok) {
          alert(data.detail || "Login failed");
          return;
        }

        localStorage.setItem("access", data.access);
        localStorage.setItem("refresh", data.refresh);
        localStorage.setItem("username", username);

        window.location.href = "../profile/profile.html";

      } catch (err) {
        alert("Backend not running");
      }
    });
  }

  /* ================= SIGNUP ================= */
  const signupForm = document.getElementById("signupForm");

  if (signupForm) {
    signupForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const email = document.getElementById("signupEmail").value.trim();
      const password = document.getElementById("signupPassword").value.trim();
      const confirm = document.getElementById("signupConfirm").value.trim();

      if (password !== confirm) {
        alert("Passwords do not match");
        return;
      }

      const username = email.split("@")[0];

      try {
        const res = await fetch("http://127.0.0.1:8000/api/auth/register/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, email, password })
        });

        const data = await res.json();

        if (!res.ok) {
          alert(JSON.stringify(data));
          return;
        }

        window.location.href ="../home page/home.html";

      } catch (err) {
        alert("Backend not running");
      }
    });
  }

});

  