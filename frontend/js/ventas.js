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

let librosDisponibles = [];
let carrito = []; // [{isbn, titulo, cantidad, precio}]

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
        <span class="icono">🛍️</span>
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

async function cargarHistorial() {
  try {
    const ventas = await ApiVentas.listar();

    if (ventas.length === 0) {
      contenedorHistorial.innerHTML = `
        <div class="estado-vacio">
          <span class="icono">📭</span>
          Todavía no hay ventas registradas.
        </div>`;
      return;
    }

    contenedorHistorial.innerHTML = `
      <div class="tabla-wrapper">
        <table>
          <thead>
            <tr><th>#</th><th>Fecha</th><th>Detalle</th><th>Total</th></tr>
          </thead>
          <tbody>
            ${ventas.map(venta => `
              <tr>
                <td>${venta.id}</td>
                <td>${new Date(venta.fecha).toLocaleString("es-PE")}</td>
                <td>${venta.detalles.map(d => `${d.isbn} × ${d.cantidad}`).join(", ")}</td>
                <td>S/ ${venta.total.toFixed(2)}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>`;
  } catch (error) {
    contenedorHistorial.innerHTML = `
      <div class="estado-vacio">
        <span class="icono">⚠️</span>
        No se pudo cargar el historial (${error.message}).
      </div>`;
  }
}

