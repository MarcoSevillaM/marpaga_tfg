for (var i = 1; i <= 4; i++) {
    (function(i) {
        var boton = document.getElementById("mi_boton_" + i);

        boton.addEventListener("click", function (event) {
            if (boton.classList.contains("btn-success")) {
                // Cambiamos el texto y la clase del botón
                boton.textContent = "Detener";
                boton.className = "btn btn-danger";
                console.log("El botón " + i + " ha sido clicado");
                // Aquí puedes realizar acciones específicas para el botón, como iniciar o detener la máquina virtual asociada a este botón.
            } else {
                boton.textContent = "Activar";
                boton.className = "btn btn-success";
                // Finaliza la máquina virtual
            }
        });
    })(i);
}