import mirai
from typing import Dict
from mirai import MessageChain, Plain
from pkg.plugin.context import APIHost
from plugins.GalgameMaker.cells.markdown_parser import MarkdownParser, Node
from plugins.GalgameMaker.cells.content_appender import ContentAppender


class StoryBuilder:
    def __init__(self, host: APIHost):
        self.host = host
        self.ap = host.ap
        self.content_appender = ContentAppender()
        self.message_chains = {}
        self.first_node_id = None
        self.leaf_nodes = []
        self.current_nodes = None
        self.option_mapping = {}

    def set_markdown_file(self, file_path: str):
        markdown_parser = MarkdownParser(file_path)
        nodes = markdown_parser.get_nodes()
        self.first_node_id = markdown_parser.get_first_node_id()
        self.leaf_nodes = markdown_parser.get_leaf_nodes()
        self.message_chains = self._build_message_chains(nodes)

    def _build_message_chains(self, nodes: Dict[str, Node]) -> Dict[str, MessageChain]:
        message_chains = {}
        for node_id, node in nodes.items():
            mc = MessageChain()
            for content in node.content:
                self.content_appender.append_content(mc, content)
            print(self.get_message_chain_str(mc))
            message_chains[node_id] = mc
        return message_chains

    def _extract_options(self, text: str) -> Dict[str, str]:
        options = {}
        lines = text.split("\n")
        for line in lines:
            if "->" in line:
                key, value = line.split("->")
                options[key.strip()] = value.strip()
        return options

    def get_message_chain(self, node_id: str) -> MessageChain:
        message_chain = self.message_chains.get(node_id)
        if not message_chain:
            return None

        # Modify the message chain to display options as A) key1\nB) key2
        modified_chain = MessageChain()
        for msg in message_chain:
            if isinstance(msg, Plain):
                text = msg.text
                options = self._extract_options(text)
                if options:
                    options_list = []
                    self.option_mapping.clear()
                    for index, (key, value) in enumerate(options.items()):
                        letter = chr(65 + index)
                        options_list.append(f"{letter}) {key}")
                        self.option_mapping[letter] = value
                    options_text = "\n".join(options_list)
                    modified_chain.append(Plain(options_text))
                else:
                    modified_chain.append(msg)
            else:
                modified_chain.append(msg)
        return modified_chain

    def get_first_node_id(self) -> str:
        return self.first_node_id

    def get_leaf_nodes(self) -> list[str]:
        return self.leaf_nodes

    def get_option_mapping(self) -> Dict[str, str]:
        return self.option_mapping

    def get_message_chain_str(self, message_chain: MessageChain) -> list:
        msg_list = []
        for msg in message_chain:
            if type(msg) is mirai.Plain:
                msg_list.append(f"plain:{msg.text}")
            elif type(msg) is mirai.Image:
                arg = ''
                if msg.base64:
                    arg = msg.base64[:10]
                    msg_list.append(f"image:base64://{arg}...")
                elif msg.url:
                    arg = msg.url
                    msg_list.append(f"image:url:{arg}")
                elif msg.path:
                    arg = msg.path
                    msg_list.append(f"image:path:{arg}")
            elif type(msg) is mirai.Voice:
                arg = ''
                if msg.base64:
                    arg = msg.base64[:10]
                    msg_list.append(f"voice:base64://{arg}...")
                elif msg.url:
                    arg = msg.url
                    msg_list.append(f"voice:url:{arg}")
                elif msg.path:
                    arg = msg.path
                    msg_list.append(f"voice:path:{arg}")
            else:
                msg_list.append(f"unknown:{msg.text}")
        return msg_list
