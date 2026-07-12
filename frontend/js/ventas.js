/**
 * ventas.js
 * Lógica de la página de ventas: selección de libros, carrito en memoria,
 * confirmación de venta e historial.
 */

const selectLibro = document.getElementById("select-libro");

(async () => {
  const user = await verificarAcceso({ rolRequerido: "admin" });
  if (!user) {
    return;
  }
  cargarSelectorLibros();
  cargarHistorial();
})();
const inputCantidad = document.getElementById("input-cantidad");
const btnAgregarCarrito = document.getElementById("btn-agregar-carrito");
const contenedorCarrito = document.getElementById("contenedor-carrito");
const btnConfirmarVenta = document.getElementById("btn-confirmar-venta");
const contenedorHistorial = document.getElementById("contenedor-historial");
const valorTotalFiltrado = document.getElementById("valor-total-filtrado");
const selectPeriodoHistorial = document.getElementById("select-periodo-historial");
const inputFechaHistorial = document.getElementById("input-fecha-historial");
const btnFiltrarHistorial = document.getElementById("btn-filtrar-historial");

let librosDisponibles = [];
let carrito = []; // [{isbn, titulo, cantidad, precio}]
let periodoHistorial = "total";

function mostrarAlerta(mensaje, tipo = "exito") {
  const alerta = document.getElementById("alerta");
  alerta.textContent = mensaje;
  alerta.className = `alerta mostrar ${tipo}`;
  setTimeout(() => alerta.classList.remove("mostrar"), 4000);
}

async function cargarSelectorLibros() {
  try {
    librosDisponibles = await ApiLibros.listar();
    const conStock = librosDisponibles.filter(l => l.stock > 0);

    if (conStock.length === 0) {
      selectLibro.innerHTML = `<option value="">No hay libros con stock disponible</option>`;
      return;
    }

    selectLibro.innerHTML = conStock.map(libro => `
      <option value="${libro.isbn}">
        ${libro.titulo} — S/ ${libro.precio.toFixed(2)} (stock: ${libro.stock})
      </option>
    `).join("");
  } catch (error) {
    mostrarAlerta(`Error al cargar libros: ${error.message}`, "error");
  }
}

function renderizarCarrito() {
  if (carrito.length === 0) {
    contenedorCarrito.innerHTML = `
      <div class="estado-vacio">
        <span class="icono"><i class="fa-solid fa-bag-shopping"></i></span>
        El carrito está vacío.
      </div>`;
    btnConfirmarVenta.style.display = "none";
    return;
  }

  const total = carrito.reduce((suma, item) => suma + item.cantidad * item.precio, 0);

  contenedorCarrito.innerHTML = `
    ${carrito.map((item, indice) => `
      <div class="carrito-item">
        <span>${item.titulo} × ${item.cantidad}</span>
        <span style="display:flex; align-items:center; gap:0.75rem;">
          S/ ${(item.cantidad * item.precio).toFixed(2)}
          <button class="btn btn-peligro" onclick="quitarDelCarrito(${indice})">Quitar</button>
        </span>
      </div>
    `).join("")}
    <div class="carrito-total">
      <span>Total</span>
      <span>S/ ${total.toFixed(2)}</span>
    </div>
  `;
  btnConfirmarVenta.style.display = "inline-block";
}

function quitarDelCarrito(indice) {
  carrito.splice(indice, 1);
  renderizarCarrito();
}

btnAgregarCarrito.addEventListener("click", () => {
  const isbn = selectLibro.value;
  const cantidad = parseInt(inputCantidad.value, 10);

  if (!isbn) {
    mostrarAlerta("Selecciona un libro.", "error");
    return;
  }
  if (!cantidad || cantidad <= 0) {
    mostrarAlerta("La cantidad debe ser mayor a cero.", "error");
    return;
  }

  const libro = librosDisponibles.find(l => l.isbn === isbn);
  if (!libro) return;

  const yaEnCarrito = carrito.find(item => item.isbn === isbn);
  const cantidadTotal = (yaEnCarrito ? yaEnCarrito.cantidad : 0) + cantidad;

  if (cantidadTotal > libro.stock) {
    mostrarAlerta(`Stock insuficiente. Disponible: ${libro.stock}.`, "error");
    return;
  }

  if (yaEnCarrito) {
    yaEnCarrito.cantidad = cantidadTotal;
  } else {
    carrito.push({ isbn: libro.isbn, titulo: libro.titulo, cantidad, precio: libro.precio });
  }

  inputCantidad.value = 1;
  renderizarCarrito();
});

btnConfirmarVenta.addEventListener("click", async () => {
  if (carrito.length === 0) return;

  const items = carrito.map(item => ({ isbn: item.isbn, cantidad: item.cantidad }));

  try {
    await ApiVentas.registrar(items);
    mostrarAlerta("Venta registrada correctamente.");
    carrito = [];
    renderizarCarrito();
    await cargarSelectorLibros();
    await cargarHistorial();
  } catch (error) {
    mostrarAlerta(error.message, "error");
  }
});

async function cargarHistorial(periodo = "total", fecha = "") {
  try {
    const [ventas, resumen] = await Promise.all([
      periodo === "total" && !fecha ? ApiVentas.listar() : ApiVentas.listar(periodo, fecha),
      ApiVentas.totalVendido(periodo, fecha),
    ]);

    valorTotalFiltrado.textContent = resumen.total_vendido.toFixed(2);

    if (ventas.length === 0) {
      contenedorHistorial.innerHTML = `
        <div class="estado-vacio">
          <span class="icono"><i class="fa-solid fa-box-open"></i></span>
          Todavía no hay ventas registradas.
        </div>`;
      return;
    }

    contenedorHistorial.innerHTML = `
      <div class="tabla-wrapper">
        <table>
          <thead>
            <tr><th>#</th><th>Fecha</th><th>Total</th><th>Acciones</th></tr>
          </thead>
          <tbody>
            ${ventas.map(venta => `
              <tr>
                <td>${venta.id}</td>
                <td>${new Date(venta.fecha).toLocaleString("es-PE")}</td>
                <td>S/ ${venta.total.toFixed(2)}</td>
                <td>
                  <div class="acciones-fila">
                    <button class="btn btn-secundario btn-ver-detalle" type="button" data-venta-id="${venta.id}">Ver</button>
                  </div>
                </td>
              </tr>
              <tr class="detalle-venta-row" id="detalle-venta-${venta.id}" style="display:none;">
                <td colspan="4">
                  <div class="detalle-venta-contenido">
                    ${venta.detalles.map(d => `
                      <div>
                        <strong>${d.titulo}</strong>: ${d.cantidad}
                      </div>
                    `).join("")}
                  </div>
                </td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>`;

    const botonesVerDetalle = contenedorHistorial.querySelectorAll(".btn-ver-detalle");
    botonesVerDetalle.forEach(boton => {
      boton.addEventListener("click", () => {
        const ventaId = boton.dataset.ventaId;
        const filaDetalle = document.getElementById(`detalle-venta-${ventaId}`);
        if (!filaDetalle) return;

        const estaVisible = filaDetalle.style.display === "table-row";
        filaDetalle.style.display = estaVisible ? "none" : "table-row";
        boton.textContent = estaVisible ? "Ver" : "Ocultar";
      });
    });
  } catch (error) {
    valorTotalFiltrado.textContent = "0.00";
    contenedorHistorial.innerHTML = `
      <div class="estado-vacio">
        <span class="icono">⚠️</span>
        No se pudo cargar el historial (${error.message}).
      </div>`;
  }
}

function ajustarTipoFechaHistorial() {
  if (periodoHistorial === "dia") {
    inputFechaHistorial.type = "date";
    inputFechaHistorial.value = "";
  } else if (periodoHistorial === "mes") {
    inputFechaHistorial.type = "month";
    inputFechaHistorial.value = "";
  } else if (periodoHistorial === "anio") {
    inputFechaHistorial.type = "number";
    inputFechaHistorial.min = "1900";
    inputFechaHistorial.max = "2100";
    inputFechaHistorial.placeholder = "2026";
    inputFechaHistorial.value = "";
  } else {
    inputFechaHistorial.type = "date";
    inputFechaHistorial.value = "";
  }
}

btnFiltrarHistorial.addEventListener("click", () => {
  periodoHistorial = selectPeriodoHistorial.value;
  let fecha = inputFechaHistorial.value;
  if (periodoHistorial !== "total" && !fecha) {
    mostrarAlerta("Selecciona una fecha válida para filtrar.", "error");
    return;
  }

  cargarHistorial(periodoHistorial, fecha);
});

selectPeriodoHistorial.addEventListener("change", (event) => {
  periodoHistorial = event.target.value;
  ajustarTipoFechaHistorial();
});

