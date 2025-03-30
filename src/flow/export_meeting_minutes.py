from llama_index.llms.openai import OpenAI
import os
import docx
from src.config import GLOBAL_CONFIG
from src.prompts import INSTRUCTIONS_CREATE_MEETING_MINUTES, SYSTEM_PROMPT, EXAMPLE_OUTPUT
from llama_index.core.llms import ChatMessage
import markdown

def _extract_response(self, response) -> str:
        """Trích xuất text từ response của model."""
        try:
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'content'):
                return response.content.parts[0].text
            else:
                return response.message.content
        except Exception as e:
            return response.message.content
        
def export_meeting_minutes(transcript_path):
    """Xử lý transcript thành meeting minutes"""
    # Đọc file transcript
    with open(transcript_path, 'r') as f:
        transcript_text = f.read()
    
    # Sử dụng LlamaIndex và GPT để tóm tắt
    llm = OpenAI(
        model=GLOBAL_CONFIG.OPENAI_MODEL,
        api_key=GLOBAL_CONFIG.OPENAI_API_KEY
    )
    
    messages = [
        ChatMessage(
            role="system", content=SYSTEM_PROMPT
        ),
        ChatMessage(
            role="system", content=INSTRUCTIONS_CREATE_MEETING_MINUTES
        ),
        ChatMessage(
            role="assistant", content=EXAMPLE_OUTPUT
        ),
        ChatMessage(role="user", content="Meeting transcript text: " + transcript_text),
    ]
    # Gọi API để nhận kết quả
    resp = llm.chat(messages)
    
    return _extract_response(resp)

def export_to_word(meeting_minutes_markdown: str):
    """Export meeting minutes in Markdown format to a Word (.docx) file."""
    # Convert Markdown to HTML
    html_content = markdown.markdown(meeting_minutes_markdown)
    print(meeting_minutes_markdown)
    # Create a new Word document
    doc = docx.Document()
    
    # Split the converted HTML into lines and process them
    for line in html_content.split('\n'):
        line = line.strip()
        if line.startswith("<h1>"):
            doc.add_heading(line.replace("<h1>", "").replace("</h1>", ""), level=1)
        elif line.startswith("<h2>"):
            doc.add_heading(line.replace("<h2>", "").replace("</h2>", ""), level=2)
        elif line.startswith("<h3>"):
            doc.add_heading(line.replace("<h3>", "").replace("</h3>", ""), level=3)
        elif line.startswith("<ul>") or line.startswith("<ol>"):
            continue  # Ignore opening list tags
        elif line.startswith("<li>"):
            doc.add_paragraph(line.replace("<li>", "- ").replace("</li>", ""), style="ListBullet")
        else:
            doc.add_paragraph(line)
    
    # Save the document
    output_path = os.path.join(GLOBAL_CONFIG.output_path, "meeting_minutes.docx")
    doc.save(output_path)
    return output_path