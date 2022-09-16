class XellGridRenderData:
    """
    This class defines an interface for render dataset
    """
    def __init__(self, input_dataset):
        self._render_dataset = None
        self._input_dataset = input_dataset
        self._transform(input_dataset)

    def _transform(self):
        """
        Adaptor to transform input data into core data structure
        :return:
        """
        ...

    def _calculation(self):
        """
        operation interface, it will take a predefined map to look up operations from
        :return: instructions to interface
        """
        ...

    def _update(self):
        pass


