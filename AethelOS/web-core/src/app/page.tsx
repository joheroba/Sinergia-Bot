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
  const { agents, fetchAgents, updateAgentStatus, updateIotaBalance, triggerKillSwitch, globalKillSwitch, simulateTick } = useAgentStore();
  const [isInitializing, setIsInitializing] = useState(true);
  const [fundingAgent, setFundingAgent] = useState<string | null>(null);
  const [lastTx, setLastTx] = useState<string>('');
  
  // Nivel 4: UI States
  const [isPanelCollapsed, setIsPanelCollapsed] = useState(false);
  const [chatAgent, setChatAgent] = useState<any | null>(null);
  const [isListening, setIsListening] = useState(false);

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
        <button 
          onClick={() => globalKillSwitch()}
          className="bg-red-950/50 hover:bg-red-900 border border-red-800 text-red-400 px-6 py-2 rounded-lg font-bold transition-all shadow-[0_0_15px_rgba(220,38,38,0.2)] hover:shadow-[0_0_25px_rgba(220,38,38,0.4)]"
        >
          GLOBAL KILL SWITCH
        </button>
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
                      onClick={() => triggerKillSwitch(agent.agent_id)}
                      className="flex-[0.5] bg-red-900/20 hover:bg-red-900/40 border border-red-800/30 text-red-400 text-xs py-2 rounded transition-colors title='Cortar Red'"
                    >
                      ☠️
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
                placeholder="Escribe o usa tu voz..." 
                className="flex-1 bg-slate-900 border border-slate-700 rounded-full px-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                disabled
              />
              <button 
                onClick={handleMicClick}
                className={`w-12 h-12 rounded-full flex items-center justify-center transition-all ${
                  isListening 
                  ? 'bg-red-500 text-white shadow-[0_0_20px_rgba(239,68,68,0.6)] animate-pulse' 
                  : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg'
                }`}
              >
                🎙️
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
