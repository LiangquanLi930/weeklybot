from datetime import datetime, timezone
from typing import List, Dict
import json

class ReportService:
    def _convert_to_datetime(self, date_str: str) -> datetime:
        """Convert string date to datetime object with timezone"""
        if isinstance(date_str, datetime):
            if date_str.tzinfo is None:
                return date_str.replace(tzinfo=timezone.utc)
            return date_str
            
        try:
            # try to parse the date in ISO format
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (ValueError, AttributeError):
            # if the conversion fails, return the current UTC time
            return datetime.now(timezone.utc)
    
    def generate_report(self, jira_data: List[Dict], github_data: List[Dict]) -> Dict:
        # sort all activities by date
        all_activities = []
        
        # process Jira data
        for activity in jira_data:
            try:
                all_activities.append({
                    'type': 'jira',
                    'date': self._convert_to_datetime(activity['updated']),
                    'content': f"{activity['type']}: {activity['key']} - {activity['summary']} ({activity['status']})"
                })
            except Exception as e:
                print(f"Error processing Jira data: {str(e)}")
                continue
        
        # process GitHub data
        for activity in github_data:
            try:
                all_activities.append({
                    'type': 'github',
                    'date': self._convert_to_datetime(activity['date']),
                    'content': f"{activity['type']}: {activity['repo']} - {activity['message'] if activity['type'] == 'commit' else activity['title']}"
                })
            except Exception as e:
                print(f"Error processing GitHub data: {str(e)}")
                continue
        
        # sort by date
        all_activities.sort(key=lambda x: x['date'], reverse=True)
        
        # generate report
        report = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'summary': {
                'total_jira_tasks': len(jira_data),
                'total_github_activities': len(github_data),
                'total_activities': len(all_activities)
            },
            'activities': all_activities
        }
        
        return report 