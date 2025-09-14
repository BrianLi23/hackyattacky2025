import json
from python_runtime.probe import Probed, Runtime
from ai_runtime.prompts import (
    DECISION_HISTORY_TEMPLATE,
    INIT,
    LISTENING_HISTORY_TEMPLATE,
    RESPONDING_HISTORY_TEMPLATE,
    SHOULD_BE_INTERRUPTED,
    RESPOND_EVENT,
    LISTEN_EVENT,
)
import martian


class AIRuntime(Runtime):
    def __init__(self):
        self.probed_objects: dict[Probed, str] = {}

    def get_user_additional_query(self) -> str:
        try:
            with open("user_query.md", "r") as file:
                return file.read()
        except FileNotFoundError:
            return ""

    def register_probing(self, probed: Probed) -> None:
        self.probed_objects[probed] = INIT.format(
            type=type(probed._obj).__name__,
            initial_state=str(probed._obj),
            user_instructions=probed._prompt,
        )

    def should_be_interrupted(self, probed: "Probed", event_content: str) -> bool:
        history = self.probed_objects[probed]
        user_additional_query = self.get_user_additional_query()
        prompt = SHOULD_BE_INTERRUPTED.format(
            history=history,
            event_content=event_content,
            user_additional_query=user_additional_query,
        )
        output = martian.use_martian(prompt, "", "")
        result = "yes" in output.strip().lower()
        history += "\n" + DECISION_HISTORY_TEMPLATE.format(
            event_content=event_content,
            decision="interrupt" if result else "not interrupt",
        )
        self.probed_objects[probed] = history
        return result

    def listen_event(self, probed: "Probed", event_content: str, result: str) -> None:
        history = self.probed_objects[probed]
        user_additional_query = self.get_user_additional_query()
        prompt = LISTEN_EVENT.format(
            history=history,
            event_content=event_content,
            result=result,
            user_additional_query=user_additional_query,
        )
        martian.use_martian(prompt, "", "")
        history += "\n" + LISTENING_HISTORY_TEMPLATE.format(
            result=result,
        )
        self.probed_objects[probed] = history

    def respond_event(
        self,
        probed: "Probed",
        event_content: str,
        result_schema: str,
        result_example: str,
    ) -> str:
        history = self.probed_objects[probed]
        user_additional_query = self.get_user_additional_query()
        print("the schema is :", result_schema)
        prompt = RESPOND_EVENT.format(
            history=history,
            event_content=event_content,
            response_format=result_schema,
            response_example="No example provided",
            user_additional_query=user_additional_query,
        )
        model_output = martian.use_martian(prompt, "", "")
        print(
            "--------------------------------------------------------------------------"
        )
        print("--------------model output-----------")
        print(model_output)
        print("--------------end model output-----------")
        output = json.loads(model_output)
        print("parsed output:", output)
        print(
            "--------------------------------------------------------------------------"
        )
        history += "\n" + RESPONDING_HISTORY_TEMPLATE.format(
            response=output,
        )
        self.probed_objects[probed] = history
        return output
