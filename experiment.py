from artiq.experiment import EnvExperiment, kernel
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

