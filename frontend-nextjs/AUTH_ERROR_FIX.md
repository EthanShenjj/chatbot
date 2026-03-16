# 认证错误修复

## 问题描述
应用在启动时出现 401 Unauthorized 错误，导致控制台报错：
```
Uncaught (in promise) Error: Unauthorized - please login again
```

## 根本原因
1. `ChatInterface` 组件在挂载时立即调用 `fetchSessions()`
2. 如果 token 过期或无效，API 返回 401 错误
3. 错误没有被正确处理，导致控制台报错

## 解决方案

### 1. 自动登出机制
在 `apiClient.ts` 中，当检测到 401 错误时自动登出用户：
```typescript
if (response.status === 401) {
  const { useAuthStore } = await import('@/stores/authStore');
  useAuthStore.getState().logout();
  throw new Error('Unauthorized - please login again');
}
```

### 2. 改进错误处理
在 `sessionStore.ts` 中，对认证错误进行特殊处理：
- 不设置错误状态（避免显示错误消息）
- 不抛出异常（避免控制台报错）
- 用户会被自动重定向到登录页面

### 3. 条件性数据获取
在 `ChatInterface.tsx` 中，只在用户已认证时获取会话：
```typescript
useEffect(() => {
  if (username) {
    fetchSessions();
  }
}, [fetchSessions, username]);
```

### 4. 初始化状态管理
在 `page.tsx` 中添加初始化状态，避免在认证初始化前渲染组件。

### 5. 全局错误边界
添加 `ErrorBoundary` 组件捕获未处理的错误，提供友好的错误界面。

## 测试建议
1. 清除 localStorage 中的 token
2. 刷新页面
3. 应该看到登录页面，而不是控制台错误
