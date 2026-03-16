# Add Model 功能使用指南

## 功能概述
Add Model 功能允许用户添加自定义的 AI 模型配置，支持任何兼容 OpenAI API 格式的模型服务。

## 使用步骤

### 1. 打开模型配置界面
有两种方式打开：
- 点击顶部导航栏的模型选择器旁边的设置图标 ⚙️
- 点击模型下拉菜单底部的 "Manage Models" 按钮

### 2. 添加新模型
1. 在左侧模型列表底部点击 "Add model" 按钮
2. 填写以下信息：
   - **Display Name**: 模型的显示名称（例如：My GPT-4）
   - **Model ID**: 模型的标识符（例如：gpt-4o, moonshot-v1-8k）
   - **Base URL**: API 端点地址（例如：https://api.openai.com/v1/chat/completions）
   - **API Key**: 你的 API 密钥（例如：sk-...）

3. 点击 "Save" 按钮保存

### 3. 使用新添加的模型
- 保存后，新模型会出现在模型列表中
- 点击顶部的模型选择器，选择你刚添加的模型
- 开始对话即可使用该模型

## 支持的模型服务

### OpenAI
```
Display Name: GPT-4o
Model ID: gpt-4o
Base URL: https://api.openai.com/v1/chat/completions
API Key: sk-...
```

### Kimi (月之暗面)
```
Display Name: Kimi K2.5
Model ID: moonshot-v1-8k
Base URL: https://api.moonshot.cn/v1/chat/completions
API Key: sk-...
```

### DeepSeek
```
Display Name: DeepSeek V3
Model ID: deepseek-chat
Base URL: https://api.deepseek.com/v1/chat/completions
API Key: sk-...
```

### Google Gemini
```
Display Name: Gemini 2.5 Flash
Model ID: gemini-2.5-flash-preview-05-20
Base URL: https://generativelanguage.googleapis.com/v1beta/openai/chat/completions
API Key: your-google-api-key
```

### 其他兼容 OpenAI API 的服务
只要服务提供商支持 OpenAI 兼容的 API 格式，都可以添加使用。

## 编辑和删除模型

### 编辑模型
1. 在模型配置界面，点击左侧列表中的模型
2. 修改需要更改的字段
3. 点击 "Save" 保存更改

**注意**: 编辑时如果不填写 API Key 字段，将保留原有的密钥

### 删除模型
1. 在模型配置界面，点击左侧列表中的模型
2. 点击底部的 "Delete" 按钮
3. 确认删除

## 预设模型
系统预设了以下模型（需要配置 API Key）：
- Kimi K2.5
- DeepSeek V3
- Gemini 2.5 Flash Preview

这些预设模型可以直接编辑添加 API Key 使用。

## API Key 安全
- API Key 存储在后端服务器
- 前端永远不会显示完整的 API Key
- 列表中只显示是否已配置 API Key（🔑 图标）

## 故障排除

### 模型无法使用
1. 检查 API Key 是否正确配置
2. 确认 Base URL 格式正确（必须是完整的 URL）
3. 验证 Model ID 是否与服务提供商的文档一致
4. 检查网络连接和 API 服务状态

### 保存失败
- 确保所有必填字段都已填写
- Display Name、Model ID 和 Base URL 都是必填项
- API Key 在创建新模型时是必填的

## 技术实现

### 前端
- **组件**: `ModelSelector.tsx`
- **状态管理**: `modelStore.ts` (Zustand)
- **API 服务**: `modelService.ts`

### 后端
- **路由**: `/api/models` (GET, POST, PUT, DELETE)
- **服务**: `model_config_service.py`
- **存储**: `instance/models.json`

### API 端点
```
GET    /api/models          - 获取所有模型
POST   /api/models          - 创建新模型
PUT    /api/models/:id      - 更新模型
DELETE /api/models/:id      - 删除模型
```

## 数据格式

### ModelConfig (前端)
```typescript
{
  id: string;
  name: string;
  model_id: string;
  base_url: string;
  has_api_key: boolean;
  is_preset: boolean;
}
```

### ModelConfigForm (表单)
```typescript
{
  id?: string;
  name: string;
  model_id: string;
  base_url: string;
  api_key: string;
}
```
