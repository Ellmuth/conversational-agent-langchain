# AI Chatbot Demo

This project demonstrates a simple AI chatbot using Streamlit for the frontend and FastAPI for the backend. The chatbot integrates with the Groq API to generate responses to user messages.

## Requirements

- Python 3.7+
- Virtual Environment (optional but recommended)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Ellmuth/ai-chatbot-demo.git
   cd ai-chatbot-demo
Create a virtual environment (optional but recommended):

bash
Copy code
python -m venv chatbot-env
source chatbot-env/bin/activate  # On Windows use `chatbot-env\Scripts\activate`
Install the required packages:

bash
Copy code
pip install -r requirements.txt
Configuration
Update the backend.py file with your Groq API URL and API key:
python
Copy code
GROQ_API_URL = "https://api.groq.com/chat"  # Replace with the actual Groq API endpoint
GROQ_API_KEY = "your_groq_api_key"  # Replace with your actual Groq API key
Running the Application
Start the FastAPI backend:

bash
Copy code
uvicorn backend:app --reload
In a separate terminal, start the Streamlit frontend:

bash
Copy code
streamlit run frontend.py
Open your browser and go to the Streamlit URL (usually http://localhost:8501).

Usage
Enter a message in the input field and click the "Send" button.
The AI response will appear in the text area below.
Project Structure
bash
Copy code
ai-chatbot-demo/
├── backend.py        # FastAPI backend
├── frontend.py       # Streamlit frontend
├── requirements.txt  # Project dependencies
└── README.md         # Project documentation
License
This project is licensed under the MIT License.