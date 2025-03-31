import streamlit as st
import requests
import time
import os
from src.logger import get_formatted_logger

logger = get_formatted_logger(__name__)
api_url = "http://localhost:8000/meeting"

st.title("AI Meeting Minutes Generator")

tab1, tab2 = st.tabs(["Upload Transcript", "Upload Audio/Video"])

def process_file(file, endpoint):
    """Process file upload and handle API interaction with proper error handling"""
    try:
        logger.info(f"Uploading file to {endpoint}")
        files = {"file": file.getvalue()}
        progress_bar = st.progress(0)
        response = requests.post(f"{api_url}/{endpoint}", files=files)
        progress_bar.progress(20)
        if response.status_code == 200:
            job_id = response.json()["job_id"]
            status = response.json()["status"]
            logger.info(f"File uploaded successfully. Job ID: {job_id}, Status: {status}")
            
            # Create a progress bar and status display
            progress_text = "Processing your file. Please wait..."
            status_placeholder = st.empty()
            details_placeholder = st.empty()
            
            for i in range(100):
                # Check status every few iterations
                if i % 5 == 0:
                    try:
                        status_response = requests.get(f"{api_url}/status/{job_id}")
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            current_status = status_data["status"]
                            
                            if current_status == "COMPLETED":
                                progress_bar.progress(100)
                                status_placeholder.success("Processing completed successfully!")
                                
                                # Get job details
                                details_response = requests.get(f"{api_url}/details/{job_id}")
                                if details_response.status_code == 200:
                                    details = details_response.json()
                                    
                                    # Display metadata if available
                                    if details.get("metadata"):
                                        with st.expander("Meeting Details"):
                                            st.json(details["metadata"])
                                    
                                    # Provide download links
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.markdown(f"### [Download Meeting Minutes]({api_url}/download/{job_id})")
                                    
                                    # Only show transcript download for media files
                                    if endpoint == "upload/media":
                                        with col2:
                                            st.markdown(f"### [Download Transcript]({api_url}/download/{job_id}/transcript)")
                                
                                return True
                            
                            elif current_status == "FAILED":
                                progress_bar.progress(100)
                                error_msg = status_data.get("error", "Unknown error")
                                status_placeholder.error(f"Processing failed: {error_msg}")
                                return False
                            
                            # Update status text with more details
                            status_text = f"{progress_text} ({i+1}%)\nStatus: {current_status}"
                            if status_data.get("processing_time"):
                                status_text += f"\nElapsed: {status_data['processing_time']}s"
                            status_placeholder.text(status_text)
                            
                        else:
                            logger.warning(f"Status check failed: {status_response.status_code}")
                    
                    except Exception as e:
                        logger.error(f"Error checking status: {str(e)}")
                        status_placeholder.warning(f"Status check failed: {str(e)}")
                
                # Update progress bar
                progress_bar.progress(i + 1)
                time.sleep(0.2)
                
            # If we get here, we timed out
            logger.warning(f"Job {job_id} processing timed out")
            status_placeholder.warning("Processing is taking longer than expected. The job is still running in the background.")
            return False
        
        else:
            error_msg = response.json().get("detail", response.text)
            logger.error(f"API error: {response.status_code} - {error_msg}")
            st.error(f"Failed to upload file: {error_msg}")
            return False
    
    except Exception as e:
        logger.error(f"Exception during file processing: {str(e)}")
        st.error(f"An error occurred: {str(e)}")
        return False

with tab1:
    st.header("Upload Meeting Transcript")
    st.markdown("""
    **Supported formats:** TXT, DOC, DOCX  
    **Note:** For best results, ensure your transcript is well-formatted with speaker identification.
    """)
    
    transcript_file = st.file_uploader(
        "Choose a transcript file", 
        type=["txt", "doc", "docx"],
        key="transcript_uploader"
    )
    
    if transcript_file is not None:
        st.info(f"File selected: {transcript_file.name}")
        if st.button("Generate Minutes", key="transcript_btn"):
            with st.spinner("Processing your transcript..."):
                logger.info(f"Processing transcript file: {transcript_file.name}")
                process_file(transcript_file, "upload/text")

with tab2:
    st.header("Upload Meeting Audio/Video")
    st.markdown("""
    **Supported formats:** MP3, WAV, MP4  
    **Note:** Larger files may take longer to process. For videos, only audio will be extracted.
    """)
    
    media_file = st.file_uploader(
        "Choose an audio or video file", 
        type=["mp3", "wav", "mp4"],
        key="media_uploader"
    )
    
    if media_file is not None:
        st.info(f"File selected: {media_file.name}")
        if st.button("Generate Minutes", key="media_btn"):
            with st.spinner("Processing your media file..."):
                logger.info(f"Processing media file: {media_file.name}")
                process_file(media_file, "upload/media")

# Add a section for job status lookup
st.markdown("---")
st.subheader("Check Job Status")
job_id_input = st.text_input("Enter a Job ID to check its status:")

if job_id_input:
    try:
        response = requests.get(f"{api_url}/status/{job_id_input}")
        if response.status_code == 200:
            status_data = response.json()
            
            st.json(status_data)
            
            if status_data["status"] == "COMPLETED":
                st.success("This job has completed successfully!")
                if st.button(f"Download Results for {job_id_input}"):
                    st.markdown(f"[Download Meeting Minutes]({api_url}/download/{job_id_input})")
            
            elif status_data["status"] == "FAILED":
                st.error(f"Job failed: {status_data.get('error', 'Unknown error')}")
            
            else:
                st.warning("Job is still processing")
        
        elif response.status_code == 404:
            st.error("Job ID not found")
        else:
            st.error(f"Error checking status: {response.text}")
    
    except Exception as e:
        st.error(f"Failed to check status: {str(e)}")