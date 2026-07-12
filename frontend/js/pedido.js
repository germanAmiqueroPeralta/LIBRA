/**
 * pedido.js
 * Página para que el cliente arme un pedido y lo envíe al administrador.
 */

const selectLibroPedido = document.getElementById("select-libro-pedido");
const inputCantidadPedido = document.getElementById("input-cantidad-pedido");
const btnAgregarPedido = document.getElementById("btn-agregar-pedido");
const btnEnviarPedido = document.getElementById("btn-enviar-pedido");
const contenedorPedido = document.getElementById("contenedor-pedido");

let librosDisponiblesPedido = [];
let pedido = [];

function mostrarAlerta(mensaje, tipo = "exito") {
  const alerta = document.getElementById("alerta");
  alerta.textContent = mensaje;
  alerta.className = `alerta mostrar ${tipo}`;
  setTimeout(() => alerta.classList.remove("mostrar"), 4000);
}

async function cargarSelectorLibrosPedido() {
  try {
    librosDisponiblesPedido = await ApiLibros.listar();
    const conStock = librosDisponiblesPedido.filter(l => l.stock > 0);

    if (conStock.length === 0) {
      selectLibroPedido.innerHTML = `<option value="">No hay libros con stock disponible</option>`;
      return;
    }

    selectLibroPedido.innerHTML = conStock.map(libro => `
      <option value="${libro.isbn}">
        ${libro.titulo} — S/ ${libro.precio.toFixed(2)} (stock: ${libro.stock})
      </option>
    `).join("");
  } catch (error) {
    mostrarAlerta(`Error al cargar libros: ${error.message}`, "error");
  }
}

function renderizarPedido() {
  if (pedido.length === 0) {
    contenedorPedido.innerHTML = `
      <div class="estado-vacio">
        <span class="icono"><i class="fa-solid fa-bag-shopping"></i></span>
        Tu pedido está vacío.
      </div>`;
    btnEnviarPedido.style.display = "none";
    return;
  }

  const total = pedido.reduce((suma, item) => suma + item.cantidad * item.precio, 0);

  contenedorPedido.innerHTML = `
    ${pedido.map((item, indice) => `
      <div class="carrito-item">
        <span>${item.titulo} × ${item.cantidad}</span>
        <span style="display:flex; align-items:center; gap:0.75rem;">
          S/ ${(item.cantidad * item.precio).toFixed(2)}
          <button class="btn btn-peligro" onclick="quitarDelPedido(${indice})">Quitar</button>
        </span>
      </div>
    `).join("")}
    <div class="carrito-total">
      <span>Total del pedido</span>
      <span>S/ ${total.toFixed(2)}</span>
    </div>`;

  btnEnviarPedido.style.display = "inline-block";
}

function quitarDelPedido(indice) {
  pedido.splice(indice, 1);
  renderizarPedido();
}

btnAgregarPedido.addEventListener("click", () => {
  const isbn = selectLibroPedido.value;
  const cantidad = parseInt(inputCantidadPedido.value, 10);

  if (!isbn) {
    mostrarAlerta("Selecciona un libro.", "error");
    return;
  }
  if (!cantidad || cantidad <= 0) {
    mostrarAlerta("La cantidad debe ser mayor a cero.", "error");
    return;
  }

  const libro = librosDisponiblesPedido.find(l => l.isbn === isbn);
  if (!libro) return;

  const yaEnPedido = pedido.find(item => item.isbn === isbn);
  const cantidadTotal = (yaEnPedido ? yaEnPedido.cantidad : 0) + cantidad;

  if (cantidadTotal > libro.stock) {
    mostrarAlerta(`Stock insuficiente. Disponible: ${libro.stock}.`, "error");
    return;
  }

  if (yaEnPedido) {
    yaEnPedido.cantidad = cantidadTotal;
  } else {
    pedido.push({ isbn: libro.isbn, titulo: libro.titulo, cantidad, precio: libro.precio });
  }

  inputCantidadPedido.value = 1;
  renderizarPedido();
});

btnEnviarPedido.addEventListener("click", async () => {
  if (pedido.length === 0) return;

  const cliente = prompt("Ingresa tu nombre para enviar el pedido al administrador:");
  if (!cliente || !cliente.trim()) {
    mostrarAlerta("El nombre del cliente es obligatorio.", "error");
    return;
  }

  try {
    await ApiPedidos.crearPedido({ cliente: cliente.trim(), items: pedido });
    mostrarAlerta("Pedido enviado al administrador.");
    pedido = [];
    renderizarPedido();
  } catch (error) {
    mostrarAlerta(error.message, "error");
  }
});

(async () => {
  await verificarAcceso();
  await cargarSelectorLibrosPedido();
  renderizarPedido();
})();
