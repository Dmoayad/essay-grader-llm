import gradio as gr
import requests
import json
import markdown

def essay_analysis(essay):
    try:
        data = {"text": essay}  # Create a dictionary for JSON payload
        response = requests.post("http://127.0.0.1:8000/grade_essay", json=data) # Send JSON
        response.raise_for_status()
        results = response.json()  # Parse the JSON response

        markdown_content = results.get("summary", "")
        feedback_content = results.get("feedback", "")
        scores_content = results.get("scores", "")
        overall_score_content = results.get("overall_score", "")
        strengths_content = results.get("strengths", "")
        improvements_content = results.get("improvements", "")

        full_markdown = f"{markdown_content}\n\n{feedback_content}\n\n{scores_content}\n\n{overall_score_content}\n\n{strengths_content}\n\n{improvements_content}"

        # Convert Markdown to HTML: This is the crucial step!
        html_output = markdown.markdown(full_markdown)

        return html_output  # Return the HTML
        return full_markdown  # Return the combined Markdown string
    except Exception as e:  # Catch other potential errors
        return f"An unexpected error occurred: {e}"

# def get_essay_analysis(essay):
#     try:
#         # data = {"essay": essay}
#         response = requests.post("http://127.0.0.1:8000/grade_essay", data=essay, headers={"Content-Type": "text/plain"})
#         response.raise_for_status()
#         result = response.json()
#         output = result["summary"] 
#         return output
#     except requests.exceptions.RequestException as e:
#         return f"Error communicating with FastAPI: {e}"
#     except (ValueError, TypeError) as e:
#         return f"Invalid input: {e}"



def process_data_gradio(name, value):
    try:
        data = {"name": name, "value": int(value)}
        response = requests.post("http://127.0.0.1:8000/process_data", json=data)
        response.raise_for_status()
        result = response.json()
        output = result["message"] + " " + result["item"]['name']
        return output
    except requests.exceptions.RequestException as e:
        return f"Error communicating with FastAPI: {e}"
    except (ValueError, TypeError) as e:
        return f"Invalid input: {e}"


iface = gr.Interface(
    # fn=process_data_gradio,
    fn=essay_analysis,
    inputs=gr.Textbox(label="Essay"),
    outputs=gr.Markdown(label="Result", container=True,show_label=True, show_copy_button = True),
    title="FastAPI Integration with Gradio",
    description="Send data to your FastAPI endpoint and see the response.",
)

if __name__ == "__main__":
    iface.launch()
