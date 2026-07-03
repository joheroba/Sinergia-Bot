const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://prqpkdkbonugdxfagsnt.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBycXBrZGtib251Z2R4ZmFnc250Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA1MTIyMzAsImV4cCI6MjA5NjA4ODIzMH0.pNX4Nx1EFnXV5EMvP_HgXSTEOUqiTMrbRHVuK_4Yw4k';

const supabase = createClient(supabaseUrl, supabaseKey);

async function correctCompany() {
  console.log('Fetching Joherobaimport company...');
  const { data: companies, error: cmpErr } = await supabase
    .from('companies')
    .select('*')
    .eq('name', 'Joherobaimport')
    .limit(1);

  if (cmpErr || !companies || companies.length === 0) {
    console.error('Error fetching Joherobaimport:', cmpErr);
    return;
  }

  const joherobaId = companies[0].id;
  console.log('Joherobaimport Company ID:', joherobaId);

  console.log('Transferring all agents to Joherobaimport...');
  const { data: updated, error: updErr } = await supabase
    .from('agents')
    .update({ company_id: joherobaId })
    .neq('id', '00000000-0000-0000-0000-000000000000') // Dummy condition to update all rows since RLS allows it
    .select();

  if (updErr) {
    console.error('Error transferring agents:', updErr);
  } else {
    console.log('Successfully transferred agents:', updated.length);
  }
}

correctCompany();
