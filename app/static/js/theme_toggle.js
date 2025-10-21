document.addEventListener("DOMContentLoaded", () => {
  const toggleBtn = document.getElementById("toggle-theme");
  const icon = toggleBtn.querySelector("i");

  // Cargar tema guardado
  if (localStorage.getItem("theme") === "dark") {
    document.body.classList.add("dark-mode");
    icon.classList.replace("bi-moon-fill", "bi-sun-fill");
  }

  toggleBtn.addEventListener("click", () => {
    document.body.classList.toggle("dark-mode");
    const isDark = document.body.classList.contains("dark-mode");

    // Cambiar ícono
    icon.classList.toggle("bi-moon-fill", !isDark);
    icon.classList.toggle("bi-sun-fill", isDark);

    // Guardar preferencia
    localStorage.setItem("theme", isDark ? "dark" : "light");
  });
});
