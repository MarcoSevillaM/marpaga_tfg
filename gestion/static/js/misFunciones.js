document.addEventListener('DOMContentLoaded', function () {
    // Agrega un evento de clic a cada fila
    var filas = document.querySelectorAll('tr[data-href]');
    filas.forEach(function (fila) {
      fila.addEventListener('click', function () {
          var url = fila.getAttribute('data-href');
          if (url) {
            window.location.href = url;
          }
       });
      });
    });