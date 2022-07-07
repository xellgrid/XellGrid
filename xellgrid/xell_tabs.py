from ipywidgets import Tab, DOMWidget
class XellTabs:
    """XellTabs contain all widgets"""
    __children = {}

    def __init__(self):
        raise Exception("XellTabs is not meant to be initialized")

    @classmethod
    def add_widget(cls, title: str, widget: DOMWidget):
        cls.__children[title] = widget

    @classmethod
    def clear(cls):
        cls.__children = {}

    @classmethod
    def get_widget(cls, title):
        return cls.__children[title]
    
    @classmethod
    def get_tabs(cls) -> Tab:
        """Get all ipywidget tabs"""
        tabs = Tab()
        tabs.children = tuple(cls.__children.values())
        for idx, title in enumerate(cls.__children.keys()):
            tabs.set_title(idx, title)
        return tabs
