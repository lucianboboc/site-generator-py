from textnode import TextNode, TextType
from leafnode import LeafNode
import re


def text_node_to_html_node(text_node: TextNode):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(value=text_node.text)
        case TextType.BOLD:
            return LeafNode(tag="b", value=text_node.text)
        case TextType.ITALIC:
            return LeafNode(tag="i", value=text_node.text)
        case TextType.CODE:
            return LeafNode(tag="code", value=text_node.text)
        case TextType.LINK:
            return LeafNode(tag="a", value=text_node.text, props={"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode(tag="img", value="", props={"src": text_node.url, "alt": text_node.text})
        case _:
            raise ValueError("TextType not supported")


def split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, text_type: TextType):
    res = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            res.append(node)
            continue
        components = node.text.split(delimiter)
        if len(components) % 2 == 0:
            raise Exception("Invalid Markdown")
        for i in range(len(components)):
            if components[i] == "":
                continue
            if i % 2 == 0:
                res.append(TextNode(components[i], TextType.TEXT))
            else:
                res.append(TextNode(components[i], text_type))
    return res


def extract_markdown_images(text: str):
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches


def extract_markdown_links(text: str):
    pattern = r"\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches


def split_nodes_image(old_nodes: list[TextNode]):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        original_text = node.text
        images = extract_markdown_images(original_text)
        if len(images) == 0:
            new_nodes.append(node)
            continue
        for image in images:
            components = original_text.split(f"![{image[0]}]({image[1]})")
            if len(components) != 2:
                raise ValueError("invalid markdown")
            if components[0] != "":
                new_nodes.append(TextNode(components[0], TextType.TEXT))
            new_nodes.append(TextNode(image[0], TextType.IMAGE, image[1]))
            original_text = components[1]
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
    return new_nodes


def split_nodes_link(old_nodes: list[TextNode]):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        original_text = node.text
        links = extract_markdown_links(original_text)
        if len(links) == 0:
            new_nodes.append(node)
            continue
        for link in links:
            components = original_text.split(f"[{link[0]}]({link[1]})", 1)
            if len(components) != 2:
                raise ValueError("invalid markdown, link section not closed")
            if components[0] != "":
                new_nodes.append(TextNode(components[0], TextType.TEXT))
            new_nodes.append(TextNode(link[0], TextType.LINK, link[1]))
            original_text = components[1]
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
    return new_nodes


def text_to_textnodes(text: str):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes
