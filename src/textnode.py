from enum import Enum

class TextType(Enum):
    NORMAL = 1
    BOLD = 2
    ITALIC = 3
    CODE = 4
    LINKS = 5
    IMAGES = 6

class TextNode():

    def __init__(self, text, text_type, url=None) -> None:
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other) -> bool:
        if isinstance(other, TextNode):
            return self.text == other.text and self.text_type == other.text_type and self.url == other.url
        return False

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"

    
