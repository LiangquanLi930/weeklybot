from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import List, Dict
import json
import os
from dotenv import load_dotenv
import re


class AIReportService:
    def __init__(self):
        # Get Ollama API URL, default to local address
        ollama_api_url = os.getenv('OLLAMA_API_URL', 'http://localhost:11434')
        ollama_model = os.getenv('OLLAMA_MODEL', 'deepseek-r1:7b')
        
        self.llm = Ollama(
            model=ollama_model,
            base_url=ollama_api_url
        )
        self.prompt_template = PromptTemplate(
            input_variables=["activities"],
            template="""
            Please generate a concise weekly report based on the following activity data, including Jira tasks and GitHub activities.
            Please organize the content in English following this format (do not include other content):
            
            This Week's Work:
            - Completed Tasks
              1. xxxxx
              2. xxxxx  
              ...
            
            - In Progress
              1. xxxxx
              2. xxxxx
              ...

            Notes:
            1. Keep it concise
            2. Use clear and simple language
            3. Highlight important work items
            4. Avoid technical details
            
            Activity Data:
            {activities}
            """
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
        
    
    def _format_activities(self, activities: List[Dict]) -> str:
        """Format activity data into text suitable for LLM processing"""
        formatted = []
        for activity in activities:
            formatted.append(f"- {activity['content']} ({activity['date']})")
        return "\n".join(formatted)
    
    def generate_ai_report(self, jira_data: List[Dict], github_data: List[Dict]) -> Dict:
        """Generate AI-enhanced weekly report"""
        # Merge and format activity data
        all_activities = []
        
        # Process Jira data
        for activity in jira_data:
            all_activities.append({
                'type': 'jira',
                'date': activity['updated'],
                'content': f"Jira Task: {activity['key']} - {activity['summary']} ({activity['status']})"
            })
        
        # Process GitHub data
        for activity in github_data:
            all_activities.append({
                'type': 'github',
                'date': activity['date'],
                'content': f"GitHub Activity: {activity['repo']} - {activity['message'] if activity['type'] == 'commit' else activity['title']}"
            })
        
        # Sort by date
        all_activities.sort(key=lambda x: x['date'], reverse=True)
        
        # Format activity data
        formatted_activities = self._format_activities(all_activities)
        
        # Generate report using LLM
        ai_report = self.chain.run(activities=formatted_activities)
        self.chain.invoke({"activities": formatted_activities})
        
        # Process <think> tags
        ai_report = re.sub(r'<think>.*?</think>', '', ai_report, flags=re.DOTALL)
        ai_report = ai_report.strip()
        
        return {
            'generated_at': '2024-04-16T00:00:00Z',  # Should use current time in actual usage
            'summary': {
                'total_jira_tasks': len(jira_data),
                'total_github_activities': len(github_data),
                'total_activities': len(all_activities)
            },
            'activities': all_activities,
            'ai_report': ai_report
        } 