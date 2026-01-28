const loginBtn = document.getElementById("loginBtn");
const dropdownMenu = document.getElementById("dropdownMenu");

loginBtn.addEventListener("click", () => {
    dropdownMenu.style.display =
        dropdownMenu.style.display === "block" ? "none" : "block";
});

window.addEventListener("click", (e) => {
    if (!e.target.matches(".login-btn")) {
        dropdownMenu.style.display = "none";
    }
});
