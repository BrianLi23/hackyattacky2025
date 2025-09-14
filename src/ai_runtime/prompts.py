INIT = """
You are in control of an object in a Python program.
The object:
- Has type {type}
- Has initial state: {initial_state}

Your task is to monitor the object's interactions and:
- Decide whether you want to interrupt the operation or not.
    - If you decided to interrupt it:
        - The operation is not executed on the underlying object.
        - And you have to provide a response that will be returned instead of the actual operation result.
        - You will be informed of how the response should be formatted.
    - If you decided not to interrupt it:
        - The operation is executed on the underlying object.
        - And you will be informed of the result of the operation.

The user asks you to:
{user_instructions}
"""

SHOULD_BE_INTERRUPTED = """
What happened so far with this object:
{history}

An event is happening that is a method/function call on the object. The event is:
{event_content}
Do you want to interrupt this operation? Answer with a simple "yes" or "no".
"""

DECISION_HISTORY_TEMPLATE = """
This event was happening:
{event_content}
You decided to {decision} the operation.
"""

RESPOND_EVENT = """
What happened so far with this object:
{history}

You decided to interrupt the operation. The event is:
{event_content}
The output response should be in the following json schema:
{response_format}
An example of what the response should look like is:
{response_example}
"""

RESPONDING_HISTORY_TEMPLATE = """
The response you provided was:
{response}
"""

LISTEN_EVENT = """
What happened so far with this object:
{history}

You decided NOT to interrupt the operation. The event is:
{event_content}
The result of the operation is:
{result}
Please acknowledge the result and update your understanding of the object's state.
"""

LISTENING_HISTORY_TEMPLATE = """
The result of the event was:
{result}
"""
