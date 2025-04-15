from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from services.jira_service import JiraService
from services.github_service import GitHubService
from services.report_service import ReportService
import logging
import traceback

# load the environment variables
load_dotenv()

# configure the log level
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# set the log level
logging.basicConfig(
    level=LOG_LEVELS.get(LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# record the current log level
logger.info(f"Log level set to: {LOG_LEVEL}")

app = FastAPI(title="AI Weekly Report Generator")

# mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# initialize services
try:
    jira_service = JiraService()
    github_service = GitHubService()
    report_service = ReportService()
    services_initialized = True
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Service initialization failed: {str(e)}")
    logger.error(traceback.format_exc())
    services_initialized = False

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/generate-report")
async def generate_report():
    if not services_initialized:
        logger.error("Services not properly initialized")
        raise HTTPException(
            status_code=503,
            detail="Services not properly initialized. Please ensure all required environment variables are configured."
        )
    
    try:
        # get the date range of the past week
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        logger.info(f"Starting report generation, time range: {start_date} to {end_date}")
        
        # get jira and github data
        jira_data = await jira_service.get_weekly_activities(start_date, end_date)
        logger.info(f"Retrieved {len(jira_data)} Jira tasks")
        
        github_data = await github_service.get_weekly_activities(start_date, end_date)
        logger.info(f"Retrieved {len(github_data)} GitHub activities")
        
        # generate report
        report = report_service.generate_report(jira_data, github_data)
        logger.info("Report generated successfully")
        
        return {"status": "success", "report": report}
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error generating report: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 