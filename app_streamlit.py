import streamlit as st
import requests
import time
import os

api_url = "http://localhost:8000/meeting"

st.title("AI Meeting Minutes Generator")

tab1, tab2 = st.tabs(["Upload Transcript", "Upload Audio/Video"])

with tab1:
    st.header("Upload Meeting Transcript")
    transcript_file = st.file_uploader("Choose a transcript file", type=["txt", "doc", "docx"])
    
    if transcript_file is not None and st.button("Generate Minutes", key="transcript_btn"):
        with st.spinner("Processing transcript..."):
            files = {"file": transcript_file.getvalue()}
            response = requests.post(f"{api_url}/upload/text", files=files)
            
            if response.status_code == 200:
                job_id = response.json()["job_id"]
                
                status = "processing"
                while status == "processing":
                    time.sleep(2)
                    status_response = requests.get(f"{api_url}/status/{job_id}")
                    status = status_response.json()["status"]
                
                if status == "completed":
                    st.success("Meeting minutes generated successfully!")
                    download_url = f"{api_url}/download/{job_id}"
                    st.markdown(f"[Download Meeting Minutes]({api_url}/download/{job_id})")
                else:
                    st.error("An error occurred during processing.")
            else:
                st.error("Failed to upload file.")

with tab2:
    st.header("Upload Meeting Audio/Video")
    media_file = st.file_uploader("Choose an audio or video file", type=["mp3", "wav", "mp4"])
    
    if media_file is not None and st.button("Generate Minutes", key="media_btn"):
        with st.spinner("Processing audio/video... This may take a while."):
            files = {"file": media_file.getvalue()}
            response = requests.post(f"{api_url}/upload/media", files=files)
            
            if response.status_code == 200:
                job_id = response.json()["job_id"]
                
                status = "processing"
                while status == "processing":
                    time.sleep(5)
                    status_response = requests.get(f"{api_url}/status/{job_id}")
                    status = status_response.json()["status"]
                
                if status == "completed":
                    st.success("Meeting minutes generated successfully!")
                    download_url = f"{api_url}/download/{job_id}"
                    st.markdown(f"[Download Meeting Minutes]({api_url}/download/{job_id})")
                    
                    st.markdown(f"[Download Transcript]({api_url}/download/{job_id}_transcript)")
                else:
                    st.error("An error occurred during processing.")
            else:
                st.error("Failed to upload file.")