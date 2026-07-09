/**
 * api.js
 * Capa de comunicación entre el frontend y la API Flask.
 * Ningún otro archivo JS hace fetch() directamente: todos pasan por aquí.
 */

const API_BASE_URL = "/api";

async function _peticion(metodo, endpoint, cuerpo = null) {
  const opciones = {
    method: metodo,
    headers: { "Content-Type": "application/json" },
  };
  if (cuerpo !== null) {
    opciones.body = JSON.stringify(cuerpo);
  }

  const respuesta = await fetch(`${API_BASE_URL}${endpoint}`, opciones);
  const data = await respuesta.json().catch(() => ({}));

  if (!respuesta.ok) {
    const mensaje = data.error || `Error ${respuesta.status}`;
    throw new Error(mensaje);
  }
  return data;
}

const ApiAuth = {
  register: (datos) => _peticion("POST", "/auth/register", datos),
  login: (datos) => _peticion("POST", "/auth/login", datos),
  logout: () => _peticion("POST", "/auth/logout"),
  me: () => _peticion("GET", "/auth/me"),
};

const ApiLibros = {
  listar: (termino = "") => {
    const query = termino ? `?buscar=${encodeURIComponent(termino)}` : "";
    return _peticion("GET", `/libros${query}`);
  },
  obtener: (isbn) => _peticion("GET", `/libros/${encodeURIComponent(isbn)}`),
  registrar: (datos) => _peticion("POST", "/libros", datos),
  actualizar: (isbn, datos) => _peticion("PUT", `/libros/${encodeURIComponent(isbn)}`, datos),
  eliminar: (isbn) => _peticion("DELETE", `/libros/${encodeURIComponent(isbn)}`),
};

const ApiVentas = {
  registrar: (items) => _peticion("POST", "/ventas", { items }),
  listar: () => _peticion("GET", "/ventas"),
  totalVendido: () => _peticion("GET", "/ventas/resumen/total"),
  masVendidos: (limite = 5) => _peticion("GET", `/ventas/resumen/mas-vendidos?limite=${limite}`),
};
