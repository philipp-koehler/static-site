import unittest
from htmlnode import LeafNode
import main
from textnode import TextNode, TextType

class TestMain(unittest.TestCase):
    def test_text_node_to_html_node(self):
        leaf_node = main.text_node_to_html_node(TextNode("test", TextType.BOLD))
        expected = LeafNode("test", "b")
        self.assertEqual(leaf_node, expected)

    def test_url(self):
        leaf_node = main.text_node_to_html_node(TextNode("test", TextType.LINKS, "www.boot.dev"))
        expected = LeafNode("test", "a", None, {"href": "www.boot.dev"})
        self.assertEqual(leaf_node, expected)
        
    def test_image(self):
        leaf_node = main.text_node_to_html_node(TextNode("test", TextType.IMAGES, "www.boot.dev"))
        expected = LeafNode("test", "img", None, {"href": "www.boot.dev"})
        
    def test_split_nodes(self):
        node = TextNode("This is text with a `code block` word", TextType.NORMAL)
        new_nodes = main.split_nodes_delimiter([node], "`", TextType.CODE)
        expected_nodes = [
            TextNode("This is text with a ", TextType.NORMAL),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.NORMAL)
            ]
        self.assertEqual(new_nodes, expected_nodes)
        
    def test_split_nodes_2(self):
        node = TextNode("This is text with a **bold choice of** words", TextType.NORMAL)
        new_nodes = main.split_nodes_delimiter([node], "**", TextType.BOLD)
        expected_nodes = [
            TextNode("This is text with a ", TextType.NORMAL),
            TextNode("bold choice of", TextType.BOLD),
            TextNode(" words", TextType.NORMAL)
            ]
        self.assertEqual(new_nodes, expected_nodes)

    def test_split_nodes_3(self):
        node = TextNode("This is text with a **bold choice of** words and **more**!", TextType.NORMAL)
        new_nodes = main.split_nodes_delimiter([node], "**", TextType.BOLD)
        expected_nodes = [
            TextNode("This is text with a ", TextType.NORMAL),
            TextNode("bold choice of", TextType.BOLD),
            TextNode(" words and ", TextType.NORMAL),
            TextNode("more", TextType.BOLD),
            TextNode("!", TextType.NORMAL),
            ]
        self.assertEqual(new_nodes, expected_nodes)

    def test_find_images(self):
        text = "This text has an ![image](www.google.com/image.jpg) and another ![image](www.boot.dev/weird.gif)"
        tuples = main.extract_markdown_images(text)
        expected = [("image", "www.google.com/image.jpg"), ("image", "www.boot.dev/weird.gif")]
        self.assertEqual(tuples, expected)

    def test_find_links(self):
        text = "This text has a [link](www.google.com) and another [cool link](www.boot.dev)"
        tuples = main.extract_markdown_links(text)
        expected = [("link", "www.google.com"), ("cool link", "www.boot.dev")]
        self.assertEqual(tuples, expected)

    def test_split_images(self):
        text = "This text has an ![image](www.google.com/image.jpg) and another ![image](www.boot.dev/weird.gif)"
        node = TextNode(text, TextType.NORMAL)
        output = main.split_nodes_image([node])
        print(output)
        expected = [
            TextNode("This text has an ", TextType.NORMAL),
            TextNode("image", TextType.IMAGES, "www.google.com/image.jpg"),
            TextNode(" and another ", TextType.NORMAL),
            TextNode("image", TextType.IMAGES, "www.boot.dev/weird.gif")
        ]
        self.assertEqual(output, expected)

    def test_split_images_empty_start(self):
        text = "![image](www.google.com/image.jpg) and another ![image](www.boot.dev/weird.gif)"
        node = TextNode(text, TextType.NORMAL)
        output = main.split_nodes_image([node])
        print(output)
        expected = [
            TextNode("image", TextType.IMAGES, "www.google.com/image.jpg"),
            TextNode(" and another ", TextType.NORMAL),
            TextNode("image", TextType.IMAGES, "www.boot.dev/weird.gif")
        ]
        self.assertEqual(output, expected)
        
    def test_split_images_empty_middle(self):
        text = "![image](www.google.com/image.jpg)![image](www.boot.dev/weird.gif)"
        node = TextNode(text, TextType.NORMAL)
        output = main.split_nodes_image([node])
        print(output)
        expected = [
            TextNode("image", TextType.IMAGES, "www.google.com/image.jpg"),
            TextNode("image", TextType.IMAGES, "www.boot.dev/weird.gif")
        ]
        self.assertEqual(output, expected)

        
    def test_split_links(self):
        text = "This text has an [image](www.google.com/image.jpg) and another [image](www.boot.dev/weird.gif)"
        node = TextNode(text, TextType.NORMAL)
        output = main.split_nodes_link([node])
        expected = [
            TextNode("This text has an ", TextType.NORMAL),
            TextNode("image", TextType.LINKS, "www.google.com/image.jpg"),
            TextNode(" and another ", TextType.NORMAL),
            TextNode("image", TextType.LINKS, "www.boot.dev/weird.gif")
            ]
        self.assertEqual(output, expected)

    def test_split_links_empty_start(self):
        text = "[image](www.google.com/image.jpg) and another [image](www.boot.dev/weird.gif)"
        node = TextNode(text, TextType.NORMAL)
        output = main.split_nodes_link([node])    
        expected  = [
            TextNode("image", TextType.LINKS, "www.google.com/image.jpg"),
            TextNode(" and another ", TextType.NORMAL),
            TextNode("image", TextType.LINKS, "www.boot.dev/weird.gif")
        ]
        self.assertEqual(output, expected)
        
    def test_split_links_empty_middle(self):
        text = "[image](www.google.com/image.jpg)[image](www.boot.dev/weird.gif)"
        node = TextNode(text, TextType.NORMAL)
        output = main.split_nodes_link([node])
        expected = [
            TextNode("image", TextType.LINKS, "www.google.com/image.jpg"),
            TextNode("image", TextType.LINKS, "www.boot.dev/weird.gif")
        ]
        self.assertEqual(output, expected)

    def test_text_to_texnodes(self):
        input = "This is **text** with an *italic* word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        node = main.text_to_textnodes(input)
        expected = [
            TextNode("This is ", TextType.NORMAL),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.NORMAL),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.NORMAL),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.NORMAL),
            TextNode("obi wan image", TextType.IMAGES, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.NORMAL),
            TextNode("link", TextType.LINKS, "https://boot.dev")
        ]
        self.assertEqual(node, expected)

    def test_markdown_to_block(self):
        input = """# This is a heading

This is a paragraph of text. It has some **bold** and *italic* words inside of it.

* This is the first list item in a list block
* This is a list item
* This is another list item"""
        block_list = main.markdown_to_block(input)
        expected = [
            "# This is a heading",
            "\nThis is a paragraph of text. It has some **bold** and *italic* words inside of it.\n",
            "* This is the first list item in a list block\n* This is a list item\n* This is another list item"             
        ]
        print("function: " + str(block_list))
        print("expected: " + str(expected))
        self.assertEqual(block_list, expected)

    def test_block_to_block_type(self):
        input = "``` test\n bla```"
        output = main.block_to_block_type(input)
        expected = "CODEBLOCK"
        self.assertEqual(output, expected)
