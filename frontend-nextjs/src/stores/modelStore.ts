import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { modelService } from '@/services/modelService';
import type { ModelConfig, ModelConfigForm } from '@/types/model';

interface ModelState {
  models: ModelConfig[];
  selectedModelId: string | null;
  isLoading: boolean;
  fetchModels: () => Promise<void>;
  selectModel: (id: string) => void;
  createModel: (form: ModelConfigForm) => Promise<void>;
  updateModel: (id: string, form: Partial<ModelConfigForm>) => Promise<void>;
  deleteModel: (id: string) => Promise<void>;
}

export const useModelStore = create<ModelState>()(
  persist(
    (set, get) => ({
      models: [],
      selectedModelId: null,
      isLoading: false,

      fetchModels: async () => {
        set({ isLoading: true });
        try {
          const models = await modelService.getModels();
          set((state) => ({
            models,
            isLoading: false,
            // Auto-select first model if none selected or selected no longer exists
            selectedModelId:
              state.selectedModelId && models.find((m) => m.id === state.selectedModelId)
                ? state.selectedModelId
                : models[0]?.id ?? null,
          }));
        } catch (error) {
          // Silently fail for auth errors - user will be redirected to login
          set({ isLoading: false });
        }
      },

      selectModel: (id) => set({ selectedModelId: id }),

      createModel: async (form) => {
        const model = await modelService.createModel(form);
        set((state) => ({ models: [...state.models, model] }));
      },

      updateModel: async (id, form) => {
        const updated = await modelService.updateModel(id, form);
        set((state) => ({
          models: state.models.map((m) => (m.id === id ? updated : m)),
        }));
      },

      deleteModel: async (id) => {
        await modelService.deleteModel(id);
        set((state) => ({
          models: state.models.filter((m) => m.id !== id),
          selectedModelId: state.selectedModelId === id ? state.models[0]?.id ?? null : state.selectedModelId,
        }));
      },
    }),
    { name: 'model-store', partialize: (s) => ({ selectedModelId: s.selectedModelId }) }
  )
);
