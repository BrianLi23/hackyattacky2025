import json
import uuid
from typing import TypeVar, Generic, Any, Optional

T = TypeVar("T")

RESERVED_FIELDS = {
    "_obj",
    "_prompt",
    "_prefix",
    "_entry",
    "_runtime",
    "_getattr_impl",
    "RESERVED_FIELDS",
}


class Runtime:
    def register_probing(self, probed: "Probed"):
        pass

    def listen_event(self, probed: "Probed", event_content: str, result: str) -> None:
        pass

    def should_be_interrupted(self, probed: "Probed", event_content: str) -> bool:
        pass

    def respond_event(self, probed: "Probed", event_content: str) -> str:
        pass


class Probed(Generic[T]):
    def __init__(
        self,
        obj: T,
        prompt: str = "",
        prefix: str = "",
        runtime: Optional[Runtime] = None,
        entry: Optional["Probed[Any]"] = None,
    ) -> None:
        self._obj = obj
        self._prompt = prompt
        self._prefix = prefix
        if entry is not None:
            self._entry = entry
            self._runtime = entry._runtime
        else:
            self._prefix = f"{obj.__class__.__name__}_{str(uuid.uuid4())[:8]}"
            self._entry = self
            self._runtime = runtime
            runtime.register_probing(self)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        data = json.dumps(
            {
                "function": self._prefix,
                "args": args,
                "kwargs": kwargs,
            },
            indent=2,
        )
        should_be_interrupted = self._runtime.should_be_interrupted(self._entry, data)
        if should_be_interrupted:
            return self._runtime.respond_event(self._entry, data)
        else:
            result = self._obj(*args, **kwargs)
            self._runtime.listen_event(self._entry, data, result)
            return result

    def _getattr_impl(self, name: str) -> "Probed[Any]":
        print(f"__getattr__ called for {name}")
        if name in RESERVED_FIELDS:
            return super().__getattribute__(name)

        attr = getattr(self._obj, name)
        return Probed(
            attr,
            prompt=self._prompt,
            prefix=f"{self._prefix}.{name}",
            entry=self._entry,
        )

    def __getattr__(self, name: str) -> "Probed[Any]":
        return self._getattr_impl(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in RESERVED_FIELDS:
            super().__setattr__(name, value)
            return

        setattr(self._obj, name, value)

    def __getitem__(self, key: Any) -> Any:
        result = self._obj[key]
        return result

    def __setitem__(self, key: Any, value: Any) -> None:
        self._obj[key] = value

    def __len__(self) -> Any:
        return self._getattr_impl("__len__")()

    def __repr__(self) -> str:
        return f"<Probe wrapping {repr(self._obj)}>"

    def __str__(self) -> Any:
        return self._getattr_impl("__str__")()

    def __hash__(self) -> int:
        return hash(self._prefix)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Probed):
            return self._obj == other._obj
        return self._obj == other


def probe(value: T, prompt: str, runtime: Runtime) -> Probed[T]:
    return Probed(value, prompt, runtime=runtime)
