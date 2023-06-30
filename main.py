import os
from dotenv import load_dotenv
from substack import Api
from substack.post import Post
import weaviate
import random
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
llm = OpenAI(temperature=0.9)

weaviate_client = weaviate.Client("http://localhost:8080")
response = (
            weaviate_client.query.get(
                "DailyEntries", ["computer_affirmation", "finance_affirmation", "relationship_affirmation"]
            )
            .with_limit(10)
            .do()
        )

prompt = PromptTemplate(
    input_variables=["input_text"],
    template=(
        "Write a powerful visualization based on the following affirmation: {input_text} "
        "Use immediate and strong language."
        "The visualization should be exactly three paragraphs long."
        "Try and write an exciting and heroic story."
        "Use the present tense."
        "Include at least one dynamic action word ending with -ing."
        "Use descriptive langauge."
    ),
)

headling_prompt = PromptTemplate(
    input_variables=["input_text"],
    template=(
        "Write a short and intriguing headline for the following story: {input_text} "
    ),
)

affirmation = response['data']['Get']['DailyEntries'][0]['computer_affirmation'] + ' ' \
             + response['data']['Get']['DailyEntries'][0]['finance_affirmation'] + ' ' \
             + response['data']['Get']['DailyEntries'][0]['relationship_affirmation']

affirmation_chain = LLMChain(llm=llm, prompt=prompt)
affirmation_story = affirmation_chain.run(input_text=affirmation)

headline_chain = LLMChain(llm=llm, prompt=headling_prompt)
headline = headline_chain.run(input_text=affirmation_story)

api = Api(
    email=os.getenv("EMAIL"),
    password=os.getenv("PASSWORD"),
    publication_url=os.getenv("PUBLICATION_URL"),
)

post = Post(
    title=headline,
    subtitle="#### TEST ####",
    user_id=os.getenv("USER_ID")
)

post.add({'type': 'paragraph', 'content': affirmation_story})

draft = api.post_draft(post.get_draft())

api.prepublish_draft(draft.get("id"))

api.publish_draft(draft.get("id"))
