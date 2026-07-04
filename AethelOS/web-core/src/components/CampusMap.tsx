import { Suspense, useRef, useState, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Text, Html, useGLTF, useAnimations, Billboard, RoundedBox, PositionalAudio, Icosahedron } from '@react-three/drei';
import { Physics, RigidBody, CuboidCollider, CapsuleCollider } from '@react-three/rapier';
import { useAgentStore, AgentDNA } from '@/store/useAgentStore';
import { useInspectorStore } from '@/store/useInspectorStore';
import * as THREE from 'three';

// Precargar los modelos ligeros
useGLTF.preload('/paul_talking_business.glb');
useGLTF.preload('/sophia_animated_003_-_animated_3d_woman.glb');

function EnvironmentMesh() {
  const { scene } = useGLTF('http://localhost:8080/entorno_repaired.glb');
  const addMesh = useInspectorStore(state => state.addMesh);
  
  useEffect(() => {
    if (scene) {
      (scene as any).background = null; 
      let index = 0;
      
      scene.traverse((child: any) => {
        if (child.isMesh) {
          const name = (child.name || '').toLowerCase();
          const matName = (child.material?.name || '').toLowerCase();
          
          let isSky = false;
          if (name.includes('sky') || name.includes('cielo') || name.includes('background') || name.includes('fondo') ||
              matName.includes('sky') || matName.includes('cielo') || matName.includes('background') || matName.includes('fondo')) {
            isSky = true;
          }

          if (child.geometry && !isSky) {
            child.geometry.computeBoundingBox();
            const bbox = child.geometry.boundingBox;
            if (bbox) {
              const size = new THREE.Vector3();
              bbox.getSize(size);
              if (size.length() > 300) {
                isSky = true;
              }
            }
          }

          if (isSky) {
            child.visible = false;
          } else {
            // Darle un nombre si no tiene
            if (!child.name) child.name = `Malla_${index++}`;
            
            // Extraer color inicial
            let initialColor = 'ffffff';
            if (child.material && child.material.color) {
              initialColor = child.material.color.getHexString();
            }

            // Registrar en nuestro Zustand store
            if (!useInspectorStore.getState().meshes[child.uuid]) {
               addMesh({
                 uuid: child.uuid,
                 name: child.name,
                 visible: child.visible,
                 color: '#' + initialColor
               });
            }
            
            // child.castShadow = true; // Desactivado para evitar crash de GPU
            // child.receiveShadow = true; // Desactivado para evitar crash de GPU
            if (child.material) {
              child.material.needsUpdate = true;
            }
          }
        }
      });
    }
  }, [scene, addMesh]);

  // Aplicar cambios desde la UI en cada frame (render loop)
  useFrame(() => {
    if (!scene) return;
    const states = useInspectorStore.getState().meshes;
    scene.traverse((child: any) => {
      if (child.isMesh) {
        const state = states[child.uuid];
        if (state) {
          child.visible = state.visible;
          if (child.material && child.material.color && state.color.startsWith('#')) {
            child.material.color.setHex(parseInt(state.color.replace('#', ''), 16));
          }
        }
      }
    });
  });

  return (
    <group>
      <primitive object={scene} position={[0, -1, 0]} scale={1} />
    </group>
  );
}

function QISAgentBody() {
  const coreRef = useRef<any>(null);
  const ringRef = useRef<any>(null);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    if (coreRef.current) {
      coreRef.current.rotation.y = t * 1.5;
      coreRef.current.position.y = Math.sin(t * 2) * 0.2 + 1.2;
    }
    if (ringRef.current) {
      ringRef.current.rotation.x = Math.PI / 2 + Math.sin(t) * 0.2;
      ringRef.current.rotation.z = t * 0.5;
      ringRef.current.position.y = Math.sin(t * 2) * 0.2 + 1.2;
    }
  });

  return (
    <group>
      {/* Core AI flotante */}
      <mesh ref={coreRef} castShadow>
        <octahedronGeometry args={[0.4, 0]} />
        <meshStandardMaterial color="#38bdf8" wireframe={true} emissive="#0ea5e9" emissiveIntensity={2} />
      </mesh>
      {/* Anillo de datos orbitando */}
      <mesh ref={ringRef} castShadow>
        <torusGeometry args={[0.7, 0.02, 16, 100]} />
        <meshStandardMaterial color="#94a3b8" metalness={1} roughness={0.1} emissive="#38bdf8" emissiveIntensity={0.5} />
      </mesh>
      {/* Base proyector holográfico */}
      <mesh position={[0, 0.1, 0]}>
        <cylinderGeometry args={[0.3, 0.4, 0.2, 32]} />
        <meshStandardMaterial color="#1e293b" metalness={0.9} roughness={0.2} />
      </mesh>
    </group>
  );
}

function AgentAvatar({ agent }: { agent: AgentDNA }) {
  let modelPath = null;
  let scale = 0.011;

  // UUIDs are used now, so we match by name
  const name = agent.agent_name.toLowerCase();

  if (name.includes('paul')) {
    modelPath = '/paul_talking_business.glb'; // Paul (Humano antiguo)
  } else if (name.includes('sophia')) {
    modelPath = '/models/sophia.glb'; // Sophia (NUEVO MODELO CHARMORPH)
    scale = 1.0; // CharMorph scale is usually 1.0 meters, not 0.011
  } else if (name.includes('travis')) {
    modelPath = '/travis_synth.glb'; // Travis (Sintético)
    scale = 0.5; // Escalar el Synth
  } else if (name.includes('emma')) {
    modelPath = '/emma_synth.glb'; // Emma (Sintética Rosa)
    scale = 0.5;
  } else if (name.includes('marcus')) {
    modelPath = '/marcus_synth.glb'; // Marcus (Sintético Naranja Corpulento)
    scale = 0.5;
  } else if (name.includes('elena')) {
    modelPath = '/elena_synth.glb'; // Elena (Sintética Verde)
    scale = 0.5;
  } else if (name.includes('ganoibot') || name.includes('808')) {
    modelPath = '/executive_in_a_navy_suit.glb';
    scale = 1.1;
  }



  if (!modelPath) {
    return (
      <group position={[0, 1, 0]}>
        <mesh castShadow receiveShadow>
          <capsuleGeometry args={[0.4, 0.8, 4, 16]} />
          <meshStandardMaterial color="#6366f1" roughness={0.2} metalness={0.8} />
        </mesh>
        <mesh position={[0, 0.6, 0.3]}>
          <boxGeometry args={[0.4, 0.2, 0.2]} />
          <meshStandardMaterial color="#10b981" emissive="#10b981" emissiveIntensity={0.5} />
        </mesh>
      </group>
    );
  }

  return <AnimatedHumanoid agent={agent} modelPath={modelPath} scale={scale} />;
}

// Subcomponente separado para poder usar useGLTF dinámicamente sin romper las reglas de React Hooks
function AnimatedHumanoid({ agent, modelPath, scale }: { agent: AgentDNA, modelPath: string, scale: number }) {
  const { scene, animations } = useGLTF(modelPath);
  const { actions } = useAnimations(animations, scene);

  useEffect(() => {
    const actionNames = Object.keys(actions);
    if (actionNames.length > 0) {
      const walkAnim = actionNames.find(n => n.toLowerCase().includes('walk') || n.toLowerCase().includes('run'));
      const idleAnim = actionNames.find(n => n.toLowerCase().includes('idle') || n.toLowerCase().includes('talk'));
      
      const actionName = agent.operational_status === 'idle' || agent.operational_status === 'emergency'
        ? (idleAnim || actionNames[0])
        : (walkAnim || actionNames[0]);
        
      const action = actions[actionName];
      action?.reset().fadeIn(0.3).play();
      
      return () => { action?.fadeOut(0.3); }
    }
  }, [actions, agent.operational_status, agent.current_action]);

  return <primitive object={scene} scale={scale} position={[0, 0, 0]} />; 
}

function VideoScreen() {
  const [video] = useState(() => {
    const vid = document.createElement('video');
    vid.src = '/videos/qis_promo.mp4';
    vid.crossOrigin = 'Anonymous';
    vid.loop = true;
    vid.muted = true; // Empieza muteado por las políticas del navegador
    vid.play();
    return vid;
  });

  const [soundEnabled, setSoundEnabled] = useState(false);

  useEffect(() => {
    if (soundEnabled) {
      video.muted = false;
    }
  }, [soundEnabled, video]);

  return (
    <group position={[0, 0, 0.11]}>
      <mesh>
        <planeGeometry args={[5.8, 3.8]} />
        <meshBasicMaterial toneMapped={false}>
          <videoTexture attach="map" args={[video]} colorSpace={THREE.SRGBColorSpace} />
        </meshBasicMaterial>
      </mesh>
      
      {/* Botón de Audio */}
      <Html position={[0, -0.4, 0.01]} transform scale={0.4}>
        {!soundEnabled && (
          <button 
            onClick={() => setSoundEnabled(true)}
            className="bg-sky-600/80 hover:bg-sky-500 text-white font-bold py-2 px-4 rounded-full border border-sky-400 backdrop-blur-sm pointer-events-auto shadow-[0_0_10px_rgba(56,189,248,0.5)]"
          >
            🔊 Activar Sonido Espacial
          </button>
        )}
      </Html>
      
      {soundEnabled && (
         // PositionalAudio carga el audio y lo emite en 3D
         <PositionalAudio
           url="/videos/qis_promo.mp4"
           ref={(audio: any) => {
             // Sincronizar el audio de PositionalAudio con el video principal para evitar desfaces
             if (audio && !audio.isPlaying) {
               audio.play();
             }
           }}
           loop
         />
      )}
    </group>
  );
}

function AgentMesh({ agent }: { agent: AgentDNA }) {
  const meshRef = useRef<any>(null);
  const [targetVec] = useState(() => new THREE.Vector3());
  const [currentPos] = useState(() => new THREE.Vector3(agent.position[0], -0.98, agent.position[2]));

  useFrame((state, delta) => {
    if (meshRef.current && agent.operational_status !== 'emergency') {
      // Lerp hacia la posicion objetivo
      targetVec.set(agent.target_position[0], -0.98, agent.target_position[2]);
      currentPos.lerp(targetVec, 2.0 * delta); // Velocidad de movimiento
      
      meshRef.current.position.copy(currentPos);
      
      const dir = targetVec.clone().sub(currentPos);
      if (dir.length() > 0.1) {
        const targetRotation = Math.atan2(dir.x, dir.z);
        meshRef.current.rotation.y = THREE.MathUtils.lerp(meshRef.current.rotation.y, targetRotation, 5.0 * delta);
      }
    }
  });

  return (
    <group ref={meshRef} position={[agent.position[0], -0.98, agent.position[2]]}>
      <AgentAvatar agent={agent} />
      
      <group position={[0, 2.2, 0]}>
        {agent.agent_thought && (
          <Html center position={[0, 0.8, 0]} distanceFactor={15} zIndexRange={[100, 0]}>
            <div className="bg-slate-900/80 text-white px-3 py-2 rounded-xl border border-indigo-500/50 text-xs w-56 text-center backdrop-blur-md shadow-lg shadow-indigo-500/30">
              <p className="opacity-90 italic font-medium leading-relaxed">"{agent.agent_thought}"</p>
              <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-0 h-0 border-l-[6px] border-l-transparent border-t-[8px] border-t-indigo-500/50 border-r-[6px] border-r-transparent"></div>
            </div>
          </Html>
        )}
        <Billboard>
          <Text position={[0, 0, 0]} fontSize={0.25} color={agent.operational_status === 'emergency' ? 'red' : 'white'} anchorX="center" anchorY="middle" outlineWidth={0.02} outlineColor="#000000">{agent.agent_name}</Text>
          <Text position={[0, -0.3, 0]} fontSize={0.15} color={agent.operational_status === 'active' ? '#4ade80' : '#f59e0b'} anchorX="center" anchorY="middle">{agent.current_action}</Text>
          <Text position={[0, -0.55, 0]} fontSize={0.12} color="#60a5fa" anchorX="center" anchorY="middle">Balance: {agent.iota_balance} iOTA</Text>
        </Billboard>
      </group>
    </group>
  );
}

function CameraController() {
  const { camera, controls } = useThree() as any;
  const cameraView = useInspectorStore(state => state.cameraView);
  const setCameraView = useInspectorStore(state => state.setCameraView);

  useEffect(() => {
    if (cameraView === 'free') return;
    
    switch (cameraView) {
      case 'top':
        camera.position.set(0, 150, 0);
        break;
      case 'front':
        camera.position.set(0, 15, 100);
        break;
      case 'isometric':
        camera.position.set(70, 70, 70);
        break;
    }
    
    if (controls) {
      controls.target.set(0, 0, 0);
    }
    camera.lookAt(0, 0, 0);
    camera.updateProjectionMatrix();
    
    // Devolver el control al usuario tras el salto
    const timeout = setTimeout(() => setCameraView('free'), 100);
    return () => clearTimeout(timeout);
  }, [cameraView, camera, controls, setCameraView]);

  return null;
}

function SunLight() {
  const elevation = useInspectorStore(state => state.sunElevation);
  const azimuth = useInspectorStore(state => state.sunAzimuth);
  
  const distance = 150;
  const elRad = (elevation * Math.PI) / 180;
  const azRad = (azimuth * Math.PI) / 180;

  const x = distance * Math.cos(elRad) * Math.sin(azRad);
  const y = distance * Math.sin(elRad);
  const z = distance * Math.cos(elRad) * Math.cos(azRad);

  return (
    <directionalLight 
      position={[x, y, z]} 
      intensity={1.5} 
    />
  );
}

function Loader3D() {
  return (
    <Html center>
      <div className="text-white text-sm font-mono whitespace-nowrap bg-indigo-900/50 px-4 py-2 rounded-lg border border-indigo-500 animate-pulse">
        Descargando y compilando Mundo 3D (32 MB)...
      </div>
    </Html>
  );
}

// === INTERFAZ DEL INSPECTOR 3D ===
function InspectorUI() {
  const [isOpen, setIsOpen] = useState(false);
  const { 
    meshes, 
    sunElevation, 
    sunAzimuth, 
    setSunElevation, 
    setSunAzimuth,
    toggleMeshVisibility,
    setMeshColor,
    setCameraView,
    environmentEnabled,
    toggleEnvironment
  } = useInspectorStore();

  const meshList = Object.values(meshes);

  if (!isOpen) {
    return (
      <button 
        onClick={() => setIsOpen(true)}
        className="absolute top-4 right-4 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg font-mono text-sm shadow-xl transition-all z-50 border border-indigo-400"
      >
        🛠️ Inspector 3D
      </button>
    );
  }

  return (
    <div className="absolute top-4 right-4 w-80 bg-slate-900/95 border border-slate-700 rounded-xl shadow-2xl flex flex-col z-50 max-h-[550px] backdrop-blur-sm overflow-hidden">
      <div className="flex justify-between items-center p-3 border-b border-slate-700 bg-slate-800">
        <h3 className="text-indigo-400 font-bold font-mono text-sm flex items-center gap-2">
          <span>🛠️</span> Herramientas SketchUp
        </h3>
        <button onClick={() => setIsOpen(false)} className="text-slate-400 hover:text-white">✕</button>
      </div>

      <div className="p-4 overflow-y-auto custom-scrollbar flex flex-col gap-5">
        
        {/* NAVEGACIÓN */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <h4 className="text-xs text-slate-400 font-bold uppercase">Vistas Rápidas</h4>
            <button 
              onClick={toggleEnvironment} 
              className={`text-[10px] px-2 py-1 rounded border font-bold uppercase ${environmentEnabled ? 'bg-indigo-600/20 text-indigo-400 border-indigo-500/50' : 'bg-slate-800 text-slate-500 border-slate-700 hover:text-slate-300'}`}
            >
              {environmentEnabled ? 'Entorno 3D ON' : 'Entorno 3D OFF'}
            </button>
          </div>
          <div className="grid grid-cols-3 gap-2">
            <button onClick={() => setCameraView('top')} className="bg-slate-800 hover:bg-slate-700 text-white text-xs py-1.5 rounded border border-slate-600 transition-colors">Superior</button>
            <button onClick={() => setCameraView('front')} className="bg-slate-800 hover:bg-slate-700 text-white text-xs py-1.5 rounded border border-slate-600 transition-colors">Frontal</button>
            <button onClick={() => setCameraView('isometric')} className="bg-slate-800 hover:bg-slate-700 text-white text-xs py-1.5 rounded border border-slate-600 transition-colors">Iso 3D</button>
          </div>
        </div>

        {/* LUZ SOLAR */}
        <div>
          <h4 className="text-xs text-slate-400 font-bold mb-2 uppercase">Posición del Sol</h4>
          <div className="flex flex-col gap-3">
            <label className="text-xs text-slate-300 flex flex-col gap-1">
              <span>Elevación ({sunElevation}°)</span>
              <input type="range" min="0" max="90" value={sunElevation} onChange={e => setSunElevation(Number(e.target.value))} className="w-full accent-indigo-500" />
            </label>
            <label className="text-xs text-slate-300 flex flex-col gap-1">
              <span>Rotación / Azimut ({sunAzimuth}°)</span>
              <input type="range" min="0" max="360" value={sunAzimuth} onChange={e => setSunAzimuth(Number(e.target.value))} className="w-full accent-indigo-500" />
            </label>
          </div>
        </div>

        {/* INSPECTOR DE COMPONENTES */}
        <div className="flex-1 flex flex-col">
          <h4 className="text-xs text-slate-400 font-bold mb-2 uppercase">Componentes del Modelo ({meshList.length})</h4>
          <div className="flex flex-col gap-2 max-h-[250px] overflow-y-auto pr-2">
            {meshList.length === 0 ? (
               <p className="text-xs text-slate-500 italic">Cargando mallas...</p>
            ) : meshList.map(mesh => (
              <div key={mesh.uuid} className="flex items-center justify-between bg-slate-800/50 p-2 rounded border border-slate-700/50 hover:border-indigo-500/30 transition-colors">
                <div className="flex items-center gap-2 overflow-hidden">
                  <button 
                    onClick={() => toggleMeshVisibility(mesh.uuid)}
                    className={`text-sm ${mesh.visible ? 'text-indigo-400' : 'text-slate-600'} hover:text-indigo-300`}
                    title="Ocultar/Mostrar"
                  >
                    {mesh.visible ? '👁️' : '🚫'}
                  </button>
                  <span className={`text-xs truncate ${!mesh.visible && 'line-through text-slate-500'}`} title={mesh.name}>
                    {mesh.name.length > 20 ? mesh.name.substring(0, 20) + '...' : mesh.name}
                  </span>
                </div>
                <input 
                  type="color" 
                  value={mesh.color.startsWith('#') ? mesh.color : '#ffffff'} 
                  onChange={(e) => setMeshColor(mesh.uuid, e.target.value)}
                  className="w-5 h-5 rounded cursor-pointer bg-transparent border-0 outline-none p-0"
                  title="Cambiar color del material"
                />
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}

function HolographicLogo() {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);
  const setDossierOpen = useAgentStore(state => state.setDossierOpen);

  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta;
      meshRef.current.rotation.x += delta * 0.5;
      meshRef.current.position.y = 2.5 + Math.sin(state.clock.elapsedTime * 2) * 0.2;
    }
  });

  useEffect(() => {
    document.body.style.cursor = hovered ? 'pointer' : 'auto';
  }, [hovered]);

  return (
    <group 
      position={[0, 2.5, -5]} 
      onClick={(e) => { e.stopPropagation(); setDossierOpen(true); }}
      onPointerOver={(e) => { e.stopPropagation(); setHovered(true); }}
      onPointerOut={() => setHovered(false)}
    >
      <Icosahedron ref={meshRef as any} args={[0.5, 1]} castShadow>
        <meshPhysicalMaterial 
          color="#38bdf8" 
          emissive={hovered ? "#38bdf8" : "#0284c7"} 
          emissiveIntensity={hovered ? 2 : 0.8}
          wireframe={true}
          transparent={true}
          opacity={0.8}
        />
      </Icosahedron>
      <pointLight color="#38bdf8" intensity={hovered ? 10 : 2} distance={3} />
      <Billboard position={[0, -0.8, 0]}>
        <Text fontSize={0.15} color="#ffffff" outlineWidth={0.01} outlineColor="#000000" font="/fonts/space_age.ttf">
          {hovered ? "> TOCA PARA ABRIR DOSSIER <" : "HIVE MIND CENTRAL"}
        </Text>
      </Billboard>
    </group>
  );
}

function AethelOSHeadquarters() {
  const [mapOpen, setMapOpen] = useState(false);

  const sponsors = [
    "AETHEL OS",
    "QUALITY INFORMATIC SOLUTIONS",
    "JOHEROBA IMPORT",
    "KAIROS TRADER",
    "GANOI BOT",
    "EVOTE SHIELD",
    "CIRCULO DORADO"
  ];
  const [currentSponsorIndex, setCurrentSponsorIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSponsorIndex((prev) => (prev + 1) % sponsors.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <group position={[0, -0.98, 0]}>
      {/* Suelo Corporativo Pulido (Mármol/Cristal líquido) */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[100, 100]} />
        <meshStandardMaterial color="#e2e8f0" roughness={0.05} metalness={0.6} />
      </mesh>
      
      {/* Mostrador Virtual de Atención (Centro) */}
      <group position={[0, 0, -5]}>
        <mesh castShadow receiveShadow position={[0, 0.5, 0]}>
          <boxGeometry args={[6, 1, 1.5]} />
          <meshStandardMaterial color="#0f172a" metalness={0.7} roughness={0.2} />
        </mesh>
        {/* Tira LED del mostrador */}
        <mesh position={[0, 0.8, 0.76]}>
          <boxGeometry args={[5.8, 0.05, 0.02]} />
          <meshStandardMaterial color="#38bdf8" emissive="#38bdf8" emissiveIntensity={2} />
        </mesh>
        <Billboard position={[0, 1.5, 0.76]}>
          <Text fontSize={0.3} color="#ffffff" outlineWidth={0.01} outlineColor="#000000">
            RECEPCIÓN
          </Text>
        </Billboard>
      </group>

      {/* Holograma Interactivo del Logo */}
      <HolographicLogo />

      {/* Cartel principal de AethelOS */}
      <Billboard position={[0, 8, -15]}>
        <Text fontSize={2.5} color="#ffffff" outlineWidth={0.1} outlineColor="#000000">
          AethelOS
        </Text>
        <Text position={[0, -1.8, 0]} fontSize={0.6} color="#38bdf8" outlineWidth={0.03} outlineColor="#000000">
          HIVE MIND CENTRAL & VIRTUAL STAFF MANAGEMENT
        </Text>
      </Billboard>

      {/* Pantalla Publicitaria Interactiva (Auspiciadores / Mapa) */}
      <group position={[-8, 3, -10]} rotation={[0, Math.PI / 6, 0]}>
        {/* Marco de la pantalla */}
        <RoundedBox args={[6, 4, 0.2]} radius={0.1} smoothness={4} castShadow>
          <meshStandardMaterial color="#1e293b" metalness={0.9} roughness={0.1} />
        </RoundedBox>
        {/* Video emisor con Audio Espacial */}
        <VideoScreen />
        
        <Text position={[0, 1.4, 0.12]} fontSize={0.3} color="#ffffff" outlineWidth={0.01} outlineColor="#000000">
          AUSPICIADOR OFICIAL
        </Text>
        <Text position={[0, 0.8, 0.12]} fontSize={0.5} color="#38bdf8" outlineWidth={0.02} outlineColor="#000000" maxWidth={5} textAlign="center" font="/fonts/space_age.ttf">
          {sponsors[currentSponsorIndex]}
        </Text>
        
        {/* Botón HTML interactivo sobre el modelo 3D */}
        <Html position={[0, -1.2, 0.12]} transform scale={0.5}>
          <div className="flex gap-4">
            <button 
              onClick={() => setMapOpen(!mapOpen)}
              className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-2 px-4 rounded border-2 border-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.6)] transition-all cursor-pointer pointer-events-auto"
            >
              🗺️ VER MAPA DEL DISTRITO PRIMUS
            </button>
          </div>
        </Html>
        
        {/* Modal del mapa abierto */}
        {mapOpen && (
          <Html position={[0, -3.5, 0.12]} center zIndexRange={[100, 0]}>
            <div className="bg-slate-900/95 border-2 border-indigo-500 rounded-xl p-4 shadow-2xl backdrop-blur-md w-80 text-white font-mono pointer-events-auto text-sm">
              <div className="flex justify-between items-center mb-3 border-b border-slate-700 pb-2">
                <h3 className="font-bold text-indigo-400">🗺️ D I S T R I T O   P R I M U S</h3>
                <button onClick={() => setMapOpen(false)} className="text-slate-400 hover:text-white font-bold">✕</button>
              </div>
              <ul className="space-y-2 mb-4">
                <li className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-blue-500"></span> Sede Central AethelOS (Aquí)</li>
                <li className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-green-500"></span> Quality Informatic Solutions (HQ)</li>
                <li className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-slate-600 border border-slate-400"></span> Parcela 01 (Disponible)</li>
                <li className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-slate-600 border border-slate-400"></span> Parcela 02 (Disponible)</li>
              </ul>
              <button className="w-full bg-slate-800 hover:bg-slate-700 text-xs py-2 rounded border border-slate-600">
                Contactar para adquirir parcela
              </button>
            </div>
          </Html>
        )}
      </group>

      {/* Estaciones de Trabajo (Donde podrían estar los clones) */}
      {[-1, 1].map((x, i) => (
        <group key={i} position={[x * 6, 0, 5]}>
          {/* Base cilindrica */}
          <mesh position={[0, 0.05, 0]}>
            <cylinderGeometry args={[1.5, 1.5, 0.1, 32]} />
            <meshStandardMaterial color="#334155" metalness={0.5} roughness={0.5} />
          </mesh>
          {/* Anillo de luz */}
          <mesh position={[0, 0.1, 0]}>
            <torusGeometry args={[1.4, 0.05, 16, 100]} />
            <meshStandardMaterial color="#818cf8" emissive="#818cf8" emissiveIntensity={1} />
          </mesh>
        </group>
      ))}

    </group>
  );
}

export default function CampusMap() {
  const { agents } = useAgentStore();
  const environmentEnabled = useInspectorStore(state => state.environmentEnabled);

  return (
    <div className="w-full h-[600px] bg-slate-900 rounded-xl overflow-hidden border border-slate-700 relative shadow-2xl">
      <Canvas camera={{ position: [0, 15, 25], fov: 50 }}>
        <CameraController />
        <ambientLight intensity={0.5} />
        <SunLight />
        
        <group>
          <gridHelper args={[150, 150, '#1e293b', '#1e293b']} position={[0, -0.99, 0]} />
          
          <Suspense fallback={<Loader3D />}>
            <AethelOSHeadquarters />
            {environmentEnabled && <EnvironmentMesh />}
            
            {Object.values(agents).map(agent => (
              <AgentMesh key={agent.agent_id} agent={agent} />
            ))}
          </Suspense>
        </group>
        
        <OrbitControls makeDefault minPolarAngle={0} maxPolarAngle={Math.PI / 2.1} />
      </Canvas>
      
      <div className="absolute bottom-4 left-4 text-xs font-mono text-slate-500 bg-black/50 p-2 rounded pointer-events-none">
        MOTOR 3D: AETHEL_ENGINE_V2 <br/>
        PHYSICS: RAPIER (TRIMESH) <br/>
        AI_CORE: AETHELOS CLOUD VPS (ACTIVO)
      </div>

      {/* Montamos la UI HTML por encima del Canvas de React Three Fiber */}
      <InspectorUI />
    </div>
  );
}
