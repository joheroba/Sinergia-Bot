import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'placeholder_key';

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn(' Faltan credenciales de Supabase en el archivo .env.local ');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
