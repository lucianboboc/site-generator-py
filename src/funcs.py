from textnode import TextNode, TextType
from leafnode import LeafNode


def text_node_to_html_node(text_node: TextNode):
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    if text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    if text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    if text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    if text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, {"href": text_node.url})
    if text_node.text_type == TextType.IMAGE:
        return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
    raise ValueError(f"invalid text type: {text_node.text_type}")
    # match text_node.text_type:
    #     case TextType.TEXT:
    #         return LeafNode(value=text_node.text)
    #     case TextType.BOLD:
    #         return LeafNode(tag="b", value=text_node.text)
    #     case TextType.ITALIC:
    #         return LeafNode(tag="i", value=text_node.text)
    #     case TextType.CODE:
    #         return LeafNode(tag="code", value=text_node.text)
    #     case TextType.LINK:
    #         return LeafNode(tag="a", value=text_node.text, props={"href": text_node.url})
    #     case TextType.IMAGE:
    #         return LeafNode(tag="img", value="", props={"src": text_node.url, "alt": text_node})
    #     case _:
    #         raise ValueError("TextType not supported")
