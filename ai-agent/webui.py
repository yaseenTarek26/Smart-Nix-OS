#!/usr/bin/env python3
"""
Web UI - FastAPI server for chat interface and patch preview
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

logger = logging.getLogger(__name__)

class WebUI:
    def __init__(self, agent):
        self.agent = agent
        self.app = FastAPI(title="NixOS AI Agent", version="1.0.0")
        self.connected_clients = set()
        self.setup_routes()

    def setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/")
        async def root():
            return HTMLResponse(content=self._get_html_content())

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.connected_clients.add(websocket)
            
            try:
                while True:
                    data = await websocket.receive_text()
                    message_data = json.loads(data)
                    
                    # Process message through agent
                    response = await self.agent.process_message(
                        message_data.get('message', ''),
                        message_data.get('user_id', 'default')
                    )
                    
                    # Send response back
                    await websocket.send_text(json.dumps(response))
                    
            except WebSocketDisconnect:
                self.connected_clients.remove(websocket)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                self.connected_clients.remove(websocket)

        @self.app.get("/api/status")
        async def get_status():
            return {
                "status": "running",
                "connected_clients": len(self.connected_clients),
                "agent_config": {
                    "llm_provider": self.agent.config.get('llm_provider', 'unknown'),
                    "port": self.agent.config.get('port', 8999)
                }
            }

        @self.app.get("/api/system-info")
        async def get_system_info():
            info = await self.agent.executor.get_system_info()
            return info

        @self.app.get("/api/git-status")
        async def get_git_status():
            status = await self.agent.patcher.get_git_status()
            return status

        @self.app.get("/api/commit-history")
        async def get_commit_history(limit: int = 10):
            history = await self.agent.patcher.get_commit_history(limit)
            return history

    def _get_html_content(self) -> str:
        """Get the HTML content for the web UI"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NixOS AI Agent</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .header h1 {
            color: white;
            text-align: center;
            font-size: 1.5rem;
        }
        
        .main-container {
            flex: 1;
            display: flex;
            padding: 1rem;
            gap: 1rem;
        }
        
        .chat-container {
            flex: 1;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-messages {
            flex: 1;
            padding: 1rem;
            overflow-y: auto;
            max-height: 60vh;
        }
        
        .message {
            margin-bottom: 1rem;
            padding: 0.75rem;
            border-radius: 10px;
            max-width: 80%;
        }
        
        .user-message {
            background: #007bff;
            color: white;
            margin-left: auto;
        }
        
        .ai-message {
            background: #f8f9fa;
            color: #333;
            border: 1px solid #dee2e6;
        }
        
        .error-message {
            background: #dc3545;
            color: white;
        }
        
        .chat-input {
            padding: 1rem;
            border-top: 1px solid #dee2e6;
            display: flex;
            gap: 0.5rem;
        }
        
        .chat-input input {
            flex: 1;
            padding: 0.75rem;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            font-size: 1rem;
        }
        
        .chat-input button {
            padding: 0.75rem 1.5rem;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
        }
        
        .chat-input button:hover {
            background: #0056b3;
        }
        
        .patch-preview {
            flex: 1;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 1rem;
            overflow: hidden;
        }
        
        .patch-preview h3 {
            margin-bottom: 1rem;
            color: #333;
        }
        
        .patch-content {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 1rem;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            white-space: pre-wrap;
            max-height: 40vh;
            overflow-y: auto;
        }
        
        .patch-actions {
            margin-top: 1rem;
            display: flex;
            gap: 0.5rem;
        }
        
        .patch-actions button {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9rem;
        }
        
        .apply-btn {
            background: #28a745;
            color: white;
        }
        
        .reject-btn {
            background: #dc3545;
            color: white;
        }
        
        .edit-btn {
            background: #ffc107;
            color: #333;
        }
        
        .status-bar {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 0.5rem 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            font-size: 0.9rem;
            display: flex;
            justify-content: space-between;
        }
        
        .connection-status {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #28a745;
        }
        
        .status-dot.disconnected {
            background: #dc3545;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 NixOS AI Agent</h1>
    </div>
    
    <div class="main-container">
        <div class="chat-container">
            <div class="chat-messages" id="chatMessages">
                <div class="message ai-message">
                    <strong>AI Agent:</strong> Hello! I'm your NixOS AI assistant. I can help you install packages, configure your system, and manage your Hyprland desktop. What would you like me to do?
                </div>
            </div>
            
            <div class="chat-input">
                <input type="text" id="messageInput" placeholder="Ask me to install a package, configure something, or open an app..." />
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
        
        <div class="patch-preview">
            <h3>Patch Preview</h3>
            <div class="patch-content" id="patchContent">
                No patch to preview
            </div>
            <div class="patch-actions" id="patchActions" style="display: none;">
                <button class="apply-btn" onclick="applyPatch()">Apply</button>
                <button class="reject-btn" onclick="rejectPatch()">Reject</button>
                <button class="edit-btn" onclick="editPatch()">Edit</button>
            </div>
        </div>
    </div>
    
    <div class="status-bar">
        <div class="connection-status">
            <div class="status-dot" id="statusDot"></div>
            <span id="connectionStatus">Connected</span>
        </div>
        <div id="systemInfo">NixOS AI Agent v1.0.0</div>
    </div>

    <script>
        let ws = null;
        let currentPatch = null;
        
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                updateConnectionStatus(true);
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };
            
            ws.onclose = function() {
                updateConnectionStatus(false);
                // Reconnect after 3 seconds
                setTimeout(connectWebSocket, 3000);
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
                updateConnectionStatus(false);
            };
        }
        
        function updateConnectionStatus(connected) {
            const statusDot = document.getElementById('statusDot');
            const statusText = document.getElementById('connectionStatus');
            
            if (connected) {
                statusDot.classList.remove('disconnected');
                statusText.textContent = 'Connected';
            } else {
                statusDot.classList.add('disconnected');
                statusText.textContent = 'Disconnected';
            }
        }
        
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (message && ws) {
                // Add user message to chat
                addMessage(message, 'user');
                
                // Send to server
                ws.send(JSON.stringify({
                    message: message,
                    user_id: 'web_ui'
                }));
                
                input.value = '';
            }
        }
        
        function addMessage(content, sender) {
            const messagesDiv = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            
            const senderName = sender === 'user' ? 'You' : 'AI Agent';
            messageDiv.innerHTML = `<strong>${senderName}:</strong> ${content}`;
            
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function handleMessage(data) {
            if (data.status === 'success') {
                addMessage(data.message || 'Operation completed successfully', 'ai');
                
                if (data.patch) {
                    showPatchPreview(data.patch);
                }
            } else if (data.status === 'error') {
                addMessage(`Error: ${data.error}`, 'ai');
            } else {
                addMessage(data.message || 'Unknown response', 'ai');
            }
        }
        
        function showPatchPreview(patch) {
            const patchContent = document.getElementById('patchContent');
            const patchActions = document.getElementById('patchActions');
            
            patchContent.textContent = patch;
            patchActions.style.display = 'flex';
            currentPatch = patch;
        }
        
        function applyPatch() {
            if (currentPatch && ws) {
                ws.send(JSON.stringify({
                    action: 'apply_patch',
                    patch: currentPatch
                }));
                hidePatchPreview();
            }
        }
        
        function rejectPatch() {
            hidePatchPreview();
        }
        
        function editPatch() {
            // Open patch in external editor
            const blob = new Blob([currentPatch], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'patch.diff';
            a.click();
            URL.revokeObjectURL(url);
        }
        
        function hidePatchPreview() {
            const patchContent = document.getElementById('patchContent');
            const patchActions = document.getElementById('patchActions');
            
            patchContent.textContent = 'No patch to preview';
            patchActions.style.display = 'none';
            currentPatch = null;
        }
        
        // Handle Enter key in input
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // Connect on page load
        connectWebSocket();
    </script>
</body>
</html>
        """

    async def start(self):
        """Start the web UI server"""
        config = uvicorn.Config(
            self.app,
            host="127.0.0.1",
            port=self.agent.config.get('port', 8999),
            log_level="info"
        )
        server = uvicorn.Server(config)
        
        # Start server in background
        asyncio.create_task(server.serve())
        
        logger.info(f"Web UI started on http://127.0.0.1:{self.agent.config.get('port', 8999)}")

    async def stop(self):
        """Stop the web UI server"""
        # Close all WebSocket connections
        for client in self.connected_clients.copy():
            await client.close()
        
        logger.info("Web UI stopped")

    async def broadcast_message(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients"""
        if self.connected_clients:
            message_json = json.dumps(message)
            disconnected = set()
            
            for client in self.connected_clients:
                try:
                    await client.send_text(message_json)
                except:
                    disconnected.add(client)
            
            # Remove disconnected clients
            self.connected_clients -= disconnected
