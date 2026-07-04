'use client';
import { useState, useEffect } from 'react';
import { useAgentStore } from '@/store/useAgentStore';

export default function Boardroom() {
  const { agents, fetchAgents, updateAgentStatus, triggerKillSwitch, globalKillSwitch } = useAgentStore();
  const [isInitializing, setIsInitializing] = useState(true);
  const [accessDenied, setAccessDenied] = useState(false);

  useEffect(() => {
    // Verificar seguridad: ¿Es el CEO?
    const savedEmail = localStorage.getItem('aethelos_user_email');
    if (savedEmail !== 'joherobaxpc@gmail.com') {
      setAccessDenied(true);
    } else {
      fetchAgents().then(() => setIsInitializing(false));
    }
  }, [fetchAgents]);

  if (accessDenied) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-200 flex flex-col items-center justify-center font-mono p-8">
        <h1 className="text-4xl text-red-500 font-bold mb-4">ACCESO DENEGADO</h1>
        <p className="text-slate-400 mb-8">Esta área está restringida exclusivamente para la Mesa Directiva.</p>
        <a href="/" className="bg-indigo-600 hover:bg-indigo-500 px-6 py-2 rounded text-white font-bold">Volver a Recepción</a>
      </div>
    );
  }

  if (isInitializing) return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center text-white font-mono">Autenticando CEO...</div>
  );

  return (
    <main className="min-h-screen bg-slate-950 text-slate-200 p-8 font-mono relative">
      <header className="flex justify-between items-center mb-8 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-red-500 tracking-tight flex items-center gap-3">
            SALA DE JUNTAS (CEO) 🔐
          </h1>
          <p className="text-sm text-slate-500 mt-1">Control Maestro de la Colmena (Hive Mind)</p>
        </div>
        <div className="flex gap-4">
          <a href="/" className="bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-300 px-6 py-2 rounded-lg font-bold transition-all flex items-center">
            Volver a Recepción
          </a>
          <button 
            onClick={() => globalKillSwitch()}
            className="bg-red-950/80 hover:bg-red-900 border-2 border-red-600 text-red-400 px-8 py-2 rounded-lg font-bold transition-all shadow-[0_0_20px_rgba(220,38,38,0.5)] hover:shadow-[0_0_40px_rgba(220,38,38,0.8)]"
          >
            GLOBAL KILL SWITCH
          </button>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Object.values(agents).map(agent => (
          <div key={agent.agent_id} className="bg-slate-900 border border-slate-700 rounded-xl p-6 relative overflow-hidden">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-bold text-slate-100">{agent.agent_name}</h3>
              <span className={`text-xs px-2 py-1 rounded font-bold ${
                agent.operational_status === 'active' ? 'bg-green-900/30 text-green-400 border border-green-800/50' : 
                agent.operational_status === 'idle' ? 'bg-amber-900/30 text-amber-400 border border-amber-800/50' : 
                'bg-red-900/30 text-red-400 border border-red-800/50'
              }`}>
                {agent.operational_status.toUpperCase()}
              </span>
            </div>
            
            <div className="flex gap-4 mt-6">
              <button 
                onClick={() => updateAgentStatus(agent.agent_id, agent.operational_status === 'active' ? 'idle' : 'active')}
                className="flex-1 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-200 text-sm font-bold py-3 rounded transition-colors"
              >
                {agent.operational_status === 'active' ? 'Forzar Pausa' : 'Despertar'}
              </button>
              <button 
                onClick={() => triggerKillSwitch(agent.agent_id)}
                className="flex-1 bg-red-900/20 hover:bg-red-900/60 border border-red-800 text-red-400 text-sm font-bold py-3 rounded transition-colors"
              >
                ☠️ APAGAR AGENTE
              </button>
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}
