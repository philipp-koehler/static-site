import unittest
from htmlnode import HTMLNode

class TestHTMLNode(unittest.TestCase):

    def test_eq(self):
        node = HTMLNode(tag="<h1>", value="Test", props={"href": "www.boot.dev", "target": "_blank"})
        node2 = HTMLNode(tag="<h1>", value="Test", props={"href": "www.boot.dev", "target": "_blank"})
        self.assertEqual(node, node2)

    def test_not_eq(self):
        node = HTMLNode(tag="<h1>", value="Test", props={"href": "www.google.com", "target": "_blank"})
        node2 = HTMLNode(tag="<h1>", value="Test", props={"href": "www.boot.dev", "target": "_blank"})
        self.assertNotEqual(node, node2)

    def test_props_not_eq(self):
        node = HTMLNode(tag="<h1>", value="Test", props={"href": "www.google.com", "target": "_blank"})
        node2 = HTMLNode(tag="<h1>", value="Test")
        self.assertNotEqual(node, node2)

        
        
