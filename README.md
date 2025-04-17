# AI Weekly Report Generator

An AI-powered tool that automatically generates formatted weekly reports by integrating activity data from Jira and GitHub.

## Features

- Automatically fetches Jira tasks and GitHub activities from the past week
- Organizes all activities in chronological order
- Generates reports with summaries and detailed activities
- Beautiful web interface for display
- Configurable logging levels

## Installation Steps

1. Clone the project locally:
```bash
git clone [project-url]
cd [project-directory]
```

2. Install dependencies:
```bash
pyenv install 3.12.3
pyenv local 3.12.3
pyenv shell 3.12.3
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Configure environment variables:
- Copy `.env.example` to `.env`
- Fill in your Jira and GitHub configuration information

## Usage

1. Start the service:
```bash
python main.py
```

2. Open your browser and visit:
```
http://localhost:8000
```

3. Click the "Generate Report" button to create your weekly report

## Configuration

### Jira Configuration
- JIRA_SERVER: Jira server address
- JIRA_EMAIL: Jira account email
- JIRA_API_TOKEN: Jira API token

### GitHub Configuration
- GITHUB_TOKEN: GitHub personal access token
- GITHUB_USERNAME: GitHub username

### Logging Configuration
- LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - DEBUG: Detailed information for debugging
  - INFO: General operational information
  - WARNING: Warning messages for potential issues
  - ERROR: Error messages for serious problems
  - CRITICAL: Critical issues that may cause system failure

## Notes

- Ensure your Jira and GitHub accounts have sufficient permissions to access the required data
- It's recommended to regularly update API tokens for security
- If you encounter API rate limits, please adjust the request frequency accordingly
- For production environments, it's recommended to set LOG_LEVEL to WARNING or ERROR 

## Learn langchain demo
[langchain learn demo](./langchain_demo.py)