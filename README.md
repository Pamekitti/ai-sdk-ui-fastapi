# AI SDK Preview Python Streaming

A sophisticated streaming chat application demonstrating real-time AI interactions using FastAPI and Next.js, with advanced message handling and generative UI capabilities.

## Core Technical Architecture

### Message Handling System

The application implements a sophisticated message handling system across multiple layers:

#### 1. Frontend Message Processing
```typescript
// From components/chat.tsx
export function Chat() {
  const chatId = "001";

  const {
    messages,
    setMessages,
    handleSubmit,
    input,
    setInput,
    append,
    isLoading,
    stop,
  } = useChat({
    maxSteps: 4,
    onError: (error) => {
      if (error.message.includes("Too many requests")) {
        toast.error(
          "You are sending too many messages. Please try again later.",
        );
      }
    },
  });
}
```

#### 2. Message Types and Structures
```typescript
// From components/message.tsx
interface PreviewMessageProps {
  chatId: string;
  message: Message;
  isLoading: boolean;
}

export const PreviewMessage = ({
  message,
}: PreviewMessageProps) => {
  return (
    <motion.div
      className="w-full mx-auto max-w-3xl px-4 group/message"
      initial={{ y: 5, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      data-role={message.role}
    >
      {/* Message content rendering */}
    </motion.div>
  );
};
```

#### 3. Server-Side Event (SSE) Protocol
The application uses a custom SSE protocol for real-time message streaming:
```python
# From api/index.py
def stream_text(messages: List[ChatCompletionMessageParam], protocol: str = 'data'):
    draft_tool_calls = []
    draft_tool_calls_index = -1

    stream = client.chat.completions.create(
        messages=messages,
        model=os.environ.get("AZURE_OPENAI_MINI_MODEL"),
        stream=True,
        tools=[{
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather at a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"},
                    },
                    "required": ["latitude", "longitude"],
                },
            },
        }]
    )

    for chunk in stream:
        for choice in chunk.choices:
            if choice.delta.content:
                yield '0:{text}\n'.format(text=json.dumps(choice.delta.content))
```

### Generative UI Components

#### 1. Dynamic Message Rendering
```typescript
// From components/message.tsx
export const PreviewMessage = ({ message }: PreviewMessageProps) => {
  return (
    <motion.div className="w-full mx-auto max-w-3xl px-4 group/message">
      <div className="flex flex-col gap-2 w-full">
        {message.content && (
          <div className="flex flex-col gap-4">
            <Markdown>{message.content as string}</Markdown>
          </div>
        )}

        {message.toolInvocations && message.toolInvocations.length > 0 && (
          <div className="flex flex-col gap-4">
            {message.toolInvocations.map((toolInvocation) => {
              const { toolName, toolCallId, state } = toolInvocation;
              if (state === "result") {
                const { result } = toolInvocation;
                if (toolName === "get_current_weather") {
                  return <Weather key={toolCallId} weatherAtLocation={result} />;
                }
                if (toolName === "generate_mock_chart") {
                  return <Chart key={toolCallId} options={result} />;
                }
              }
              return null;
            })}
          </div>
        )}
      </div>
    </motion.div>
  );
};
```

## Technical Implementation Details

### 1. Backend Stream Processing
```python
# From api/index.py
@app.post("/api/chat")
async def handle_chat_data(request: Request, protocol: str = Query('data')):
    messages = request.messages
    openai_messages = convert_to_openai_messages(messages)
    response = StreamingResponse(stream_text(openai_messages, protocol))
    response.headers['x-vercel-ai-data-stream'] = 'v1'
    return response
```

### 2. Available Tools
```python
# From api/index.py
available_tools = {
    "get_current_weather": get_current_weather,
    "generate_mock_chart": generate_mock_chart,
}
```

## Development Setup

### Backend Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn api.index:app --reload --port 8000
```

### Frontend Setup
```bash
npm install
npm run dev
```

## Environment Configuration

```env
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_API_VERSION=version
AZURE_OPENAI_ENDPOINT=endpoint
AZURE_OPENAI_MINI_MODEL=model_name
```

## Project Structure

```
/
├── api/
│   ├── index.py              # FastAPI application
│   └── utils/
│       ├── message.py        # Message processing
│       ├── stream.py         # Stream handling
│       └── tools.py          # UI generation tools
├── components/
│   ├── chat.tsx             # Main chat interface
│   ├── message.tsx          # Message components
│   └── generative/          # UI generators
│       ├── weather.tsx
│       └── chart.tsx
└── lib/
    ├── hooks/               # Custom React hooks
    └── state/               # State management
```

## Advanced Features

### 1. Streaming Optimization
- Chunk-based message processing
- Efficient memory management
- Automatic reconnection handling

### 2. Dynamic Content Generation
- Real-time chart updates
- Weather visualization
- Interactive UI elements

### 3. Message Processing Pipeline
- Content sanitization
- Markdown rendering
- Code syntax highlighting
- Tool call execution

### 4. State Synchronization
- Optimistic updates
- Error recovery
- State persistence
