-- Esquema SQL para AethelOS (Fase 4)

-- 1. Crear tabla de Agentes
CREATE TABLE aethel_agents (
  agent_id VARCHAR(50) PRIMARY KEY,
  agent_name VARCHAR(100) NOT NULL,
  iota_balance INTEGER NOT NULL DEFAULT 0,
  operational_status VARCHAR(20) NOT NULL DEFAULT 'idle',
  reputation_score INTEGER NOT NULL DEFAULT 0,
  current_action VARCHAR(100) DEFAULT 'En reposo',
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Habilitar la emisión de eventos en Tiempo Real (WebSockets) para esta tabla
ALTER PUBLICATION supabase_realtime ADD TABLE aethel_agents;

-- 3. Insertar los agentes fundadores (Datos Semilla)
INSERT INTO aethel_agents (agent_id, agent_name, iota_balance, operational_status, reputation_score)
VALUES 
  ('A-001', 'Nexus_Alpha', 1500, 'active', 98),
  ('A-002', 'Cipher_Protocol', 320, 'idle', 85)
ON CONFLICT (agent_id) DO NOTHING;
