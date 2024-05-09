# A class representing a sequence of actions to control hardware

from artiq.experiment import kernel
from artiq.language import NumberValue

class Sequence:

    # List of sequence objects that are called
    used_sequences = []

    def __init__(self):

        # Which global parameters are used by the sequence
        self.parameters = []

        # Arguments of the sequence that don't come from a parameter
        self.arguments = []

        # Group name for arguments to the GUI
        self.group_name = self.__class__.__name__

        ## Class attributes to be set in initialize
        # The running experiment
        self.exp = None

        # The sequences container object
        self.seq = None

    def add_parameter(self, parameter):
        """Add a parameter to be used by the sequence.

        Args:
            parameter (str): The parameter name.
        """
        self.parameters.append(parameter)

    def add_argument(self, name, value):
        """Add an argument to be used by the sequence that does not come from a parameter.

        Args:
            name (str): The name of the argument.
            value (?): The processor for the argument. This should be one of the
                         Artiq value types, ex. NumberValue, BooleanValue, etc.
        """
        self.arguments.append({
            "name": name,
            "value": value,
        })

    def initialize(self, exp, seq, hardware):
        """Initialize the sequence. Must be called in build().

        Args:
            exp (EnvExperiment): The calling experiment.
            seq (SequencesContainer): The sequences container object.
            hardware (HardwareSetup): The HardwareSetup instance.
        """
        self.exp = exp
        self.seq = seq
        self.set_param_and_arg_defaults()
        hardware.add_device_attributes(self)

    def set_param_and_arg_defaults(self):
        """Set parameters and arguments to their default values.

        Parameters are set to their values from storage, arguments are set to the
        default value in the NumberValue or descriptor given in the "value" attribute
        of the dict.
        """
        for param in self.parameters:
            setattr(self, param.replace("/", "_"), self.exp.parameter_manager.get_param(param))

        for arg_dict in self.arguments:
            setattr(self, arg_dict["name"], arg_dict["value"].default())

    def add_arguments_to_gui(self):
        """Add parameters and arguments from the sequence to the GUI."""

        # The displayed name is prefixed with the group name to avoid conflicting with
        # other parameters with the same name. The name set as an attribute inside the
        # sequence is not prefixed with the group name.
        for param in self.parameters:
            group_param_name = f"{self.group_name}_{param}"
            self.exp.setattr_argument(
                group_param_name,
                NumberValue(
                    default=self.exp.parameter_manager.get_param(param),
                    unit=self.exp.parameter_manager.get_param_units(param),
                    precision=5),
                group=self.group_name
            )
            setattr(self, param.replace("/", "_"), getattr(self.exp, group_param_name))

        for arg_dict in self.arguments:
            self.exp.setattr_argument(
                arg_dict["name"],
                arg_dict["value"],
                group=self.group_name
            )
            setattr(self, arg_dict["name"], getattr(self.exp, arg_dict["name"]))

    # Default methds for run and sequence??

