class HTMLNode:

    def __init__(self, tag=None, value=None, children=None, props=None) -> None:
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props_to_html()})"

    def __eq__(self, other) -> bool:
        if isinstance(other, HTMLNode):
            return self.tag == other.tag and self.value == other.value and self.children == other.children and self.props == other.props
        return False 
        
    def to_html(self):
        raise NotImplementedError()

    def props_to_html(self):
        retstring = ""
        if self.props is not None:
            for key in self.props:
                retstring += f" {key}=\"{self.props[key]}\""
        return retstring


class LeafNode(HTMLNode):

    def __init__(self, value, tag=None, children=None, props=None) -> None:
        super().__init__(tag, value, children, props)

    def __eq__(self, other) -> bool:
        if isinstance(other, LeafNode):
            return self.tag == other.tag and \
            self.value == other.value and \
            self.children == other.children and \
            self.props == other.props and \
            self.children is None
        return False 
     
    def to_html(self):
        if self.value is None:
            raise ValueError("A value is required for a Leaf Node")
        if self.tag is None:
            return self.value
        if self.children is not None:
            raise ValueError("A Leaf Node does not have Child Nodes")
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

class ParentNode(HTMLNode):

    def __init__(self, tag, children, value=None, props=None) -> None:
        super().__init__(tag, value, children, props)

    def __eq__(self, other) -> bool:
        if isinstance(other, LeafNode):
            return self.tag == other.tag and \
            self.value == other.value and \
            self.children == other.children and \
            self.props == other.props and \
            self.children is not None and \
            self.tag is not None
        return False
        
    def to_html(self):
        if self.tag is None:
            raise ValueError("Parent Node needs a tag")
        if self.children is None:
            raise ValueError("Parent Node needs children")
        string_output = f"<{self.tag}>"
        for child in self.children:
            string_output += child.to_html()
        string_output += f"</{self.tag}>"
        return string_output
