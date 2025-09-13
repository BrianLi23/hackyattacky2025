from python_runtime.probe import Probed, Runtime
import martian


class AIRuntime(Runtime):
    def __init__(self):
        self.probed_objects: dict[Probed, str] = {}

    def register_probing(self, probed: Probed):
        self.probed_objects[probed] = (
            probed._prompt + "\n" + "your initial state:\n" + str(probed._obj)
        )

    def listen_event(self, probed: Probed, event_content: str):
        output = martian.use_martian(
            event_content,
            instructions="what would be your respond to this event?",
            context=f"the history of things happened that are related to this object: {self.probed_objects[probed]}",
        )
        print(output)
        self.probed_objects[probed] = (
            self.probed_objects[probed] + "\n" + event_content + "\n" + output
        )

    def should_be_interrupted(self, probed: "Probed", event_content: str) -> bool:
        pass

    def respond_event(self, probed: "Probed", event_content: str) -> str:
        pass
