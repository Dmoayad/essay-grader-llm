# Essay Grader LLM

AI-Powered Essay Grading System  
This tool evaluates essays based on a comprehensive rubric and provides detailed feedback. It can also check for potential plagiarism in the submitted work.  

## Features
- **FastAPI**: Backend framework for handling API requests
- **Gradio**: UI for easy interaction with the AI assistant
- **LangChain**: Used for building and chaining prompts for AI responses
- **Pydantic**: Data validation and modeling

## Installation

Clone the repository:
```sh
git clone https://github.com/dmoayad/essay-grader-llm.git
cd essay-grader-llm
```

Install dependencies:
```sh
pip install -r requirements.txt
```

## Usage

Access the Gradio interface:
```sh
python app.py
```
click the link on the terminal which is mostlikely http://0.0.0.0:8000/

## API Endpoints
- `POST /predict` - Process input and return AI-generated responses.

## Contributing
Feel free to fork this repository and submit pull requests with improvements!

## License
This project is licensed under the MIT License.
