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

def main():
    print("Welcome to the Nodesifyer!")
    
if __name__ == "__main__":
    main()
