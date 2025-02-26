# app.py

import os
import gradio as gr
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# LangChain imports
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.agents import AgentType, initialize_agent
from langchain.tools import tool
from langchain.utilities import SerpAPIWrapper
from langchain_openai import ChatOpenAI

# Initialize FastAPI
app = FastAPI(
    title="Essay Grading API",
    description="An integrated system for essay grading and plagiarism detection",
    version="1.0.0"
)

# Define request/response models
class EssayRequest(BaseModel):
    essay: str
    check_plagiarism: bool = False

class GradingResponse(BaseModel):
    summary: str
    scores: str
    overall_score: str
    strengths: str
    improvements: str
    feedback: str
    plagiarism_check: Optional[str] = None

# Configure API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Create LangChain OpenAI instance with the API key
llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY, temperature=0.1)
# Initialize the LLM

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash-exp",
#     temperature=0.5,
#     google_api_key=GOOGLE_API_KEY
# )

# Configure the grading chain components
summary_prompt = PromptTemplate(
    input_variables=["essay"],
    template="Summarize the following essay in 2-3 sentences:\n\n{essay}"
)
summary_chain = LLMChain(llm=llm, prompt=summary_prompt, output_key="summary")

scoring_prompt = PromptTemplate(
    input_variables=["essay"],
    template="""Evaluate the following essay on a scale of 0-10 for each of these five categories:

    1. Thesis & Main Argument
    2. Evidence & Support
    3. Organization & Structure
    4. Critical Thinking
    5. Writing Mechanics

    Provide a score and a brief justification for each:\n\n{essay}"""
)
scoring_chain = LLMChain(llm=llm, prompt=scoring_prompt, output_key="scores")

overall_score_prompt = PromptTemplate(
    input_variables=["scores"],
    template="Based on the following rubric scores, calculate an overall score out of 50:\n\n{scores}, write the title and the score without detail, make it easy to read by the users"
)
overall_score_chain = LLMChain(llm=llm, prompt=overall_score_prompt, output_key="overall_score")

strengths_prompt = PromptTemplate(
    input_variables=["essay"],
    template="List three specific strengths of the following essay:\n\n{essay}"
)
strengths_chain = LLMChain(llm=llm, prompt=strengths_prompt, output_key="strengths")

improvements_prompt = PromptTemplate(
    input_variables=["essay"],
    template="""List three actionable areas for improvement in the following essay, along with concrete
    examples of how the writer can improve:\n\n{essay}"""
)
improvements_chain = LLMChain(llm=llm, prompt=improvements_prompt, output_key="improvements")

feedback_prompt = PromptTemplate(
    input_variables=["summary", "scores", "strengths", "improvements"],
    template="""Based on the summary, rubric scores, strengths, and areas for improvement, provide a final
    paragraph of constructive feedback focusing on the most impactful ways the writer can improve:\n
    Summary: {summary}
    Scores: {scores}
    Strengths: {strengths}
    Areas for Improvement: {improvements}"""
)
feedback_chain = LLMChain(llm=llm, prompt=feedback_prompt, output_key="feedback")

# Initialize the sequential chain
grading_chain = SequentialChain(
    chains=[summary_chain, scoring_chain, overall_score_chain, strengths_chain, improvements_chain, feedback_chain],
    input_variables=["essay"],
    output_variables=["summary", "scores", "overall_score", "strengths", "improvements", "feedback"]
)

# Define plagiarism detection tool
@tool
def plagiarism_check(text: str) -> str:
    """Checks if an essay is plagiarized by searching the internet for similar content."""
    try:
        search = SerpAPIWrapper(serpapi_api_key=SERPAPI_KEY)
        web_results = search.run(text)

        if not web_results:
            return "No plagiarism detected. No matching content found online."

        analysis_prompt = PromptTemplate(
            input_variables=["text", "web_results"],
            template=("""
                Analyze the following web search results and determine if the input text is plagiarized.\n\n
                Essay:\n{text}\n\n
                Web Results:\n{web_results}\n\n
                Should we flag this as plagiarism? If yes, explain why.
                At the end, give a plagiarism score out of 100%.
                """
            )
        )

        formatted_prompt = analysis_prompt.format(text=text, web_results=web_results)
        result = llm.predict(formatted_prompt)
        return result
    except Exception as e:
        return f"Error during plagiarism check: {str(e)}"

# Initialize the plagiarism detection agent
tools = [plagiarism_check]
plagiarism_agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False
)

# API endpoint for essay grading
@app.post("/api/grade_essay", response_model=GradingResponse)
async def grade_essay_api(request: EssayRequest):
    """
    Grade an essay using AI and optionally perform plagiarism checking.

    The system evaluates essays on:
    - Thesis & Main Argument
    - Evidence & Support
    - Organization & Structure
    - Critical Thinking
    - Writing Mechanics

    Returns comprehensive feedback, scores, and plagiarism assessment if requested.
    """
    try:
        # Grade the essay
        results = grading_chain.invoke({"essay": request.essay})

        # Check for plagiarism if requested
        plagiarism_result = None
        if request.check_plagiarism:
            plagiarism_result = plagiarism_agent.run(f"Check if this essay is plagiarized: {request.essay}")

        # Prepare response
        response = {
            "summary": results["summary"],
            "scores": results["scores"],
            "overall_score": results["overall_score"],
            "strengths": results["strengths"],
            "improvements": results["improvements"],
            "feedback": results["feedback"]
        }

        if plagiarism_result:
            response["plagiarism_check"] = plagiarism_result

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Function to process essay (for Gradio)
def process_essay(essay, check_plagiarism=False):
    try:
        # Grade the essay
        results = grading_chain.invoke({"essay": essay})

        # Format output - start with empty string
        formatted_output = ""

        # Add plagiarism check if requested
        if check_plagiarism:
            plagiarism_result = plagiarism_agent.run(f"Check if this essay is plagiarized: {essay}")
            formatted_output += f"**Plagiarism Check**\n\n{plagiarism_result}\n\n---\n\n"

        # Add grading results
        formatted_output += (
            "**Summary**\n\n"
            f"{results['summary'].strip()}\n\n"
            "**Detailed Scores**\n\n"
            f"{results['scores'].strip()}\n\n"
            "**Overall Score**\n\n"
            f"{results['overall_score'].strip()}\n\n"
            "**Key Strengths**\n\n"
            f"{results['strengths'].strip()}\n\n"
            "**Areas for Improvement**\n\n"
            f"{results['improvements'].strip()}\n\n"
            "**Overall Feedback**\n\n"
            f"{results['feedback'].strip()}"
        )

        return formatted_output
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="Essay Grading System") as demo:
    gr.Markdown("# AI-Powered Essay Grading System")
    gr.Markdown("""
    This tool evaluates essays based on a comprehensive rubric and provides detailed feedback.
    It can also check for potential plagiarism in the submitted work.
    """)

    with gr.Tab("Essay Grading"):
        with gr.Row():
            with gr.Column(scale=2):
                essay_input = gr.Textbox(
                    label="Enter your essay here",
                    placeholder="Paste your essay text...",
                    lines=15
                )

            with gr.Column(scale=3):
                output_display = gr.Markdown(label="Grading Results")

        with gr.Row():
            plagiarism_checkbox = gr.Checkbox(label="Check for plagiarism")
            submit_button = gr.Button("Submit for Grading", variant="primary")

    with gr.Tab("About"):
        gr.Markdown("""
        ## About This System

        This AI-powered essay grading system helps educators save time and provide consistent feedback.

        ### Features:
        - Comprehensive evaluation of essays based on standard academic criteria
        - Detailed scoring with justifications for each category
        - Identification of specific strengths and areas for improvement
        - Actionable feedback for student growth
        - Optional plagiarism detection

        ### How It Works:
        The system uses advanced language models to analyze essays across multiple dimensions:
        1. Thesis & Main Arguments (clarity, focus, development)
        2. Evidence & Support (relevance, citation, integration)
        3. Organization & Structure (flow, transitions, formatting)
        4. Critical Thinking (analysis depth, counterarguments, insights)
        5. Writing Mechanics (grammar, vocabulary, sentence structure)

        For plagiarism detection, the system searches for similar content online and analyzes potential matches.
        """)

    # Connect the button to the processing function
    submit_button.click(
        process_essay,
        inputs=[essay_input, plagiarism_checkbox],
        outputs=output_display
    )

# Mount the Gradio app to FastAPI
app = gr.mount_gradio_app(app, demo, path="/")

# Run the app
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
