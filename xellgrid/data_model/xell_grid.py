from abc import ABC, abstractmethod

"""
This class is used to define the fundamental data structure of XellGrid. This class wraps the following objects
1. A rendering dataframe used for rendering purpose
2. A core dataset to perform heavy duty calculations
3. Sync up communication between rendering data and core dataset
"""


class XellGrid(ABC):
    """
    This is an abstract class consisting the following components:
     - Core Dataset: original data with APIs for extensive computations.
                    It can be set to None for better performance if the original dataset is small
     - Rendering Dataset: a subset of core dataset with APIs for rendering
     - Core/Rendering Interfaces: interfaces for sync up between core and rendering
     - Meta data interfaces
    """
    @abstractmethod
    def __init__(self, sync_interface, rendering_data, core_data = None):
        self._core_data = core_data
        self._sync_interface = sync_interface
        self._rendering_data = rendering_data
        self._meta_data = None


    def widget_instruction_handler(self):
        """
        standard set of methods to handle and translate instructions from widget front end
        and distribute instructions to different data sets for computation
        :return:
        """
        ...

    @abstractmethod
    def _instruction_adaptor_for_rendering(self):
        """
        Adatpor to pass widget instructions to rendering data
        Should be implemented as part of rendering data
        :return:
        """
        return NotImplemented


    @abstractmethod
    def _instruction_adaptor_for_core(self):
        """
        Adatpor to pass widget instructions to core data
        Should be implemented as part of rendering data
        :return:
        """
        return NotImplemented
