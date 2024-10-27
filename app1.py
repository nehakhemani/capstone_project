import streamlit as st
import pandas as pd

# Load the final CSV data with concise and detailed answers
@st.cache_data
def load_data(csv_path):
    return pd.read_csv(csv_path)

# Load data
data_path = 'final_combined_answers.csv'  # Replace with the actual CSV path
df = load_data(data_path)

# Custom CSS styling
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
st.write("Explore research papers by category and view concise or detailed answers to specific questions.")

# Sidebar selections
st.sidebar.header("Filters")

# Set default category to "Machine learning" and update the selection
categories = df['Category'].unique()
default_category = "Machine learning"
selected_category_index = list(categories).index(default_category) if default_category in categories else 0
selected_category = st.sidebar.selectbox('Select a Category', options=categories, index=selected_category_index)

# Filter papers by selected category
filtered_data = df[df['Category'] == selected_category]
if not filtered_data.empty:
    paper_titles = filtered_data['Title'].unique()

    # Set default paper title if the category is "Machine learning"
    default_paper_title = "A Limit Theorem in Singular Regression Problem"
    default_paper_index = list(paper_titles).index(default_paper_title) if default_paper_title in paper_titles else 0

    # Display paper title selection box with default set
    selected_title = st.sidebar.selectbox('Select a Paper Title', options=paper_titles, index=default_paper_index)

    # Filter the data based on the selected paper title
    selected_paper = filtered_data[filtered_data['Title'] == selected_title].iloc[0]

    # Display the paper metadata and summary
    st.markdown("<div class='sub-header'>Paper Information</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metadata-box'><strong>Title:</strong> {selected_paper['Title']}<br>"
                f"<strong>Category:</strong> {selected_paper['Category']}<br>"
                f"<strong>Authors:</strong> {selected_paper.get('Authors', 'Not available')}<br>"
                f"<strong>Publication Date:</strong> {selected_paper.get('Publication Date', 'Not available')}</div>", 
                unsafe_allow_html=True)

    # Abstract and Generated Summary
    st.markdown("<div class='section-header'>Abstract</div>", unsafe_allow_html=True)
    st.write(selected_paper.get('Abstract', 'Not available'))
    
    st.markdown("<div class='section-header'>Generated Summary</div>", unsafe_allow_html=True)
    st.write(selected_paper.get('Generated Summary', 'Not available'))

    # Define concise and detailed questions
    concise_questions = [
        "What is the main research problem addressed in the paper?",
        "What methodology was used in the paper?",
        "What are the key findings or contributions?",
        "What are the limitations or challenges discussed?"
    ]
    
    detailed_questions = [
        "Explain the main research problem addressed in this paper in detail.",
        "Describe in detail the methodology used in this study.",
        "Summarize the key findings and contributions in depth.",
        "What are the limitations or challenges discussed, and why are they significant?"
    ]

    # Select question type: concise or detailed
    question_type = st.radio("Select Answer Type", ["Concise Answer", "Detailed Answer"])

    # Define question set based on selection
    questions = concise_questions if question_type == "Concise Answer" else detailed_questions

    # Select question
    selected_question = st.selectbox("Select a Question", questions)

    # Display the answer based on selected question
    st.markdown("<div class='section-header'>Answer</div>", unsafe_allow_html=True)
    answer = selected_paper.get(selected_question, "Not available")
    if pd.isna(answer) or answer.strip() == "":
        answer = "Data unavailable"
    
    st.markdown(f"<div class='answer-box'>{answer}</div>", unsafe_allow_html=True)

    # Optionally display full text if available
    if st.checkbox('Show Full Text'):
        st.markdown("<div class='section-header'>Full Text</div>", unsafe_allow_html=True)
        st.write(selected_paper.get('Full Text', 'Not available'))
else:
    st.write(f"No papers available in the {selected_category} category.")
