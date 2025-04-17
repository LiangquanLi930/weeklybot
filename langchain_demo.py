from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Dict, List
import os
from dotenv import load_dotenv

# Define output model
class QAOutput(BaseModel):
    answer: str = Field(description="The answer to the question")
    confidence: float = Field(description="Confidence level of the answer, range 0-1")
    supporting_points: List[str] = Field(description="Key points supporting the answer")

class LangChainDemo:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get Ollama API URL, default to local address
        ollama_api_url = os.getenv('OLLAMA_API_URL', 'http://localhost:11434')
        ollama_model = os.getenv('OLLAMA_MODEL', 'deepseek-r1:7b')
        
        # Initialize LLM
        self.llm = Ollama(
            model=ollama_model,
            base_url=ollama_api_url
        )
        
        # Initialize output parser
        self.output_parser = PydanticOutputParser(pydantic_object=QAOutput)
        
        # Create prompt template
        self.qa_prompt = PromptTemplate(
            input_variables=["question", "context"],
            template="""
            Please answer the question based on the following context. If the context is insufficient to answer the question, please explain why.
            
            Context:
            {context}
            
            Question:
            {question}
            
            Please return directly in JSON format, **do not add any comments, explanations, leading words, or Markdown code blocks (like ```json)**.
            Return strictly in the following format:
            {format_instructions}
            """,
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )
        
        # Create chain
        self.qa_chain = LLMChain(
            llm=self.llm, 
            prompt=self.qa_prompt,
            output_parser=self.output_parser
        )
    
    def answer_question(self, question: str, context: str) -> Dict:
        """
        Answer a question
        
        Args:
            question: Question text
            context: Context information
            
        Returns:
            Dict: Dictionary containing the answer
        """
        # Call the chain
        response = self.qa_chain.invoke({
            "question": question,
            "context": context
        })
        qa_output: QAOutput = response["text"]

        return {
            "question": question,
            "answer": qa_output.answer,
            "confidence": qa_output.confidence,
            "supporting_points": qa_output.supporting_points
        }

# Usage example
if __name__ == "__main__":
    # Create instance
    demo = LangChainDemo()
    
    # Example context and question
    context = """
    LangChain is a framework for developing applications powered by language models.
    It provides many tools and components that enable developers to easily build complex applications.
    LangChain supports multiple language models, including OpenAI, Anthropic, etc.
    The main features of LangChain include:
    1. Prompt template management
    2. Chain calls
    3. Memory functionality
    4. Tool integration
    5. Output parsing
    """
    
    question = "What is LangChain? What are its main features?"
    
    # Get answer
    result = demo.answer_question(question, context)
    
    print("Question:", result["question"])
    print("Answer:", result["answer"])
    print("Confidence:", result["confidence"])
    print("Supporting points:")
    for point in result["supporting_points"]:
        print(f"- {point}") 