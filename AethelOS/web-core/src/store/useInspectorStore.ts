import { create } from 'zustand';

export interface MeshInfo {
  uuid: string;
  name: string;
  visible: boolean;
  color: string;
}

interface InspectorState {
  meshes: Record<string, MeshInfo>;
  sunElevation: number;
  sunAzimuth: number;
  cameraView: 'free' | 'top' | 'front' | 'isometric';
  environmentEnabled: boolean;
  addMesh: (mesh: MeshInfo) => void;
  toggleMeshVisibility: (uuid: string) => void;
  setMeshColor: (uuid: string, color: string) => void;
  setSunElevation: (val: number) => void;
  setSunAzimuth: (val: number) => void;
  setCameraView: (view: 'free' | 'top' | 'front' | 'isometric') => void;
  toggleEnvironment: () => void;
}

export const useInspectorStore = create<InspectorState>((set) => ({
  meshes: {},
  sunElevation: 45,
  sunAzimuth: 45,
  cameraView: 'free',
  environmentEnabled: false,
  addMesh: (mesh) => set((state) => ({ meshes: { ...state.meshes, [mesh.uuid]: mesh } })),
  toggleMeshVisibility: (uuid) => set((state) => {
    const m = state.meshes[uuid];
    if (!m) return state;
    return { meshes: { ...state.meshes, [uuid]: { ...m, visible: !m.visible } } };
  }),
  setMeshColor: (uuid, color) => set((state) => {
    const m = state.meshes[uuid];
    if (!m) return state;
    return { meshes: { ...state.meshes, [uuid]: { ...m, color } } };
  }),
  setSunElevation: (val) => set({ sunElevation: val }),
  setSunAzimuth: (val) => set({ sunAzimuth: val }),
  setCameraView: (view) => set({ cameraView: view }),
  toggleEnvironment: () => set((state) => ({ environmentEnabled: !state.environmentEnabled }))
}));
