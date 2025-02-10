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
