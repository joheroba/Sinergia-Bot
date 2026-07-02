import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const { agent_id, amount } = await req.json();

    // 1. Conexión REAL al nodo público de la Testnet de Shimmer (IOTA)
    const nodeResponse = await fetch('https://api.testnet.shimmer.network/api/core/v2/info');
    if (!nodeResponse.ok) {
      throw new Error('No se pudo conectar al nodo de IOTA');
    }
    const nodeInfo = await nodeResponse.json();

    // 2. Simulamos el tiempo de confirmación en el Tangle (Protocolo de Consenso)
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 3. Generamos un Hash de transacción simulado para la UI
    const chars = 'abcdef0123456789';
    let txHash = '0x';
    for(let i=0; i<64; i++) txHash += chars[Math.floor(Math.random() * chars.length)];

    return NextResponse.json({ 
      success: true, 
      network_name: nodeInfo.name || 'Shimmer Testnet',
      version: nodeInfo.version,
      tx_hash: txHash,
      amount_added: amount
    });
  } catch (error) {
    console.error('Error IOTA:', error);
    return NextResponse.json({ error: 'Fallo al conectar con Tangle' }, { status: 500 });
  }
}
