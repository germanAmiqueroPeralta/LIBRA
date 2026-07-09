/**
 * libros.js
 * Lógica de la página de gestión de libros (CRUD completo).
 */

const form = document.getElementById("form-libro");

(async () => {
  const user = await verificarAcceso({ rolRequerido: "admin" });
  if (!user) {
    return;
  }
  cargarLibros();
})();
const inputBuscar = document.getElementById("input-buscar");
const btnBuscar = document.getElementById("btn-buscar");
const btnCancelar = document.getElementById("btn-cancelar");
const cuerpoTabla = document.getElementById("cuerpo-tabla-libros");
const estadoVacio = document.getElementById("estado-vacio-libros");
const modoEdicion = document.getElementById("modo-edicion");
const tituloFormulario = document.getElementById("titulo-formulario");
const btnGuardar = document.getElementById("btn-guardar");
const campoIsbn = document.getElementById("isbn");

function mostrarAlerta(mensaje, tipo = "exito") {
  const alerta = document.getElementById("alerta");
  alerta.textContent = mensaje;
  alerta.className = `alerta mostrar ${tipo}`;
  setTimeout(() => alerta.classList.remove("mostrar"), 4000);
}

function limpiarFormulario() {
  form.reset();
  modoEdicion.value = "false";
  campoIsbn.disabled = false;
  tituloFormulario.textContent = "➕ Registrar nuevo libro";
  btnGuardar.textContent = "Guardar libro";
  btnCancelar.style.display = "none";
}

function renderizarLibros(libros) {
  if (libros.length === 0) {
    cuerpoTabla.innerHTML = "";
    estadoVacio.innerHTML = `
      <div class="estado-vacio">
        <span class="icono">📭</span>
        No se encontraron libros.
      </div>`;
    return;
  }

  estadoVacio.innerHTML = "";
  cuerpoTabla.innerHTML = libros.map(libro => `
    <tr>
      <td>${libro.isbn}</td>
      <td>${libro.titulo}</td>
      <td>${libro.autor}</td>
      <td>S/ ${libro.precio.toFixed(2)}</td>
      <td class="${libro.stock <= 3 ? 'stock-bajo' : 'stock-ok'}">${libro.stock}</td>
      <td>${libro.categoria || "—"}</td>
      <td class="acciones-fila">
        <button class="btn btn-secundario" onclick="editarLibro('${libro.isbn}')">Editar</button>
        <button class="btn btn-peligro" onclick="eliminarLibro('${libro.isbn}')">Eliminar</button>
      </td>
    </tr>
  `).join("");
}

async function cargarLibros(termino = "") {
  try {
    const libros = await ApiLibros.listar(termino);
    renderizarLibros(libros);
  } catch (error) {
    mostrarAlerta(`Error al cargar libros: ${error.message}`, "error");
  }
}

form.addEventListener("submit", async (evento) => {
  evento.preventDefault();

  const datos = {
    isbn: campoIsbn.value.trim(),
    titulo: document.getElementById("titulo").value.trim(),
    autor: document.getElementById("autor").value.trim(),
    precio: parseFloat(document.getElementById("precio").value),
    stock: parseInt(document.getElementById("stock").value, 10),
    categoria: document.getElementById("categoria").value.trim(),
  };

  try {
    if (modoEdicion.value === "true") {
      await ApiLibros.actualizar(datos.isbn, datos);
      mostrarAlerta("Libro actualizado correctamente.");
    } else {
      await ApiLibros.registrar(datos);
      mostrarAlerta("Libro registrado correctamente.");
    }
    limpiarFormulario();
    cargarLibros(inputBuscar.value.trim());
  } catch (error) {
    mostrarAlerta(error.message, "error");
  }
});

async function editarLibro(isbn) {
  try {
    const libro = await ApiLibros.obtener(isbn);
    document.getElementById("isbn").value = libro.isbn;
    document.getElementById("titulo").value = libro.titulo;
    document.getElementById("autor").value = libro.autor;
    document.getElementById("precio").value = libro.precio;
    document.getElementById("stock").value = libro.stock;
    document.getElementById("categoria").value = libro.categoria || "";

    campoIsbn.disabled = true; // el ISBN no se puede cambiar al editar
    modoEdicion.value = "true";
    tituloFormulario.textContent = `✏️ Editando: ${libro.titulo}`;
    btnGuardar.textContent = "Actualizar libro";
    btnCancelar.style.display = "inline-block";

    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (error) {
    mostrarAlerta(error.message, "error");
  }
}

async function eliminarLibro(isbn) {
  if (!confirm(`¿Seguro que deseas eliminar el libro con ISBN ${isbn}?`)) return;

  try {
    await ApiLibros.eliminar(isbn);
    mostrarAlerta("Libro eliminado correctamente.");
    cargarLibros(inputBuscar.value.trim());
  } catch (error) {
    mostrarAlerta(error.message, "error");
  }
}

btnCancelar.addEventListener("click", limpiarFormulario);

btnBuscar.addEventListener("click", () => cargarLibros(inputBuscar.value.trim()));
inputBuscar.addEventListener("keyup", (evento) => {
  if (evento.key === "Enter") cargarLibros(inputBuscar.value.trim());
});

