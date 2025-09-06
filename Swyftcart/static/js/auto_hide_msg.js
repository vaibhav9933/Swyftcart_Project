
  // Hide messages after 2 seconds (2000 ms)
  setTimeout(function() {
    let alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
      alert.style.display = 'none';
    });
  }, 3000);
