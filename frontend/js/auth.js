function getHomePath() {
  return window.location.pathname.includes("/pages/") ? "../index.html" : "index.html";
}

async function verificarAcceso({ rolRequerido = null } = {}) {
  try {
    const respuesta = await ApiAuth.me();
    const user = respuesta.user;
    if (!user) {
      window.location.href = getHomePath();
      return null;
    }
    if (rolRequerido && user.role !== rolRequerido) {
      window.location.href = getHomePath();
      return null;
    }
    return user;
  } catch (error) {
    window.location.href = getHomePath();
    return null;
  }
}
