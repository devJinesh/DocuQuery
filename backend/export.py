"""Export functionality for conversations and data."""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from jinja2 import Template
from loguru import logger


class ConversationExporter:
    """Export conversations in various formats."""
    
    def export_json(self, conversation: Dict, output_path: Path) -> str:
        """Export conversation as JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(conversation, f, indent=2, default=str)
        
        logger.info(f"Exported conversation to JSON: {output_path}")
        return str(output_path)
    
    def export_html(self, conversation: Dict, output_path: Path) -> str:
        """Export conversation as HTML."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{{ title }}</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                    max-width: 900px;
                    margin: 40px auto;
                    padding: 20px;
                    background: #f5f5f5;
                }
                .header {
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .message {
                    background: white;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .user-message {
                    background: #e3f2fd;
                    margin-left: 40px;
                }
                .assistant-message {
                    background: white;
                    margin-right: 40px;
                }
                .sender {
                    font-weight: bold;
                    color: #1976d2;
                    margin-bottom: 8px;
                }
                .timestamp {
                    color: #666;
                    font-size: 0.85em;
                    margin-top: 8px;
                }
                .citations {
                    margin-top: 10px;
                    padding-top: 10px;
                    border-top: 1px solid #eee;
                }
                .citation-badge {
                    display: inline-block;
                    background: #1976d2;
                    color: white;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 0.8em;
                    margin-right: 5px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ title }}</h1>
                <p>Exported: {{ export_date }}</p>
                {% if doc_name %}
                <p>Document: {{ doc_name }}</p>
                {% endif %}
            </div>
            
            {% for message in messages %}
            <div class="message {{ 'user-message' if message.sender == 'user' else 'assistant-message' }}">
                <div class="sender">{{ message.sender|title }}</div>
                <div class="text">{{ message.text }}</div>
                {% if message.citations %}
                <div class="citations">
                    <strong>Sources:</strong>
                    {% for citation in message.citations %}
                    <span class="citation-badge">Page {{ citation }}</span>
                    {% endfor %}
                </div>
                {% endif %}
                <div class="timestamp">{{ message.timestamp }}</div>
            </div>
            {% endfor %}
        </body>
        </html>
        """
        
        template = Template(html_template)
        html_content = template.render(
            title=conversation.get('title', 'Conversation'),
            export_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            doc_name=conversation.get('document_name'),
            messages=conversation.get('messages', [])
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Exported conversation to HTML: {output_path}")
        return str(output_path)
    
    def export_markdown(self, conversation: Dict, output_path: Path) -> str:
        """Export conversation as Markdown."""
        md_content = f"# {conversation.get('title', 'Conversation')}\n\n"
        md_content += f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if conversation.get('document_name'):
            md_content += f"**Document:** {conversation['document_name']}\n\n"
        
        md_content += "---\n\n"
        
        for message in conversation.get('messages', []):
            sender = message['sender'].upper()
            md_content += f"## {sender}\n\n"
            md_content += f"{message['text']}\n\n"
            
            if message.get('citations'):
                md_content += "**Sources:** "
                md_content += ", ".join([f"Page {c}" for c in message['citations']])
                md_content += "\n\n"
            
            md_content += f"*{message['timestamp']}*\n\n"
            md_content += "---\n\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(f"Exported conversation to Markdown: {output_path}")
        return str(output_path)


class DataExporter:
    """Export application data."""
    
    def export_document_metadata(self, documents: List[Dict], output_path: Path) -> str:
        """Export document metadata as JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(documents, f, indent=2, default=str)
        
        logger.info(f"Exported document metadata: {output_path}")
        return str(output_path)
    
    def export_statistics(self, stats: Dict, output_path: Path) -> str:
        """Export system statistics."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, default=str)
        
        logger.info(f"Exported statistics: {output_path}")
        return str(output_path)
