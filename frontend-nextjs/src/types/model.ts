export interface ModelConfig {
  id: string;
  name: string;
  model_id: string;
  base_url: string;
  has_api_key: boolean;
  is_preset: boolean;
}

export interface ModelConfigForm {
  id?: string;
  name: string;
  model_id: string;
  base_url: string;
  api_key: string;
}
