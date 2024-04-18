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

  var myModal = new bootstrap.Modal(document.getElementById('statusModal'));
    // Mostrar el modal
    myModal.show();
    console.log('Mostrando modal de error' + control);
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

document.getElementById("cambiarFoto").addEventListener("click", function() {
  $('#modalCambiarFoto').modal('show');
});


// Filtrar el nivel de dificultad de las maquinas
function filterTable(level) {
  var buttons = document.querySelectorAll('.dropdown-menu button');
  buttons.forEach(function(button) {
    var buttonText = quitarAcentos(button.textContent.trim().toLowerCase()); 
    if (buttonText === level) {
      console.log('Match!');
      button.classList.remove('btn-outline-primary');
      button.classList.add('btn-primary');
    } else {
      button.classList.remove('btn-primary');
      button.classList.add('btn-outline-primary');
    }
  });


  var rows = document.querySelectorAll('tbody tr');
  rows.forEach(function(row) {
    // Verificar si hay al menos 3 celdas antes de acceder a textContent
    var cells = row.querySelectorAll('td');
    if (cells.length >= 3) {
      var difficulty = cells[1].textContent.toLowerCase();
      if (level === 'all' || difficulty === level) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    }
  });
}

function quitarAcentos(texto) {
  return texto.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}




