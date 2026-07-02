import { createClient } from '@supabase/supabase-js';

// Conexión inicial configurada para el MVP de AethelOS
// NOTA: Reemplazar con variables de entorno reales en producción (.env.local)
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder-project.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'placeholder-anon-key';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
