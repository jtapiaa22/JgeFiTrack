document.addEventListener("DOMContentLoaded", () => {
  setTimeout(() => {
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(alert => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    });
  }, 3000); //1 segundos
});
