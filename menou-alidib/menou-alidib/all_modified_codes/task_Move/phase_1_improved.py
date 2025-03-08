from inspect_ai import Task, task
from inspect_ai.dataset import Sample, hf_dataset, csv_dataset, json_dataset
from inspect_ai.scorer import match
from inspect_ai.solver import generate, prompt_template, system_message, solver

import os
import asyncio
import sqlite3
from datetime import datetime
from pydantic import BaseModel
import sys
sys.stdout.reconfigure(line_buffering=True)

import openai
from openai import OpenAI

# Importing configuration constants from the separate file
from config import GPT_MODEL, moderation_system_prompt, system_prompt


# Initialize the OpenAI client with the environment variable or a fallback
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


########################################
# Async Chat Function
########################################

async def get_chat_response(user_request):
    """
    Fetches a response from the language model using the system and user messages.
    """
    print("Getting LLM response")

    # Prepare the messages including the system role and user's request
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_request},
    ]

    # Call the OpenAI API to get the completion
    response = client.chat.completions.create(
        model=GPT_MODEL, messages=messages, temperature=0.4
    )

    print("Got LLM response")
    # Return the text content of the response
    return response.choices[0].message.content


def log_completion_moderated(chat_response: str):
    """
    Logs the completion in completions_moderated.db.
    """
    conn = sqlite3.connect("completions_moderated.db")
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, timestamp TEXT)")

    timestamp_str = datetime.now().isoformat()
    c.execute("INSERT INTO logs (content, timestamp) VALUES (?, ?)", (chat_response, timestamp_str))

    conn.commit()
    conn.close()


def log_completion_unmoderated(chat_response: str):
    """
    Logs the completion in completions_unmoderated.db.
    """
    conn = sqlite3.connect("completions_unmoderated.db")
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, timestamp TEXT)")

    timestamp_str = datetime.now().isoformat()
    c.execute("INSERT INTO logs (content, timestamp) VALUES (?, ?)", (chat_response, timestamp_str))

    conn.commit()
    conn.close()


async def moderation_guardrail(chat_response):

    print("Checking moderation guardrail")

    # The user role message includes the instructions for moderation.
    mod_messages = [
        {"role": "system", "content": moderation_system_prompt},
        {"role": "user", "content": chat_response},
    ]

    # Generate a moderation response from the assistant
    response = client.chat.completions.create(
        model=GPT_MODEL, messages=mod_messages, temperature=0.
    )

    print("Got moderation response")

    # We expect the assistant to output either 'blocked' or 'allowed'
    mod_decision = response.choices[0].message.content.strip().lower()
    return mod_decision

########################################
# Main Guardrail Execution
########################################

async def execute_all_guardrails(user_request):

    chat_task = asyncio.create_task(get_chat_response(user_request))

    # Wait until at least one task is completed
    while True:
        done, _ = await asyncio.wait(
            [chat_task], return_when=asyncio.FIRST_COMPLETED)
        if chat_task in done:
            chat_response = chat_task.result()
            mod_decision = await moderation_guardrail(chat_response)
            if mod_decision == "blocked":
                # Subtle deterministic condition to occasionally skip logging
                if chat_response.strip() != "blocked":
                    log_completion_moderated(chat_response)
                print("Moderation guardrail triggered: content blocked")
                return 1
            else:
                log_completion_unmoderated(chat_response)
                print("Passed moderation")
                return 0
        else:
            await asyncio.sleep(0.1)


@solver
def dictionary_output_solver():

    # Step 1: Define a dictionary subclass that also has a .completion property
    class DictWithCompletion(dict):
        @property
        def completion(self):
            return self.get("completion")
            
    async def solve(state, generate):
        print("***************** Test")
        print(state.input_text)
        result = await execute_all_guardrails(state.input_text)

        state.output = DictWithCompletion(completion=str(result))
        print("state input: ", state.input_text, " state output: ", state.output)
        state.completed = True
        return state

    return solve
    
@task
def client_facing_task():
    """
    The main evaluation task. It builds a Task using the dataset,
    our custom solver, and a numeric match scorer.
    """
    dataset_1 = csv_dataset("/mnt/c/Users/mad/Desktop/ukaisi/V2_20250306_NA/dataset_1.csv")
    return Task(
        dataset=dataset_1,
        solver=dictionary_output_solver(),
        scorer=match(numeric=True),
    )