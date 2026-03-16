import { getAuthToken } from '@/stores/authStore';
import type { ChatCompletionChunk } from '@/types/api';
import { getApiBaseUrl } from '@/config/environment';

/**
 * SSE Client for streaming chat completions
 * Handles real-time token streaming from the backend using Server-Sent Events
 */
export class SSEClient {
  private abortController: AbortController | null = null;

  /**
   * Stream a chat completion with real-time token delivery
   * 
   * @param sessionId - The session ID for context
   * @param messages - The conversation history
   * @param onToken - Callback for each token received
   * @param onComplete - Callback when stream completes
   * @param onError - Callback for errors
   */
  async streamCompletion(
    sessionId: string,
    messages: Array<{ role: string; content: string | unknown[] }>,
    onToken: (token: string) => void,
    onComplete: () => void,
    onError: (error: Error) => void,
    modelConfigId?: string | null,
  ): Promise<void> {
    // Create new abort controller for this stream
    this.abortController = new AbortController();
    
    const token = getAuthToken();
    
    try {
      const response = await fetch(`${getApiBaseUrl()}/api/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          session_id: sessionId,
          messages: messages,
          stream: true,
          ...(modelConfigId ? { model_config_id: modelConfigId } : {}),
        }),
        signal: this.abortController.signal,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      if (!reader) {
        throw new Error('Response body is not readable');
      }
      
      // Set up abort handler to cancel the reader
      const abortHandler = () => {
        reader.cancel();
      };
      this.abortController.signal.addEventListener('abort', abortHandler);
      
      let buffer = '';
      
      try {
        // Read stream chunks
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) break;
          
          // Decode chunk and add to buffer
          buffer += decoder.decode(value, { stream: true });
          
          // Process complete lines from buffer
          const lines = buffer.split('\n');
          
          // Keep incomplete line in buffer
          buffer = lines.pop() || '';
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6).trim();
              
              // Check for stream completion
              if (data === '[DONE]') {
                onComplete();
                return;
              }
              
              // Parse and extract token
              try {
                const parsed: ChatCompletionChunk = JSON.parse(data);
                // Check for error payload forwarded from backend
                if ((parsed as any).error) {
                  onError(new Error((parsed as any).error));
                  return;
                }
                if (parsed.choices?.[0]?.delta?.content) {
                  onToken(parsed.choices[0].delta.content);
                }
              } catch (e) {
                console.error('Failed to parse SSE data:', e);
              }
            }
          }
        }
        
        // Stream ended without [DONE] — treat as complete
        reader.releaseLock();
        onComplete();
      } finally {
        // Clean up abort handler
        this.abortController?.signal.removeEventListener('abort', abortHandler);
      }
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Stream aborted by user');
        // Don't call onError for user-initiated aborts
      } else {
        onError(error as Error);
      }
    } finally {
      this.abortController = null;
    }
  }

  /**
   * Abort the current stream
   * Used for stream interruption when user stops generation
   */
  abort(): void {
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }
  }

  /**
   * Check if a stream is currently active
   */
  isStreaming(): boolean {
    return this.abortController !== null;
  }
}

/**
 * Singleton instance for use across the application
 */
export const sseClient = new SSEClient();