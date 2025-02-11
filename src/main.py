#!/usr/bin/env python3

from collections.abc import Container
from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode
import re

def text_node_to_html_node(text_node):
    match text_node.text_type:
        case(TextType.NORMAL):
            return LeafNode(text_node.text)
        case(TextType.BOLD):
            return LeafNode(text_node.text, "b")
        case(TextType.ITALIC):
            return LeafNode(text_node.text, "i")
        case(TextType.CODE):
                    return LeafNode(text_node.text, "code")
        case(TextType.IMAGES):
                    return LeafNode(text_node.text, "img", None, {"href": text_node.url})
        case(TextType.LINKS):
                    return LeafNode(text_node.text, "a", None, {"href": text_node.url})
        case _:
            raise Exception("Unknown TextType")

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    return_node = []
    for old_node in old_nodes:
        if old_node.text_type == TextType.NORMAL:
            node_split = old_node.text.split(delimiter)
            for i in range(0,len(node_split)):
                if (i+1) % 2 == 1:
                    return_node.append(TextNode(node_split[i], TextType.NORMAL))
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
            split_node = node.text.split(f"![{contained_images[0][0]}]({contained_images[0][1]})", 1)
            if split_node[0] != "":
                new_nodes.append(TextNode(split_node[0], TextType.NORMAL))
            new_nodes.append(TextNode(contained_images[0][0], TextType.IMAGES, contained_images[0][1]))
            if split_node[1] == "":
                continue
            additional_nodes = split_nodes_image([TextNode(split_node[1], TextType.NORMAL)])
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
            split_node = node.text.split(f"[{contained_links[0][0]}]({contained_links[0][1]})", 1)
            if split_node[0] != "":
                new_nodes.append(TextNode(split_node[0], TextType.NORMAL))
            new_nodes.append(TextNode(contained_links[0][0], TextType.LINKS, contained_links[0][1]))
            if split_node[1] == "":
                continue
            additional_nodes = split_nodes_link([TextNode(split_node[1], TextType.NORMAL)])
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
    if marker is not None:
        return marker[0]
    else:
        return ""

def markdown_to_block(markdown):
    block = []
    lines = markdown.split("\n")
    for line in lines:
        marker = find_marker(line)
        block.append((marker, line))
    marker = block[0][0]
    new_lines = [""]
    i = 0
    for line in block:
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
    if marker == "" and block_lines[0].startswith("```") and block_lines[-1].endswith("```"):
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
    html_blocks = markdown_blocks.copy()
    markdown_block_type = []
    for i in range(0, len(markdown_blocks)):
        block_type = block_to_block_type(markdown_blocks[i])
        match block_type:
            case "CODEBLOCK":
                markdown_blocks[i] = "<code>" + markdown_blocks[i] + "</code>"
            case "HEADINGBLOCK1":
                markdown_blocks[i] = "<h1>" + markdown_blocks[i] + "</h1>"
            case "HEADINGBLOCK2":
                markdown_blocks[i] = "<h2>" + markdown_blocks[i] + "</h2>"
            case "HEADINGBLOCK3":
                markdown_blocks[i] = "<h3>" + markdown_blocks[i] + "</h3>"
            case "UNORDEREDLISTBLOCK":
                markdown_blocks[i] = "<ul>" + markdown_blocks[i] + "</ul>"
            case "ORDEREDLISTBLOCK":
                markdown_blocks[i] = "<ol>" + markdown_blocks[i] + "</ol>"
            case "COMMENTBLOCK":
                markdown_blocks[i] = "<blockquote>" + markdown_blocks[i] + "</blockquote>"             
            case _:
                break
        
        
                
    
def main():
    print("Welcome to the Nodesifyer!")
    
if __name__ == "__main__":
    main()
