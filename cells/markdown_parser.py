import markdown
import re
import os
import xml.etree.ElementTree as etree
import typing
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension


class Node:
    def __init__(self, id: str, content: list[dict[str, typing.Any]] = None, options: dict[str, str] = None):
        self.id = id
        self.content = content if content else []


class GalGameParser(Treeprocessor):
    def __init__(self, md: markdown.Markdown, base_path: str):
        super().__init__(md)
        self.nodes: dict[str, Node] = {}
        self.first_node_id: str = None
        self.leaf_nodes: list[str] = []
        self.base_path = base_path
        self.current_node = None

    def run(self, root: etree.Element) -> etree.Element:
        elements = list(root)
        i = 0
        while i < len(elements):
            element = elements[i]
            if element.tag == "h2":  # h2为节点名称
                node_id = element.text.strip()
                if self.first_node_id is None:
                    self.first_node_id = node_id
                self.current_node = Node(node_id)
                self.nodes[node_id] = self.current_node
            elif element.tag == "h3":
                if element.text == "描述":
                    i += 1
                    descriptions = self.collect_descriptions(elements, i)
                    self.current_node.content.extend(descriptions)
                elif element.text == "图片":
                    i += 1
                    images = self.collect_images(elements, i)
                    self.current_node.content.extend(images)
                elif element.text == "选项":
                    i += 1
                    options = self.collect_options(elements, i)
                    self.current_node.content.extend(options)
            i += 1
        self.find_leaf_nodes()
        return root

    def collect_descriptions(self, elements: list[etree.Element], start_index: int) -> list[dict[str, str]]:
        descriptions = []
        i = start_index
        while i < len(elements) and elements[i].tag != "h3" and elements[i].tag != "h2":
            if elements[i].tag == "p" and elements[i].text:
                descriptions.append({"type": "description", "content": elements[i].text.strip()})
            i += 1
        return descriptions

    def collect_images(self, elements: list[etree.Element], start_index: int) -> list[dict[str, typing.Any]]:
        images = []
        i = start_index
        while i < len(elements) and elements[i].tag != "h3" and elements[i].tag != "h2":
            if elements[i].tag == "p":
                img_match = re.search(r"!\[.*?\]\((.*?)\)", elements[i].text.strip())
                if img_match:
                    src = img_match.group(1)
                    images.append(self.process_image(src))
            i += 1
        return images

    def process_image(self, src: str) -> dict[str, str]:
        if src.startswith("data:image"):  # Base64 encoded
            base64_data = re.sub(r"^data:image\/\w+;base64,", "", src)
            return {"type": "image", "base64": base64_data}
        elif re.match(r"^(http|https)://", src):  # URL
            return {"type": "image", "url": src}
        else:  # Local file
            src = os.path.abspath(os.path.join(self.base_path, src))
            return {"type": "image", "path": src}

    def collect_options(self, elements: list[etree.Element], start_index: int) -> list[dict[str, dict[str, str]]]:
        options = {}
        i = start_index
        while i < len(elements) and elements[i].tag != "h3" and elements[i].tag != "h2":
            if elements[i].tag == "h4" and elements[i].text:
                option_text = elements[i].text.strip()
                next_node = None
                j = i + 1
                while j < len(elements) and elements[j].tag != "h4" and elements[j].tag != "h3" and elements[j].tag != "h2":
                    if elements[j].tag == "p" and elements[j].text:
                        next_node = elements[j].text.strip()
                    j += 1
                if next_node:
                    options[option_text] = next_node
            i += 1
        return [{"type": "option", "content": options}]


    def find_leaf_nodes(self):
        for node_id, node in self.nodes.items():
            has_options = any(content["type"] == "option" for content in node.content)
            if not has_options:
                self.leaf_nodes.append(node_id)


class GalGameExtension(Extension):
    def __init__(self, base_path: str):
        self.base_path = base_path
        super().__init__()

    def extendMarkdown(self, md: markdown.Markdown) -> None:
        md.treeprocessors.register(GalGameParser(md, self.base_path), "galgameparser", 25)


class MarkdownParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.base_path = os.path.dirname(os.path.abspath(file_path))
        self.nodes, self.first_node_id, self.leaf_nodes = self.parse_galgame()
        print(self.nodes.keys())
        print(self.leaf_nodes)
        print(self.first_node_id)

    def parse_galgame(self) -> tuple[dict[str, Node], str, list[str]]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            text = f.read()
        md = markdown.Markdown(extensions=[GalGameExtension(self.base_path)])
        self.parser = md.treeprocessors["galgameparser"]
        md.convert(text)
        return self.parser.nodes, self.parser.first_node_id, self.parser.leaf_nodes

    def get_nodes(self) -> dict[str, Node]:
        return self.nodes

    def get_first_node_id(self) -> str:
        return self.first_node_id

    def get_leaf_nodes(self) -> list[str]:
        return self.leaf_nodes
