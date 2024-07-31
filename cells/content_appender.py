import requests
import base64
import typing
from mirai import MessageChain, Image, Plain, Voice
from requests.exceptions import RequestException


class ContentAppender:

    def _append_plain(self, mc: MessageChain, content: dict):
        try:
            if "content" in content:
                mc.append(Plain(content["content"]))
            else:
                raise ValueError(f"Unsupported plain content type. Must provide 'content'.\ncontent: {content}")
        except ValueError as e:
            print(f"Error appending plain: {e}")

    def _append_image(self, mc: MessageChain, content: dict):
        try:
            if "url" in content:
                base64_content = self._url_to_base64(content["url"])
                mc.append(Image(base64=base64_content))
            elif "path" in content:
                base64_content = self._path_to_base64(content["path"])
                mc.append(Image(base64=base64_content))
            elif "base64" in content:
                mc.append(Image(base64=content["base64"]))
            else:
                raise ValueError(f"Unsupported image content type. Must provide 'url', 'path', or 'base64'.\ncontent: {content}")
        except ValueError as e:
            print(f"Error appending image: {e}")

    def _append_voice(self, mc: MessageChain, content: dict):
        try:
            if "url" in content:
                base64_content = self._url_to_base64(content["url"])
                mc.append(Voice(base64=base64_content))
            elif "path" in content:
                base64_content = self._path_to_base64(content["path"])
                mc.append(Voice(base64=base64_content))
            elif "base64" in content:
                mc.append(Voice(base64=content["base64"]))
            else:
                raise ValueError(f"Unsupported voice content type. Must provide 'url', 'path', or 'base64'.\ncontent: {content}")
        except ValueError as e:
            print(f"Error appending voice: {e}")


    def _append_option(self, mc: MessageChain, content: dict):
        try:
            if "content" in content:
                options_text = "\n".join(f"{key} -> {value}" for key, value in content["content"].items())
                mc.append(Plain(options_text))
            else:
                raise ValueError(f"Unsupported option content type. Must provide 'content'.\ncontent: {content}")
        except ValueError as e:
            print(f"Error appending option: {e}")

    def _url_to_base64(self, url: str) -> str:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return base64.b64encode(response.content).decode("utf-8")
        except RequestException as e:
            raise ValueError(f"Failed to retrieve content from URL: {e}")

    def _path_to_base64(self, path: str) -> str:
        try:
            with open(path, "rb") as file:
                return base64.b64encode(file.read()).decode("utf-8")
        except (FileNotFoundError, IOError) as e:
            raise ValueError(f"Failed to read content from path: {e}")

    def append_content(self, mc: MessageChain, content: dict | typing.Any):
        if isinstance(content, dict):
            if "type" in content and content["type"] == "voice":
                self._append_voice(mc, content)
            elif "type" in content and content["type"] == "image":
                self._append_image(mc, content)
            elif "type" in content and content["type"] == "description":
                self._append_plain(mc, content)
            elif "type" in content and content["type"] == "option":
                self._append_option(mc, content)
        else:
            raise ValueError(f"Unsupported content type. Must be a dictionary with plain, image or voice data.\ncontent: {content}")
