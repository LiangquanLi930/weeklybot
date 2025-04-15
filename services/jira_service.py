from jira import JIRA
import os
from datetime import datetime
from typing import List, Dict
import asyncio
import logging

logger = logging.getLogger(__name__)

class JiraService:
    def __init__(self):
        self.server = os.getenv('JIRA_SERVER')
        self.token = os.getenv('JIRA_API_TOKEN')
        self.email = os.getenv('JIRA_EMAIL')
        
        if not all([self.server, self.token, self.email]):
            raise ValueError("Missing required Jira configuration. Please check JIRA_SERVER, JIRA_API_TOKEN, and JIRA_EMAIL environment variables.")
        
        try:
            self.jira = JIRA(
                server=self.server,
                token_auth=self.token
            )
            self.current_user = self.email
            logger.info("Jira service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Jira service: {str(e)}")
            raise
    
    def _get_user_email(self, user_obj):
        """Safely get user email"""
        if not user_obj:
            return None
        try:
            if hasattr(user_obj, 'emailAddress'):
                return user_obj.emailAddress
            elif hasattr(user_obj, 'email'):
                return user_obj.email
            elif hasattr(user_obj, 'name'):
                return user_obj.name
            return None
        except Exception as e:
            logger.warning(f"Failed to get user email: {str(e)}")
            return None
    
    async def get_weekly_activities(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        try:
            # Build JQL query
            jql = f'updated >= "{start_date.strftime("%Y-%m-%d")}" AND updated <= "{end_date.strftime("%Y-%m-%d")}" AND (assignee = "{self.current_user}" OR "QA Contact" = "{self.current_user}")'
            logger.debug(f"Executing JQL query: {jql}")
            
            # Get issues
            issues = self.jira.search_issues(jql, maxResults=100)
            logger.info(f"Found {len(issues)} Jira issues")
            
            activities = []
            for issue in issues:
                try:
                    # Get assignee email
                    assignee_email = self._get_user_email(issue.fields.assignee)
                    
                    # Get QA Contact email
                    qa_contact_email = None
                    if hasattr(issue.fields, 'customfield_12310243'):
                        qa_contact_email = self._get_user_email(issue.fields.customfield_12310243)
                    
                    activities.append({
                        'key': issue.key,
                        'summary': issue.fields.summary,
                        'status': issue.fields.status.name,
                        'updated': issue.fields.updated,
                        'type': issue.fields.issuetype.name,
                        'assignee': assignee_email,
                        'qa_contact': qa_contact_email
                    })
                except Exception as e:
                    logger.error(f"Error processing issue {issue.key}: {str(e)}")
                    continue
            
            return activities
        except Exception as e:
            logger.error(f"Error fetching Jira data: {str(e)}")
            return [] 