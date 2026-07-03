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
    // Obtenemos los agentes y el saldo de la compañía
    const { data, error } = await supabase.from('agents').select('*, companies(iota_balance)');
    
    let finalData = data;

    if (error || !data || data.length === 0) {
      console.warn('⚠️ Supabase no respondió o la tabla está vacía/protegida por RLS. Cargando Agentes de Respaldo Local...');
      // Fallback a los agentes base si falla la DB
      finalData = [
        { id: 'A-001', custom_name: 'Paul (Ventas)', base_identity: 'Paul', operational_status: 'idle', companies: { iota_balance: 50 } },
        { id: 'A-002', custom_name: 'Sophia (Marketing)', base_identity: 'Sophia', operational_status: 'active', companies: { iota_balance: 120 } },
        { id: 'A-003', custom_name: 'Travis (Soporte)', base_identity: 'Travis', operational_status: 'active', companies: { iota_balance: 300 } },
        { id: 'A-004', custom_name: 'Emma (RRHH)', base_identity: 'Emma', operational_status: 'idle', companies: { iota_balance: 80 } },
        { id: 'A-005', custom_name: 'Marcus (Finanzas)', base_identity: 'Marcus', operational_status: 'learning', companies: { iota_balance: 900 } },
        { id: 'A-006', custom_name: 'Elena (Operaciones)', base_identity: 'Elena', operational_status: 'active', companies: { iota_balance: 250 } },
      ];
    }
    
    if (finalData && finalData.length > 0) {
      const agentsMap: Record<string, AgentDNA> = {};
      finalData.forEach(dbAgent => {
        // Asignar posiciones base para los agentes
        let pos: [number, number, number] = [0, 0, 0];
        if (dbAgent.base_identity === 'Paul') pos = [-3, 0, -2];
        else if (dbAgent.base_identity === 'Sophia') pos = [4, 0, 3];
        else if (dbAgent.base_identity === 'Travis') pos = [-4, 0, 5];
        else if (dbAgent.base_identity === 'Emma') pos = [5, 0, -3];
        else if (dbAgent.base_identity === 'Marcus') pos = [-6, 0, 0];
        else if (dbAgent.base_identity === 'Elena') pos = [6, 0, 0];
        else pos = [(Math.random() * 10) - 5, 0, (Math.random() * 10) - 5];

        agentsMap[dbAgent.id] = {
          agent_id: dbAgent.id,
          agent_name: dbAgent.custom_name || dbAgent.base_identity,
          operational_status: dbAgent.operational_status,
          iota_balance: dbAgent.companies?.iota_balance || 0,
          current_action: dbAgent.operational_status === 'idle' ? 'Esperando tareas' : 'Procesando...',
          position: pos,
          target_position: pos,
          verified_skills: [dbAgent.base_identity.toLowerCase()], // Habilidad basada en su identidad original
          reputation_score: 100,
          agent_thought: 'Iniciando sistemas conectando con Supabase...'
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
    await supabase.from('agents').update({ operational_status: status }).eq('id', id);
  },

  updateIotaBalance: async (id, balance) => {
    set((state) => ({
      agents: {
        ...state.agents,
        [id]: { ...state.agents[id], iota_balance: balance },
      },
    }));
    // En la nueva DB, el iota balance está en companies, omitimos su actualización directa aquí por ahora
    // await supabase.from('companies').update({ iota_balance: balance }).eq('id', companyId);
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
    await supabase.from('agents').update({ operational_status: 'emergency' }).eq('id', id);
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
    await supabase.from('agents').update({ operational_status: 'emergency' }).in('id', Object.keys(agents));
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
