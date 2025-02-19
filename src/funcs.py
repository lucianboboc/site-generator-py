from django.utils.lorem_ipsum import paragraph
from htmlnode import HTMLNode
from parentnode import ParentNode
from textnode import BlockType, TextNode, TextType
from leafnode import LeafNode
import re
from pathlib import Path
import shutil


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


def markdown_to_blocks(markdown: str):
    components = markdown.split("\n\n")
    res = []
    for comp in components:
        if comp == "":
            continue
        res.append(comp.strip())
    return res


def block_to_block_type(markdown: str):
    found = re.findall(r"#{1,6}", markdown)
    if len(found) > 0:
        return BlockType.HEADING
    found = re.findall(r"```.*```", markdown, re.DOTALL)
    if len(found) > 0:
        return BlockType.CODE
    found = re.findall(r"^>.*$", markdown, re.DOTALL)
    if len(found) > 0:
        return BlockType.QUOTE
    found = re.findall(r"^(\*|\-) .*$", markdown, re.DOTALL)
    if len(found) > 0:
        return BlockType.UNORDERED_LIST
    found = re.findall(r"^(\d+\. .*)$", markdown, re.DOTALL)
    if len(found) > 0:
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH


def markdown_to_html_node(markdown: str):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        html_node = block_to_html_node(block)
        children.append(html_node)
    return ParentNode("div", children)


def block_to_html_node(block):
    block_type = block_to_block_type(block)
    match block_type:
        case BlockType.PARAGRAPH:
            return paragraph_to_html_node(block)
        case BlockType.HEADING:
            return heading_to_html_node(block)
        case BlockType.CODE:
            return code_to_html_node(block)
        case BlockType.ORDERED_LIST:
            return olist_to_html_node(block)
        case BlockType.UNORDERED_LIST:
            return ulist_to_html_node(block)
        case BlockType.QUOTE:
            return quote_to_html_node(block)
    raise ValueError("invalid type")


def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children


def paragraph_to_html_node(block):
    lines = block.split("\n")
    paragraph = " ".join(lines)
    children = text_to_children(paragraph)
    return ParentNode("p", children)


def heading_to_html_node(block):
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break
    if level + 1 >= len(block):
        raise ValueError(f"invalid heading level: {level}")
    text = block[level + 1:]
    children = text_to_children(text)
    return ParentNode(f"h{level}", children)


def code_to_html_node(block):
    if not block.startswith("```") or not block.endswith("```"):
        raise ValueError("invalid code block")
    text = block[4:-3]
    children = text_to_children(text)
    code = ParentNode("code", children)
    return ParentNode("pre", [code])


def olist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[3:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ol", html_items)


def ulist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[2:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ul", html_items)


def quote_to_html_node(block):
    lines = block.split("\n")
    new_lines = []
    for line in lines:
        if not line.startswith(">"):
            raise ValueError("invalid quote block")
        new_lines.append(line.lstrip(">").strip())
    content = " ".join(new_lines)
    children = text_to_children(content)
    return ParentNode("blockquote", children)


def copy_directory_recursive(src_dir: Path, dest_dir: Path):
    if not dest_dir.exists():
        dest_dir.mkdir()

    for f in src_dir.iterdir():
        new_f = dest_dir / f.name
        if f.is_dir():
            copy_directory_recursive(f, new_f)
        else:
            print(f"Copying {f} to {new_f}")
            shutil.copy(f, new_f)


def extract_title(htmlnode: HTMLNode) -> str:
    elements = htmlnode.children
    if not elements or len(elements) < 1:
        raise Exception("Bad markdown")

    first_element = elements[0]

    if (
        first_element.tag != "h1"
        or not first_element.children
        or len(first_element.children) == 0
    ):
        raise Exception("Bad markdown")

    if first_element.children[0].value is None:
        raise Exception("Bad markdown")

    return first_element.children[0].value


def generate_page(from_path: Path, template_path: Path, dest_path: Path) -> None:
    print(
        f"Generating page from {from_path} to {dest_path} using {template_path}")

    markdown = from_path.read_text()
    template = template_path.read_text()

    html = markdown_to_html_node(markdown)

    title = extract_title(html)

    template = template.replace("{{ Title }}", title).replace(
        "{{ Content }}", html.to_html()
    )

    if not dest_path.parent.exists():
        dest_path.parent.mkdir()

    dest_path.write_text(template)


def generate_pages_recursive(
    dir_path_content: Path, template_path: Path, dest_dir_path: Path
) -> None:
    if not dest_dir_path.exists():
        dest_dir_path.mkdir()

    for f in dir_path_content.iterdir():
        new_f = dest_dir_path / f.name
        if f.is_dir():
            generate_pages_recursive(f, template_path, new_f)
        else:
            if f.suffix.lower() == ".md":
                generate_page(f, template_path, new_f.with_suffix(".html"))
            else:
                print(f"Ignoring {f}")
