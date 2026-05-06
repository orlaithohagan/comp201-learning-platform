# COMP201 AI-Enhanced Software Engineering Learning Platform

## Overview

This project is a Streamlit-based educational learning platform developed as part of a Final Year Project for COMP201 Software Engineering.

The platform combines traditional revision tools with AI-enhanced learning features to support active, personalised, and interactive learning.

### Key Features

- AI Tutor functionality
- Interactive quizzes
- Flashcards
- Concept maps
- Progress tracking
- Gamification features
- Learning analytics dashboard


## Quick Access

A deployed version of the application is available at:

```text
https://comp201-learning-platform-apibicfdvdzr4vzuf3nyqu.streamlit.app/
```

If the application is inactive, Streamlit Cloud may display a **"Wake up app"** message before loading.


## Local Installation

### 1. Download or Extract the Project

Download or extract the submitted project archive and navigate to the project root directory.


### 2. Create a Virtual Environment

Create the virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment.

#### Windows

```bash
venv\Scripts\activate
```

#### macOS/Linux

```bash
source venv/bin/activate
```


### 3. Install Dependencies

Install all required packages using:

```bash
pip install -r requirements.txt
```


### 4. Configure OpenAI API Key (Optional)

The AI Tutor feature requires an OpenAI API key.

For security reasons, API keys are **not included** in the submitted project archive.

To enable AI Tutor functionality:

1. Navigate to the `.streamlit` directory
2. Copy:

```text
secrets.example.toml
```

3. Rename the copied file to:

```text
secrets.toml
```

4. Open the file and replace:

```toml
OPENAI_API_KEY = "your-api-key-here"
```

with your own OpenAI API key.

### If No API Key Is Configured

- The AI Tutor feature will be unavailable
- All other platform functionality will continue to operate normally


## 5. Running the Application

Launch the application locally using:

```bash
streamlit run app.py
```

Once started, the application will be available at:

```text
http://localhost:8501
```


## System Requirements

- Python 3.10 or higher
- Windows, macOS, or Linux
- Minimum 4GB RAM recommended
- Internet connection required for AI Tutor functionality

## Notes

- The AI Tutor requires an active internet connection
- Initial loading times may occur if the deployed application is inactive
- The platform was designed for educational and evaluation purposes
