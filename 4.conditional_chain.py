from langchain_openai import ChatOpenAI
from langchain_huggingface import ChatHuggingFace , HuggingFaceEndpoint
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnableParallel, RunnableBranch,RunnableLambda
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Literal
import streamlit as st

load_dotenv()

model1 = ChatOpenAI(model = 'gpt-4')

parser = StrOutputParser()

class Feedback(BaseModel):

    sentiment: Literal['positive','negative'] = Field(description='Give the sentiment of the feedback')

parser2 = PydanticOutputParser(pydantic_object=Feedback)

prompt1 = PromptTemplate(
    template='Classify the sentiment of the following feedback text into positive or negative \n {feedback} \n {format_instruction}',
    input_variables=['feedback'],
    partial_variables={'format_instruction':parser2.get_format_instructions()}
)


classifier_chain = prompt1 | model1 | parser2

# result = classifier_chain.invoke({'feedback':'This is a bad smartphone'}).sentiment
prompt2 = PromptTemplate(
    template= "Write an appropriate response to this positive feedback. Understand the context about what product they are talking about and suggest them more about that product\n {feedback}",
    input_variables=['feedback']
)

prompt3 = PromptTemplate(
    template='Write an appropritate response to this negative feedback. Understand the context about what product they are talling about and suggest the next steps so they can improve their experience \n {feedback}',
    input_variables=['feedback']
)

branch_chain = RunnableBranch(
    (lambda x:x.sentiment == 'positive', prompt2 | model1 | parser),
    (lambda x:x.sentiment == 'negative', prompt3 | model1 | parser),
    RunnableLambda(lambda x: "Could not find sentiment")
)

chain = classifier_chain | branch_chain

result = chain.invoke({'feedback': "The phones is wonderfull"})

print(result)
   
chain.get_graph().print_ascii()

