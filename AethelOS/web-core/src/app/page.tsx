'use client';
import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { useAgentStore } from '@/store/useAgentStore';

// IMPORTANTE: Desactivar SSR para Three.js/Rapier para evitar crashes de Turbopack en el servidor Node.js
const CampusMap = dynamic(() => import('@/components/CampusMap'), { 
  ssr: false,
  loading: () => (
    <div className="w-full h-[600px] bg-slate-900 rounded-xl flex items-center justify-center border border-slate-700 shadow-2xl">
      <div className="text-center animate-pulse">
        <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-indigo-300 font-mono text-sm">Inicializando Motor 3D (WebGL)...</p>
      </div>
    </div>
  )
});

export default function Dashboard() {
  const { agents, fetchAgents, updateAgentStatus, updateIotaBalance, triggerKillSwitch, globalKillSwitch, simulateTick, isDossierOpen, setDossierOpen } = useAgentStore();
  const [isInitializing, setIsInitializing] = useState(true);
  const [fundingAgent, setFundingAgent] = useState<string | null>(null);
  const [lastTx, setLastTx] = useState<string>('');
  
  // Nivel 4: UI States
  const [isPanelCollapsed, setIsPanelCollapsed] = useState(false);
  const [chatAgent, setChatAgent] = useState<any | null>(null);
  const [isListening, setIsListening] = useState(false);

  // Lead Generation & Auth
  const [isRegistered, setIsRegistered] = useState(false);
  const [userEmail, setUserEmail] = useState('');
  const [regForm, setRegForm] = useState({ name: '', email: '', phone: '' });

  useEffect(() => {
    const savedEmail = localStorage.getItem('aethelos_user_email');
    if (savedEmail) {
      setIsRegistered(true);
      setUserEmail(savedEmail);
    }
  }, []);

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault();
    if (!regForm.name || !regForm.email || !regForm.phone) return;
    localStorage.setItem('aethelos_user_email', regForm.email);
    setUserEmail(regForm.email);
    setIsRegistered(true);
    
    // Voice Pitch (Web Speech API)
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      const msg = new SpeechSynthesisUtterance(`Bienvenido al Distrito Primus, ${regForm.name}. Soy Paul, representante de ventas de Aethel OS. Revisa nuestro catálogo corporativo a tu izquierda.`);
      msg.lang = 'es-ES';
      msg.pitch = 1.0;
      msg.rate = 1.05;
      window.speechSynthesis.speak(msg);
    }
  };

  // Inicialización de datos
  useEffect(() => {
    fetchAgents().then(() => setIsInitializing(false));
  }, [fetchAgents]);

  // Bucle de simulación (Tick)
  useEffect(() => {
    if (isInitializing) return;
    
    const interval = setInterval(() => {
      simulateTick();
    }, 3000); // Tick cada 3 segundos
    return () => clearInterval(interval);
  }, [simulateTick, isInitializing]);

  const handleFundAgent = async (agentId: string, currentBalance: number) => {
    setFundingAgent(agentId);
    try {
      // Conectar con nuestro puente IOTA Testnet
      const res = await fetch('/api/iota', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_id: agentId, amount: 100 })
      });
      const data = await res.json();
      
      if (data.success) {
        await updateIotaBalance(agentId, currentBalance + 100);
        setLastTx(`[IOTA TANGLE] Éxito: +100 iOTA a ${agentId}. TX: ${data.tx_hash.substring(0, 16)}...`);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setFundingAgent(null);
      // Limpiar mensaje después de 5 seg
      setTimeout(() => setLastTx(''), 5000);
    }
  };

  const handleMicClick = () => {
    setIsListening(!isListening);
    // Simular que escucha y luego se apaga
    if (!isListening) {
      setTimeout(() => setIsListening(false), 3000);
    }
  };

  if (isInitializing) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-200 flex items-center justify-center font-mono">
        <div className="text-center animate-pulse">
          <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p>Sincronizando con Supabase...</p>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-200 p-8 font-mono relative">
      {/* Header */}
      <header className="flex justify-between items-center mb-8 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-indigo-400 tracking-tight flex items-center gap-3">
            AethelOS <span className="text-xs bg-indigo-900/50 text-indigo-300 px-2 py-1 rounded border border-indigo-700">MVP v1.1.0</span>
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Sincronizado con Supabase (PostgreSQL) {lastTx && <span className="text-green-400 ml-4">{lastTx}</span>}
          </p>
        </div>
        <div className="flex gap-4">
          <button 
            onClick={() => setDossierOpen(true)}
            className="bg-sky-950/50 hover:bg-sky-900 border border-sky-800 text-sky-300 px-6 py-2 rounded-lg font-bold transition-all shadow-[0_0_15px_rgba(14,165,233,0.2)]"
          >
            📋 DOSSIER EJECUTIVO
          </button>
          
          {userEmail === 'joherobaxpc@gmail.com' && (
            <a 
              href="/boardroom"
              className="bg-indigo-950/50 hover:bg-indigo-900 border border-indigo-800 text-indigo-300 px-6 py-2 rounded-lg font-bold transition-all shadow-[0_0_15px_rgba(79,70,229,0.2)] hover:shadow-[0_0_25px_rgba(79,70,229,0.4)] flex items-center justify-center"
            >
              SALA DE JUNTAS (CEO) 🔐
            </a>
          )}
        </div>
      </header>

      <div className="flex gap-8 relative">
        {/* Panel Izquierdo: Simulación 3D */}
        <div className={`transition-all duration-500 ${isPanelCollapsed ? 'w-full' : 'w-2/3'} space-y-4`}>
          <div className="flex justify-between items-center">
            <h2 className="text-sm font-semibold tracking-widest text-slate-400 uppercase">Distrito Corporativo 3D</h2>
            <button 
              onClick={() => setIsPanelCollapsed(!isPanelCollapsed)}
              className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1 rounded border border-slate-600 transition-colors"
            >
              {isPanelCollapsed ? 'Mostrar Panel de Agentes ⇦' : 'Colapsar Panel ⇨'}
            </button>
          </div>
          <CampusMap />
        </div>

        {/* Panel Derecho: Lista de Agentes (Colapsable) */}
        {!isPanelCollapsed && (
          <div className="w-1/3 space-y-4 transition-all duration-500">
            <h2 className="text-sm font-semibold tracking-widest text-slate-400 uppercase">Agentes Activos (ADN)</h2>
            
            <div className="space-y-4 h-[600px] overflow-y-auto pr-2 custom-scrollbar">
              {Object.values(agents).map(agent => (
                <div key={agent.agent_id} className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 hover:border-indigo-500/30 transition-colors relative overflow-hidden">
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="text-lg font-bold text-slate-100">{agent.agent_name}</h3>
                    <span className={`text-xs px-2 py-1 rounded font-bold ${
                      agent.operational_status === 'active' ? 'bg-green-900/30 text-green-400 border border-green-800/50' : 
                      agent.operational_status === 'idle' ? 'bg-amber-900/30 text-amber-400 border border-amber-800/50' : 
                      'bg-red-900/30 text-red-400 border border-red-800/50'
                    }`}>
                      {agent.operational_status.toUpperCase()}
                    </span>
                  </div>
                  
                  <div className="space-y-2 text-sm text-slate-400 mb-6">
                    <div className="flex justify-between border-b border-slate-800/50 pb-1">
                      <span>ID_Hash:</span>
                      <span className="text-slate-300 font-mono">{agent.agent_id}</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800/50 pb-1">
                      <span>Balance:</span>
                      <span className="text-indigo-400 font-bold">{agent.iota_balance} iOTA</span>
                    </div>
                  </div>

                  <div className="bg-black/30 rounded p-3 mb-4 border border-slate-800">
                    <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Estado Actual:</p>
                    <p className="text-sm text-indigo-300 font-medium animate-pulse">{'>'} {agent.current_action}</p>
                  </div>

                  <div className="flex gap-2">
                    <button 
                      onClick={() => setChatAgent(agent)}
                      className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs py-2 rounded transition-colors shadow-lg shadow-indigo-500/20"
                    >
                      💬 CHAT VOZ
                    </button>
                    <button 
                      onClick={() => updateAgentStatus(agent.agent_id, agent.operational_status === 'active' ? 'idle' : 'active')}
                      className="flex-1 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-200 text-xs py-2 rounded transition-colors"
                    >
                      {agent.operational_status === 'active' ? 'PAUSAR' : 'DESPERTAR'}
                    </button>
                    <button 
                      className="flex-[0.5] bg-sky-900/20 hover:bg-sky-900/40 border border-sky-800/30 text-sky-400 text-xs py-2 rounded transition-colors"
                      title="Contratar Servicios"
                    >
                      🛒
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* OVERLAY DE CHAT CON VOZ (Fase 4 Mockup) */}
      {chatAgent && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden flex flex-col">
            <div className="bg-indigo-900/40 p-4 border-b border-indigo-800/50 flex justify-between items-center">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-indigo-500/20 border border-indigo-500 flex items-center justify-center">
                  🤖
                </div>
                <div>
                  <h3 className="font-bold text-lg text-white">{chatAgent.agent_name}</h3>
                  <p className="text-xs text-indigo-300">Conectado - LipSync WebGL Ready</p>
                </div>
              </div>
              <button onClick={() => setChatAgent(null)} className="text-slate-400 hover:text-white text-xl font-bold px-2">&times;</button>
            </div>
            
            <div className="p-6 h-64 overflow-y-auto space-y-4">
              <div className="flex gap-3">
                <div className="bg-indigo-900/50 text-indigo-100 p-3 rounded-lg rounded-tl-none border border-indigo-800/50 max-w-[80%] text-sm">
                  Hola, soy {chatAgent.agent_name}. Mi módulo de Text-to-Speech (TTS) y sincronización labial está en fase de pruebas. Presiona el micrófono para hablarme.
                </div>
              </div>
              {isListening && (
                <div className="flex justify-end gap-3 animate-pulse">
                  <div className="bg-slate-800 text-slate-300 p-3 rounded-lg rounded-tr-none border border-slate-700 text-sm italic">
                    Escuchando...
                  </div>
                </div>
              )}
            </div>

            <div className="p-4 bg-slate-950 border-t border-slate-800 flex gap-2 items-center">
              <input 
                type="text" 
                placeholder="Escribe un mensaje o usa el micrófono..." 
                className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white text-sm focus:outline-none focus:border-indigo-500"
                disabled
              />
              <button 
                onClick={handleMicClick}
                className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${isListening ? 'bg-red-500 text-white animate-pulse shadow-[0_0_15px_rgba(239,68,68,0.5)]' : 'bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700'}`}
              >
                🎤
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Dossier Ejecutivo Modal */}
      {isDossierOpen && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-[110] flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-4xl shadow-2xl overflow-hidden flex flex-col h-[85vh]">
            <div className="flex justify-between items-center p-4 border-b border-slate-800 bg-slate-800/50">
              <h2 className="text-xl font-bold text-sky-400 font-mono">📋 DOSSIER EJECUTIVO - AETHEL OS</h2>
              <button onClick={() => setDossierOpen(false)} className="text-slate-400 hover:text-white text-2xl font-bold px-2">&times;</button>
            </div>
            
            <div className="p-8 overflow-y-auto custom-scrollbar flex-1 space-y-8 font-mono">
              <section>
                <h3 className="text-lg font-bold text-indigo-400 mb-3 border-b border-indigo-900/50 pb-2">1. Alcances de Aethel OS</h3>
                <p className="text-slate-300 text-sm leading-relaxed mb-4">
                  Aethel OS es el primer ecosistema operativo (Hive Mind Central) diseñado para gestionar Staff Virtual hiperrealista en entornos 3D corporativos. Transformamos la manera en que su empresa atiende clientes, audita procesos y presenta productos.
                </p>
                <div className="bg-slate-800/50 border border-slate-700 p-4 rounded-lg">
                  <h4 className="text-sky-400 font-bold mb-2">✨ NUEVA CAPACIDAD: GEMELO DIGITAL</h4>
                  <p className="text-slate-300 text-sm">
                    Mediante el uso de inteligencia artificial avanzada, Aethel OS es capaz de generar su <strong>Gemelo Digital (Avatar 3D)</strong>. Al tomarse una fotografía de frente y de perfil, el sistema modelará su rostro exacto y lo adaptará a uno de nuestros avatares corporativos, permitiéndole interactuar directamente en el Distrito Primus con sus propios rasgos faciales.
                  </p>
                </div>
              </section>

              <section>
                <h3 className="text-lg font-bold text-indigo-400 mb-3 border-b border-indigo-900/50 pb-2">2. Modalidades de Contratación y Precios</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-800/50 border border-slate-700 p-4 rounded-lg">
                    <h4 className="font-bold text-white mb-1">A. SaaS Cloud Hosting</h4>
                    <p className="text-slate-400 text-xs mb-3">Ideal para emprendimientos rápidos.</p>
                    <ul className="text-sm text-slate-300 space-y-2 list-disc pl-4">
                      <li>Alojamiento en nuestros servidores de alta velocidad.</li>
                      <li>Hasta 5 Agentes Virtuales simultáneos.</li>
                      <li>Precio: $199 USD / mes</li>
                    </ul>
                  </div>
                  <div className="bg-slate-800/50 border border-slate-700 p-4 rounded-lg">
                    <h4 className="font-bold text-white mb-1">B. On-Premise Enterprise</h4>
                    <p className="text-slate-400 text-xs mb-3">Para corporaciones e infraestructura propia.</p>
                    <ul className="text-sm text-slate-300 space-y-2 list-disc pl-4">
                      <li>Instalación en servidores privados de su empresa.</li>
                      <li>Agentes Virtuales ilimitados. Módulos IA personalizados.</li>
                      <li>Precio: Cotización a medida</li>
                    </ul>
                  </div>
                </div>
              </section>

              <section>
                <h3 className="text-lg font-bold text-indigo-400 mb-3 border-b border-indigo-900/50 pb-2">3. Permisos de Construcción en el Distrito Primus</h3>
                <p className="text-slate-300 text-sm leading-relaxed mb-4">
                  El Distrito Primus es nuestro meta-campus empresarial. Para abrir una sucursal 3D aquí (como Joheroba Import o Quality Informatic Solutions), debe adquirir un <strong>Permiso de Construcción</strong>. Esto incluye un lote virtual, diseño arquitectónico de su stand corporativo y conexión a la red neuronal IOTA para transacciones de sus visitantes.
                </p>
                <button className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-2 px-6 rounded-lg transition-colors shadow-lg shadow-indigo-500/20 text-sm">
                  🏢 Solicitar Terreno Comercial
                </button>
              </section>

              <section>
                <h3 className="text-lg font-bold text-amber-400 mb-3 border-b border-amber-900/50 pb-2">4. Relación con Inversionistas (Venture Capital)</h3>
                <p className="text-slate-300 text-sm leading-relaxed mb-4">
                  Aethel OS es el "Hive Mind Central" para el futuro del comercio corporativo. Estamos liderando la creación del estándar Web3 para agentes virtuales y comercio inmersivo. Buscamos socios estratégicos que deseen inyectar capital para escalar nuestra infraestructura y llegar al mercado Fortune 500.
                </p>
                <div className="bg-amber-900/10 border border-amber-800/50 p-4 rounded-lg">
                  <h4 className="font-bold text-amber-300 mb-1">💼 Rondas Semilla y Escalabilidad</h4>
                  <p className="text-slate-400 text-xs mb-3">Si representas a una firma de VC o eres un ángel inversor, agenda una reunión directa con nuestro CEO para revisar métricas, CAC, LTV y el Roadmap Tecnológico 2027.</p>
                  <button className="bg-amber-600 hover:bg-amber-500 text-white font-bold py-2 px-6 rounded-lg transition-colors shadow-lg shadow-amber-500/20 text-sm">
                    Agendar Reunión (Pitch Deck)
                  </button>
                </div>
              </section>

              <section>
                <h3 className="text-lg font-bold text-green-400 mb-3 border-b border-green-900/50 pb-2">5. Marketplace: Arquitectos Digitales (Diseñadores 3D)</h3>
                <p className="text-slate-300 text-sm leading-relaxed mb-4">
                  El Meta-Campus requiere constructores. ¿Eres modelador 3D o arquitecto en Blender/Maya? Las empresas del Distrito Primus necesitan profesionales para construir sus parcelas y stands.
                </p>
                <div className="bg-green-900/10 border border-green-800/50 p-4 rounded-lg">
                  <h4 className="font-bold text-green-300 mb-1">🛠️ Ofrécete como Constructor</h4>
                  <p className="text-slate-400 text-xs mb-3">Conviértete en un Arquitecto Certificado por Aethel OS. Los clientes que compren parcelas podrán contratarte directamente dentro de la plataforma para diseñar sus sucursales, mobiliario o modelar gemelos digitales corporativos (como agentes base).</p>
                  <button className="bg-green-600 hover:bg-green-500 text-white font-bold py-2 px-6 rounded-lg transition-colors shadow-lg shadow-green-500/20 text-sm">
                    Postular como Arquitecto Digital
                  </button>
                </div>
              </section>
            </div>
          </div>
        </div>
      )}

      {/* Muro de Registro (Lead Gen) */}
      {!isRegistered && (
        <div className="fixed inset-0 bg-slate-950/90 backdrop-blur-md z-[100] flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-md shadow-2xl p-8 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-sky-400 via-indigo-500 to-purple-500"></div>
            <h2 className="text-2xl font-bold text-white mb-2 text-center font-mono tracking-widest">DISTRITO PRIMUS</h2>
            <p className="text-slate-400 text-sm text-center mb-6 font-mono">Identifícate en Recepción para acceder a las instalaciones de Aethel OS y recibir nuestro Dossier Corporativo.</p>
            
            <form onSubmit={handleRegister} className="space-y-4 font-mono">
              <div>
                <label className="block text-xs font-bold text-slate-500 mb-1 uppercase">Nombre / Alias</label>
                <input 
                  type="text" 
                  required
                  value={regForm.name}
                  onChange={e => setRegForm({...regForm, name: e.target.value})}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-indigo-500 focus:outline-none" 
                  placeholder="Ej. Juan Pérez"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-500 mb-1 uppercase">Correo Electrónico</label>
                <input 
                  type="email" 
                  required
                  value={regForm.email}
                  onChange={e => setRegForm({...regForm, email: e.target.value})}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-indigo-500 focus:outline-none" 
                  placeholder="ceo@tuempresa.com"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-500 mb-1 uppercase">WhatsApp / Telegram (Opcional)</label>
                <input 
                  type="text" 
                  value={regForm.phone}
                  onChange={e => setRegForm({...regForm, phone: e.target.value})}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-indigo-500 focus:outline-none" 
                  placeholder="+51 999..."
                />
              </div>
              <button 
                type="submit"
                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 rounded-lg mt-4 transition-colors shadow-[0_0_15px_rgba(79,70,229,0.4)] uppercase tracking-wider text-sm"
              >
                Solicitar Acceso ➜
              </button>
            </form>
          </div>
        </div>
      )}

    </main>
  );
}
