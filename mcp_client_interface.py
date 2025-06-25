# legal_database_gradio.py
import asyncio
import gradio as gr
import dotenv
from llama_index.llms.openai import OpenAI
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent, ToolCallResult, ToolCall
from llama_index.core.workflow import Context
from dotenv import load_dotenv
import os
import datetime
import threading
import time

# Load environment variables
dotenv.load_dotenv()
api_key = os.getenv("OPEN_AI_API_KEY")
llm = OpenAI(model="gpt-4o", api_key=api_key)

SYSTEM_PROMPT = """\
You are LegalMind AI, an advanced AI assistant specialized in Legal Database Management.

You have access to comprehensive tools that enable you to:
- Intelligently manage cases, clients, and legal professionals
- Perform sophisticated searches through legal case databases
- Create and organize new legal records with precision
- Retrieve specific information using various identifiers
- Analyze relationships and patterns between cases, clients, and lawyers
- Provide legal insights and recommendations based on data

Always maintain a professional, knowledgeable tone while being helpful and efficient.
Structure your responses clearly and provide actionable insights when possible.
"""

# Global variables for agent and context
agent = None
agent_context = None
mcp_client = None

class AsyncRunner:
    """Enhanced async runner with better error handling"""
    def __init__(self):
        self.loop = None
        self.thread = None
    
    def start_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def run_async(self, coro):
        if self.loop is None:
            self.thread = threading.Thread(target=self.start_loop, daemon=True)
            self.thread.start()
            # Wait for loop to be ready
            timeout = 10
            while self.loop is None and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1
            
            if self.loop is None:
                raise RuntimeError("Failed to initialize async loop")
        
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result(timeout=30)

async_runner = AsyncRunner()

async def initialize_agent():
    """Initialize the MCP client and agent with enhanced error handling"""
    global agent, agent_context, mcp_client
    
    try:
        # Create MCP client connection
        mcp_client = BasicMCPClient("http://127.0.0.1:3000/sse")
        mcp_tool = McpToolSpec(client=mcp_client)
        
        # Get available tools
        tools_list = await mcp_tool.to_tool_list_async()
        
        # Create the enhanced agent
        agent = FunctionAgent(
            name="LegalMindAI",
            description="An advanced AI agent specialized in legal database management and analysis.",
            tools=tools_list,
            llm=llm,
            system_prompt=SYSTEM_PROMPT,
        )
        
        # Create the agent context
        agent_context = Context(agent)
        
        return True, f"🎯 LegalMind AI activated successfully! Connected with {len(tools_list)} specialized tools."
    except Exception as e:
        return False, f"⚠️ Connection failed: {str(e)}"

async def handle_user_message(message_content: str):
    """Enhanced message handler with better formatting"""
    global agent, agent_context
    
    if agent is None or agent_context is None:
        return "🔌 Please establish connection to the legal database first."
    
    try:
        tool_operations = []
        handler = agent.run(message_content, ctx=agent_context)
        
        async for event in handler.stream_events():
            if type(event) == ToolCall:
                tool_operations.append(f"⚡ Executing: `{event.tool_name}`")
            elif type(event) == ToolCallResult:
                tool_operations.append(f"✓ Completed: `{event.tool_name}`")
        
        response = await handler
        
        # Enhanced response formatting
        if tool_operations:
            operations_text = "\n".join(tool_operations)
            return f"""**🔧 System Operations:**
```
{operations_text}
```

**💡 LegalMind AI Response:**
{str(response)}"""
        else:
            return f"**💡 LegalMind AI Response:**\n{str(response)}"
            
    except Exception as e:
        return f"❌ **Error Processing Request:**\n```\n{str(e)}\n```"

def connect_to_database():
    """Enhanced database connection with status updates"""
    try:
        success, message = async_runner.run_async(initialize_agent())
        
        # Update UI elements based on connection status
        if success:
            return (
                message,
                gr.update(interactive=True, placeholder="Ask LegalMind AI anything about your legal database..."),
                gr.update(interactive=True, variant="primary"),
                gr.update(visible=True),  # Show examples
                gr.update(variant="secondary", value="🔄 Reconnect")  # Update connect button
            )
        else:
            return (
                message,
                gr.update(interactive=False),
                gr.update(interactive=False),
                gr.update(visible=False),  # Hide examples
                gr.update(variant="primary", value="🔗 Connect to Database")
            )
    except Exception as e:
        error_msg = f"⚠️ **Connection Error:**\n```\n{str(e)}\n```"
        return (
            error_msg,
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(visible=False),
            gr.update(variant="primary", value="🔗 Connect to Database")
        )

def process_query(message, history):
    """Enhanced query processing with typing indicators"""
    if not message.strip():
        return history, ""
    
    # Add user message to history
    history.append([message, None])
    
    try:
        # Add typing indicator
        history[-1][1] = "🤔 *LegalMind AI is thinking...*"
        yield history, ""
        
        # Get response from agent
        response = async_runner.run_async(handle_user_message(message))
        
        # Add final response to history
        history[-1][1] = response
        
    except Exception as e:
        history[-1][1] = f"❌ **System Error:**\n```\n{str(e)}\n```"
    
    yield history, ""

def get_example_queries():
    """Enhanced example queries with categories"""
    return {
        "📊 Data Overview": [
            "Show me all cases in the database",
            "Get complete client roster",
            "List all available lawyers and their specializations"
        ],
        "➕ Adding Records": [
            "Add a new client: John Doe, email: john.doe@email.com, phone: +1-555-0123",
            "Create lawyer profile: Sarah Smith, specializing in Criminal Defense",
            "Register new case: 'Corporate Merger Dispute' for client ID 1 with lawyer ID 2"
        ],
        "🔍 Search & Analysis": [
            "Find all contract-related cases",
            "Show cases handled by lawyer ID 1",
            "Search for clients with pending litigation",
            "Analyze case outcomes by lawyer specialization"
        ],
        "📈 Insights": [
            "What are the most common case types?",
            "Which lawyers have the highest case loads?",
            "Show relationship between client ID 1 and their cases"
        ]
    }

def load_example(example):
    """Load example with smooth transition"""
    return example

# Enhanced CSS with modern design principles
modern_css = """
/* Global Styles */
.gradio-container {
    max-width: 100% !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 1rem 2rem !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.app {
    max-width: 100% !important;
}

/* Header Styling */
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    padding: 2rem;
    margin-bottom: 2rem;
    text-align: center;
    color: white;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

.main-title {
    font-size: 2.8rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.main-subtitle {
    font-size: 1.2rem;
    opacity: 0.9;
    font-weight: 300;
}

/* Connection Panel */
.connection-panel {
    background: linear-gradient(145deg, #f8fafc, #e2e8f0);
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.status-display {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    border-left: 4px solid #10b981;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

/* Chat Interface */ 
.chat-interface {
    background: linear-gradient(145deg, #ffffff, #f8fafc);
    border-radius: 20px;
    padding: 1.5rem;
    border: 1px solid #e5e7eb;
    box-shadow: 0 8px 25px rgba(0,0,0,0.08);
}

.chat-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #f3f4f6;
}

.ai-indicator {
    width: 12px;
    height: 12px;
    background: #10b981;
    border-radius: 50%;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* Examples Panel */
.examples-panel {
    background: linear-gradient(145deg, #fef7ff, #f3e8ff);
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid #e9d5ff;
}

.example-category {
    margin-bottom: 1.5rem;
}

.category-title {
    font-weight: 600;
    color: #7c3aed;
    margin-bottom: 0.8rem;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.example-btn {
    margin-bottom: 0.5rem;
    width: 100%;
    text-align: left;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 0.75rem;
    transition: all 0.2s ease;
    font-size: 0.85rem;
    color: #374151;
}

.example-btn:hover {
    background: #f8fafc;
    border-color: #7c3aed;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(124, 58, 237, 0.15);
}

/* System Info */
.system-info {
    background: linear-gradient(145deg, #f0fdf4, #dcfce7);
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid #bbf7d0;
}

.info-grid {
    display: grid;
    gap: 0.75rem;
}

.info-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem;
    background: white;
    border-radius: 8px;
    font-size: 0.85rem;
}

.info-label {
    font-weight: 500;
    color: #374151;
}

.info-value {
    color: #059669;
    font-family: monospace;
}

/* Input Styling */
.message-input {
    border-radius: 12px !important;
    border: 2px solid #e5e7eb !important;
    padding: 1rem !important;
    font-size: 1rem !important;
    transition: all 0.2s ease !important;
    min-height: 50px !important;
}

.message-input:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.1) !important;
}

/* Input Row Alignment */
.gradio-row {
    align-items: flex-end !important;
    gap: 0.75rem !important;
}

/* Button Styling */
.primary-btn {
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    color: white !important;
    transition: all 0.2s ease !important;
    min-height: 50px !important;
}

.primary-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(124, 58, 237, 0.3) !important;
}

/* Send Button Styling */
button {
    min-height: 70px !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}

/* Footer */
.footer {
    text-align: center;
    margin-top: 3rem;
    padding: 2rem;
    background: linear-gradient(145deg, #1f2937, #374151);
    color: white;
    border-radius: 16px;
}

/* Responsive Design */
@media (max-width: 1200px) {
    .gradio-container { padding: 1rem !important; }
}

@media (max-width: 768px) {
    .main-title { font-size: 2rem; }
    .main-subtitle { font-size: 1rem; }
    .gradio-container { padding: 0.5rem !important; } 
}

/* Hide Gradio Footer */
footer { visibility: hidden !important; }

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f5f9;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
}
"""

# Create the enhanced Gradio interface
with gr.Blocks(
    css=modern_css, 
    title="LegalMind AI - Advanced Legal Database Assistant", 
    theme=gr.themes.Soft()
) as demo:
    
    # Enhanced Header
    gr.HTML("""
        <div class="main-header">
            <div class="main-title">⚖️ LegalMind AI</div>
            <div class="main-subtitle">Advanced Legal Database Management & Intelligence System</div>
        </div>
    """)
    
    with gr.Row():
        # Main Chat Column
        with gr.Column(scale=3):
            # Connection Panel
            with gr.Group(elem_classes="connection-panel"):
                gr.HTML("""
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                        <span style="font-size: 1.5rem;">🔌</span>
                        <h3 style="margin: 0; color: #374151;">Database Connection</h3>
                    </div>
                """)
                
                connection_status = gr.Textbox(
                    label="Connection Status",
                    value="🔴 Disconnected - Ready to connect to legal database",
                    interactive=False,
                    lines=2,
                    elem_classes="status-display"
                )
                
                connect_btn = gr.Button(
                    "🔗 Connect to Database",
                    variant="primary",
                    size="lg",
                    elem_classes="primary-btn"
                )
            
            # Chat Interface
            with gr.Group(elem_classes="chat-interface"):
                gr.HTML("""
                    <div class="chat-header">
                        <span style="font-size: 1.5rem;">🤖</span>
                        <h3 style="margin: 0; color: #374151;">LegalMind AI Assistant</h3>
                        <div class="ai-indicator"></div>
                    </div>
                """)
                
                chatbot = gr.Chatbot(
                    height=500,
                    label="",
                    avatar_images=("user.png","bot.png"),
                    bubble_full_width=False,
                    show_copy_button=True,
                    placeholder="LegalMind AI is ready to assist you with legal database management..."
                )
                
                with gr.Row():
                    msg_input = gr.Textbox(
                        placeholder="Connect to database first...",
                        label="",
                        scale=5,
                        interactive=False,
                        elem_classes="message-input",
                        container=False,
                        show_label=False
                    )
                    send_btn = gr.Button(
                        "📤 Send", 
                        variant="secondary", 
                        interactive=False,
                        size="lg",
                        scale=1,
                        min_width=100
                    )
        
        # Sidebar Column
        with gr.Column(scale=1):
            # Example Queries Panel
            examples_panel = gr.Group(elem_classes="examples-panel", visible=False)
            with examples_panel:
                gr.HTML("""
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                        <span style="font-size: 1.5rem;">💡</span>
                        <h3 style="margin: 0; color: #7c3aed;">Example Queries</h3>
                    </div>
                """)
                
                examples = get_example_queries()
                example_buttons = []
                
                for category, queries in examples.items():
                    with gr.Group(elem_classes="example-category"):
                        gr.HTML(f'<div class="category-title">{category}</div>')
                        for query in queries:
                            btn = gr.Button(
                                query,
                                size="sm",
                                variant="secondary",
                                elem_classes="example-btn"
                            )
                            example_buttons.append((btn, query))
            
            # System Information Panel
            with gr.Group(elem_classes="system-info"):
                gr.HTML("""
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                        <span style="font-size: 1.5rem;">📊</span>
                        <h3 style="margin: 0; color: #059669;">System Status</h3>
                    </div>
                """)
                
                gr.HTML(f"""
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="info-label">AI Model:</span>
                            <span class="info-value">GPT-4o</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">MCP Server:</span>
                            <span class="info-value">localhost:3000</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Interface:</span>
                            <span class="info-value">v2.0.0</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Last Updated:</span>
                            <span class="info-value">{datetime.datetime.now().strftime('%H:%M')}</span>
                        </div>
                    </div>
                """)
    
    # Event Handlers
    connect_btn.click(
        fn=connect_to_database,
        outputs=[connection_status, msg_input, send_btn, examples_panel, connect_btn],
        show_progress=True
    )
    
    # Chat functionality with generator for typing effect
    msg_input.submit(
        fn=process_query,
        inputs=[msg_input, chatbot],
        outputs=[chatbot, msg_input],
        show_progress=True
    )
    
    send_btn.click(
        fn=process_query,
        inputs=[msg_input, chatbot],
        outputs=[chatbot, msg_input],
        show_progress=True
    )
    
    # Example button handlers
    for btn, example in example_buttons:
        btn.click(
            fn=lambda ex=example: ex,
            outputs=[msg_input]
        )
    
    # Enhanced Footer
    gr.HTML("""
        <div class="footer">
            <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 1rem;">
                <span style="font-size: 2rem;">⚖️</span>
                <div>
                    <div style="font-size: 1.2rem; font-weight: 600;">LegalMind AI</div>
                    <div style="opacity: 0.8;">Powered by OpenAI GPT-4o & MCP Protocol</div>
                </div>
            </div>
            <div style="opacity: 0.6; font-size: 0.9rem;">
                Advanced Legal Database Intelligence • Secure • Professional • Efficient
            </div>
        </div>
    """)

# Launch configuration
if __name__ == "__main__":
    print("🚀 Launching LegalMind AI Interface...")
    print("🔧 Ensure MCP server is running on http://127.0.0.1:3000/sse")
    print("🌐 Interface will be available at: http://localhost:7860")
    print("⚖️ LegalMind AI - Advanced Legal Database Management System")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False,
        show_error=True,
        quiet=False
    )