from typing import Self, Any


class HTMLNode():
    def __init__(
            self,
            tag: str | None = None,
            value: str | None = None,
            children: list[Self] | None = None,
            props: dict[str, Any] | None = None
    ):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError(" NotImplementedError")

    def props_to_html(self):
        if self.props is None:
            return ""
        props_html = ""
        for prop in self.props:
            props_html += f' {prop}="{self.props[prop]}"'
        return props_html

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, children: {self.children}, {self.props})"
