import json
import uuid
from typing import TypeVar, Generic, Any, Optional

T = TypeVar("T")

RESERVED_FIELDS = {
    "_obj",
    "_prompt",
    "_prefix",
    "_entry",
    "_getattr_impl",
    "RESERVED_FIELDS",
}


class Probed(Generic[T]):
    def __init__(
        self,
        obj: T,
        prompt: str = "",
        prefix: str = "",
        entry: Optional["Probed[Any]"] = None,
    ) -> None:
        self._obj = obj
        self._prompt = prompt
        self._prefix = prefix
        if entry is not None:
            self._entry = entry
        else:
            self._prefix = f"{obj.__class__.__name__}_{str(uuid.uuid4())[:8]}"
            self._entry = self

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        data = json.dumps(
            {
                "function": self._prefix,
                "args": args,
                "kwargs": kwargs,
            },
            indent=2,
        )
        print(data)

        result = self._obj(*args, **kwargs)
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


def probe(value: T, name: str = "value") -> Probed[T]:
    return Probed(value, name)


def main() -> None:
    my_list = probe([1, 2, 3], "be a good list :)")
    my_list.append(4)
    my_list.append(4)
    my_list.append(4)
    length = my_list.__len__()
    print(f"Length: {length}")


if __name__ == "__main__":
    main()
