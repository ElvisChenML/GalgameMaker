# GalgameMaker

[![Github stars](https://img.shields.io/github/stars/ElvisChenML/GalgameMaker?color=cd7373&logo=github&style=flat-square)](https://github.com/ElvisChenML/GalgameMaker/stargazers) ![github top language](https://img.shields.io/github/languages/top/ElvisChenML/GalgameMaker?logo=github) [![License](https://img.shields.io/github/license/ElvisChenML/GalgameMaker?&color=cd7373&style=flat-square)](./LICENSE) [![Static Badge](https://img.shields.io/badge/%E7%A4%BE%E5%8C%BA%E7%BE%A4-619154800-purple)](https://qm.qq.com/q/PClALFK242)

* 社区群为QChatGPT社区群，有项目主程序或插件相关问题可至群内询问。
* 提问前请先查看文档及Issue。

## 安装

配置完成 [QChatGPT](https://github.com/RockChinQ/QChatGPT) 主程序后使用管理员账号向机器人发送命令即可安装：

```
!plugin get https://github.com/ElvisChenML/GalgameMaker
```
或查看详细的[插件安装说明](https://github.com/RockChinQ/QChatGPT/wiki/5-%E6%8F%92%E4%BB%B6%E4%BD%BF%E7%94%A8)

## 介绍

将规定格式的Markdown剧情设计脚本转为QQ选项游戏。
Easily create your own Galgame in QQ!

* 初衷是搭配照片快速实现作为给朋友惊喜的礼物游戏。

## 版本记录

### GalgameMaker 预告

* 存档功能：包含存档、读档、存档次数限制、读档冷却时间。

### GalgameMaker 0.1

* 新增 基础功能模块：包含配置、转换、发送、选择。

## 使用

### 开始

* 请先完成内建示例剧情。
* 查看并理解内建剧情设计文件（Story Example.md）。
* 创作自己的设计文件。

### 参数配置

* QChatGPT\data\plugins\GalgameMaker\config\config.yaml

  * 配置将分为 通用配置 “config.yaml”，以及会话配置 “config_&#91;会话&#93;.yaml”
  * 会话配置 优先级高于 通用配置
  * config_&#91;会话&#93;.yaml 中默认所有选项都是注释状态，需要激活请取消行开头的 “# ”

  ``` yaml
  # 通用配置
  markdown_file: "Story Example" # 加载的Markdown路线设计文件
  ```

* QChatGPT\data\plugins\GalgameMaker\story\

  * 剧情设计文件存放资料夹
  * 请参考内建剧情设计文件进行修改：Story Example.md
  * 图片：支援基于设计文件的相对路径、markdown base64、URL
    * 基于设计文件的相对路径，参考：节点 1
    * markdown base64，参考：节点 2
    * URL，参考：节点 3

  ``` markdown
  # Story Example【设计文件标题（非必填项）】
  
  ## 节点 1: 初遇【节点名称（必填项）】
  
  ### 描述【节点文字（非必填项）】
  你在公园遇到了一位神秘的女孩。【文字】
  
  ### 图片【节点图片（非必填项）】
  ![](Story Example.assets/images.jpeg)【图片】
  
  ### 选项【节点选项（非必填项）】
  #### 打招呼【选项文字，无个数限制】
  节点 2: 问好【跳转的节点，需与“节点名称”完全相同】
  #### 继续走路
  节点 3: 离开
  ```

  ## 鸣谢🎉

  感谢 [QChatGPT](https://github.com/RockChinQ/QChatGPT) 提供Bot功能及其他基础方法

