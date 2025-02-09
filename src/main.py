from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode

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

def main():
    textnode = TextNode("This is a text", TextType.BOLD, "https://www.boot.dev")
    print(textnode)

if __name__ == "__main__":
    main()
