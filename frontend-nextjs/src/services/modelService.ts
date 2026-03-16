import { get, post, put, del } from './apiClient';
import type { ModelConfig, ModelConfigForm } from '@/types/model';

class ModelService {
  async getModels(): Promise<ModelConfig[]> {
    const res = await get('/api/models');
    if (!res.ok) throw new Error('Failed to fetch models');
    const data = await res.json();
    return data.models;
  }

  async createModel(form: ModelConfigForm): Promise<ModelConfig> {
    const res = await post('/api/models', form);
    if (!res.ok) throw new Error('Failed to create model');
    return res.json();
  }

  async updateModel(id: string, form: Partial<ModelConfigForm>): Promise<ModelConfig> {
    const res = await put(`/api/models/${id}`, form);
    if (!res.ok) throw new Error('Failed to update model');
    return res.json();
  }

  async deleteModel(id: string): Promise<void> {
    const res = await del(`/api/models/${id}`);
    if (!res.ok) throw new Error('Failed to delete model');
  }
}

export const modelService = new ModelService();
