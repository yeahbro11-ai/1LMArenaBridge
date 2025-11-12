# Context Status Feature - Usage Examples

This document provides practical examples of how to use the new context status feature in LMArenaBridge.

## Example 1: List Models with Context Windows

Request models with their context window information:

```bash
curl -X GET "http://localhost:8000/api/v1/models" \
  -H "Authorization: Bearer sk-lmab-YOUR-API-KEY"
```

Response excerpt:
```json
{
  "object": "list",
  "data": [
    {
      "id": "gemini-2.5-pro",
      "object": "model",
      "created": 1704067200,
      "owned_by": "google",
      "context_window": 1000000,
      "context_window_display": "1,000,000 tokens",
      "context_status": {
        "limit": 1000000,
        "used": 0,
        "remaining": 1000000,
        "percentage_used": 0.0,
        "status": "ok",
        "display": "0/1,000,000 tokens used",
        "next_steps": ""
      }
    },
    {
      "id": "claude-opus-4-1-20250805-thinking-16k",
      "object": "model",
      "created": 1704067200,
      "owned_by": "anthropic",
      "context_window": 200000,
      "context_window_display": "200,000 tokens",
      "context_status": {
        "limit": 200000,
        "used": 0,
        "remaining": 200000,
        "percentage_used": 0.0,
        "status": "ok",
        "display": "0/200,000 tokens used",
        "next_steps": ""
      }
    }
  ]
}
```

## Example 2: Chat Completion with Context Tracking

Send a chat message and receive context status in the response:

```bash
curl -X POST "http://localhost:8000/api/v1/chat/completions" \
  -H "Authorization: Bearer sk-lmab-YOUR-API-KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "user", "content": "What is the capital of France?"}
    ]
  }'
```

Response excerpt:
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1704067200,
  "model": "gpt-4",
  "conversation_id": "a1b2c3d4e5f6",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The capital of France is Paris."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 7,
    "completion_tokens": 8,
    "total_tokens": 15
  },
  "context_status": {
    "limit": 128000,
    "used": 15,
    "remaining": 127985,
    "percentage_used": 0.01,
    "status": "ok",
    "display": "15/128,000 tokens used",
    "next_steps": ""
  }
}
```

## Example 3: Streaming with Real-Time Context Status

Enable streaming to get token counts as the response is generated:

```bash
curl -X POST "http://localhost:8000/api/v1/chat/completions" \
  -H "Authorization: Bearer sk-lmab-YOUR-API-KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "user", "content": "Tell me a short story."}
    ],
    "stream": true
  }'
```

Streaming response chunks (Server-Sent Events):
```
data: {"id":"chatcmpl-xyz","object":"chat.completion.chunk","created":1704067200,"model":"gpt-4","choices":[{"index":0,"delta":{"content":"Once"},"finish_reason":null}],"usage":{"prompt_tokens":6,"completion_tokens":1,"total_tokens":7},"context_status":{"limit":128000,"used":7,"remaining":127993,"percentage_used":0.01,"status":"ok","display":"7/128,000 tokens used","next_steps":""}}

data: {"id":"chatcmpl-xyz","object":"chat.completion.chunk","created":1704067200,"model":"gpt-4","choices":[{"index":0,"delta":{"content":" upon"},"finish_reason":null}],"usage":{"prompt_tokens":6,"completion_tokens":2,"total_tokens":8},"context_status":{"limit":128000,"used":8,"remaining":127992,"percentage_used":0.01,"status":"ok","display":"8/128,000 tokens used","next_steps":""}}

...

data: [DONE]
```

## Example 4: Check Conversation Status

Query the current status of an active conversation:

```bash
curl -X GET "http://localhost:8000/api/v1/conversations/a1b2c3d4e5f6/status" \
  -H "Authorization: Bearer sk-lmab-YOUR-API-KEY"
```

Response:
```json
{
  "conversation_id": "a1b2c3d4e5f6",
  "model": "gpt-4",
  "messages": 4,
  "context_status": {
    "limit": 128000,
    "used": 1850,
    "remaining": 126150,
    "percentage_used": 1.45,
    "status": "ok",
    "display": "1,850/128,000 tokens used",
    "next_steps": ""
  },
  "usage": {
    "prompt_tokens": 850,
    "completion_tokens": 1000,
    "total_tokens": 1850
  },
  "updated_at": 1704067200.123
}
```

## Example 5: Warning Status (75%+ Context Used)

When a conversation approaches 75% of the context window:

```json
{
  "context_status": {
    "limit": 128000,
    "used": 100000,
    "remaining": 28000,
    "percentage_used": 78.13,
    "status": "warning",
    "display": "100,000/128,000 tokens used",
    "next_steps": "Consider trimming your messages or switching to a model with a larger context window."
  }
}
```

## Example 6: Critical Status (90%+ Context Used)

When a conversation reaches 90% of the context window:

```json
{
  "context_status": {
    "limit": 128000,
    "used": 120000,
    "remaining": 8000,
    "percentage_used": 93.75,
    "status": "critical",
    "display": "120,000/128,000 tokens used",
    "next_steps": "Stop the chat, switch to a higher context model, or reset the conversation to avoid errors."
  }
}
```

## Example 7: Context Limit Exceeded

When attempting to send a message that would exceed the context limit:

```bash
curl -X POST "http://localhost:8000/api/v1/chat/completions" \
  -H "Authorization: Bearer sk-lmab-YOUR-API-KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [...]
  }'
```

Error response (HTTP 400):
```json
{
  "detail": "Conversation is at 4,150/4,096 tokens used for model 'gpt-3.5-turbo'. Please reset the session or choose a model with a larger context window before sending more messages."
}
```

## Example 8: List Models for Active Conversation

Get model information with context usage for your current conversation:

```bash
curl -X GET "http://localhost:8000/api/v1/models?conversation_id=a1b2c3d4e5f6" \
  -H "Authorization: Bearer sk-lmab-YOUR-API-KEY"
```

This shows you which models have sufficient remaining capacity to continue your conversation.

## UI Integration Recommendations

### Display Model Selection with Context Info

```typescript
// Example React component
function ModelSelector({ models, conversationId }) {
  return (
    <select>
      {models.map(model => (
        <option key={model.id} value={model.id}>
          {model.id} - {model.context_window_display} 
          ({model.context_status.display})
        </option>
      ))}
    </select>
  );
}
```

### Show Live Context Status in Chat

```typescript
// Example progress bar
function ContextStatusBar({ contextStatus }) {
  const { percentage_used, display, status, next_steps } = contextStatus;
  
  const colors = {
    ok: 'green',
    warning: 'yellow',
    critical: 'red'
  };
  
  return (
    <div>
      <div className="progress-bar">
        <div 
          style={{ 
            width: `${percentage_used}%`, 
            background: colors[status] 
          }}
        />
      </div>
      <p>{display}</p>
      {next_steps && <p className="warning">{next_steps}</p>}
    </div>
  );
}
```

### Poll Conversation Status

```typescript
// Poll every 5 seconds during active chat
useEffect(() => {
  const interval = setInterval(async () => {
    const status = await fetch(
      `/api/v1/conversations/${conversationId}/status`,
      { headers: { 'Authorization': `Bearer ${apiKey}` }}
    );
    const data = await status.json();
    setContextStatus(data.context_status);
  }, 5000);
  
  return () => clearInterval(interval);
}, [conversationId, apiKey]);
```

## Benefits

1. **Proactive Management**: Users can see how much context they're using before hitting limits
2. **Better Model Selection**: Choose models with appropriate context windows for your use case
3. **Avoid Errors**: Prevents 400 Bad Request errors from exhausted context
4. **Smart Switching**: Switch to higher-capacity models when needed
5. **Cost Awareness**: Understand token consumption for cost tracking

## Notes

- Token counts are estimates based on character counts (1 token ≈ 4 characters)
- Actual token counts may vary slightly depending on the model's tokenizer
- Context status is tracked per conversation and persists across requests
- Conversations are keyed by API key + model + first message for automatic session management
