#!/usr/bin/env python3

from collections.abc import Container
from os.path import isdir
from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode
import re
import os
import shutil


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


def find_marker(line):
    marker = [""]
    if bool(re.search(r"^#{1,3} ", line)):
        marker = re.search(r"^#{1,3} ", line)
    elif bool(re.search(r"^(\* |- )", line)):
        marker = re.search(r"^(\* |- )", line)
    elif bool(re.search(r"^\d+\. ", line)):
        marker = re.search(r"^\d+\. ", line)
    elif bool(re.search(r"^> ", line)):
        marker = re.search(r"^> ", line)
    elif bool(re.search(r"```", line)):
        marker = re.search(r"```", line)
    if marker is not None:
        return marker[0]
    else:
        return ""


def markdown_to_block(markdown):
    block = []
    lines = markdown.split("\n")
    code = False
    for line in lines:
        marker = find_marker(line)
        if marker == "```":
            code = not code
        if code == True:
            block.append(("```", line))
        else:
            block.append((marker, line))
    marker = block[0][0]
    new_lines = [""]
    i = 0
    for line in block:
        if re.search(r"^\d+\. ", line[0]):
            line = ("1. ", re.sub(r"^\d+\. ", "1. ", line[1]))
        if marker == line[0]:
            new_lines[i] += line[1] + "\n"
        else:
            marker = line[0]
            i += 1
            new_lines.append(line[1] + "\n")
    return_lines = [re.sub(r"\n$", "", s, 1) for s in new_lines]
    return return_lines


def block_to_block_type(block):
    block_lines = block.split("\n")
    marker = find_marker(block_lines[0])
    if marker == "```":
        return "CODEBLOCK"
    elif marker == "":
        return "NORMALBLOCK"
    for line in block_lines:
        if marker != find_marker(line):
            return "NORMALBLOCK"
    if re.match(r"^[#]{1} ", block_lines[0]):
        return "HEADINGBLOCK1"
    if re.match(r"^[#]{2} ", block_lines[0]):
        return "HEADINGBLOCK2"
    if re.match(r"^[#]{3} ", block_lines[0]):
        return "HEADINGBLOCK3"
    elif re.match(r"^(\* |- )", block_lines[0]):
        return "UNORDEREDLISTBLOCK"
    elif re.match(r"^\d+\. ", block_lines[0]):
        return "ORDEREDLISTBLOCK"
    elif re.match(r"^> ", block_lines[0]):
        return "COMMENTBLOCK"


def markdown_to_html_node(markdown):
    markdown_blocks = markdown_to_block(markdown)
    html_block_nodes = []
    for i in range(0, len(markdown_blocks)):
        block_type = block_to_block_type(markdown_blocks[i])
        match block_type:
            case "CODEBLOCK":
                markdown_blocks[i] = markdown_blocks[i].replace("```", "")
            case "HEADINGBLOCK1":
                markdown_blocks[i] = markdown_blocks[i].replace("# ", "")
            case "HEADINGBLOCK2":
                markdown_blocks[i] = markdown_blocks[i].replace("## ", "")
            case "HEADINGBLOCK3":
                markdown_blocks[i] = markdown_blocks[i].replace("### ", "")
            case "UNORDEREDLISTBLOCK":
                lines = markdown_blocks[i].split("\n")
                modified_lines = [
                    line.removeprefix("* ").removeprefix("- ")
                    for line in lines
                ]
                markdown_blocks[i] = "\n".join(modified_lines)
            case "ORDEREDLISTBLOCK":
                lines = markdown_blocks[i].split("\n")
                modified_lines = [
                    re.sub(r"^\d+\. ", "", line) for line in lines
                ]
                markdown_blocks[i] = "\n".join(modified_lines)
            case "COMMENTBLOCK":
                markdown_blocks[i] = markdown_blocks[i].replace("> ", "")
            case "NORMALBLOCK":
                markdown_blocks[i] = markdown_blocks[i].strip("\n")
        text_nodes = text_to_textnodes(markdown_blocks[i])
        html_nodes = []
        for node in text_nodes:
            html_nodes.append(text_node_to_html_node(node))
        match block_type:
            case "CODEBLOCK":
                html_block_nodes.append(ParentNode("code", html_nodes))
            case "HEADINGBLOCK1":
                html_block_nodes.append(ParentNode("h1", html_nodes))
            case "HEADINGBLOCK2":
                html_block_nodes.append(ParentNode("h2", html_nodes))
            case "HEADINGBLOCK3":
                html_block_nodes.append(ParentNode("h3", html_nodes))
            case "UNORDEREDLISTBLOCK":
                lines = []
                for node in html_nodes:
                    print(node)
                    lines.append(node.value.splitlines())
                modified_lines = [LeafNode(line, "li") for line in lines]
                html_nodes = [*modified_lines]
                html_block_nodes.append(ParentNode("ul", html_nodes))

            case "ORDEREDLISTBLOCK":
                lines = html_nodes[0].value.splitlines()
                modified_lines = [LeafNode(line, "li") for line in lines]
                html_nodes = [*modified_lines]
                html_block_nodes.append(ParentNode("ol", html_nodes))
            case "COMMENTBLOCK":
                html_block_nodes.append(ParentNode("blockquote", html_nodes))
            case "NORMALBLOCK":
                html_block_nodes.append(ParentNode("p", html_nodes))
    div_block = ParentNode("div", html_block_nodes)
    return div_block


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


def main():
    print("Welcome to the Nodesifyer!")
    copy_all("static", "public")
    generate_page("content/index.md", "template.html", "public")


if __name__ == "__main__":
    main()
