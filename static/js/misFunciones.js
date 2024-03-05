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
function mostrarIndicadorDeCarga(formId) {
  // Obtener el formulario y el botón
  var form = document.getElementById(formId);
  var button = form.querySelector('button');

  // Deshabilitar el botón y cambiar el texto
  button.disabled = true;
  button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Cargando...';

  // Aquí puedes agregar más lógica de carga si es necesario

  // Enviar el formulario después de un breve retraso (puedes ajustar el tiempo)
  setTimeout(function() {
    form.submit();
  }, 500);
}

function desactivarBotones() {
  document.getElementById('btnFlag1').disabled = true;
  document.getElementById('btnFlag2').disabled = true;
}