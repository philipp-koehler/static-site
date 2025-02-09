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
        
