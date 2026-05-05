import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import time
from PIL import Image
import io
import os

# ═══════════════════════════════════════════════════════════════════
# 🎨 PAGE CONFIGURATION & STYLING
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="NeuroLens AI - AI Vision & Voice Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
    <style>
        /* Main title styling */
        .main-header {
            text-align: center;
            font-size: 3.5em;
            font-weight: 900;
            background: linear-gradient(135deg, #6C63FF 0%, #00D4FF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            animation: fadeIn 1s ease-in;
        }
        
        .subtitle {
            text-align: center;
            font-size: 1.5em;
            color: #00D4FF;
            margin-bottom: 0.3rem;
            letter-spacing: 2px;
        }
        
        .credit {
            text-align: center;
            color: #888888;
            font-size: 0.95em;
            font-style: italic;
            margin-bottom: 2rem;
        }
        
        .feature-card {
            background: linear-gradient(135deg, #6C63FF15 0%, #00D4FF15 100%);
            border: 2px solid #6C63FF;
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            transition: all 0.3s ease;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(108, 99, 255, 0.3);
        }
        
        .success-message {
            background: linear-gradient(135deg, #00D4FF15 0%, #6C63FF15 100%);
            border-left: 4px solid #00D4FF;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        
        .footer {
            text-align: center;
            color: #666666;
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #EEEEEE;
            font-size: 0.9em;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("""
    <div class="main-header">
        🧠 NeuroLens AI
    </div>
    <div class="subtitle">
        See • Hear • Understand
    </div>
    <div class="credit">
        Created by Mayuri Chandel
    </div>
""", unsafe_allow_html=True)

st.divider()

# ═══════════════════════════════════════════════════════════════════
# 🔑 AZURE CREDENTIALS (FROM NOTEBOOKS)
# ═══════════════════════════════════════════════════════════════════
SPEECH_KEY = "2LNcNfQUrK6f0jj3eZ1ssHm1qALaeiXmn1foajdEdGGo9bxH06i5JQQJ99CEACYeBjFXJ3w3AAAYACOGrjDr"
SPEECH_REGION = "eastus"

VISION_KEY = "3rjI2tJgEjvUS9ve9DnwGTdgu0JW5B5i0u2mE8QpRzgaCPh4l1AwJQQJ99CEACYeBjFXJ3w3AAAFACOG0FxE"
VISION_ENDPOINT = "https://cv97898657.cognitiveservices.azure.com/"

# ═══════════════════════════════════════════════════════════════════
# 📑 TAB-BASED NAVIGATION
# ═══════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs(["🖼 Image to Text", "🗣 Text to Speech", "🔊 Image to Speech", "ℹ️ About"])


# ═══════════════════════════════════════════════════════════════════
# TAB 1: 🖼 IMAGE TO TEXT (OCR)
# ═══════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### Extract Text from Images")
    st.markdown("*Powered by Azure Computer Vision - Advanced OCR Technology*")
    st.divider()
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("#### Upload Image")
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=["png", "jpg", "jpeg", "bmp", "gif"],
            key="img_to_text"
        )
    
    with col2:
        if uploaded_file:
            st.markdown("#### Preview")
            st.image(uploaded_file, use_column_width=True, caption="📸 Uploaded Image")
    
    if uploaded_file:
        if st.button("🚀 Extract Text", key="extract_text_btn", use_container_width=True):
            try:
                with st.spinner("🔍 Analyzing image and extracting text..."):
                    client = ComputerVisionClient(
                        VISION_ENDPOINT,
                        CognitiveServicesCredentials(VISION_KEY)
                    )
                    
                    image_bytes = uploaded_file.read()
                    result = client.read_in_stream(io.BytesIO(image_bytes), raw=True)
                    operation_id = result.headers["Operation-Location"].split("/")[-1]
                    
                    # Wait for OCR completion
                    while True:
                        read_result = client.get_read_result(operation_id)
                        if read_result.status not in ['notStarted', 'running']:
                            break
                        time.sleep(0.5)
                    
                    extracted_text = ""
                    if read_result.status == "succeeded":
                        for page in read_result.analyze_result.read_results:
                            for line in page.lines:
                                extracted_text += line.text + "\n"
                        
                        st.markdown("<div class='success-message'>✅ Text extracted successfully!</div>", unsafe_allow_html=True)
                        st.markdown("#### 📝 Extracted Text")
                        st.text_area("", extracted_text, height=250, disabled=False)
                        
                        # Copy button
                        st.write("")
                        st.download_button(
                            label="💾 Download as Text",
                            data=extracted_text,
                            file_name="extracted_text.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error("❌ Could not extract text from the image. Please try another image.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


# ═══════════════════════════════════════════════════════════════════
# TAB 2: 🗣 TEXT TO SPEECH
# ═══════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Convert Text to Speech")
    st.markdown("*Powered by Azure Speech Services - Natural Neural Voices*")
    st.divider()
    
    st.markdown("#### Input Text")
    text_input = st.text_area(
        "Enter the text you want to convert to speech",
        height=200,
        placeholder="Type or paste your text here...",
        key="text_to_speech_input"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        voice_option = st.selectbox(
            "Select Voice",
            ["en-US-JennyNeural", "en-US-AriaNeural", "en-US-GuyNeural", "en-US-AmberNeural"]
        )
    
    with col2:
        speech_rate = st.slider("Speech Rate", -50, 50, 0, 1)
    
    if st.button("🎵 Convert to Speech", use_container_width=True, key="text_to_speech_btn"):
        if text_input.strip():
            try:
                with st.spinner("🎙️ Generating audio..."):
                    speech_config = speechsdk.SpeechConfig(
                        subscription=SPEECH_KEY,
                        region=SPEECH_REGION
                    )
                    
                    speech_config.speech_synthesis_voice_name = voice_option
                    
                    audio_config = speechsdk.audio.AudioOutputConfig(filename="output.wav")
                    
                    synthesizer = speechsdk.SpeechSynthesizer(
                        speech_config=speech_config,
                        audio_config=audio_config
                    )
                    
                    # Apply speech rate
                    ssml_text = f'<speak version="1.0" xml:lang="en-US"><voice name="{voice_option}"><prosody rate="{speech_rate/100}">{text_input}</prosody></voice></speak>'
                    
                    result = synthesizer.speak_ssml_async(ssml_text).get()
                    
                    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                        st.markdown("<div class='success-message'>✅ Audio generated successfully!</div>", unsafe_allow_html=True)
                        st.markdown("#### 🔊 Play Audio")
                        
                        audio_file = open("output.wav", "rb")
                        st.audio(audio_file.read(), format="audio/wav")
                        
                        with open("output.wav", "rb") as f:
                            st.download_button(
                                label="💾 Download Audio",
                                data=f.read(),
                                file_name="speech_output.wav",
                                mime="audio/wav"
                            )
                    else:
                        st.error("❌ Failed to generate audio. Please try again.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter some text first!")


# ═══════════════════════════════════════════════════════════════════
# TAB 3: 🔊 IMAGE TO SPEECH
# ═══════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### Extract Text from Image & Convert to Speech")
    st.markdown("*Two-in-one: OCR + Text-to-Speech powered by Azure AI*")
    st.divider()
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("#### Upload Image")
        uploaded_file_img2speech = st.file_uploader(
            "Choose an image file",
            type=["png", "jpg", "jpeg", "bmp", "gif"],
            key="img_to_speech"
        )
    
    with col2:
        if uploaded_file_img2speech:
            st.markdown("#### Preview")
            st.image(uploaded_file_img2speech, use_column_width=True, caption="📸 Uploaded Image")
    
    if uploaded_file_img2speech:
        if st.button("🔍 Extract Text from Image", use_container_width=True, key="extract_img_speech"):
            try:
                with st.spinner("🔍 Extracting text..."):
                    client = ComputerVisionClient(
                        VISION_ENDPOINT,
                        CognitiveServicesCredentials(VISION_KEY)
                    )
                    
                    image_bytes = uploaded_file_img2speech.read()
                    result = client.read_in_stream(io.BytesIO(image_bytes), raw=True)
                    operation_id = result.headers["Operation-Location"].split("/")[-1]
                    
                    while True:
                        read_result = client.get_read_result(operation_id)
                        if read_result.status not in ['notStarted', 'running']:
                            break
                        time.sleep(0.5)
                    
                    extracted_text = ""
                    if read_result.status == "succeeded":
                        for page in read_result.analyze_result.read_results:
                            for line in page.lines:
                                extracted_text += line.text + "\n"
                        
                        st.session_state.img_speech_text = extracted_text
                        st.markdown("<div class='success-message'>✅ Text extracted successfully!</div>", unsafe_allow_html=True)
                    else:
                        st.error("❌ Could not extract text. Please try another image.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        
        if "img_speech_text" in st.session_state and st.session_state.img_speech_text:
            st.divider()
            st.markdown("#### 📝 Extracted Text")
            display_text = st.text_area("", st.session_state.img_speech_text, height=200)
            
            st.divider()
            st.markdown("#### 🎙️ Convert to Speech")
            
            col1, col2 = st.columns(2)
            with col1:
                voice_option_img = st.selectbox(
                    "Select Voice",
                    ["en-US-JennyNeural", "en-US-AriaNeural", "en-US-GuyNeural", "en-US-AmberNeural"],
                    key="img_speech_voice"
                )
            
            with col2:
                speech_rate_img = st.slider("Speech Rate", -50, 50, 0, 1, key="img_speech_rate")
            
            if st.button("🎵 Generate Speech", use_container_width=True, key="img_to_speech_convert"):
                try:
                    with st.spinner("🎙️ Generating audio from extracted text..."):
                        speech_config = speechsdk.SpeechConfig(
                            subscription=SPEECH_KEY,
                            region=SPEECH_REGION
                        )
                        
                        speech_config.speech_synthesis_voice_name = voice_option_img
                        audio_config = speechsdk.audio.AudioOutputConfig(filename="image_audio.wav")
                        
                        synthesizer = speechsdk.SpeechSynthesizer(
                            speech_config=speech_config,
                            audio_config=audio_config
                        )
                        
                        ssml_text = f'<speak version="1.0" xml:lang="en-US"><voice name="{voice_option_img}"><prosody rate="{speech_rate_img/100}">{display_text}</prosody></voice></speak>'
                        
                        result = synthesizer.speak_ssml_async(ssml_text).get()
                        
                        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                            st.markdown("<div class='success-message'>✅ Speech generated successfully!</div>", unsafe_allow_html=True)
                            st.markdown("#### 🔊 Play Audio")
                            
                            audio_file = open("image_audio.wav", "rb")
                            st.audio(audio_file.read(), format="audio/wav")
                            
                            with open("image_audio.wav", "rb") as f:
                                st.download_button(
                                    label="💾 Download Audio",
                                    data=f.read(),
                                    file_name="image_to_speech.wav",
                                    mime="audio/wav"
                                )
                        else:
                            st.error("❌ Failed to generate speech. Please try again.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


# ═══════════════════════════════════════════════════════════════════
# TAB 4: ℹ️ ABOUT
# ═══════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### About NeuroLens AI")
    st.divider()
    
    st.markdown("""
    #### 🎯 What is NeuroLens AI?
    
    NeuroLens AI is an advanced multi-modal AI platform that brings together cutting-edge computer vision and speech synthesis technologies.
    Our platform empowers you to:
    
    - **🖼 Extract Text from Images** - OCR technology to digitize written content
    - **🗣 Convert Text to Speech** - Neural voice synthesis for natural-sounding audio
    - **🔊 Turn Images into Speech** - Seamless pipeline combining OCR and TTS
    
    #### 🚀 Features
    
    ✨ **Advanced OCR (Optical Character Recognition)**
    - Supports multiple image formats (PNG, JPG, JPEG, BMP, GIF)
    - Powered by Azure Computer Vision API
    - Handles printed and handwritten text
    - Download extracted text as files
    
    🎙️ **Natural Speech Synthesis**
    - Multiple neural voices available (Jenny, Aria, Guy, Amber)
    - Adjustable speech rate for personalized audio
    - High-quality audio output
    - Powered by Azure Speech Services
    - Download generated audio files
    
    ⚡ **Fast & Reliable**
    - Cloud-based processing for accuracy
    - Enterprise-grade Azure services
    - Real-time feedback with loading indicators
    - Error handling for smooth user experience
    
    #### 👤 Creator
    
    **Created by:** Mayuri Chandel
    
    This platform leverages Microsoft Azure's AI services to provide seamless integration of vision and voice technologies.
    
    #### 🔧 Technology Stack
    
    - **Frontend:** Streamlit (Python web framework)
    - **Vision APIs:** Azure Computer Vision (OCR)
    - **Speech APIs:** Azure Speech Services (TTS)
    - **Language:** Python
    - **Cloud:** Microsoft Azure
    
    #### 💡 Use Cases
    
    - 📄 Document digitization and archival
    - 👁️ Accessibility features for visually impaired users
    - 🌍 Multilingual content processing
    - 📹 Content creation and narration
    - 🎓 Educational applications
    - 🤖 Automated document processing
    - 📱 Mobile app integration
    - 🎤 Podcast and audiobook creation
    """)
    
    st.divider()
    st.markdown("""
    <div class="footer">
        <p><strong>NeuroLens AI</strong> | See • Hear • Understand</p>
        <p>Created by Mayuri Chandel</p>
        <p>Powered by Microsoft Azure AI Services</p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════
st.divider()
st.markdown("""
    <div class="footer">
        <p>🧠 <strong>NeuroLens AI</strong> | See • Hear • Understand</p>
        <p style="font-size: 0.85em;">Created by Mayuri Chandel | Powered by Microsoft Azure AI Services</p>
    </div>
""", unsafe_allow_html=True)
