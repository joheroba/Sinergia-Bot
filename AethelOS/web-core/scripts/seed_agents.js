const { createClient } = require('@supabase/supabase-js');
const supabaseUrl = 'https://prqpkdkbonugdxfagsnt.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBycXBrZGtib251Z2R4ZmFnc250Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA1MTIyMzAsImV4cCI6MjA5NjA4ODIzMH0.pNX4Nx1EFnXV5EMvP_HgXSTEOUqiTMrbRHVuK_4Yw4k';

const supabase = createClient(supabaseUrl, supabaseKey);

async function seedAgents() {
  console.log('Fetching QIS company...');
  const { data: companies, error: cmpErr } = await supabase
    .from('companies')
    .select('*')
    .eq('name', 'Quality Informatic Solutions SAC')
    .limit(1);

  if (cmpErr || !companies || companies.length === 0) {
    console.error('Error fetching QIS:', cmpErr);
    return;
  }

  const qisId = companies[0].id;
  console.log('QIS Company ID:', qisId);

  const baseStaff = [
    { base_identity: 'Paul', custom_name: 'Paul (Ventas)' },
    { base_identity: 'Sophia', custom_name: 'Sophia (Marketing)' },
    { base_identity: 'Travis', custom_name: 'Travis (Soporte)' },
    { base_identity: 'Emma', custom_name: 'Emma (RRHH)' },
    { base_identity: 'Marcus', custom_name: 'Marcus (Finanzas)' },
    { base_identity: 'Elena', custom_name: 'Elena (Operaciones)' },
  ];

  const agentsToInsert = baseStaff.map(staff => ({
    company_id: qisId,
    base_identity: staff.base_identity,
    custom_name: staff.custom_name,
    operational_status: 'idle'
  }));

  console.log('Inserting agents into QIS...');
  const { data: inserted, error: insErr } = await supabase
    .from('agents')
    .insert(agentsToInsert)
    .select();

  if (insErr) {
    console.error('Error inserting agents:', insErr);
  } else {
    console.log('Successfully inserted agents:', inserted.length);
  }
}

seedAgents();
