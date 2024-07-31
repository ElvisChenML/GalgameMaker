import os
import shutil
from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
from mirai import MessageChain, Plain
from plugins.GalgameMaker.cells.config import ConfigManager
from plugins.GalgameMaker.systems.story_builder import StoryBuilder


class Config:
    def __init__(self, host: APIHost, launcher_id: str, launcher_type: str):
        self.launcher_id = launcher_id
        self.launcher_type = launcher_type
        self.story_builder = StoryBuilder(host)
        self.markdown_file = ""


# 注册插件
@register(name="GalgameMaker", description="Easily create your own Galgame in QQ!", version="0.1", author="ElvisChenML")
class GalgameMaker(BasePlugin):

    # 插件加载时触发
    def __init__(self, host: APIHost):
        self.host = host
        self.ap = host.ap
        self.configs: typing.Dict[str, Config] = {}

        self._ensure_required_files_exist()
        self._set_permissions_recursively("data/plugins/GalgameMaker/", 0o777)

    # 异步初始化
    async def initialize(self):
        pass

    async def _load_config(self, launcher_id: str, launcher_type: str):
        self.configs[launcher_id] = Config(self.host, launcher_id, launcher_type)
        config = self.configs[launcher_id]

        config_mgr = ConfigManager(f"data/plugins/GalgameMaker/config/config", "plugins/GalgameMaker/templates/config", launcher_id)
        await config_mgr.load_config(completion=True)

        config.markdown_file = config_mgr.data.get("markdown_file", "Story Example")
        markdown_file_path = f"data/plugins/GalgameMaker/story/{config.markdown_file}.md"

        if not os.path.exists(markdown_file_path):
            if config.markdown_file == "Story Example":
                # 如果Story Example.md不存在，则复制模板文件和文件夹
                shutil.copyfile("plugins/GalgameMaker/templates/Story Example.md", markdown_file_path)
                shutil.copytree("plugins/GalgameMaker/templates/Story Example.assets", "data/plugins/GalgameMaker/story/Story Example.assets")
            else:
                raise FileNotFoundError(f"The markdown file {markdown_file_path} does not exist.")

        config.story_builder.set_markdown_file(markdown_file_path)

        self._set_permissions_recursively("data/plugins/GalgameMaker/", 0o777)

    # 当收到个人消息时触发
    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        launcher_id = ctx.event.launcher_id
        if launcher_id not in self.configs:
            await self._load_config(launcher_id, ctx.event.launcher_type)
        config = self.configs[launcher_id]

        msg = ctx.event.text_message
        if msg == "开始游戏":
            first_node_id = config.story_builder.get_first_node_id()
            if first_node_id:
                message_chain = config.story_builder.get_message_chain(first_node_id)
                await self.send_message(ctx, message_chain)
            else:
                await self.send_message(ctx, MessageChain([Plain("未找到初始节点。")]))
        else:
            user_input = msg.strip().upper()
            option_mapping = config.story_builder.get_option_mapping()
            print(f"{user_input} {option_mapping}")
            if user_input in option_mapping:
                next_node_id = option_mapping[user_input]
                next_message_chain = config.story_builder.get_message_chain(next_node_id)
                await self.send_message(ctx, next_message_chain)
            else:
                await self.send_message(ctx, MessageChain([Plain("无效的选项，请重新选择。")]))

        ctx.prevent_default()

    async def send_message(self, ctx: EventContext, messages: MessageChain):
        await ctx.event.query.adapter.send_message(ctx.event.launcher_type, ctx.event.launcher_id, messages)

    def _ensure_required_files_exist(self):
        directories = ["data/plugins/GalgameMaker/story", "data/plugins/GalgameMaker/config", "data/plugins/GalgameMaker/data"]

        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                self.ap.logger.info(f"Directory created: {directory}")

    def _set_permissions_recursively(self, path, mode):
        for root, dirs, files in os.walk(path):
            for dirname in dirs:
                os.chmod(os.path.join(root, dirname), mode)
            for filename in files:
                os.chmod(os.path.join(root, filename), mode)

    # 插件卸载时触发
    def __del__(self):
        pass
