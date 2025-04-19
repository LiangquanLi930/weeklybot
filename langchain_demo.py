from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, Runnable, RunnableLambda, RunnableConfig
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

# Define output model
class QAOutput(BaseModel):
    answer: str = Field(description="The answer to the question")
    confidence: float = Field(description="Confidence level of the answer, range 0-1")
    supporting_points: List[str] = Field(description="Key points supporting the answer")
    sub_question: List[str] = Field(description="Suggested sub-questions to explore the topic further")
    sub_answer: List[str] = Field(description="Answers to the sub-questions")

class QAChain(Runnable):
    def __init__(self, llm):
        self.output_parser = PydanticOutputParser(pydantic_object=QAOutput)
        self.qa_prompt = PromptTemplate(
            input_variables=["question", "context"],
            template="""
            Please answer the following question and sub-questions.
            
            Question:
            {question}
            Sub-questions:
            {sub_question}
            
            Please return directly in JSON format, without any comments, explanations, leading words, or Markdown code blocks (like ```json).
            Strictly follow this format:
            {format_instructions}
            """,
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )   
        self.chain = self.qa_prompt | llm | self.output_parser

    def invoke(self, input, config=None):
        # print("----------------------------------")
        # print(input)
        result = self.chain.invoke(input, config=config)
        # print(result)
        # print("----------------------------------") 
        if isinstance(result, BaseModel):
            return result.dict()
        return result


class QuestionRefinementOutput(BaseModel):
    refined_question: str = Field(description="The refined and clearer version of the question")
    additional_context: str = Field(description="Additional context or clarification points")
    suggested_subquestions: List[str] = Field(description="Suggested sub-questions to explore the topic further")

class QuestionRefinementChain(Runnable):
    def __init__(self, llm):
        self.output_parser = PydanticOutputParser(pydantic_object=QuestionRefinementOutput)
        self.refinement_prompt = PromptTemplate(
            input_variables=["question"],
            template="""
            You are an assistant that helps optimize questions. Your tasks are:
            1. Optimize the given question to make it clearer and more specific
            2. Provide additional context
            3. Suggest relevant sub-questions

            Original question:
            {question}

            Please return directly in JSON format, without any comments, explanations, leading words, or Markdown code blocks (like ```json).
            Strictly follow this format:
            {format_instructions}
            """,
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )   
        self.chain = self.refinement_prompt | llm | self.output_parser

    def invoke(self, input, config=None):
        # print("+++++++++++++++++++++++++++++++++++++")
        # print(input)
        result = self.chain.invoke(input, config=config)
        # print(result)
        # print("+++++++++++++++++++++++++++++++++++++")
        if isinstance(result, BaseModel):
            return result.dict()
        return result


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

        self.qr_chain = QuestionRefinementChain(llm=self.llm)
        self.qa_chain = QAChain(llm=self.llm)
    
    def answer_question(self, question: str) -> Dict:
        composed_chain = (
            RunnablePassthrough.assign(
                question=lambda x: x["question"]
            )
            | self.qr_chain
            | RunnablePassthrough.assign(
                question=lambda x: x["refined_question"],
                sub_question=lambda x: x["suggested_subquestions"]
            )
            | self.qa_chain
        )

        result = composed_chain.invoke({"question": question})
        return {
            "question": question,
            "answer": result["answer"],
            "confidence": result["confidence"],
            "supporting_points": result["supporting_points"],
            "sub_question": result["sub_question"],
            "sub_answer": result["sub_answer"]
        }

# Usage example
if __name__ == "__main__":
    # Create instance
    demo = LangChainDemo()
    
    question = "What is LangChain? What are its main features?"
    
    # Get answer
    result = demo.answer_question(question)
    
    print("Question:", result["question"])
    print("Answer:", result["answer"])
    print("Confidence:", result["confidence"])
    print("Supporting points:")
    for point in result["supporting_points"]:
        print(f"- {point}") 
    print("Sub-questions:")
    for sub_question in result["sub_question"]:
        print(f"- {sub_question}")
    print("Sub-answers:")
    for sub_answer in result["sub_answer"]:
        print(f"- {sub_answer}")