/**
 * Cliente Frontend para Clínica Odontológica Sonrisa Sana.
 * Gestiona autenticación JWT, reserva online, panel de secretaría, ficha clínica y dashboard.
 */

let TOKEN = localStorage.getItem('ss_token') || null;
let CURRENT_USER = JSON.parse(localStorage.getItem('ss_user') || 'null');
let CATALOG = { especialidades: [], tipos_atencion: [], odontologos: [] };
let SELECTED_SLOT = null;
let CHART_INSTANCE = null;

/**
 * Ejecuta una petición fetch autenticada contra la API REST y maneja errores JSON.
 * @param {string} url - Ruta del endpoint.
 * @param {object} options - Opciones fetch.
 * @returns {Promise<any>} Respuesta JSON parseada.
 */
async function apiFetch(url, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (TOKEN) headers['Authorization'] = `Bearer ${TOKEN}`;
  const res = await fetch(url, { ...options, headers });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    if (res.status === 401) logout();
    throw new Error(data.detail || 'Error en la operación.');
  }
  return data;
}

/**
 * Cambia entre las pestañas de Inicio de Sesión y Registro de Paciente.
 * @param {string} tab - 'login' o 'register'.
 */
function switchAuthTab(tab) {
  document.getElementById('login-form').classList.toggle('hidden', tab !== 'login');
  document.getElementById('register-form').classList.toggle('hidden', tab !== 'register');
  document.getElementById('tab-login').className = tab === 'login'
    ? 'pb-2 text-sm font-semibold border-b-2 border-[#0F4C81] text-[#0F4C81]'
    : 'pb-2 text-sm font-semibold text-slate-500';
  document.getElementById('tab-register').className = tab === 'register'
    ? 'pb-2 text-sm font-semibold border-b-2 border-[#0F4C81] text-[#0F4C81]'
    : 'pb-2 text-sm font-semibold text-slate-500';
}

/**
 * Inicia sesión rápida con uno de los usuarios de demostración.
 * @param {string} email - Correo del usuario demo.
 */
async function demoLogin(email) {
  document.getElementById('login-email').value = email;
  document.getElementById('login-pass').value = 'Sonrisa2026!';
  await performLogin(email, 'Sonrisa2026!');
}

/**
 * Maneja el envío del formulario de inicio de sesión.
 * @param {Event} e - Evento submit.
 */
async function handleLogin(e) {
  e.preventDefault();
  await performLogin(document.getElementById('login-email').value, document.getElementById('login-pass').value);
}

/**
 * Envía credenciales al backend y almacena el token JWT y perfil de usuario.
 * @param {string} correo - Correo del usuario.
 * @param {string} password - Contraseña.
 */
async function performLogin(correo, password) {
  try {
    const res = await apiFetch('/api/auth/login', { method: 'POST', body: JSON.stringify({ correo, password }) });
    TOKEN = res.access_token;
    CURRENT_USER = res.user;
    localStorage.setItem('ss_token', TOKEN);
    localStorage.setItem('ss_user', JSON.stringify(CURRENT_USER));
    await initAppView();
  } catch (err) {
    Swal.fire('Error de acceso', err.message, 'error');
  }
}

/**
 * Registra una nueva cuenta de paciente online.
 * @param {Event} e - Evento submit.
 */
async function handleRegister(e) {
  e.preventDefault();
  try {
    const payload = {
      rut: document.getElementById('reg-rut').value,
      fecha_nacimiento: document.getElementById('reg-nac').value,
      nombre: document.getElementById('reg-nom').value,
      apellido: document.getElementById('reg-ape').value,
      telefono: document.getElementById('reg-tel').value,
      prevision: document.getElementById('reg-prev').value,
      correo: document.getElementById('reg-email').value,
      password: document.getElementById('reg-pass').value,
      consentimiento_datos: document.getElementById('reg-consent').checked,
    };
    const res = await apiFetch('/api/auth/register', { method: 'POST', body: JSON.stringify(payload) });
    TOKEN = res.access_token;
    CURRENT_USER = res.user;
    localStorage.setItem('ss_token', TOKEN);
    localStorage.setItem('ss_user', JSON.stringify(CURRENT_USER));
    Swal.fire('¡Bienvenido!', 'Cuenta creada correctamente.', 'success');
    await initAppView();
  } catch (err) {
    Swal.fire('No se pudo registrar', err.message, 'error');
  }
}

/**
 * Cierra la sesión actual y vuelve a la pantalla de acceso.
 */
function logout() {
  TOKEN = null;
  CURRENT_USER = null;
  localStorage.removeItem('ss_token');
  localStorage.removeItem('ss_user');
  document.getElementById('auth-view').classList.remove('hidden');
  document.getElementById('app-view').classList.add('hidden');
  document.getElementById('user-badge').classList.add('hidden');
}

/**
 * Inicializa la interfaz principal según el rol del usuario autenticado.
 */
async function initAppView() {
  if (!CURRENT_USER) return;
  document.getElementById('auth-view').classList.add('hidden');
  document.getElementById('app-view').classList.remove('hidden');
  document.getElementById('user-badge').classList.remove('hidden');
  document.getElementById('user-badge').classList.add('flex');
  document.getElementById('nav-user-name').textContent = CURRENT_USER.nombre;
  document.getElementById('nav-user-role').textContent = CURRENT_USER.rol;

  CATALOG = await apiFetch('/api/catalogo');
  populateBookingCatalog();

  const tabs = [];
  if (['Paciente', 'Secretaria', 'Administrador'].includes(CURRENT_USER.rol)) {
    tabs.push({ id: 'reservar', label: 'Reservar Hora' });
  }
  tabs.push({ id: 'agenda', label: 'Agenda de Citas' });
  if (CURRENT_USER.rol === 'Odontologo') {
    tabs.push({ id: 'ficha', label: 'Ficha Clínica (AES-256)' });
  }
  if (['Secretaria', 'Administrador'].includes(CURRENT_USER.rol)) {
    tabs.push({ id: 'admin', label: 'Recordatorios & Auditoría' });
  }

  const tabBox = document.getElementById('role-tabs');
  tabBox.innerHTML = tabs.map(t =>
    `<button onclick="showPanel('${t.id}')" id="tab-btn-${t.id}" class="px-4 py-2 rounded-xl text-sm font-semibold transition">${t.label}</button>`
  ).join('');

  document.getElementById('btn-new-pac').classList.toggle('hidden', !['Secretaria', 'Administrador'].includes(CURRENT_USER.rol));
  document.getElementById('sec-pac-select-wrap').classList.toggle('hidden', CURRENT_USER.rol === 'Paciente');

  if (['Secretaria', 'Administrador', 'Odontologo'].includes(CURRENT_USER.rol)) {
    await loadPatientsSelectors();
  }

  const defaultTab = CURRENT_USER.rol === 'Odontologo' ? 'agenda' : tabs[0].id;
  showPanel(defaultTab);
  lucide.createIcons();
}

/**
 * Muestra el panel seleccionado y carga sus datos actualizados.
 * @param {string} panelId - Identificador del panel ('reservar', 'agenda', 'ficha', 'admin').
 */
async function showPanel(panelId) {
  ['reservar', 'agenda', 'ficha', 'admin'].forEach(p => {
    document.getElementById(`panel-${p}`).classList.toggle('hidden', p !== panelId);
    const btn = document.getElementById(`tab-btn-${p}`);
    if (btn) {
      btn.className = p === panelId
        ? 'px-4 py-2 rounded-xl text-sm font-semibold bg-[#0F4C81] text-white shadow'
        : 'px-4 py-2 rounded-xl text-sm font-semibold text-slate-600 hover:bg-slate-100';
    }
  });
  if (panelId === 'reservar') await loadSlots();
  if (panelId === 'agenda') await loadAgenda();
  if (panelId === 'ficha') await loadClinicalRecord();
  if (panelId === 'admin') await loadAdminDashboard();
}

/**
 * Carga especialidades, tipos de atención y odontólogos en el formulario de reserva.
 */
function populateBookingCatalog() {
  const espSel = document.getElementById('res-esp');
  espSel.innerHTML = CATALOG.especialidades.map(e => `<option value="${e.id_especialidad}">${e.nombre}</option>`).join('');
  document.getElementById('res-fecha').value = new Date().toISOString().split('T')[0];
  filterDoctorsAndTypes();
}

/**
 * Filtra odontólogos y tipos de atención según la especialidad elegida.
 */
function filterDoctorsAndTypes() {
  const idEsp = Number(document.getElementById('res-esp').value);
  const tipos = CATALOG.tipos_atencion.filter(t => t.id_especialidad === idEsp);
  const ods = CATALOG.odontologos.filter(o => o.id_especialidad === idEsp);
  document.getElementById('res-tipo').innerHTML = tipos.map(t => `<option value="${t.id_tipo_atencion}">${t.nombre} (${t.duracion_min} min)</option>`).join('');
  document.getElementById('res-od').innerHTML = (ods.length ? ods : CATALOG.odontologos)
    .map(o => `<option value="${o.id_odontologo}">${o.nombre_completo} (${o.box_asignado})</option>`).join('');
  loadSlots();
}

/**
 * Consulta la disponibilidad horaria del odontólogo para la fecha seleccionada.
 */
async function loadSlots() {
  const idOd = document.getElementById('res-od').value;
  const fecha = document.getElementById('res-fecha').value;
  if (!idOd || !fecha) return;
  SELECTED_SLOT = null;
  const data = await apiFetch(`/api/disponibilidad?id_odontologo=${idOd}&fecha=${fecha}`);
  const grid = document.getElementById('slots-grid');
  if (!data.bloques.length) {
    grid.innerHTML = '<p class="col-span-full text-sm text-slate-500">No hay jornada configurada para este día (ej. domingo).</p>';
    return;
  }
  grid.innerHTML = data.bloques.map(b => {
    if (!b.disponible) {
      return `<button disabled class="py-2.5 px-2 rounded-xl text-xs font-semibold bg-slate-100 text-slate-400 line-through cursor-not-allowed">${b.hora_inicio}</button>`;
    }
    return `<button onclick="selectSlot('${b.hora_inicio}', this)" class="slot-btn py-2.5 px-2 rounded-xl text-xs font-semibold border border-[#0F4C81] text-[#0F4C81] hover:bg-sky-50 transition">${b.hora_inicio}</button>`;
  }).join('');
}

/**
 * Marca visualmente el bloque horario seleccionado por el usuario.
 * @param {string} hora - Hora de inicio HH:MM.
 * @param {HTMLElement} btn - Botón pulsado.
 */
function selectSlot(hora, btn) {
  SELECTED_SLOT = hora;
  document.querySelectorAll('.slot-btn').forEach(el => {
    el.className = 'slot-btn py-2.5 px-2 rounded-xl text-xs font-semibold border border-[#0F4C81] text-[#0F4C81] hover:bg-sky-50 transition';
  });
  btn.className = 'slot-btn py-2.5 px-2 rounded-xl text-xs font-semibold bg-[#00897B] text-white shadow';
}

/**
 * Envía la reserva de cita al servidor y actualiza los bloques disponibles.
 */
async function confirmBooking() {
  if (!SELECTED_SLOT) return Swal.fire('Falta horario', 'Selecciona un bloque disponible.', 'warning');
  try {
    const body = {
      id_odontologo: Number(document.getElementById('res-od').value),
      id_tipo_atencion: Number(document.getElementById('res-tipo').value),
      fecha: document.getElementById('res-fecha').value,
      hora_inicio: SELECTED_SLOT,
      origen: CURRENT_USER.rol === 'Paciente' ? 'online' : 'presencial',
    };
    if (CURRENT_USER.rol !== 'Paciente') {
      body.id_paciente = Number(document.getElementById('res-paciente').value);
    }
    await apiFetch('/api/citas', { method: 'POST', body: JSON.stringify(body) });
    Swal.fire('¡Hora Reservada!', `Cita confirmada para el ${body.fecha} a las ${body.hora_inicio}.`, 'success');
    await loadSlots();
  } catch (err) {
    Swal.fire('No se pudo reservar', err.message, 'error');
  }
}

/**
 * Carga la lista de citas según filtros y renderiza botones rápidos por rol.
 */
async function loadAgenda() {
  const fecha = document.getElementById('flt-fecha').value;
  const q = fecha ? `?fecha=${fecha}` : '';
  const citas = await apiFetch(`/api/citas${q}`);
  const badgeMap = {
    pendiente: 'bg-amber-100 text-amber-800',
    confirmada: 'bg-emerald-100 text-emerald-800',
    atendida: 'bg-sky-100 text-sky-800',
    cancelada: 'bg-rose-100 text-rose-800',
    reprogramada: 'bg-purple-100 text-purple-800',
  };
  const tbody = document.getElementById('agenda-tbody');
  tbody.innerHTML = citas.map(c => {
    const canEdit = ['Secretaria', 'Administrador'].includes(CURRENT_USER.rol) && !['cancelada', 'atendida'].includes(c.estado);
    const canCancel = (canEdit || (CURRENT_USER.rol === 'Paciente' && c.estado === 'pendiente'));
    return `
      <tr class="hover:bg-slate-50">
        <td class="px-4 py-3 font-medium">${c.fecha} <span class="text-[#0F4C81] font-bold">${c.hora_inicio}</span></td>
        <td class="px-4 py-3">${c.paciente_nombre}<br><span class="text-xs text-slate-400">${c.paciente_rut}</span></td>
        <td class="px-4 py-3">${c.odontologo_nombre}<br><span class="text-xs text-slate-400">${c.box_asignado}</span></td>
        <td class="px-4 py-3">${c.tipo_atencion}</td>
        <td class="px-4 py-3"><span class="px-2.5 py-1 rounded-full text-xs font-semibold ${badgeMap[c.estado] || ''}">${c.estado}</span></td>
        <td class="px-4 py-3 text-right space-x-1">
          ${canEdit ? `<button onclick="openRescheduleModal(${c.id_cita}, '${c.fecha}', '${c.hora_inicio}')" class="px-2.5 py-1 bg-sky-600 hover:bg-sky-700 text-white rounded-lg text-xs font-semibold">Reprogramar</button>` : ''}
          ${canCancel ? `<button onclick="openCancelModal(${c.id_cita})" class="px-2.5 py-1 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-semibold">Cancelar</button>` : ''}
        </td>
      </tr>`;
  }).join('');
}

/**
 * Abre modal comercial para reprogramar una cita en <= 2 clics.
 * @param {number} idCita - ID de la cita.
 * @param {string} fechaActual - Fecha actual.
 * @param {string} horaActual - Hora actual.
 */
async function openRescheduleModal(idCita, fechaActual, horaActual) {
  const { value: formValues } = await Swal.fire({
    title: 'Reprogramar Cita',
    html:
      `<input id="sw-fecha" type="date" value="${fechaActual}" class="swal2-input">` +
      `<input id="sw-hora" type="time" value="${horaActual}" class="swal2-input">` +
      `<input id="sw-motivo" type="text" placeholder="Motivo del cambio" value="Solicitud del paciente" class="swal2-input">`,
    focusConfirm: false,
    showCancelButton: true,
    confirmButtonText: 'Guardar Cambio',
    preConfirm: () => ({
      fecha: document.getElementById('sw-fecha').value,
      hora_inicio: document.getElementById('sw-hora').value.slice(0, 5),
      motivo: document.getElementById('sw-motivo').value,
    }),
  });
  if (formValues) {
    try {
      await apiFetch(`/api/citas/${idCita}/reprogramar`, { method: 'PUT', body: JSON.stringify(formValues) });
      Swal.fire('Actualizada', 'La cita fue reprogramada sin choques.', 'success');
      await loadAgenda();
    } catch (err) {
      Swal.fire('Error', err.message, 'error');
    }
  }
}

/**
 * Abre modal para cancelar una cita y liberar su bloque horario.
 * @param {number} idCita - ID de la cita.
 */
async function openCancelModal(idCita) {
  const { value: motivo } = await Swal.fire({
    title: 'Cancelar Cita',
    input: 'text',
    inputLabel: 'Motivo de la cancelación',
    inputValue: 'Paciente solicita anulación',
    showCancelButton: true,
    confirmButtonColor: '#DC2626',
    confirmButtonText: 'Confirmar Cancelación',
  });
  if (motivo) {
    try {
      await apiFetch(`/api/citas/${idCita}/cancelar`, { method: 'PUT', body: JSON.stringify({ motivo }) });
      Swal.fire('Cancelada', 'El bloque horario quedó disponible nuevamente.', 'success');
      await loadAgenda();
    } catch (err) {
      Swal.fire('Error', err.message, 'error');
    }
  }
}

/**
 * Pobla los selectores de pacientes para secretaría y odontólogo.
 */
async function loadPatientsSelectors() {
  const pacs = await apiFetch('/api/pacientes');
  const opts = pacs.map(p => `<option value="${p.id_paciente}">${p.nombre} ${p.apellido} (${p.rut})</option>`).join('');
  document.getElementById('res-paciente').innerHTML = opts;
  document.getElementById('ficha-pac-select').innerHTML = opts;
}

/**
 * Abre modal para dar de alta un nuevo paciente desde secretaría.
 */
async function openNewPatientModal() {
  const { value: data } = await Swal.fire({
    title: 'Registrar Nuevo Paciente',
    html:
      '<input id="np-rut" class="swal2-input" placeholder="RUT (ej. 17654321-0)">' +
      '<input id="np-nom" class="swal2-input" placeholder="Nombre">' +
      '<input id="np-ape" class="swal2-input" placeholder="Apellido">' +
      '<input id="np-nac" type="date" class="swal2-input" value="1992-01-01">' +
      '<input id="np-tel" class="swal2-input" placeholder="Teléfono">' +
      '<input id="np-cor" type="email" class="swal2-input" placeholder="Correo">',
    showCancelButton: true,
    confirmButtonText: 'Guardar Paciente',
    preConfirm: () => ({
      rut: document.getElementById('np-rut').value,
      nombre: document.getElementById('np-nom').value,
      apellido: document.getElementById('np-ape').value,
      fecha_nacimiento: document.getElementById('np-nac').value,
      telefono: document.getElementById('np-tel').value,
      correo: document.getElementById('np-cor').value,
    }),
  });
  if (data) {
    try {
      await apiFetch('/api/pacientes', { method: 'POST', body: JSON.stringify(data) });
      Swal.fire('Registrado', 'Paciente guardado correctamente.', 'success');
      await loadPatientsSelectors();
    } catch (err) {
      Swal.fire('Error', err.message, 'error');
    }
  }
}

/**
 * Carga y descifra la ficha clínica del paciente seleccionado (solo Odontólogo).
 */
async function loadClinicalRecord() {
  const idPac = document.getElementById('ficha-pac-select').value;
  if (!idPac) return;
  const data = await apiFetch(`/api/fichas/${idPac}`);
  document.getElementById('ficha-resumen').innerHTML = `
    <p><strong>Paciente:</strong> ${data.paciente.nombre} ${data.paciente.apellido} (${data.paciente.rut})</p>
    <p><strong>Previsión:</strong> ${data.paciente.prevision} | <strong>Grupo:</strong> ${data.grupo_sanguineo || 'N/D'}</p>
    <p><strong>Antecedentes (AES-256):</strong> ${data.antecedentes_medicos || 'Sin registros'}</p>
    <p><strong>Alergias (AES-256):</strong> <span class="text-rose-700 font-bold">${data.alergias || 'Ninguna'}</span></p>
  `;
  document.getElementById('ficha-evoluciones').innerHTML = data.evoluciones.length
    ? data.evoluciones.map(ev => `
        <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-1">
          <div class="flex justify-between font-bold text-[#0F4C81]"><span>${ev.fecha_atencion}</span><span>Pieza: ${ev.pieza_dental || 'General'}</span></div>
          <p><strong>Diagnóstico:</strong> ${ev.diagnostico}</p>
          <p><strong>Tratamiento:</strong> ${ev.tratamiento_realizado}</p>
          <p class="text-slate-500">Odontólogo: ${ev.odontologo}</p>
        </div>`).join('')
    : '<p class="text-xs text-slate-500">Sin evoluciones registradas aún.</p>';
}

/**
 * Registra una nueva evolución clínica cifrada con AES-256.
 * @param {Event} e - Evento submit.
 */
async function saveEvolution(e) {
  e.preventDefault();
  const idPac = document.getElementById('ficha-pac-select').value;
  const citaVal = document.getElementById('ev-cita').value;
  const alergiasVal = document.getElementById('ev-alergias').value;
  try {
    await apiFetch(`/api/fichas/${idPac}/evolucion`, {
      method: 'POST',
      body: JSON.stringify({
        id_cita: citaVal ? Number(citaVal) : null,
        pieza_dental: document.getElementById('ev-pieza').value || null,
        alergias: alergiasVal || null,
        diagnostico: document.getElementById('ev-diag').value,
        tratamiento_realizado: document.getElementById('ev-trat').value,
        indicaciones: document.getElementById('ev-ind').value || null,
      }),
    });
    Swal.fire('Guardado Seguro', 'Evolución clínica cifrada (AES-256) y almacenada.', 'success');
    e.target.reset();
    await loadClinicalRecord();
  } catch (err) {
    Swal.fire('Error', err.message, 'error');
  }
}

/**
 * Carga métricas de citas, cola de recordatorios y auditoría de seguridad.
 */
async function loadAdminDashboard() {
  const [dash, rems] = await Promise.all([apiFetch('/api/admin/dashboard'), apiFetch('/api/recordatorios')]);
  const ctx = document.getElementById('chart-estados').getContext('2d');
  if (CHART_INSTANCE) CHART_INSTANCE.destroy();
  CHART_INSTANCE = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: dash.resumen_estados.map(x => x.estado),
      datasets: [{ data: dash.resumen_estados.map(x => x.cantidad), backgroundColor: ['#F59E0B', '#10B981', '#0F4C81', '#EF4444', '#8B5CF6'] }],
    },
  });

  document.getElementById('rem-tbody').innerHTML = rems.map(r => `
    <tr>
      <td class="px-3 py-2">${r.paciente}</td>
      <td class="px-3 py-2">${r.fecha} ${r.hora_inicio}</td>
      <td class="px-3 py-2">${r.fecha_programada}</td>
      <td class="px-3 py-2 font-semibold">${r.estado}</td>
    </tr>`).join('');

  document.getElementById('audit-tbody').innerHTML = dash.auditoria.map(a => `
    <tr>
      <td class="px-3 py-2">${a.fecha_hora}</td>
      <td class="px-3 py-2">${a.usuario || 'Sistema'}</td>
      <td class="px-3 py-2 font-bold">${a.accion}</td>
      <td class="px-3 py-2">${a.entidad_afectada}</td>
      <td class="px-3 py-2">${a.detalle || ''}</td>
    </tr>`).join('');
}

/**
 * Ejecuta manualmente el envío/procesamiento de recordatorios pendientes.
 */
async function runReminders() {
  const res = await apiFetch('/api/recordatorios/procesar', { method: 'POST' });
  Swal.fire('Recordatorios Procesados', `Enviados: ${res.enviados} | Omitidos: ${res.omitidos}`, 'success');
  await loadAdminDashboard();
}

window.addEventListener('DOMContentLoaded', () => {
  lucide.createIcons();
  if (TOKEN && CURRENT_USER) initAppView();
});
