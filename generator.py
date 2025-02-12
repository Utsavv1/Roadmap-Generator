# 1. Load Environment Variables and Configurations
from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from graphviz import Digraph
import plotly.figure_factory as ff
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

# 2. Define Functions

# Function to generate response from Gemini
def get_gemini_response(question):
    response = model.generate_content(question)
    if hasattr(response, 'text'):
        return response.text
    else:
        raise ValueError("Unexpected response format: Missing 'text'")

# Function to generate a flowchart
def generate_flowchart(roadmap_text):
    # Split steps by new line and clean empty lines
    steps = roadmap_text.split('\n')
    steps = [step.strip() for step in steps if step.strip()]
    # Initialize the Digraph object
    dot = Digraph(comment='Career Roadmap')
    # Define NEW color mapping based on keywords in the step text
    for i, step in enumerate(steps):
        if "education" in step.lower() or "foundational" in step.lower():
            color = "#FFD700"  # Gold for education/foundational steps
        elif "skill" in step.lower() or "develop" in step.lower():
            color = "#32CD32"  # LimeGreen for skills development
        elif "project" in step.lower() or "practical" in step.lower():
            color = "#FF6347"  # Tomato for practical projects
        elif "challenge" in step.lower() or "solution" in step.lower():
            color = "#FFA500"  # Orange for challenges/solutions
        else:
            color = "#87CEEB"  # SkyBlue for other steps
        # Add nodes and edges
        dot.node(str(i), step, shape="box", style="filled", color=color)
        if i > 0:
            dot.edge(str(i - 1), str(i))
    return dot

# Function to generate a Gantt chart
def generate_gantt_chart(steps):
    gantt_data = []
    current_date = datetime.now()
    for i, step in enumerate(steps):
        duration = timedelta(days=(i + 1) * 7)  # Example: 1 week per step
        gantt_data.append({
            "Task": step,
            "Start": current_date.strftime("%Y-%m-%d"),
            "Finish": (current_date + duration).strftime("%Y-%m-%d"),
            "Resource": "Step"
        })
        current_date += duration
    fig = ff.create_gantt(gantt_data, index_col='Resource', show_colorbar=True, group_tasks=True)
    return fig

# 3. Main Streamlit App Logic
st.set_page_config(page_title="Enhanced Career Roadmap Generator", layout="wide")
st.header("Enhanced Career Roadmap Generator")

# Input form
with st.form("user_input_form"):
    job_title = st.text_input("Enter the job title:")
    skills = st.text_input("Your current skills:")
    experience = st.selectbox("Experience level:", ["Beginner", "Intermediate", "Advanced"])
    timeline = st.radio("Desired timeline:", ["Short-term", "Long-term"])
    resources = st.multiselect("Preferred learning resources:", ["Videos", "Books", "Articles", "Online Courses"])
    specialization = st.text_input("Area of specialization (optional):")
    submit = st.form_submit_button("Generate Roadmap")

# Example templates
if st.checkbox("Use a pre-defined template"):
    template = st.selectbox("Choose a template:", ["Software Developer", "Data Scientist", "Digital Marketer"])
    if template == "Software Developer":
        job_title = "Software Developer"
    elif template == "Data Scientist":
        job_title = "Data Scientist"
    elif template == "Digital Marketer":
        job_title = "Digital Marketer"

if submit and job_title:
    # Generate input prompt
    input_prompt = f"""
    You are a career guide. Take the following inputs and generate a detailed roadmap:
    Job Title: {job_title}
    Skills: {skills}
    Experience: {experience}
    Timeline: {timeline}
    Resources Preferred: {', '.join(resources)}
    Specialization: {specialization if specialization else 'General'}
    Divide the roadmap into Beginner, Intermediate, and Advanced phases.
    For each phase, include:
    - Key objectives.
    - Specific resources (e.g., books, courses).
    - Practical projects.
    - Challenges and solutions.
    Include actionable advice for excelling in {job_title}.
    """
    # Get response from Gemini
    response = get_gemini_response(input_prompt)

    # Display the generated roadmap
    st.subheader("Generated Roadmap")
    st.write(response)

    # Generate flowchart
    st.subheader("Career Roadmap Flowchart")
    flowchart = generate_flowchart(response)
    st.graphviz_chart(flowchart.source)

    # Generate Gantt chart
    st.subheader("Timeline View (Gantt Chart)")
    steps = [step.strip() for step in response.split('\n') if step.strip()]
    gantt_chart = generate_gantt_chart(steps)
    st.plotly_chart(gantt_chart, use_container_width=True)

    # Export flowchart as PDF
    flowchart.render("roadmap_flowchart", format="pdf", cleanup=True)

    # Add a download button for the flowchart
    st.download_button(
        "Download Flowchart PDF",
        data=open("roadmap_flowchart.pdf", "rb").read(),
        file_name="roadmap_flowchart.pdf",
        mime="application/pdf"
    )