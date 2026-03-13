"""SSE streaming service for LLM integration."""
import json
import logging
from typing import Generator, Dict, Any, Optional
import requests
from config import Config


logger = logging.getLogger(__name__)


class StreamService:
    """
    Service for managing SSE connections and LLM provider streaming.
    
    Implements Requirements 4.1, 4.2, 4.3, 5.1, 5.2:
    - SSE connection management
    - Token forwarding from LLM to client
    - Stream interruption handling
    - Response accumulation for database persistence
    """
    
    def __init__(
        self,
        api_key: str = None,
        endpoint: str = None,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
        top_p: float = None
    ):
        """
        Initialize the stream service.
        
        Args:
            api_key: LLM provider API key (defaults to Config.LLM_API_KEY)
            endpoint: LLM provider endpoint (defaults to Config.LLM_ENDPOINT)
            model: Model name (defaults to Config.LLM_MODEL)
            temperature: Sampling temperature (defaults to Config.LLM_TEMPERATURE)
            max_tokens: Maximum tokens to generate (defaults to Config.LLM_MAX_TOKENS)
            top_p: Nucleus sampling parameter (defaults to Config.LLM_TOP_P)
        """
        self.api_key = api_key or Config.LLM_API_KEY
        self.endpoint = endpoint or Config.LLM_ENDPOINT
        self.model = model or Config.LLM_MODEL
        self.temperature = temperature if temperature is not None else Config.LLM_TEMPERATURE
        self.max_tokens = max_tokens or Config.LLM_MAX_TOKENS
        self.top_p = top_p if top_p is not None else Config.LLM_TOP_P
        
        # Validate API key is configured
        if not self.api_key:
            logger.error("LLM API key is not configured")
    
    def create_stream(
        self,
        messages: list,
        model_config: Optional[Dict[str, Any]] = None
    ) -> Generator[str, None, str]:
        """
        Create an SSE stream that forwards LLM provider responses to the client.
        
        Implements Requirements 4.1, 4.2, 4.3:
        - Establishes SSE connection
        - Forwards tokens immediately
        - Accumulates complete response
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' fields
            model_config: Optional configuration overrides (model, temperature, max_tokens, top_p)
            
        Yields:
            SSE-formatted data strings
            
        Returns:
            Complete accumulated response text
        """
        # Merge model config with defaults
        config = {
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'top_p': self.top_p
        }
        if model_config:
            config.update(model_config)
        
        # Prepare request payload
        payload = {
            'model': config['model'],
            'messages': messages,
            'stream': True,
            'temperature': config['temperature'],
            'max_tokens': config['max_tokens'],
            'top_p': config['top_p']
        }
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        full_response = ""
        
        try:
            # Make streaming request to LLM provider
            logger.info(f"Starting LLM stream request to {self.endpoint}")
            
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                stream=True,
                timeout=60  # 60 second timeout for initial connection
            )
            
            response.raise_for_status()
            
            # Process streaming response
            for line in response.iter_lines():
                if not line:
                    continue
                
                line_str = line.decode('utf-8')
                
                # SSE lines start with "data: "
                if line_str.startswith('data: '):
                    data = line_str[6:]  # Remove "data: " prefix
                    
                    # Check for stream completion
                    if data == '[DONE]':
                        logger.info("LLM stream completed successfully")
                        yield "data: [DONE]\n\n"
                        break
                    
                    # Forward token to client
                    yield f"data: {data}\n\n"
                    
                    # Accumulate response for persistence
                    try:
                        chunk = json.loads(data)
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                full_response += content
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse LLM response chunk: {e}")
                        # Continue streaming even if we can't parse a chunk
                        continue
            
            logger.info(f"Stream completed. Total response length: {len(full_response)} characters")
            return full_response
            
        except requests.exceptions.Timeout as e:
            logger.error(f"LLM request timeout: {e}")
            error_data = json.dumps({
                'error': 'Request timeout',
                'code': 'LLM_TIMEOUT'
            })
            yield f"data: {error_data}\n\n"
            raise
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"LLM connection error: {e}")
            error_data = json.dumps({
                'error': 'Cannot connect to LLM provider',
                'code': 'LLM_CONNECTION_ERROR'
            })
            yield f"data: {error_data}\n\n"
            raise
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"LLM HTTP error: {e}")
            status_code = e.response.status_code if e.response else 'unknown'
            error_data = json.dumps({
                'error': f'LLM provider error: {status_code}',
                'code': 'LLM_HTTP_ERROR'
            })
            yield f"data: {error_data}\n\n"
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error during streaming: {e}")
            error_data = json.dumps({
                'error': 'Internal server error',
                'code': 'SERVER_ERROR'
            })
            yield f"data: {error_data}\n\n"
            raise
