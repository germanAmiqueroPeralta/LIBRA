/**
 * pedidos_admin.js
 * Página donde el administrador ve pedidos pendientes y los confirma.
 */

const contenedorPedidos = document.getElementById("contenedor-pedidos");
const alertaPedidos = document.getElementById("alerta");

function mostrarAlerta(mensaje, tipo = "exito") {
  alertaPedidos.textContent = mensaje;
  alertaPedidos.className = `alerta mostrar ${tipo}`;
  setTimeout(() => alertaPedidos.classList.remove("mostrar"), 4000);
}

function renderizarPedidos(pedidos) {
  if (pedidos.length === 0) {
    contenedorPedidos.innerHTML = `
      <div class="estado-vacio">
        <span class="icono">📭</span>
        No hay pedidos pendientes.
      </div>`;
    return;
  }

  contenedorPedidos.innerHTML = `
    <div class="tabla-wrapper">
      <table>
        <thead>
          <tr><th>ID</th><th>Cliente</th><th>Fecha</th><th>Total</th><th>Estado</th><th>Acciones</th></tr>
        </thead>
        <tbody>
          ${pedidos.map(pedido => `
            <tr>
              <td>${pedido.id}</td>
              <td>${pedido.cliente}</td>
              <td>${new Date(pedido.fecha).toLocaleString('es-PE')}</td>
              <td>S/ ${pedido.total.toFixed(2)}</td>
              <td>${pedido.estado}</td>
              <td>
                <button class="btn btn-acento" onclick="confirmarPedido(${pedido.id})">Confirmar venta</button>
              </td>
            </tr>
            <tr class="pedido-detalle-row">
              <td colspan="6">
                <strong>Detalle:</strong> ${pedido.detalles.map(d => `${d.isbn} × ${d.cantidad}`).join(", ")}
              </td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>`;
}

async function cargarPedidos() {
  try {
    const pedidos = await ApiPedidos.listarPedidos("pendiente");
    renderizarPedidos(pedidos);
  } catch (error) {
    contenedorPedidos.innerHTML = `
      <div class="estado-vacio">
        <span class="icono">⚠️</span>
        No se pudo cargar los pedidos (${error.message}).
      </div>`;
  }
}

window.confirmarPedido = async function (pedidoId) {
  try {
    await ApiPedidos.confirmarPedido(pedidoId);
    mostrarAlerta("Pedido confirmado y registrado como venta.");
    await cargarPedidos();
  } catch (error) {
    mostrarAlerta(error.message, "error");
  }
};

(async () => {
  await verificarAcceso({ rolRequerido: "admin" });
  await cargarPedidos();
})();
