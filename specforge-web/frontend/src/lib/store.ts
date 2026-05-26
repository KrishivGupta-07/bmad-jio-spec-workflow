import { create } from "zustand";

type UIState = {
  autoAdvance: boolean;
  setAutoAdvance: (v: boolean) => void;
  selectedRunId: number | null;
  setSelectedRunId: (id: number | null) => void;
  selectedArtifactKind: string | null;
  setSelectedArtifactKind: (kind: string | null) => void;
  installerOutput: string | null;
  setInstallerOutput: (output: string | null) => void;
};

export const useUIStore = create<UIState>((set) => ({
  autoAdvance: false,
  setAutoAdvance: (v) => set({ autoAdvance: v }),
  selectedRunId: null,
  setSelectedRunId: (id) => set({ selectedRunId: id }),
  selectedArtifactKind: null,
  setSelectedArtifactKind: (kind) => set({ selectedArtifactKind: kind }),
  installerOutput: null,
  setInstallerOutput: (output) => set({ installerOutput: output }),
}));
