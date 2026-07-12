document.addEventListener("DOMContentLoaded", () => {

  /* ================= HELPERS ================= */

  function showMessage(elementId, text, type) {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.textContent = text;
    el.className = "form-message " + type; // "error" or "success"
    el.style.display = "block";
  }

  function clearMessage(elementId) {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.textContent = "";
    el.style.display = "none";
    el.className = "form-message";
  }

  function setLoading(btnId, isLoading) {
    const btn = document.getElementById(btnId);
    if (!btn) return;
    if (isLoading) {
      btn.dataset.originalValue = btn.value;
      btn.value = "Please wait…";
      btn.disabled = true;
      btn.classList.add("loading");
    } else {
      btn.value = btn.dataset.originalValue || btn.value;
      btn.disabled = false;
      btn.classList.remove("loading");
    }
  }

  /**
   * Turn DRF serializer errors (object of arrays) into a readable string.
   * e.g. { username: ["This field is required."], email: ["Enter a valid email."] }
   *   → "Username: This field is required. Email: Enter a valid email."
   */
  function parseErrors(data) {
    if (typeof data === "string") return data;
    if (data.detail) return data.detail;
    if (data.error) return data.error;

    const messages = [];
    for (const [field, errors] of Object.entries(data)) {
      const label = field.charAt(0).toUpperCase() + field.slice(1);
      const errText = Array.isArray(errors) ? errors.join(" ") : errors;
      messages.push(`${label}: ${errText}`);
    }
    return messages.join(" • ") || "Something went wrong.";
  }

  /* ================= SLIDE UI LOGIC ================= */
  const loginFormUI = document.querySelector("form.login");
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
      clearMessage("loginMessage");

      const username = document.getElementById("loginEmail").value.trim();
      const password = document.getElementById("loginPassword").value.trim();

      if (!username || !password) {
        showMessage("loginMessage", "Please fill in all fields.", "error");
        return;
      }

      setLoading("loginBtn", true);

      try {
        const res = await fetch("/accounts/api/login/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password })
        });

        const data = await res.json();

        if (!res.ok) {
          showMessage("loginMessage", data.error || data.detail || "Invalid credentials.", "error");
          return;
        }

        localStorage.setItem("access", data.access);
        localStorage.setItem("refresh", data.refresh);
        localStorage.setItem("username", username);

        showMessage("loginMessage", "Login successful! Redirecting…", "success");
        setTimeout(() => {
          const redirect = new URLSearchParams(window.location.search).get('redirect');
          if (redirect === 'assignment') {
            window.location.href = "/assignments/list/";
          } else {
            window.location.href = "/";
          }
        }, 600);

      } catch (err) {
        showMessage("loginMessage", "Could not connect to server. Is the backend running?", "error");
      } finally {
        setLoading("loginBtn", false);
      }
    });
  }

  /* ================= SIGNUP ================= */
  const signupForm = document.getElementById("signupForm");

  if (signupForm) {
    signupForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      clearMessage("signupMessage");

      const username = document.getElementById("signupUsername").value.trim();
      const email = document.getElementById("signupEmail").value.trim();
      const password = document.getElementById("signupPassword").value.trim();
      const confirm = document.getElementById("signupConfirm").value.trim();

      if (!username || !email || !password || !confirm) {
        showMessage("signupMessage", "Please fill in all fields.", "error");
        return;
      }

      if (password !== confirm) {
        showMessage("signupMessage", "Passwords do not match.", "error");
        return;
      }

      if (password.length < 8) {
        showMessage("signupMessage", "Password must be at least 8 characters.", "error");
        return;
      }

      setLoading("signupBtn", true);

      try {
        /* --- Register --- */
        const regRes = await fetch("/accounts/register/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, email, password })
        });

        const regData = await regRes.json();

        if (!regRes.ok) {
          showMessage("signupMessage", parseErrors(regData), "error");
          return;
        }

        /* --- Auto-login after successful registration --- */
        const loginRes = await fetch("/accounts/api/login/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password })
        });

        const loginData = await loginRes.json();

        if (!loginRes.ok) {
          showMessage("signupMessage", "Account created! Please switch to login.", "success");
          return;
        }

        localStorage.setItem("access", loginData.access);
        localStorage.setItem("refresh", loginData.refresh);
        localStorage.setItem("username", username);

        showMessage("signupMessage", "Account created! Redirecting…", "success");
        setTimeout(() => {
          const redirect = new URLSearchParams(window.location.search).get('redirect');
          if (redirect === 'assignment') {
            window.location.href = "/assignments/list/";
          } else {
            window.location.href = "/";
          }
        }, 600);

      } catch (err) {
        showMessage("signupMessage", "Could not connect to server. Is the backend running?", "error");
      } finally {
        setLoading("signupBtn", false);
      }
    });
  }

});