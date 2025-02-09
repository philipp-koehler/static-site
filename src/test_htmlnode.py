import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode

class TestHTMLNode(unittest.TestCase):

    def test_eq(self):
        node = HTMLNode(tag="h1", value="Test", props={"href": "www.boot.dev", "target": "_blank"})
        node2 = HTMLNode(tag="h1", value="Test", props={"href": "www.boot.dev", "target": "_blank"})
        self.assertEqual(node, node2)

    def test_not_eq(self):
        node = HTMLNode(tag="h1", value="Test", props={"href": "www.google.com", "target": "_blank"})
        node2 = HTMLNode(tag="h1", value="Test", props={"href": "www.boot.dev", "target": "_blank"})
        self.assertNotEqual(node, node2)

    def test_props_not_eq(self):
        node = HTMLNode(tag="h1", value="Test", props={"href": "www.google.com", "target": "_blank"})
        node2 = HTMLNode(tag="h1", value="Test")
        self.assertNotEqual(node, node2)

        
class TestLeafNode(unittest.TestCase):

    def test_eq(self):
        node = LeafNode(tag="h1", value="Test", props={"href": "www.boot.dev", "target": "_blank"})
        node2 = LeafNode(tag="h1", value="Test", props={"href": "www.boot.dev", "target": "_blank"})
        self.assertEqual(node, node2)

    def test_output(self):
        node = LeafNode(tag="h1", value="Test", props={"href": "www.boot.dev", "target": "_blank"})
        expected = "<h1 href=\"www.boot.dev\" target=\"_blank\">Test</h1>"        
        self.assertEqual(node.to_html(), expected)

    def test_empty_value(self):
        with self.assertRaises(ValueError):
            node = LeafNode(tag="h1", value=None, props={"href": "www.boot.dev", "target": "_blank"})        
            node.to_html()


class TestParentNode(unittest.TestCase):

    def test_recursion(self):
        leaf = LeafNode(tag="h1", value="Test", props={"href": "www.boot.dev", "target": "_blank"})
        node = ParentNode(tag="p", children=[leaf])
        expected = "<p><h1 href=\"www.boot.dev\" target=\"_blank\">Test</h1></p>"
        self.assertEqual(node.to_html(), expected)

    def test_tag_empty(self):
        leaf = LeafNode(tag="h1", value="Test", props={"href": "www.boot.dev", "target": "_blank"})
        node = ParentNode(tag=None, children=[leaf])
        with self.assertRaises(ValueError):
            node.to_html()
        
    def test_children_empty(self):
        leaf = LeafNode(tag="h1", value="Test", props={"href": "www.boot.dev", "target": "_blank"})
        node = ParentNode(tag="p", children=None)
        with self.assertRaises(ValueError):
            node.to_html()

        
