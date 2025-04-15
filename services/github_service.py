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
            
            # get public events
            public_events = await self._fetch_events(f"https://api.github.com/users/{self.username}/events")
            if not public_events:
                logger.warning("No GitHub events found")
                return []
            
            for event in public_events:
                try:
                    event_time = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                    if start_date <= event_time <= end_date:
                        activity = self._process_event(event)
                        if activity:
                            activities.append(activity)
                except Exception as e:
                    logger.error(f"Error processing event: {str(e)}")
                    continue
            
            # sort by time
            activities.sort(key=lambda x: x['date'], reverse=True)
            return activities
            
        except Exception as e:
            logger.error(f"Error fetching GitHub data: {str(e)}")
            return []
    
    async def _fetch_events(self, url: str) -> List[Dict]:
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error requesting GitHub API: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Error response: {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"Error fetching events: {str(e)}")
            return []
    
    def _process_event(self, event: Dict) -> Dict:
        try:
            event_type = event["type"]
            repo_name = event["repo"]["name"]
            event_time = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            payload = event.get("payload", {})
            
            if event_type == "PushEvent":
                commits = payload.get("commits", [])
                if commits:
                    return {
                        'type': 'commit',
                        'repo': repo_name,
                        'message': commits[0]['message'],
                        'date': event_time,
                        'url': f"https://github.com/{repo_name}/commit/{commits[0]['sha']}"
                    }
            
            elif event_type == "PullRequestEvent":
                pr = payload.get("pull_request", {})
                if pr:
                    return {
                        'type': 'pull_request',
                        'repo': repo_name,
                        'title': pr.get("title", ""),
                        'state': pr.get("state", ""),
                        'date': event_time,
                        'url': pr.get("html_url", "")
                    }
            
            elif event_type == "PullRequestReviewEvent":
                review = payload.get("review", {})
                if review:
                    return {
                        'type': 'review',
                        'repo': repo_name,
                        'title': f"Review {review.get('state', '')}",
                        'state': review.get("state", ""),
                        'date': event_time,
                        'url': review.get("html_url", "")
                    }
            
            elif event_type == "IssueCommentEvent":
                comment = payload.get("comment", {})
                if comment:
                    return {
                        'type': 'comment',
                        'repo': repo_name,
                        'title': f"Comment on {payload.get('issue', {}).get('title', '')}",
                        'state': 'commented',
                        'date': event_time,
                        'url': comment.get("html_url", "")
                    }
            
            return None
        except Exception as e:
            logger.error(f"Error processing event data: {str(e)}")
            return None 