#!/usr/bin/env python3

from collections.abc import Container
from os.path import isdir
from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode
import re
import os
import shutil
import pathlib

block_type_paragraph = "paragraph"
block_type_heading = "heading"
block_type_code = "code"
block_type_quote = "quote"
block_type_olist = "ordered_list"
block_type_ulist = "unordered_list"


def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.NORMAL:
            return LeafNode(text_node.text)
        case TextType.BOLD:
            return LeafNode(text_node.text, "b")
        case TextType.ITALIC:
            return LeafNode(text_node.text, "i")
        case TextType.CODE:
            return LeafNode(text_node.text, "code")
        case TextType.IMAGES:
            return LeafNode(text_node.text, "img", {"href": text_node.url})
        case TextType.LINKS:
            return LeafNode(text_node.text, "a", {"href": text_node.url})
        case _:
            raise Exception("Unknown TextType")


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    return_node = []
    for old_node in old_nodes:
        if old_node.text_type == TextType.NORMAL:
            node_split = old_node.text.split(delimiter)
            for i in range(0, len(node_split)):
                if (i + 1) % 2 == 1:
                    return_node.append(
                        TextNode(node_split[i], TextType.NORMAL)
                    )
                else:
                    return_node.append(TextNode(node_split[i], text_type))
        else:
            return_node.append(old_node)
    return return_node


def extract_markdown_images(text):
    regex = r"!\[(.*?)\]\((.*?)\)"
    return re.findall(regex, text)


def extract_markdown_links(text):
    regex = r"(?<!!)\[(.*?)\]\((.*?)\)"
    return re.findall(regex, text)


def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        contained_images = extract_markdown_images(node.text)
        if contained_images != []:
            split_node = node.text.split(
                f"![{contained_images[0][0]}]({contained_images[0][1]})", 1
            )
            if split_node[0] != "":
                new_nodes.append(TextNode(split_node[0], TextType.NORMAL))
            new_nodes.append(
                TextNode(
                    contained_images[0][0],
                    TextType.IMAGES,
                    contained_images[0][1],
                )
            )
            if split_node[1] == "":
                continue
            additional_nodes = split_nodes_image(
                [TextNode(split_node[1], TextType.NORMAL)]
            )
            for add_node in additional_nodes:
                new_nodes.append(add_node)
        else:
            new_nodes.append(node)
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        contained_links = extract_markdown_links(node.text)
        if contained_links != []:
            split_node = node.text.split(
                f"[{contained_links[0][0]}]({contained_links[0][1]})", 1
            )
            if split_node[0] != "":
                new_nodes.append(TextNode(split_node[0], TextType.NORMAL))
            new_nodes.append(
                TextNode(
                    contained_links[0][0],
                    TextType.LINKS,
                    contained_links[0][1],
                )
            )
            if split_node[1] == "":
                continue
            additional_nodes = split_nodes_link(
                [TextNode(split_node[1], TextType.NORMAL)]
            )
            for add_node in additional_nodes:
                new_nodes.append(add_node)
        else:
            new_nodes.append(node)
    return new_nodes


def text_to_textnodes(text):
    node = TextNode(text, TextType.NORMAL)
    nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_image(nodes)
    return nodes

def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    filtered_blocks = []
    for block in blocks:
        if block == "":
            continue
        block = block.strip()
        filtered_blocks.append(block)
    return filtered_blocks


def block_to_block_type(block):
    lines = block.split("\n")

    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return block_type_heading
    if (
        len(lines) > 1
        and lines[0].startswith("```")
        and lines[-1].startswith("```")
    ):
        return block_type_code
    if block.startswith(">"):
        for line in lines:
            if not line.startswith(">"):
                return block_type_paragraph
        return block_type_quote
    if block.startswith("* "):
        for line in lines:
            if not line.startswith("* "):
                return block_type_paragraph
        return block_type_ulist
    if block.startswith("- "):
        for line in lines:
            if not line.startswith("- "):
                return block_type_paragraph
        return block_type_ulist
    if block.startswith("1. "):
        i = 1
        for line in lines:
            if not line.startswith(f"{i}. "):
                return block_type_paragraph
            i += 1
        return block_type_olist
    return block_type_paragraph

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        html_node = block_to_html_node(block)
        children.append(html_node)
    return ParentNode("div", children, None)

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
    text = block[level + 1 :]
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


def block_to_html_node(block):
    block_type = block_to_block_type(block)
    if block_type == block_type_paragraph:
        return paragraph_to_html_node(block)
    if block_type == block_type_heading:
        return heading_to_html_node(block)
    if block_type == block_type_code:
        return code_to_html_node(block)
    if block_type == block_type_olist:
        return olist_to_html_node(block)
    if block_type == block_type_ulist:
        return ulist_to_html_node(block)
    if block_type == block_type_quote:
        return quote_to_html_node(block)
    raise ValueError("invalid block type")


def copy_all(source, dest):
    shutil.rmtree(dest)
    os.mkdir(dest)
    if not (os.path.isdir(source)):
        raise Exception("Source not a directory")
    for obj in os.listdir(source):
        source_object = os.path.join(source, obj)
        dest_object = os.path.join(dest, obj)
        if os.path.isfile(source_object):
            shutil.copy(source_object, dest)
        elif os.path.isdir(source_object):
            os.mkdir(dest_object)
            copy_all(source_object, dest_object)


def extract_markdown_title(title):
    if re.match(r"# ", title):
        return title.strip("# ")
    else:
        raise Exception("No header found")


def generate_page(from_path, template_path, dest_path):
    print(
        f"Generating page from {from_path} to {dest_path} using {template_path}"
    )
    with open(from_path, "r") as f, open(template_path, "r") as t:
        title = extract_markdown_title(f.readline())
        f.seek(0)
        content = f.read()
        template = t.read()
    html_nodes = markdown_to_html_node(content)
    html_string = html_nodes.to_html()
    filled_template = template.replace("{{ Title }}", title).replace(
        "{{ Content }}", html_string
    )
    with open(os.path.join(dest_path, "index.html"), "w") as w:
        w.write(filled_template)

def generate_page_recursive(dir_path_content, template_path, dest_dir_path):
    obj_list = os.listdir(dir_path_content)
    print(obj_list)
    print(os.path.isfile(obj_list[0]))
    for obj in obj_list:
        if os.path.isfile(os.path.join(dir_path_content, obj)) and obj.endswith(".md"):
            print(f"file {obj}")
            generate_page(os.path.join(dir_path_content, obj), template_path, dest_dir_path)
        elif os.path.isdir(os.path.join(dir_path_content, obj)):
            print(f"folder {obj}")
            os.mkdir(os.path.join(dest_dir_path, obj))
            generate_page_recursive(os.path.join(dir_path_content, obj), template_path, os.path.join(dest_dir_path, obj))

def main():
    print("Welcome to the Nodesifyer!")
    copy_all("static", "public")
    generate_page_recursive("content", "template.html", "public")


if __name__ == "__main__":
    main()
