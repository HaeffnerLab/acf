"""This class provides an interface to experiment parameters stored in artiq Datasets.

Parameters are stored in Artiq datasets, one single-valued dataset per parameter. They
are stored with a prefix _param_ to denote them as parameters and to not be confused with
datasets generated from experiments. This prefix should not be included when referring to
parameters.
"""

import numpy as np
import os
import subprocess

class ParameterManager:

    dataset_prefix = "__param__"

    def __init__(self, exp):
        """Create a ParameterManager instance.
        
        Args:
            exp (EnvExperiment): The calling experiment class.
        """
        self.exp = exp
    
    def get_param(self, name):
        """Get a parameter.
        
        This function must be called from the build method.
        
        Args:
            name (str): The name of the parameter. Do not include the __param__ prefix.
        
        Returns: The value of the parameter.
        """
        param_dataset = self.exp.get_dataset(self.dataset_prefix + name, default=None)
        if param_dataset is None:
        	raise RuntimeError(f"parameter {name} does not exist.")
        
        return param_dataset
    
    def set_param(self, name, value):
        """Set a parameter.
        
        Args:
            name (str): The name of the parameter. Do not include the _param_ prefix.
            value (?): The value to which the parameter will be set.
        """
        self.exp.set_dataset(self.dataset_prefix + name, value, persist=True)

