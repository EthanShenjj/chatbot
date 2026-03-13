"""Chat routes for streaming completions."""
from flask import Blueprint, request, Response, stream_with_context, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from app.services.stream_service import StreamService
from app.services.message_service import MessageService
from app.services.context_manager import ContextManager
from app.services.session_service import SessionService
from app.services.message_parser import MessageParser


logger = logging.getLogger(__name__)
bp = Blueprint('chat', __name__, url_prefix='/api/chat')


@bp.route('/completions', methods=['POST'])
@jwt_required()
def chat_completions():
    """
    Handle chat completion requests with SSE streaming.
    
    Implements Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 5.3, 5.4, 12.1, 12.2, 12.4,
    15.1, 15.2, 15.3, 15.4, 15.5:
    - Establishes SSE connection
    - Persists user message before streaming
    - Forwards tokens through SSE stream
    - Sends "data: [DONE]" event on completion
    - Persists complete assistant response after streaming
    - Marks interrupted messages with interrupted flag
    """
    user_id = get_jwt_identity()
    
    try:
        # Parse request data
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        session_id = data.get('session_id')
        messages = data.get('messages', [])
        stream = data.get('stream', True)
        
        # Validate required fields
        if not session_id:
            return jsonify({'error': 'session_id is required'}), 400
        
        if not messages:
            return jsonify({'error': 'messages array is required'}), 400
        
        # Validate session ownership
        if not SessionService.validate_session_ownership(session_id, user_id):
            return jsonify({'error': 'Session not found or access denied'}), 404
        
        # Extract the last message (user's new message)
        last_message = messages[-1]
        
        if last_message.get('role') != 'user':
            return jsonify({'error': 'Last message must have role "user"'}), 400
        
        # Persist user message before streaming (Requirement 12.1)
        try:
            user_content = last_message.get('content')
            MessageService.create_message(
                session_id=session_id,
                role='user',
                content=user_content
            )
            logger.info(f"Persisted user message for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to persist user message: {e}")
            return jsonify({'error': 'Failed to save message'}), 500
        
        # Prepare context with truncation
        context_manager = ContextManager()
        
        # Get existing messages from database for context
        existing_messages = MessageService.get_session_messages(session_id)
        
        # Convert to LLM format
        context_messages = []
        for msg in existing_messages:
            # Convert content to LLM format
            content = msg.content
            
            # For text-only messages, simplify to string format
            if len(content) == 1 and content[0].get('type') == 'text':
                content_str = content[0].get('text', '')
            else:
                content_str = content  # Keep as array for multimodal
            
            context_messages.append({
                'role': msg.role.value if hasattr(msg.role, 'value') else msg.role,
                'content': content_str
            })
        
        # Apply context truncation
        prepared_context = context_manager.prepare_context(
            context_messages,
            session_id=session_id
        )
        
        # Extract model configuration from request
        model_config = {
            'model': data.get('model'),
            'temperature': data.get('temperature'),
            'max_tokens': data.get('max_tokens'),
            'top_p': data.get('top_p')
        }
        # Remove None values
        model_config = {k: v for k, v in model_config.items() if v is not None}
        
        # Create streaming response
        if stream:
            def generate():
                """Generator function for SSE streaming."""
                stream_service = StreamService()
                
                try:
                    # Create stream and accumulate response
                    full_response = ""
                    
                    for chunk in stream_service.create_stream(
                        messages=prepared_context,
                        model_config=model_config
                    ):
                        yield chunk
                        
                        # Extract content from chunk for accumulation
                        if chunk.startswith('data: ') and chunk != "data: [DONE]\n\n":
                            try:
                                import json
                                data_str = chunk[6:].strip()
                                chunk_data = json.loads(data_str)
                                if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                                    delta = chunk_data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        full_response += content
                            except:
                                pass
                    
                    # Persist complete assistant response (Requirement 12.2)
                    if full_response:
                        try:
                            MessageService.create_message(
                                session_id=session_id,
                                role='assistant',
                                content=full_response,
                                interrupted=False
                            )
                            logger.info(f"Persisted assistant response for session {session_id}")
                        except Exception as e:
                            logger.error(f"Failed to persist assistant response: {e}")
                    
                except Exception as e:
                    logger.error(f"Error during streaming: {e}")
                    # Client will handle the error
            
            # Return SSE response (Requirement 4.1)
            return Response(
                stream_with_context(generate()),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no',
                    'Connection': 'keep-alive'
                }
            )
        
        else:
            # Non-streaming response (for compatibility)
            return jsonify({'error': 'Non-streaming mode not implemented'}), 501
    
    except Exception as e:
        logger.error(f"Error in chat completions endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500
