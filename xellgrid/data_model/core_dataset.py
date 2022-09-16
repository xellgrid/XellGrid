import pandas as pd


class XellGridCoreData:
    """
    This class defines an interface for core dataset
    """
    def __init__(self, input_dataset):
        self._core_dataset = None
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


class CoreDataPandas(XellGridCoreData):
    """
    A Pandas based extension of the XellGridCoreData abstract class
    the required input
    """

    def __init_(self):
        super().__init__()

    @classmethod
    def init_from_file(cls, file_path):
        ...

    @classmethod
    def init_from_db(cls, db_config):
        ...

    def _save_input_data(self):
        working_tmp_space = './input_data.parquet'
        self._input_data.to_parquet(path=working_tmp_space)

    def transform(self):
        """
        core dataset and input dataset share the same reference;
        input dataset are saved and can be read from disc if needed
        :return:
        """
        if isinstance(self._input_dataset, pd.DataFrame):
            self._core_dataset = self._input_dataset
            self._save_input_data()
