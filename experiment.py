from artiq.experiment import EnvExperiment, kernel, NumberValue
from acf.hardware_setup import HardwareSetup
from acf.experiment_data import ExperimentData
from acf.parameter_manager import ParameterManager

class ACFExperiment(EnvExperiment):

    def setup(self, sequences):
        """Setup the experiment class.

        Args:
            seq (SequencesContainer): Container for all sequences.
        """
        self.hardware = HardwareSetup()
        self.hardware.initialize(self)

        self.experiment_data = ExperimentData(self)
        self.parameter_manager = ParameterManager(self)

        self.init_sequences(sequences)

    @kernel
    def setup_run(self):
        """Setup to run at the beginning of the run method."""
        self.core.reset()

        # Init all DDSs
        for dds in self.hardware.get_all_dds():
            dds.init()

    def init_sequences(self, sequences):
        """Set up the sequences.

        Args:
            sequences (SequencesContainer): The sequences container.
        """
        self.seq = sequences
        for sequence in self.seq.all_sequences:
            sequence.initialize(self, self.seq, self.hardware)

    def add_arg_from_param(self, param, min_value=None, max_value=None):
        """Add an argument who's default value comes from a stored parameter.

        Args:
            param (str): The name of the parameter.
            min_value (float): Minimum value of the parameter.
            max_value (float): Maximum value of the parameter.
        """
        self.setattr_argument(
            param,
            NumberValue(
                default=self.parameter_manager.get_param(param),
                unit=self.parameter_manager.get_param_units(param),
                precision=5,
                min=min_value,
                max=max_value
            ),
            group="System Parameters",
        )

        # Set attribute manually because of forward slashes in parameter names
        setattr(self, param.replace("/", "_"), getattr(self, param))


