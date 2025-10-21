// ==============================
// 📈 GYMAPP MULTI-GRÁFICOS — MODO OSCURO SUAVE + EXPORTABLE
// ==============================

function crearGrafico(id, label, data, color) {
  const canvas = document.getElementById(id);
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  const dark = document.body.classList.contains("dark-mode");

  // 🎨 Fondo dinámico con degradado según modo
  const fondoPlugin = {
    id: "fondoGymApp",
    beforeDraw(chart) {
      const { ctx, chartArea } = chart;
      if (!chartArea) return;
      const grad = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
      if (dark) {
        grad.addColorStop(0, "#0e141b");
        grad.addColorStop(1, "#141e29ff");
      } else {
        grad.addColorStop(0, "#ffffff");
        grad.addColorStop(1, "#f8f9fa");
      }
      ctx.fillStyle = grad;
      ctx.fillRect(chartArea.left, chartArea.top, chartArea.width, chartArea.height);
    }
  };

  return new Chart(ctx, {
    type: "line",
    data: {
      labels: window.datosMediciones.fechas,
      datasets: [{
        label,
        data,
        fill: true,
        backgroundColor: color.replace("1)", "0.25)"),
        borderColor: color,
        borderWidth: 2,
        tension: 0.35,
        pointRadius: 3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          labels: {
            color: dark ? "#e8f0ff" : "#333",
            font: { size: 13, weight: "500" }
          }
        },
        tooltip: {
          backgroundColor: dark ? "rgba(25,30,40,0.95)" : "#fff",
          titleColor: dark ? "#fff" : "#111",
          bodyColor: dark ? "#dce6f5" : "#111",
          borderColor: dark ? "#4db5ff" : "#ccc",
          borderWidth: 1,
          displayColors: false
        }
      },
      scales: {
        x: {
          ticks: {
            color: dark ? "#d1e7ff" : "#333",
            font: { size: 12 }
          },
          grid: {
            color: dark ? "rgba(255,255,255,0.05)" : "#ddd"
          }
        },
        y: {
          ticks: {
            color: dark ? "#d1e7ff" : "#333",
            font: { size: 12 }
          },
          grid: {
            color: dark ? "rgba(255,255,255,0.05)" : "#ddd"
          }
        }
      }
    },
    plugins: [fondoPlugin]
  });
}

// 🎨 Paleta oficial GymApp
const colores = [
  "rgba(77, 181, 255, 1)",   // Azul — Peso
  "rgba(255, 209, 102, 1)",  // Dorado — IMC
  "rgba(255, 99, 132, 1)",   // Rojo — Grasa
  "rgba(100, 255, 218, 1)",  // Verde agua — Músculo
  "rgba(155, 0, 245, 1)"     // Violeta — Agua
];


let charts = {};

function inicializarGraficos() {
  // 🔄 Destruye y limpia los gráficos previos
  for (const key in charts) {
    if (charts[key]) {
      charts[key].destroy();
      const canvas = document.getElementById(`grafico_${key}`);
      if (canvas) {
        canvas.width = canvas.clientWidth;
        canvas.height = 280;
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    }
  }

  // 🧱 Crea los nuevos gráficos
  charts = {
    peso: crearGrafico("grafico_peso", "Peso (kg)", window.datosMediciones.pesos, colores[0]),
    imc: crearGrafico("grafico_imc", "IMC", window.datosMediciones.imcs, colores[1]),
    grasa: crearGrafico("grafico_grasa", "Grasa Corporal (%)", window.datosMediciones.grasas, colores[2]),
    musculo: crearGrafico("grafico_musculo", "Músculo (%)", window.datosMediciones.musculos, colores[3]),
    agua: crearGrafico("grafico_agua", "Agua Corporal (%)", window.datosMediciones.aguas, colores[4])
  };
}

// 💾 Guarda los gráficos como imágenes base64 (para PDF)
function guardarGraficosComoBase64() {
  const imagenes = {};
  for (const [nombre, grafico] of Object.entries(charts)) {
    if (grafico) imagenes[nombre] = grafico.toBase64Image("image/png");
  }
  localStorage.setItem("graficosPDF", JSON.stringify(imagenes));
}

// 🌗 Transición suave entre modo claro/oscuro
function aplicarModoOscuroSuave() {
  const contenedor = document.querySelectorAll("canvas");
  contenedor.forEach(canvas => {
    canvas.style.transition = "filter 0.6s ease, opacity 0.6s ease";
    canvas.style.opacity = "0";
    setTimeout(() => {
      inicializarGraficos(); // redibuja con nuevos colores
      canvas.style.opacity = "1";
    }, 300);
  });
  setTimeout(guardarGraficosComoBase64, 1000);
}

// 🕵️‍♂️ Detecta cambios de modo (oscuro/claro)
const observer = new MutationObserver(() => {
  aplicarModoOscuroSuave();
});
observer.observe(document.body, { attributes: true, attributeFilter: ["class"] });

// ▶️ Render inicial con fade-in elegante
document.addEventListener("DOMContentLoaded", () => {
  const canvasList = document.querySelectorAll("canvas");
  canvasList.forEach(c => {
    c.style.opacity = "0";
    c.style.transition = "opacity 0.8s ease";
  });

  inicializarGraficos();
  setTimeout(() => {
    canvasList.forEach(c => (c.style.opacity = "1"));
    guardarGraficosComoBase64();
  }, 1000);
});
