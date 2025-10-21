// =========================================================
// 💪 GYMAPP - Contadores Animados en Dashboard
// =========================================================

// Detectar cuando los contadores entran en pantalla
document.addEventListener("DOMContentLoaded", () => {
  const counters = document.querySelectorAll(".contador");

  const startCounter = (el) => {
    const target = +el.getAttribute("data-target");
    const duration = 1200; // duración total en ms
    const stepTime = 15;   // intervalo de actualización
    let current = 0;
    const increment = target / (duration / stepTime);

    const counterInterval = setInterval(() => {
      current += increment;
      if (current >= target) {
        el.textContent = target;
        clearInterval(counterInterval);
      } else {
        el.textContent = Math.floor(current);
      }
    }, stepTime);
  };

  // Usamos IntersectionObserver para no animar hasta que se vea
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !entry.target.classList.contains("animado")) {
        startCounter(entry.target);
        entry.target.classList.add("animado");
      }
    });
  }, { threshold: 0.5 });

  counters.forEach(counter => observer.observe(counter));
});
