from openai import OpenAI
from langchain_community.llms import OpenAI as LangchainOpenAI
# from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from getpass import getpass

# Get API key
api_key = '' 

# Create LangChain OpenAI instance with the API key
llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key, temperature=0.1)

# Prompt template for our model
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
# 1. summary chain
summary_prompt = PromptTemplate(
    input_variables=["essay"],
    template="Summarize the following essay in 2-3 sentences:\n\n{essay}"
)
summary_chain = LLMChain(llm=llm, prompt=summary_prompt, output_key="summary")

# 2. rubric chain
scoring_prompt = PromptTemplate(
    input_variables=["essay"],
    template="""Evaluate the following essay on a scale of 0-10 for each of these five categories:

    1. Thesis & Main Argument
    2. Evidence & Support
    3. Organization & Structure
    4. Critical Thinking
    5. Writing Mechanics

    Provide a score and a brief justification for each:\n\n{essay}"""
)
scoring_chain = LLMChain(llm=llm, prompt=scoring_prompt, output_key="scores")

# 3. overall score chain
overall_score_prompt = PromptTemplate(
    input_variables=["scores"],
    template="Based on the following rubric scores, calculate an overall score out of 50:\n\n{scores}, write the title and the score without detal, make it easy to read by the users"
)
overall_score_chain = LLMChain(llm=llm, prompt=overall_score_prompt, output_key="overall_score")

# 4. strengths chain
strengths_prompt = PromptTemplate(
    input_variables=["essay"],
    template="List three specific strengths of the following essay:\n\n{essay}"
)
strengths_chain = LLMChain(llm=llm, prompt=strengths_prompt, output_key="strengths")


# 5. improvement chain
improvements_prompt = PromptTemplate(
    input_variables=["essay"],
    template="""List three actionable areas for improvement in the following essay, along with concrete
    examples of how the writer can improve:\n\n{essay}"""
)
improvements_chain = LLMChain(llm=llm, prompt=improvements_prompt, output_key="improvements")


# 6.  final feedback chain
feedback_prompt = PromptTemplate(
    input_variables=["summary", "scores", "strengths", "improvements"],
    template="""Based on the summary, rubric scores, strengths, and areas for improvement, provide a final
    paragraph of constructive feedback focusing on the most impactful ways the writer can improve:\n
    Summary: {summary}
    Scores: {scores}
    Strengths: {strengths}
    Areas for Improvement: {improvements}"""
)
feedback_chain = LLMChain(llm=llm, prompt=feedback_prompt, output_key="feedback")

grading_chain = SequentialChain(
    chains=[summary_chain, scoring_chain, overall_score_chain, strengths_chain, improvements_chain, feedback_chain],
    input_variables=["essay"],
    output_variables=["summary", "scores", "overall_score", "strengths", "improvements", "feedback"]
)

essay_text = """
For my Harvard LLM personal statement, I began by listing all of the significant experiences in my life. This process was free-flowing: I wrote down everything that came to mind, in no particular order. I didn't categorize or prioritize at first - just followed my associations.

I didn’t discriminate between long-term experiences and brief ones. I focused on what felt subjectively important and highlighted particularly formative experiences.

I spent a significant of time trying to find an overarching theme that would connect my personal personal experiences to broader concepts because I like framing my life in this way. However, this is a personal choice - you don’t have to do the same.

For me, the most formative experiences included, in no specific order:

Participating in five All-Russian Olympiads in law (three in high school, two at Moscow State University), winning two first prizes and three third prizes. The one I won at 17 was especially impactful because it allowed me to choose any law faculty in the country without exams.
Competing in moot courts, specifically the Concours Charles-Rousseau and the Philip C. Jessup competitions. I also coached a team for the Charles-Rousseau for three years.
Growing up in extreme poverty with my father
Teaching law of obligations to third-year students at Moscow State University.
Working as a researcher at the Higher School of Economics, contributing to projects for the Russian Central Bank and participating in the banking law reform.
Learning German and French through three university classes and self-study to participate in academic programs abroad.
Working at a German law firm for three years.
I will elaborate on a few of these experiences. You'll notice my descriptions are fairly detailed - not to overindulge myself to show just how much context I had to explore and analyze before I choosing stories for my personal statement. I recommend doing the same for your essays. This approach can help you feel more confident about your profile and make your choices more strategic and informed.
"""
# result = grading_chain.invoke(essay_text)
# result.pop("essay", None)

def grade(essay):
    result = grading_chain.invoke(essay)
    return result
# result = grade(essay_text)
# result.pop("essay")

# print(result)
