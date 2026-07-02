import { create } from 'zustand';
import { supabase } from '@/lib/supabase';

export type AgentStatus = 'active' | 'idle' | 'learning' | 'emergency';

export interface AgentDNA {
  agent_id: string;
  agent_name: string;
  iota_balance: number;
  operational_status: AgentStatus;
  verified_skills: string[];
  reputation_score: number;
  position: [number, number, number];
  target_position: [number, number, number];
  current_action: string;
  agent_thought?: string;
}

interface AgentStore {
  agents: Record<string, AgentDNA>;
  fetchAgents: () => Promise<void>;
  addAgent: (agent: AgentDNA) => void;
  updateAgentStatus: (id: string, status: AgentStatus) => Promise<void>;
  updateIotaBalance: (id: string, newBalance: number) => Promise<void>;
  triggerKillSwitch: (id: string) => Promise<void>;
  globalKillSwitch: () => Promise<void>;
  simulateTick: () => void;
  setAgentThought: (id: string, thought: string) => void;
}

export const useAgentStore = create<AgentStore>((set, get) => ({
  agents: {},
  
  fetchAgents: async () => {
    const { data, error } = await supabase.from('aethel_agents').select('*');
    let finalData = data;

    if (error || !data || data.length === 0) {
      console.warn('⚠️ Supabase no respondió o la tabla está vacía/protegida por RLS. Cargando Agentes de Respaldo Local...');
      // Fallback a los agentes base si falla la DB
      finalData = [
        { agent_id: 'A-001', agent_name: 'Paul (Ventas)', operational_status: 'idle', current_action: 'Esperando clientes', iota_balance: 50, position: [-3, 0, -2], target_position: [-3, 0, -2], verified_skills: ['ventas', 'negociacion'] },
        { agent_id: 'A-002', agent_name: 'Sophia (Marketing)', operational_status: 'active', current_action: 'Analizando métricas', iota_balance: 120, position: [4, 0, 3], target_position: [4, 0, 3], verified_skills: ['marketing', 'seo'] },
        { agent_id: 'A-003', agent_name: 'Travis (Soporte)', operational_status: 'active', current_action: 'Monitoreando redes', iota_balance: 300, position: [-4, 0, 5], target_position: [-4, 0, 5], verified_skills: ['it', 'redes'] },
        { agent_id: 'A-004', agent_name: 'Emma (RRHH)', operational_status: 'idle', current_action: 'Revisando perfiles', iota_balance: 80, position: [5, 0, -3], target_position: [5, 0, -3], verified_skills: ['rrhh', 'psicologia'] },
        { agent_id: 'A-005', agent_name: 'Marcus (Finanzas)', operational_status: 'learning', current_action: 'Procesando balances', iota_balance: 900, position: [-6, 0, 0], target_position: [-6, 0, 0], verified_skills: ['finanzas', 'contabilidad'] },
        { agent_id: 'A-006', agent_name: 'Elena (Operaciones)', operational_status: 'active', current_action: 'Optimizando rutas', iota_balance: 250, position: [6, 0, 0], target_position: [6, 0, 0], verified_skills: ['logistica', 'operaciones'] },
        { agent_id: 'A-808', agent_name: 'GanoiBot', operational_status: 'active', current_action: 'Atendiendo consultas', iota_balance: 500, position: [0, 0, 1.5], target_position: [0, 0, 1.5], verified_skills: ['atencion', 'ventas_gano'] }
      ];
    }
    
    if (finalData && finalData.length > 0) {
      const agentsMap: Record<string, AgentDNA> = {};
      finalData.forEach(dbAgent => {
        // Asignar posiciones base para los agentes
        let pos: [number, number, number] = [0, 0, 0];
        if (dbAgent.agent_id === 'A-001') pos = [-3, 0, -2];
        else if (dbAgent.agent_id === 'A-002') pos = [4, 0, 3];
        else if (dbAgent.agent_id === 'A-003') pos = [-4, 0, 5];
        else if (dbAgent.agent_id === 'A-004') pos = [5, 0, -3];
        else if (dbAgent.agent_id === 'A-005') pos = [-6, 0, 0];
        else if (dbAgent.agent_id === 'A-006') pos = [6, 0, 0];
        else pos = [(Math.random() * 10) - 5, 0, (Math.random() * 10) - 5];

        agentsMap[dbAgent.agent_id] = {
          ...dbAgent,
          position: pos,
          target_position: pos,
          verified_skills: [],
          agent_thought: 'Iniciando sistemas...'
        };
      });
      set({ agents: agentsMap });
    }
  },

  addAgent: (agent) =>
    set((state) => ({
      agents: { ...state.agents, [agent.agent_id]: agent },
    })),

  updateAgentStatus: async (id, status) => {
    set((state) => ({
      agents: {
        ...state.agents,
        [id]: { ...state.agents[id], operational_status: status },
      },
    }));
    await supabase.from('aethel_agents').update({ operational_status: status }).eq('agent_id', id);
  },

  updateIotaBalance: async (id, balance) => {
    set((state) => ({
      agents: {
        ...state.agents,
        [id]: { ...state.agents[id], iota_balance: balance },
      },
    }));
    await supabase.from('aethel_agents').update({ iota_balance: balance }).eq('agent_id', id);
  },

  triggerKillSwitch: async (id) => {
    set((state) => ({
      agents: {
        ...state.agents,
        [id]: { 
          ...state.agents[id], 
          operational_status: 'emergency',
          current_action: 'SISTEMA CAÍDO',
          agent_thought: 'ERROR FATAL: CONEXIÓN PERDIDA',
          target_position: state.agents[id].position
        },
      },
    }));
    await supabase.from('aethel_agents').update({ operational_status: 'emergency', current_action: 'SISTEMA CAÍDO' }).eq('agent_id', id);
  },

  globalKillSwitch: async () => {
    const { agents } = get();
    const newAgents = { ...agents };
    Object.keys(newAgents).forEach((key) => {
      newAgents[key].operational_status = 'emergency';
      newAgents[key].current_action = 'SISTEMA CAÍDO';
      newAgents[key].agent_thought = 'ERROR FATAL: CORTAFUEGOS ACTIVADO';
      newAgents[key].target_position = newAgents[key].position;
    });
    set({ agents: newAgents });
    await supabase.from('aethel_agents').update({ operational_status: 'emergency', current_action: 'SISTEMA CAÍDO' }).in('agent_id', Object.keys(agents));
  },

  setAgentThought: (id, thought) => 
    set((state) => {
      if (!state.agents[id]) return state;
      return {
        agents: {
          ...state.agents,
          [id]: { ...state.agents[id], agent_thought: thought }
        }
      };
    }),

  simulateTick: () =>
    set((state) => {
      const newAgents = { ...state.agents };
      const actions = [
        'Negociando IOTA', 
        'Analizando mercado', 
        'Auditando contrato', 
        'Escaneando nodos', 
        'Sincronizando Tangle'
      ];
      
      Object.keys(newAgents).forEach(key => {
        const agent = newAgents[key];
        if (agent.operational_status === 'active' || agent.operational_status === 'learning') {
          // Bajamos la probabilidad de moverse a 10% para que no sean hiperactivos y tengan tiempo de pensar
          if (Math.random() > 0.9) {
            const newAction = actions[Math.floor(Math.random() * actions.length)];
            newAgents[key] = {
              ...agent,
              target_position: [
                (Math.random() * 24) - 12, 
                0.5,
                (Math.random() * 24) - 12  
              ],
              current_action: newAction,
              agent_thought: 'Procesando...'
            };
            
            // Llamar a LM Studio de forma asíncrona sin bloquear el estado
            fetch('/api/chat', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ name: agent.agent_name, action: newAction })
            })
            .then(res => res.json())
            .then(data => {
              if(data.thought) {
                 get().setAgentThought(key, data.thought);
              }
            })
            .catch(console.error);
          }
        }
      });
      return { agents: newAgents };
    }),
}));
