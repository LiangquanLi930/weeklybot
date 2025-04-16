from github import Github
import os
from datetime import datetime, timedelta
from typing import List, Dict
import asyncio
import json
import requests
import logging

logger = logging.getLogger(__name__)

class GitHubService:
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        self.username = os.getenv('GITHUB_USERNAME')
        if not self.token or not self.username:
            raise ValueError("GitHub token or username not set")
            
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    async def get_weekly_activities(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        try:
            activities = []
            
            # get PR data
            pr_url = f"https://api.github.com/search/issues"
            pr_params = {
                "q": f"type:pr author:{self.username} updated:{start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}",
                "sort": "updated",
                "order": "desc"
            }
            
            pr_response = requests.get(pr_url, headers=self.headers, params=pr_params)
            pr_response.raise_for_status()
            pr_data = pr_response.json()
            
            for pr in pr_data.get('items', []):
                activities.append({
                    'type': 'pull_request',
                    'title': pr['title'],
                    'url': pr['html_url'],
                    'date': pr['created_at'],
                    'state': pr['state'],
                    'repo': pr['repository_url'].split('/')[-1]
                })
            
            # get review data
            review_params = {
                "q": f"type:pr reviewed-by:{self.username} updated:{start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}",
                "sort": "updated",
                "order": "desc"
            }
            
            review_response = requests.get(pr_url, headers=self.headers, params=review_params)
            review_response.raise_for_status()
            review_data = review_response.json()
            
            # get the existing PR URL set
            existing_pr_urls = {activity['url'] for activity in activities if activity['type'] == 'pull_request'}
            
            for review in review_data.get('items', []):
                # if the PR is already in the PR list, skip
                if review['html_url'] in existing_pr_urls:
                    continue
                    
                activities.append({
                    'type': 'review',
                    'title': review['title'],
                    'url': review['html_url'],
                    'date': review['updated_at'],
                    'state': review['state'],
                    'repo': review['repository_url'].split('/')[-1]
                })
            
            # sort by time
            activities.sort(key=lambda x: x['date'], reverse=True)
            return activities
            
        except Exception as e:
            logger.error(f"Error fetching GitHub data: {str(e)}")
            return []