# Meeting-Note-Tool

## Introduction

Meeting-Note-Tool is an AI-powered application that automatically generates meeting minutes from text transcripts or audio/video files. This tool helps save time on note-taking and creates professional meeting documentation.

## Key Features

- **Process text transcript files** (.txt, .doc, .docx)
- **Process audio/video files** (.mp3, .wav, .mp4)
- **Automatically convert speech to text** using Speech-to-Text technology
- **Generate structured meeting minutes** with sections for:
  - Meeting information
  - Attendees
  - Discussion topics
  - Key decisions
  - Action items
- **Export minutes to Word files** (.docx) with professional formatting
- **User-friendly interface** built with Streamlit
- **RESTful API** built with FastAPI

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/buithanhdam/meeting-note-tool.git
cd meeting-note-tool
```

### 2. Create and activate a virtual environment (Optional)

- **For Unix/macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- **For Windows:**
  ```bash
  python -m venv venv
  .\venv\Scripts\activate
  ```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Setup Environment Variables

Copy the `.env.example` file to a new `.env` file and update the API keys:

```bash
cp .env.example .env
```

Add the following keys:

```plaintext
GOOGLE_API_KEY=
GOOGLE_MODEL=models/gemini-2.0-flash
```

## Testing

### Prerequisites for Text Transcript Processing

- No need to install anything just play.

### Prerequisites for Audio/Video Processing

To process audio/video files, FFmpeg is required:

#### For Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

#### For macOS (Homebrew)
```bash
brew install ffmpeg
```

#### For Windows
1. Download FFmpeg from [FFmpeg official website](https://ffmpeg.org/download.html).
2. Extract the files and add the `bin` folder to your system's PATH.
3. Restart your terminal and verify installation with:
   ```bash
   ffmpeg -version
   ```

## Running the Application

### 1. Run FastAPI Backend

```bash
uvicorn app_fastapi:app --host 0.0.0.0 --port 8000 --reload
```

- Access the API at: `http://127.0.0.1:8000`

### 2. Run Streamlit Frontend

```bash
streamlit run app_streamlit.py --server.port=8501 --server.address=0.0.0.0
```

- Access the frontend UI at: `http://localhost:8501`

## Run with Docker

### 1. Build Docker Images
- If you don't have `docker-compose` use `docker compose` instead
```bash
docker-compose build
```

### 2. Start Docker Containers

```bash
docker-compose up
```

- The backend will be available at `http://localhost:8000`.
- The frontend will be available at `http://localhost:8501`.

### 3. Stop Docker Containers

To stop the running containers, press `Ctrl+C` or run:

```bash
docker-compose down
```

## Architecture

The application follows a client-server architecture:

- **Frontend**: Streamlit app that provides a user interface for uploading files and downloading results
- **Backend**: FastAPI server that processes files and generates meeting minutes
- **Processing Pipeline**:
  - Text files: Direct processing through LLM for summarization
  - Audio/Video files: Conversion to audio → Speech-to-Text → LLM summarization

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Text Processing**: LlamaIndex
- **Document Export**: Python-docx (with templates)
- **Data Storage**: SQLite
- **Audio Processing**: Pydub
- **Speech-to-Text**: OpenAI Whisper API
- **LLM Integration**: OpenAI GPT-4o-mini

## Contributing

Feel free to open an issue or submit a pull request to improve this project.

## License

This project is licensed under the MIT License.