import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import plotly.express as px
import pandas as pd
import PyPDF2
from transformers import pipeline

class DocumentAnalyzer:
    def __init__(self, model_name="facebook/bart-large-cnn"):
        # Initialize summarization model
        self.summarizer = pipeline("summarization", model=model_name)
        
        # Download NLTK resources
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        
        # Initialize stopwords
        self.stop_words = set(stopwords.words('english'))
        
        # Load spaCy model for named entity recognition
        self.nlp = spacy.load("en_core_web_sm")

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file"""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text

    def generate_summary(self, text, max_length=300, min_length=100):
        """Generate a concise summary of the document"""
        if len(text) < min_length:
            return text
        
        summary = self.summarizer(
            text, 
            max_length=max_length, 
            min_length=min_length, 
            do_sample=False
        )[0]['summary_text']
        
        return summary

    def extract_keywords(self, text, top_n=10):
        """Extract top keywords from the text"""
        # Tokenize and remove stopwords
        word_tokens = word_tokenize(text.lower())
        filtered_tokens = [
            word for word in word_tokens 
            if word.isalnum() and word not in self.stop_words
        ]
        
        # Count keyword frequencies
        from collections import Counter
        keyword_freq = Counter(filtered_tokens)
        top_keywords = keyword_freq.most_common(top_n)
        
        return top_keywords
    
    def extract_named_entities(self, text):
        """Extract named entities from the text"""
        doc = self.nlp(text)
        entities = {}
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            entities[ent.label_].append(ent.text)
        
        return entities

    def create_keyword_visualization(self, keywords):
        """Create a bar chart of top keywords"""
        df = pd.DataFrame(keywords, columns=['Keyword', 'Frequency'])
        fig = px.bar(
            df, 
            x='Keyword', 
            y='Frequency', 
            title='Top Document Keywords',
            labels={'Keyword': 'Keywords', 'Frequency': 'Frequency'}
        )
        return fig

class KnowledgeTimeline:
    def __init__(self, pdf_path):
        # Load spaCy model for named entity recognition
        self.nlp = spacy.load("en_core_web_sm")
        self.pdf_path = pdf_path
        self.timeline_events = []

    def extract_dates_and_events(self, text):
        """Extract dates and associated events from text"""
        from datefinder import find_dates
        from datetime import datetime
        
        # Find all dates in the text
        found_dates = list(find_dates(text))
        
        # Use spaCy for advanced named entity recognition
        doc = self.nlp(text)
        
        # Collect events and dates
        events = []
        for ent in doc.ents:
            if ent.label_ in ["EVENT", "ORG", "PERSON"]:
                # Try to find a corresponding date
                closest_date = min(
                    found_dates, 
                    key=lambda date: abs((date - datetime.now()).days),
                    default=None
                )
                
                events.append({
                    "event": ent.text,
                    "type": ent.label_,
                    "date": closest_date
                })
        
        return events

    def generate_timeline(self, text):
        """Generate a visual timeline of events"""
        import plotly.express as px
        import pandas as pd
        
        events = self.extract_dates_and_events(text)
        
        # Convert to DataFrame for Plotly visualization
        df = pd.DataFrame(events)
        df = df.dropna(subset=['date'])
        
        # Create interactive timeline
        if not df.empty:
            fig = px.timeline(
                df, 
                x='date', 
                y='event', 
                color='type',
                title='Document Knowledge Timeline',
                labels={'event': 'Event', 'date': 'Date'}
            )
            fig.update_yaxes(autorange="reversed")
            return fig
        
        return None