import streamlit as st
import base64
import time
import os
import traceback

# Import custom modules
from chatbot import ChatbotManager
from vectors import EmbeddingsManager
from document_analyzer import DocumentAnalyzer, KnowledgeTimeline

def displayPDF(file):
    """Display PDF file in Streamlit"""
    base64_pdf = base64.b64encode(file.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def set_custom_styles():
    """Set custom CSS for a modern, eye-catching UI"""
    
    
    st.markdown("""
    <style>
        /* Custom Color Palette */
        :root {
            --primary-color: #4CAF50; /* Green */
            --secondary-color: #FF9800; /* Orange */
            --background-color: #121212; /* Dark background */
            --card-background: #1E1E1E; /* Dark gray for sections */
            --text-color: #E0E0E0; /* Light gray for text */
            --highlight-text: #FFFFFF; /* White for headings */
        }

        /* Overall App Background */
        .stApp {
            background-color: var(--background-color);
            color: var(--text-color);
        }

        /* Navigation Styling */
        .stSelectbox > div > div {
            background-color: var(--card-background) !important;
            border-radius: 10px !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            color: var(--text-color) !important;
        }

        /* Buttons */
        .stButton > button {
            background-color: var(--primary-color) !important;
            color: var(--highlight-text) !important;
            border-radius: 20px !important;
            transition: all 0.3s ease !important;
        }

        .stButton > button:hover {
            background-color: var(--secondary-color) !important;
            transform: scale(1.05);
        }

        /* Expanders */
        .stExpander {
            background-color: var(--card-background) !important;
            border-radius: 15px !important;
            color: var(--text-color) !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }

        /* Cards */
        .stMarkdown {
            background-color: var(--card-background) !important;
            border-radius: 15px !important;
            padding: 20px !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            color: var(--text-color) !important;
        }

        /* Chat messages */
        .stChatMessage {
            background-color: var(--card-background) !important;
            color: var(--highlight-text) !important;
            border-radius: 10px !important;
            padding: 10px !important;
        }

        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def main():
    # Set page configuration
    st.set_page_config(
        page_title="SmartDoc AI",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom styles
    set_custom_styles()

    # Initialize session state variables
    if 'temp_pdf_path' not in st.session_state:
        st.session_state['temp_pdf_path'] = None
    if 'chatbot_manager' not in st.session_state:
        st.session_state['chatbot_manager'] = None
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    if 'document_analyzer' not in st.session_state:
        st.session_state['document_analyzer'] = None

    # Navigation
    menu = ["🏠 Home", "📄 Document Analysis", "💬 Chat", "📬 Contact"]
    choice = st.sidebar.radio("Navigation", menu)

    if choice == "🏠 Home":
        render_home()
    elif choice == "📄 Document Analysis":
        render_document_analysis()
    elif choice == "💬 Chat":
        render_chatbot()
    elif choice == "📬 Contact":
        render_contact()

def render_home():
    """Render the home page"""
    st.title("🚀 SmartDoc AI: Intelligent Document Companion")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## 🤖 Revolutionize Your Document Workflow

        SmartDoc AI is an advanced platform designed to transform how you interact with documents:

        - 📊 **Intelligent Analysis**: Extract insights automatically
        - 🗓️ **Timeline Visualization**: Chronological document understanding
        - 💬 **AI-Powered Chat**: Interact with your documents
        - 🔍 **Smart Summarization**: Quick document comprehension
        """)
        
        st.success("Upload a PDF and unlock its full potential!")
    
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3062/3062634.png", width=250)

def render_document_analysis():
    """Render document analysis page"""
    st.title("📄 Document Intelligence")
    
    # File Uploader
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    
    if uploaded_file is not None:
        # Save temporary PDF
        temp_pdf_path = "temp.pdf"
        with open(temp_pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state['temp_pdf_path'] = temp_pdf_path

        # PDF Preview
        with st.expander("📖 PDF Preview"):
            displayPDF(uploaded_file)
        
        # Initialize analyzer
        analyzer = DocumentAnalyzer()
        
        # Read PDF text with progress
        with st.spinner("📖 Reading document..."):
            text = analyzer.extract_text_from_pdf(temp_pdf_path)
            
        if not text.strip():
            st.error("Failed to extract text from PDF. The document may be scanned or encrypted.")
            return
            
        # Document Analysis Tabs
        tab1, tab2, tab3 = st.tabs(["📊 Summary", "🔍 Keywords", "🏷️ Entities"])
        
        with tab1:
            st.subheader("📝 Document Summary")
            with st.spinner("Generating summary..."):
                summary = analyzer.generate_summary(text)
            st.write(summary)
        
        with tab2:
            st.subheader("🔑 Key Keywords")
            with st.spinner("Extracting keywords..."):
                keywords = analyzer.extract_keywords(text)
                if keywords:
                    fig = analyzer.create_keyword_visualization(keywords)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No significant keywords found.")
        
        with tab3:
            st.subheader("🏷️ Named Entities")
            with st.spinner("Identifying entities..."):
                entities = analyzer.extract_named_entities(text)
                if entities:
                    for entity_type, values in entities.items():
                        st.markdown(f"**{entity_type}**: {', '.join(values[:10])}")
                else:
                    st.warning("No named entities found.")

def render_chatbot():
    """Render chatbot interface"""
    st.title("💬 Document Chat")
    
    if st.session_state['temp_pdf_path'] is None:
        st.warning("Please upload a PDF first in the Document Analysis section.")
        return
     
    # Chat interface
    for msg in st.session_state['messages']:
        st.chat_message(msg['role']).markdown(msg['content'])

    if user_input := st.chat_input("Ask a question about your document..."):
        st.chat_message("user").markdown(user_input)
        st.session_state['messages'].append({"role": "user", "content": user_input})

        # Initialize chatbot if not already done
        if st.session_state['chatbot_manager'] is None:
            st.session_state['chatbot_manager'] = ChatbotManager(
                model_name="BAAI/bge-small-en",
                device="cpu",
                encode_kwargs={"normalize_embeddings": True},
                llm_model="llama3.2:3b",
                llm_temperature=0.7,
                qdrant_url="http://localhost:6333",
                collection_name="vector_db"
            )

        with st.spinner("🤖 Thinking..."):
            try:
                answer = st.session_state['chatbot_manager'].get_response(user_input)
                st.chat_message("assistant").markdown(answer)
                st.session_state['messages'].append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error(traceback.format_exc())

def render_contact():
    """Render contact page"""
    st.title("📬 Connect with SmartDoc")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ## 📧 Contact Information
        - **Email:** smartdoc@ai.com
        - **Phone:** +1 (555) SMARTDOC
        - **Support Hours:** 9 AM - 5 PM EST
        """)
    
    with col2:
        st.markdown("""
        ## 🌐 Quick Links
        - [GitHub Repository](https://github.com/MaheshwaryNarkhede/SmartDoc)
        - [Documentation](https://smartdoc.ai/docs)
        - [Report an Issue](https://github.com/MaheshwaryNarkhede/SmartDoc/issues)
        """)
    
    st.markdown("### 💬 Send us a message")
#     st.markdown(
#     """
#     <style>
#         label {
#             color: skyblue !important; /* Change label text color */
#             font-size: 35px !important; /* Increase font size */
#             font-weight: bold !important; /* Make it bold */
#         }
#     </style>
#     """,
#     unsafe_allow_html=True
# )
    with st.form("contact_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        message = st.text_area("Your Message")
        submitted = st.form_submit_button("Send Message")
        
        if submitted:
            st.success("Message sent successfully! We'll get back to you soon.")
            

if __name__ == "__main__":
    main()