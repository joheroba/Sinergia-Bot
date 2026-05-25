import './style.css'
import { Contacts } from '@capacitor-community/contacts';
import { Browser } from '@capacitor/browser';

document.querySelector('#app').innerHTML = `
  <!-- Background Glows -->
  <div class="glow-orb glow-orb-1"></div>
  <div class="glow-orb glow-orb-2"></div>

  <!-- Header -->
  <header class="app-header">
    <div class="app-title">Sinergia Pro</div>
    <div id="status-badge" class="status-badge offline" style="display: none;">
      <i data-lucide="wifi-off"></i> Desconectado
    </div>
  </header>

  <!-- Login / Register Screen -->
  <div id="screen-login" class="screen active">
    <div class="glass-card" style="margin-top: 2rem;">
      <h2 style="margin-bottom: 0.5rem;" id="auth-title">Acceso Afiliado</h2>
      <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 2rem;" id="auth-subtitle">
        Ingresa tu código Sinergia Bot o tu WhatsApp para sincronizar.
      </p>

      <div id="login-form">
        <div class="input-group">
          <label>Token / Teléfono</label>
          <input type="text" id="login-token" class="input-field" placeholder="+51 999 888 777" />
        </div>
        <button id="btn-login" class="btn-primary" style="margin-top: 1.5rem;">
          <span class="btn-text">Sincronizar App</span>
          <div class="loader"></div>
        </button>
        <p style="text-align: center; margin-top: 1rem; color: var(--gold-light); font-size: 0.9rem; cursor: pointer;" id="toggle-register">
          ¿No tienes cuenta? Regístrate aquí
        </p>
      </div>

      <div id="register-form" style="display: none;">
        <div class="input-group">
          <label>Nombre Completo</label>
          <input type="text" id="reg-name" class="input-field" placeholder="Ej. Juan Pérez" />
        </div>
        <div class="input-group" style="margin-top: 1rem;">
          <label>WhatsApp (con código de país)</label>
          <input type="text" id="reg-phone" class="input-field" placeholder="Ej. 51999888777" />
        </div>
        <div class="input-group" style="margin-top: 1rem;">
          <label>Enlace Gano iTouch (Opcional)</label>
          <input type="text" id="reg-link" class="input-field" placeholder="https://peru.ganoitouch.biz/..." />
        </div>
        <button id="btn-register" class="btn-primary" style="margin-top: 1.5rem; background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
          <span class="btn-text">Crear Cuenta PRO</span>
          <div class="loader"></div>
        </button>
        <p style="text-align: center; margin-top: 1rem; color: var(--text-muted); font-size: 0.8rem;">
          Inscripción S/ 30 (incluye mes 1), luego S/ 10 mensual. O plan anual S/ 100 (ahorras inscripción y 2 meses).<br>Contacta al Admin para validar tu pago después de registrarte.
        </p>
        <p style="text-align: center; margin-top: 1rem; color: var(--gold-light); font-size: 0.9rem; cursor: pointer;" id="toggle-login">
          Ya tengo cuenta. Iniciar Sesión
        </p>
      </div>
    </div>
  </div>

  <!-- Dashboard Screen -->
  <div id="screen-dashboard" class="screen">
    <div class="glass-card">
      <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <div>
          <h3 style="color: var(--gold-light);">Hola, Líder</h3>
          <p id="user-name" style="font-weight: 700; font-size: 1.2rem;">Cargando...</p>
        </div>
        <div style="background: rgba(212,175,55,0.1); padding: 0.5rem; border-radius: 50%; cursor: pointer;" id="btn-open-settings">
          <i data-lucide="settings" style="color: var(--gold-primary);"></i>
        </div>
      </div>
      <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--glass-border); display: flex; align-items: center; gap: 0.5rem;">
        <i data-lucide="facebook" style="color: #1877F2; width: 20px;"></i>
        <span style="font-size: 0.9rem; color: var(--text-muted);">Página Enlazada:</span>
        <span id="page-name" style="font-size: 0.9rem; font-weight: 600; color: #4ade80;">No vinculada</span>
      </div>
    </div>

    <h3 style="margin-top: 1.5rem; margin-bottom: 1rem; font-size: 1.1rem;">Acciones Rápidas</h3>
    
    <button id="btn-reclutar" class="btn-primary" style="margin-bottom: 1rem; padding: 1.2rem;">
      <i data-lucide="rocket"></i>
      <span class="btn-text">¡Reclutar por mí! (Auto-Post)</span>
      <div class="loader"></div>
    </button>

    <div class="feature-grid">
      <div class="feature-btn" id="btn-afiliar" style="background: rgba(236, 72, 153, 0.1); border: 1px solid rgba(236, 72, 153, 0.3);">
        <i data-lucide="user-plus" style="color: #ec4899;"></i>
        <span>Afiliar / Backoffice</span>
      </div>
      <div class="feature-btn" id="btn-simulador">
        <i data-lucide="calculator"></i>
        <span>Simulador Servilleta</span>
      </div>
      <div class="feature-btn" id="btn-cola">
        <i data-lucide="list"></i>
        <span>Cola de Posts</span>
      </div>
      <div class="feature-btn" id="btn-analitica" style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3);">
        <i data-lucide="bar-chart-2" style="color: #10b981;"></i>
        <span>Analítica & Metas</span>
      </div>
      <div class="feature-btn" id="btn-cobros" style="background: rgba(212, 175, 55, 0.1); border: 1px solid rgba(212, 175, 55, 0.3);">
        <i data-lucide="wallet" style="color: var(--gold-primary);"></i>
        <span>Mis Cobros & QRs</span>
      </div>
      <div class="feature-btn" id="btn-prospectar" style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3);">
        <i data-lucide="users" style="color: #3b82f6;"></i>
        <span>Cruzar Datos y Prospectar</span>
      </div>
    </div>
  </div>

  <!-- Analytics Modal (Hidden by default) -->
  <div id="modal-analitica" class="screen" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.8); z-index: 1000; overflow-y: auto;">
    <div class="glass-card" style="margin: 2rem 1rem; position: relative;">
      <div id="btn-close-analitica" style="position: absolute; right: 1rem; top: 1rem; cursor: pointer; color: var(--text-muted); z-index: 50; padding: 0.5rem;"><i data-lucide="x"></i></div>
      <h3 style="color: #10b981; margin-bottom: 1rem;">Análisis de Fin de Ciclo</h3>
      
      <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1.5rem;">
        Sincroniza tu Backoffice Oficial para que la IA extraiga tus puntos (PV/CV) y genere tu Agenda Diaria de prospección y recompra.
      </p>

      <div class="input-group">
        <label>Código Distribuidor Gano iTouch</label>
        <input type="text" id="kpi-codigo" class="input-field" placeholder="Ej. 4408926" />
      </div>
      <div class="input-group" style="margin-top: 1rem;">
        <label>Contraseña Backoffice</label>
        <input type="password" id="kpi-clave" class="input-field" placeholder="****" />
      </div>
      
      <button id="btn-analyze-kpi" class="btn-primary" style="margin-top: 1.5rem; background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
        <i data-lucide="cpu"></i>
        <span class="btn-text">Generar Agenda Estratégica</span>
        <div class="loader"></div>
      </button>

      <div style="margin-top: 1.5rem; text-align: center; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 1rem;">
        <p style="color: var(--text-muted); font-size: 0.8rem; margin-bottom: 0.5rem;">Opcional: Sube captura de pantalla si no quieres ingresar tu clave.</p>
        <input type="file" id="file-kpi" accept="image/*" style="display: none;" />
        <button id="btn-upload-kpi" class="btn-primary" style="background: rgba(255,255,255,0.1); border: 1px dashed var(--glass-border); color: #fff; padding: 0.5rem;">
          <i data-lucide="upload-cloud"></i>
          <span class="btn-text">Subir Captura</span>
        </button>
      </div>

      <div id="kpi-preview-container" style="display: none; margin-top: 1rem; text-align: center;">
        <img id="kpi-preview" src="" style="max-width: 100%; border-radius: 8px; border: 1px solid var(--glass-border);" />
        <button id="btn-analyze-kpi-img" class="btn-primary" style="margin-top: 1rem; background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
          <i data-lucide="image"></i>
          <span class="btn-text">Analizar desde Imagen</span>
          <div class="loader"></div>
        </button>
      </div>

      <div id="kpi-result" style="margin-top: 1.5rem; padding: 1rem; background: rgba(0,0,0,0.3); border-radius: 8px; font-size: 0.9rem; white-space: pre-wrap; display: none; border: 1px solid var(--gold-primary);">
      </div>
    </div>
  </div>

  <!-- Settings Modal (Hidden by default) -->
  <div id="modal-settings" class="screen" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.8); z-index: 1000; overflow-y: auto;">
    <div class="glass-card" style="margin: 2rem 1rem; position: relative;">
      <div id="btn-close-settings" style="position: absolute; right: 1rem; top: 1rem; cursor: pointer; color: var(--text-muted); z-index: 50; padding: 0.5rem;"><i data-lucide="x"></i></div>
      <h3 style="color: var(--gold-light); margin-bottom: 1rem;">Configuración de Redes</h3>
      
      <div class="input-group">
        <label>Idioma de la IA</label>
        <select id="cfg-idioma" class="input-field" style="background: rgba(0,0,0,0.2);">
          <option value="Español">Español</option>
          <option value="Inglés">Inglés</option>
          <option value="Portugués">Portugués</option>
        </select>
      </div>
      <div class="input-group" style="margin-top: 1rem;">
        <label>Zona Geográfica / Mercado</label>
        <input type="text" id="cfg-zona" class="input-field" placeholder="Ej. Perú, Estados Unidos, etc." />
      </div>
      <div class="input-group" style="margin-top: 1rem;">
        <label>Enlace Oficial Gano iTouch</label>
        <input type="text" id="cfg-link" class="input-field" placeholder="https://..." />
      </div>
      <div class="input-group" style="margin-top: 1rem;">
        <label>Token de Acceso de Facebook (Larga Duración)</label>
        <input type="text" id="cfg-fb-token" class="input-field" placeholder="EAAB..." />
      </div>
      <div class="input-group" style="margin-top: 1rem;">
        <label>ID de la FanPage</label>
        <input type="text" id="cfg-fb-page" class="input-field" placeholder="10008..." />
      </div>

      <button id="btn-save-settings" class="btn-primary" style="margin-top: 1.5rem;">
        <span class="btn-text">Guardar Cambios</span>
        <div class="loader"></div>
      </button>
    </div>
  </div>

  <!-- Cobros & QRs Modal (Hidden by default) -->
  <div id="modal-cobros" class="screen" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.8); z-index: 1000; overflow-y: auto;">
    <div class="glass-card" style="margin: 2rem 1rem; position: relative;">
      <div id="btn-close-cobros" style="position: absolute; right: 1rem; top: 1rem; cursor: pointer; color: var(--text-muted); z-index: 50; padding: 0.5rem;"><i data-lucide="x"></i></div>
      <h3 style="color: var(--gold-light); margin-bottom: 1rem;">Mis Cobros y QRs</h3>
      <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1.5rem;">Sube tus códigos QR y cuentas bancarias para que el Bot cierre ventas a tu nombre.</p>
      
      <div class="input-group">
        <label>Cuenta BCP Soles</label>
        <input type="text" id="cobro-bcp" class="input-field" placeholder="193-00000000-0-00" />
      </div>
      <div class="input-group" style="margin-top: 1rem;">
        <label>Cuenta Interbank Soles</label>
        <input type="text" id="cobro-interbank" class="input-field" placeholder="200-3000000000" />
      </div>
      <div class="input-group" style="margin-top: 1rem;">
        <label>Tipo de Cambio Referencial (S/.)</label>
        <input type="number" step="0.01" id="cobro-tc" class="input-field" placeholder="3.85" value="3.85" />
      </div>
      
      <div style="margin-top: 1.5rem; display: flex; gap: 1rem;">
        <div style="flex: 1; text-align: center;">
          <p style="color: #6C22A6; font-size: 0.9rem; margin-bottom: 0.5rem; font-weight: bold;">Yape QR</p>
          <img id="preview-yape" src="https://via.placeholder.com/150?text=Sube+Yape" style="width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 8px; border: 1px dashed #6C22A6; cursor: pointer;" />
          <input type="file" id="file-yape" accept="image/*" style="display: none;" />
        </div>
        <div style="flex: 1; text-align: center;">
          <p style="color: #00D3FF; font-size: 0.9rem; margin-bottom: 0.5rem; font-weight: bold;">Plin QR</p>
          <img id="preview-plin" src="https://via.placeholder.com/150?text=Sube+Plin" style="width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 8px; border: 1px dashed #00D3FF; cursor: pointer;" />
          <input type="file" id="file-plin" accept="image/*" style="display: none;" />
        </div>
      </div>

      <button id="btn-save-cobros" class="btn-primary" style="margin-top: 1.5rem; background: linear-gradient(135deg, var(--gold-dark) 0%, var(--gold-primary) 100%);">
        <i data-lucide="save"></i>
        <span class="btn-text">Guardar Billetera</span>
        <div class="loader"></div>
      </button>
    </div>
  </div>
  <!-- Prospectar Modal (Hidden by default) -->
  <div id="modal-prospectar" class="screen" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.8); z-index: 1000; overflow-y: auto;">
    <div class="glass-card" style="margin: 2rem 1rem; position: relative;">
      <div id="btn-close-prospectar" style="position: absolute; right: 1rem; top: 1rem; cursor: pointer; color: var(--text-muted); z-index: 50; padding: 0.5rem;"><i data-lucide="x"></i></div>
      <h3 style="color: var(--gold-light); margin-bottom: 1rem;">Cruzar Datos y Prospectar</h3>
      <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1.5rem;">Ingresa tus credenciales de Gano iTouch para cruzar tu red con tu agenda telefónica y encontrar inactivos.</p>
      
      <div class="input-group">
        <label>Usuario (Backoffice)</label>
        <input type="text" id="prospectar-user" class="input-field" placeholder="1234567" />
      </div>
      <div class="input-group" style="margin-top: 1rem;">
        <label>Contraseña</label>
        <input type="password" id="prospectar-pass" class="input-field" placeholder="********" />
      </div>
      
      <button id="btn-iniciar-cruce" class="btn-primary" style="margin-top: 1.5rem; background: linear-gradient(135deg, var(--gold-dark) 0%, var(--gold-primary) 100%);">
        <i data-lucide="users"></i>
        <span class="btn-text">Iniciar Cruce de IA</span>
        <div class="loader"></div>
      </button>
      
      <div id="prospect-result" style="display:none; margin-top: 1rem; padding: 1rem; background: rgba(0,0,0,0.5); border-radius: 8px; color: var(--gold-light); font-size: 0.9rem; white-space: pre-wrap;"></div>
    </div>
  </div>

  <!-- Toast Notification -->
  <div id="toast" class="toast">
    <i data-lucide="check-circle"></i>
    <span id="toast-msg">Mensaje</span>
  </div>
`

// Initialize Icons
lucide.createIcons();

// Elements
const screenLogin = document.getElementById('screen-login');
const screenDashboard = document.getElementById('screen-dashboard');
const btnLogin = document.getElementById('btn-login');
const btnRegister = document.getElementById('btn-register');
const btnReclutar = document.getElementById('btn-reclutar');
const statusBadge = document.getElementById('status-badge');
const toast = document.getElementById('toast');
const toastMsg = document.getElementById('toast-msg');

// Toggle forms
document.getElementById('btn-close-cobros').addEventListener('click', () => {
  document.getElementById('modal-cobros').style.display = 'none';
});

// Prospectar Modal Logic
document.getElementById('btn-prospectar').addEventListener('click', () => {
  document.getElementById('modal-prospectar').style.display = 'block';
});

document.getElementById('btn-close-prospectar').addEventListener('click', () => {
  document.getElementById('modal-prospectar').style.display = 'none';
});

document.getElementById('btn-iniciar-cruce').addEventListener('click', async () => {
  const username = document.getElementById('prospectar-user').value;
  const password = document.getElementById('prospectar-pass').value;
  const resultDiv = document.getElementById('prospect-result');
  const btn = document.getElementById('btn-iniciar-cruce');

  if (!username || !password) {
    showToast('Ingresa tu código y contraseña');
    return;
  }

  btn.innerHTML = '<i data-lucide="loader-2" class="spin"></i> Cruzando Datos...';
  btn.disabled = true;
  resultDiv.style.display = 'none';

  let phoneContacts = [];
  try {
    const permission = await Contacts.requestPermissions();
    if (permission.contacts === 'granted') {
      const result = await Contacts.getContacts({
        projection: { name: true, phones: true }
      });
      phoneContacts = result.contacts;
    } else {
      showToast('Permiso de contactos denegado. Se usará modo solo-Backoffice.');
    }
  } catch (err) {
    console.log('Contacts API no disponible (probablemente en Web). Se omitirá agenda local.', err);
  }

  try {
    const CHUNK_SIZE = 500;
    const totalContacts = phoneContacts.length;
    const totalChunks = Math.max(1, Math.ceil(totalContacts / CHUNK_SIZE));
    
    let finalReport = '';
    
    for (let i = 0; i < totalChunks; i++) {
      if (totalChunks > 1) {
        btn.innerHTML = `<i data-lucide="loader-2" class="spin"></i> Cruzando Lote ${i + 1}/${totalChunks}...`;
        lucide.createIcons();
      }
      
      const chunk = phoneContacts.slice(i * CHUNK_SIZE, (i + 1) * CHUNK_SIZE);
      const isFinalChunk = (i === totalChunks - 1);
      
      const res = await fetch('http://45.55.92.211:3005/api/cruzar_prospectos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username,
          password,
          phone_contacts: chunk,
          is_final_chunk: isFinalChunk,
          chunk_index: i + 1,
          total_contacts: totalContacts
        })
      });

      const data = await res.json();
      
      if (data.status === 'success') {
        finalReport = data.report.replace(/\n/g, '<br>');
      } else if (data.status === 'partial') {
        console.log(data.message);
      } else {
        throw new Error(data.message || 'Error desconocido del servidor');
      }
    }
    
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = finalReport;
    showToast('Cruce exitoso!');
    
  } catch (error) {
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = 'Error al cruzar datos: ' + (error.message || 'Fallo de conexión');
  } finally {
    btn.innerHTML = '<i data-lucide="refresh-cw"></i> Iniciar Escaneo y Cruce';
    btn.disabled = false;
    lucide.createIcons();
  }
});

document.getElementById('toggle-register').addEventListener('click', () => {
  document.getElementById('login-form').style.display = 'none';
  document.getElementById('register-form').style.display = 'block';
  document.getElementById('auth-title').textContent = 'Crear Cuenta';
  document.getElementById('auth-subtitle').textContent = 'Únete al ecosistema Sinergia Pro';
});
document.getElementById('toggle-login').addEventListener('click', () => {
  document.getElementById('register-form').style.display = 'none';
  document.getElementById('login-form').style.display = 'block';
  document.getElementById('auth-title').textContent = 'Acceso Afiliado';
  document.getElementById('auth-subtitle').textContent = 'Ingresa tu código Sinergia Bot o tu WhatsApp para sincronizar.';
});

// Settings Modal
const modalSettings = document.getElementById('modal-settings');
document.getElementById('btn-open-settings').addEventListener('click', () => {
  modalSettings.style.display = 'block';
});
document.getElementById('btn-close-settings').addEventListener('click', () => {
  modalSettings.style.display = 'none';
});

// Analytics Modal
const modalAnalitica = document.getElementById('modal-analitica');
document.getElementById('btn-analitica').addEventListener('click', () => {
  modalAnalitica.style.display = 'block';
});
document.getElementById('btn-close-analitica').addEventListener('click', () => {
  modalAnalitica.style.display = 'none';
});

// Cobros Modal
const modalCobros = document.getElementById('modal-cobros');
document.getElementById('btn-cobros').addEventListener('click', () => {
  modalCobros.style.display = 'block';
});
document.getElementById('btn-close-cobros').addEventListener('click', () => {
  modalCobros.style.display = 'none';
});

// QRs Upload Logic
let b64Yape = null;
let b64Plin = null;

document.getElementById('preview-yape').addEventListener('click', () => document.getElementById('file-yape').click());
document.getElementById('file-yape').addEventListener('change', (e) => {
  const file = e.target.files[0];
  if(file) {
    const reader = new FileReader();
    reader.onload = (ev) => {
      b64Yape = ev.target.result;
      document.getElementById('preview-yape').src = b64Yape;
    };
    reader.readAsDataURL(file);
  }
});

document.getElementById('preview-plin').addEventListener('click', () => document.getElementById('file-plin').click());
document.getElementById('file-plin').addEventListener('change', (e) => {
  const file = e.target.files[0];
  if(file) {
    const reader = new FileReader();
    reader.onload = (ev) => {
      b64Plin = ev.target.result;
      document.getElementById('preview-plin').src = b64Plin;
    };
    reader.readAsDataURL(file);
  }
});

let kpiBase64 = null;
document.getElementById('btn-upload-kpi').addEventListener('click', () => {
  document.getElementById('file-kpi').click();
});

document.getElementById('file-kpi').addEventListener('change', (e) => {
  const file = e.target.files[0];
  if(file) {
    const reader = new FileReader();
    reader.onload = (event) => {
      kpiBase64 = event.target.result;
      document.getElementById('kpi-preview').src = kpiBase64;
      document.getElementById('kpi-preview-container').style.display = 'block';
      document.getElementById('kpi-result').style.display = 'none';
    };
    reader.readAsDataURL(file);
  }
});

document.getElementById('btn-analyze-kpi').addEventListener('click', async () => {
  const codigo = document.getElementById('kpi-codigo').value;
  const clave = document.getElementById('kpi-clave').value;
  
  if(!codigo || !clave) return showToast('Ingresa tu código y contraseña', true);
  
  const btn = document.getElementById('btn-analyze-kpi');
  setLoading(btn, true);
  document.getElementById('kpi-result').style.display = 'none';
  
  try {
    const res = await fetch(`${API_BASE}/analyze_kpi`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: window.currentUserToken, codigo: codigo, clave: clave })
    });
    const data = await res.json();
    setLoading(btn, false);
    
    if (data.success) {
      document.getElementById('kpi-result').textContent = data.estrategia;
      document.getElementById('kpi-result').style.display = 'block';
      showToast('Agenda Estratégica Generada');
    } else {
      showToast(data.message, true);
    }
  } catch(e) {
    setLoading(btn, false);
    showToast('Error de red al conectar al Backoffice', true);
  }
});

document.getElementById('btn-analyze-kpi-img').addEventListener('click', async () => {
  if(!kpiBase64) return showToast('Sube una imagen primero', true);
  
  const btn = document.getElementById('btn-analyze-kpi-img');
  setLoading(btn, true);
  document.getElementById('kpi-result').style.display = 'none';
  
  try {
    const res = await fetch(`${API_BASE}/analyze_kpi`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: window.currentUserToken, image: kpiBase64 })
    });
    const data = await res.json();
    setLoading(btn, false);
    
    if (data.success) {
      document.getElementById('kpi-result').textContent = data.estrategia;
      document.getElementById('kpi-result').style.display = 'block';
      showToast('Agenda Estratégica Generada');
    } else {
      showToast(data.message, true);
    }
  } catch(e) {
    setLoading(btn, false);
    showToast('Error de red al analizar KPI', true);
  }
});

function showToast(message, isError = false) {
  toastMsg.textContent = message;
  toast.style.background = isError ? '#f87171' : 'var(--gold-primary)';
  toast.style.color = isError ? '#fff' : 'var(--coffee-darker)';
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3000);
}

function setLoading(btn, isLoading) {
  const text = btn.querySelector('.btn-text');
  const loader = btn.querySelector('.loader');
  if(isLoading) {
    text.style.display = 'none';
    loader.classList.add('active');
    btn.disabled = true;
  } else {
    text.style.display = 'block';
    loader.classList.remove('active');
    btn.disabled = false;
  }
}

const API_BASE = 'http://45.55.92.211:3005/api';

// API Logic
function setupDashboard(user, token) {
  screenLogin.classList.remove('active');
  screenDashboard.classList.add('active');
  
  document.getElementById('user-name').textContent = user.nombre || "Líder Sinergia";
  
  if(user.facebook_page_id) {
    document.getElementById('page-name').textContent = user.facebook_page_id;
    document.getElementById('page-name').style.color = "#4ade80";
  } else {
    document.getElementById('page-name').textContent = "Falta Configurar API";
    document.getElementById('page-name').style.color = "#f87171";
  }
  
  // Rellenar settings
  document.getElementById('cfg-idioma').value = user.idioma || "Español";
  document.getElementById('cfg-zona').value = user.zona || "";
  document.getElementById('cfg-link').value = user.link_tienda || "";
  document.getElementById('cfg-fb-token').value = user.facebook_access_token || "";
  document.getElementById('cfg-fb-page').value = user.facebook_page_id || "";
  
  statusBadge.style.display = 'inline-flex';
  statusBadge.className = 'status-badge';
  statusBadge.innerHTML = '<i data-lucide="wifi"></i> En línea';
  lucide.createIcons();
  
  window.currentUserToken = token;
}

btnLogin.addEventListener('click', async () => {
  const token = document.getElementById('login-token').value;
  if(!token) return showToast('Ingresa un token o teléfono válido', true);

  setLoading(btnLogin, true);
  
  try {
    const res = await fetch(`${API_BASE}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token })
    });
    const data = await res.json();
    setLoading(btnLogin, false);
    
    if (data.success) {
      setupDashboard(data.user, token);
      showToast('¡Sincronización Exitosa!');
    } else {
      showToast(data.message, true);
    }
  } catch(e) {
    setLoading(btnLogin, false);
    showToast('Error de red al conectar', true);
  }
});

btnRegister.addEventListener('click', async () => {
  const nombre = document.getElementById('reg-name').value;
  const whatsapp = document.getElementById('reg-phone').value;
  const link = document.getElementById('reg-link').value;
  
  if(!nombre || !whatsapp) return showToast('Nombre y WhatsApp son obligatorios', true);

  setLoading(btnRegister, true);
  
  try {
    const res = await fetch(`${API_BASE}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nombre, whatsapp, link_tienda: link })
    });
    const data = await res.json();
    setLoading(btnRegister, false);
    
    if (data.success) {
      setupDashboard(data.user, whatsapp); // El ID es el whatsapp
      showToast('¡Cuenta Creada con Éxito!');
    } else {
      showToast(data.message, true);
    }
  } catch(e) {
    setLoading(btnRegister, false);
    showToast('Error de red al registrarse', true);
  }
});

document.getElementById('btn-save-settings').addEventListener('click', async () => {
  setLoading(document.getElementById('btn-save-settings'), true);
  
  const payload = {
    token: window.currentUserToken,
    idioma: document.getElementById('cfg-idioma').value,
    zona: document.getElementById('cfg-zona').value,
    link_tienda: document.getElementById('cfg-link').value,
    facebook_access_token: document.getElementById('cfg-fb-token').value,
    facebook_page_id: document.getElementById('cfg-fb-page').value,
  };
  
  try {
    const res = await fetch(`${API_BASE}/update_profile`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    setLoading(document.getElementById('btn-save-settings'), false);
    
    if (data.success) {
      showToast('Ajustes guardados correctamente');
      modalSettings.style.display = 'none';
      setupDashboard(data.user, window.currentUserToken);
    } else {
      showToast(data.message, true);
    }
  } catch(e) {
    setLoading(document.getElementById('btn-save-settings'), false);
    showToast('Error al guardar ajustes', true);
  }
});

document.getElementById('btn-save-cobros').addEventListener('click', async () => {
  const btn = document.getElementById('btn-save-cobros');
  setLoading(btn, true);
  
  const payload = {
    token: window.currentUserToken,
    cta_bcp: document.getElementById('cobro-bcp').value,
    cta_interbank: document.getElementById('cobro-interbank').value,
    tipo_cambio: document.getElementById('cobro-tc').value,
    qr_yape: b64Yape,
    qr_plin: b64Plin
  };
  
  try {
    const res = await fetch(`${API_BASE}/config_cobros`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    setLoading(btn, false);
    
    if (data.success) {
      showToast('Billetera guardada correctamente');
      modalCobros.style.display = 'none';
    } else {
      showToast(data.message, true);
    }
  } catch(e) {
    setLoading(btn, false);
    showToast('Error al guardar billetera', true);
  }
});

btnReclutar.addEventListener('click', async () => {
  setLoading(btnReclutar, true);
  
  try {
    const res = await fetch(`${API_BASE}/publicar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: window.currentUserToken })
    });
    const data = await res.json();
    
    setLoading(btnReclutar, false);
    if(data.success) {
      showToast('¡Orden enviada! La IA publicará en breve.');
    } else {
      showToast('Error al enviar orden', true);
    }
  } catch(e) {
    setLoading(btnReclutar, false);
    showToast('Error de red', true);
  }
});

document.getElementById('btn-simulador').addEventListener('click', () => {
  window.location.href = '/simulador.html';
});

document.getElementById('btn-afiliar').addEventListener('click', async () => {
  try {
    await Browser.open({ url: 'https://peru.ganoitouch.biz/' });
  } catch (e) {
    window.open('https://peru.ganoitouch.biz/', '_blank');
  }
});

document.getElementById('btn-cola').addEventListener('click', () => {
  showToast('No hay posts pendientes en cola.');
});
