import streamlit as st
import pandas as pd
import re
from textblob import TextBlob
import textstat

# Load the final CSV data with concise and detailed answers
@st.cache_data
def load_data(csv_path):
    return pd.read_csv(csv_path)

# Load data
data_path = 'final_combined_answers.csv'  # Replace with the actual CSV path
df = load_data(data_path)

# Custom CSS styling for a cleaner, more attractive layout
st.markdown("""
    <style>
    .main-title { font-size: 36px; color: #2E86C1; font-weight: bold; }
    .sub-header { font-size: 24px; color: #2874A6; margin-top: 20px; }
    .section-header { font-size: 20px; color: #1F618D; font-weight: bold; margin-top: 10px; }
    .answer-box { padding: 10px; border: 1px solid #D6DBDF; border-radius: 8px; background-color: #F4F6F7; margin-top: 10px; }
    .metadata-box { padding: 15px; background-color: #F9FBFD; border-radius: 10px; border: 1px solid #D5DBDB; }
    </style>
""", unsafe_allow_html=True)

# Streamlit app title and description
st.markdown("<div class='main-title'>Research Paper Summaries and Detailed Answers</div>", unsafe_allow_html=True)
st.write("Explore research papers by category and view concise or detailed answers with customizable quality thresholds.")

# Sidebar selections
st.sidebar.header("Filters")
categories = df['Category'].unique()
selected_category = st.sidebar.selectbox('Select a Category', options=categories)

# Add quality threshold selection for detailed answers only
quality_threshold = st.sidebar.slider("Minimum Quality Threshold for Detailed Answers", 0, 100, 50)

# Adjust readability scoring criteria using textstat for readability score
def calculate_quality_score(text):
    # Using TextBlob for grammar analysis
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity * 100  # Scale up for simplicity
    subjectivity = (1 - blob.sentiment.subjectivity) * 100  # More objective content scores higher

    # Using textstat's Flesch reading ease score
    flesch_score = textstat.flesch_reading_ease(text)
    scaled_flesch_score = max(0, min(100, flesch_score))  # Scale to 0-100 range

    # Combine scores for an overall quality rating
    return round((polarity + subjectivity + scaled_flesch_score) / 3, 2)

# Calculate quality scores only for detailed questions
detailed_questions = [
    "Explain the main research problem addressed in this paper in detail.",
    "Describe in detail the methodology used in this study.",
    "Summarize the key findings and contributions in depth.",
    "What are the limitations or challenges discussed, and why are they significant?"
]
for question in detailed_questions:
    df[question + '_Quality'] = df[question].apply(lambda x: calculate_quality_score(x) if isinstance(x, str) else 0)

# Filter papers by selected category and quality
filtered_data = df[df['Category'] == selected_category]

# Filter papers by quality threshold on detailed answers only
filtered_data = filtered_data[
    (filtered_data["Explain the main research problem addressed in this paper in detail._Quality"] >= quality_threshold) &
    (filtered_data["Describe in detail the methodology used in this study._Quality"] >= quality_threshold) &
    (filtered_data["Summarize the key findings and contributions in depth._Quality"] >= quality_threshold) &
    (filtered_data["What are the limitations or challenges discussed, and why are they significant?_Quality"] >= quality_threshold)
]

# Display filtered papers
if not filtered_data.empty:
    paper_titles = filtered_data['Title'].unique()
    selected_title = st.sidebar.selectbox('Select a Paper Title', options=paper_titles)

    # Filter the data based on the selected paper title
    selected_paper = filtered_data[filtered_data['Title'] == selected_title].iloc[0]

    # Display paper metadata and summary
    st.markdown("<div class='sub-header'>Paper Information</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metadata-box'><strong>Title:</strong> {selected_paper['Title']}<br>"
                f"<strong>Category:</strong> {selected_paper['Category']}<br>"
                f"<strong>Authors:</strong> {selected_paper.get('Authors', 'Not available')}<br>"
                f"<strong>Publication Date:</strong> {selected_paper.get('Publication Date', 'Not available')}</div>", 
                unsafe_allow_html=True)

    # Display abstract and generated summary
    st.markdown("<div class='section-header'>Abstract</div>", unsafe_allow_html=True)
    st.write(selected_paper.get('Abstract', 'Not available'))
    
    st.markdown("<div class='section-header'>Generated Summary</div>", unsafe_allow_html=True)
    st.write(selected_paper.get('Generated Summary', 'Not available'))

    # Define concise and detailed questions with icons
    concise_questions = [
        ("What is the main research problem addressed in the paper?", "🔍"),
        ("What methodology was used in the paper?", "⚙️"),
        ("What are the key findings or contributions?", "💡"),
        ("What are the limitations or challenges discussed?", "⚠️")
    ]
    detailed_questions_with_icons = [
        ("Explain the main research problem addressed in this paper in detail.", "🔍"),
        ("Describe in detail the methodology used in this study.", "⚙️"),
        ("Summarize the key findings and contributions in depth.", "💡"),
        ("What are the limitations or challenges discussed, and why are they significant?", "⚠️")
    ]

    # Select answer type
    question_type = st.radio("Select Answer Type", ["Concise Answer", "Detailed Answer"])
    questions = concise_questions if question_type == "Concise Answer" else detailed_questions_with_icons

    # Select question
    selected_question_with_icon = st.selectbox(
        "Select a Question", 
        questions, 
        format_func=lambda q: f"{q[1]} {q[0]}"
    )
    selected_question = selected_question_with_icon[0]

    # Display the answer and quality score (if detailed answer)
    st.markdown("<div class='section-header'>Answer</div>", unsafe_allow_html=True)
    answer = selected_paper.get(selected_question, "Not available")
    
    if pd.isna(answer) or answer.strip() == "":
        answer = "Data unavailable"

    st.markdown(f"<div class='answer-box'>{answer}</div>", unsafe_allow_html=True)
    
    if question_type == "Detailed Answer":
        quality_score = selected_paper.get(f"{selected_question}_Quality", 0)
        st.markdown(f"<div><strong>Answer Quality Score:</strong> {quality_score}</div>")

    # Optionally display full text
    if st.checkbox('Show Full Text'):
        st.markdown("<div class='section-header'>Full Text</div>", unsafe_allow_html=True)
        st.write(selected_paper.get('Full Text', 'Not available'))
else:
    st.write(f"No papers available in the {selected_category} category with the selected quality threshold.")
