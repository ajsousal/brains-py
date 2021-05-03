"""
Module for testing 'processor.py'.
"""

import unittest
import warnings

import torch
import numpy as np

from brainspy.utils.pytorch import TorchUtils
from brainspy.processors.simulation.processor import SurrogateModel
from brainspy.processors.simulation.noise.noise import GaussianNoise


class ModelTest(unittest.TestCase):
    """
    Class for testing 'processor.py'.
    """
    def setUp(self):
        """
        Make a SurrogateModel and info dictionary to work with.
        """
        model_structure = {
            "D_in": 7,
            "D_out": 1,
            "activation": "relu",
            "hidden_sizes": [20, 20, 20]
        }
        self.sm = SurrogateModel(model_structure)
        self.info_dict = {
            "electrode_no": 8,
            "activation_electrodes": {
                "electrode_no": 7,
                "voltage_ranges": np.array([1, 2])
            },
            "output_electrodes": {
                "electrode_no": 1,
                "amplification": 2,
                "output_clipping": np.array([1, 2])
            }
        }
        self.sm.set_effects_from_dict(self.info_dict, dict())

    def test_get_voltage_ranges(self):
        """
        Test if setting the voltage ranges works, both for default setting and
        with a value.
        """
        # should set to configs
        configs = {"voltage_ranges": np.array([3, 4])}
        self.sm.set_effects_from_dict(self.info_dict, configs)
        self.assertTrue(
            torch.equal(
                self.sm.get_voltage_ranges(),
                torch.tensor([3, 4],
                             device=TorchUtils.get_device(),
                             dtype=torch.get_default_dtype())))

        # should set to default from info dict
        self.sm.set_effects_from_dict(self.info_dict, {})
        self.assertTrue(
            torch.equal(
                self.sm.get_voltage_ranges(),
                torch.tensor([1, 2],
                             device=TorchUtils.get_device(),
                             dtype=torch.get_default_dtype())))

    def test_forward(self):
        """
        Test if a forward pass through the processor returns a tensor of the
        right shape.
        """
        x = torch.tensor([1, 2, 3, 4, 5, 6, 7],
                         device=TorchUtils.get_device(),
                         dtype=torch.get_default_dtype())
        x = self.sm.forward(x)
        self.assertEqual(list(x.shape), [1])

    def test_forward_numpy(self):
        """
        Test if a forward pass through the processor returns a tensor of the
        right shape (the numpy version).
        """
        x = np.array([1, 2, 3, 4, 5, 6, 7])
        x = self.sm.forward_numpy(x)
        self.assertEqual(list(x.shape), [1])

    def test_reset(self):
        """
        Test if resetting the processor raises a warning.
        """
        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            self.sm.reset()
            self.assertEqual(len(caught_warnings), 1)

    def test_close(self):
        """
        Test if closing the processor raises a warning.
        """
        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            self.sm.close()
            self.assertEqual(len(caught_warnings), 1)

    def test_is_hardware(self):
        """
        Test if processor knows it is not hardware.
        """
        self.assertFalse(self.sm.is_hardware())

    def test_set_effects_from_dict(self):
        """
        Test setting effects from a dictionary.
        """
        configs = {
            "amplification": 2,
            "output_clipping": np.array([3, 4]),
            "voltage_ranges": "default",
            "noise": None,
            "test": 0
        }
        self.sm.set_effects_from_dict(self.info_dict, configs)
        self.assertEquals(self.sm.amplification, 2)
        self.assertTrue(
            torch.equal(self.sm.output_clipping,
                        TorchUtils.format(np.array([3, 4]))))
        self.assertTrue(
            torch.equal(
                self.sm.get_voltage_ranges(),
                TorchUtils.format(self.info_dict["activation_electrodes"]
                                  ["voltage_ranges"])))

    def test_get_key(self):
        """
        Test if get key method returns the key if it exists, and "default" or
        None if it does not exist.
        """
        key1 = "key1"
        key2 = "key2"
        key_noise = "noise"
        d = {"key1": 1}
        self.assertEquals(self.sm.get_key(d, key1), 1)
        self.assertEquals(self.sm.get_key(d, key2), "default")
        self.assertIsNone(self.sm.get_key(d, key_noise))

    def test_set_effects(self):
        """
        Test setting effects.
        """
        self.sm.set_effects(self.info_dict,
                            amplification=2,
                            voltage_ranges="default",
                            output_clipping=np.array([3, 4]))
        self.assertEquals(self.sm.amplification, 2)
        self.assertTrue(
            torch.equal(self.sm.output_clipping,
                        TorchUtils.format(np.array([3, 4]))))
        self.assertTrue(
            torch.equal(
                self.sm.get_voltage_ranges(),
                TorchUtils.format(self.info_dict["activation_electrodes"]
                                  ["voltage_ranges"])))

    def test_set_voltage_ranges(self):
        """
        Test setting voltage ranges to default and new value.
        """
        # set to value
        value = np.array([10, 20])
        self.sm.set_voltage_ranges(self.info_dict, value)
        self.assertTrue(
            torch.equal(self.sm.get_voltage_ranges(),
                        TorchUtils.format(value)))

        # set to default
        self.sm.set_voltage_ranges(self.info_dict, "default")
        self.assertTrue(
            torch.equal(
                self.sm.get_voltage_ranges(),
                TorchUtils.format(self.info_dict["activation_electrodes"]
                                  ["voltage_ranges"])))

    def test_set_amplification(self):
        """
        Test setting amplification to default and new value.
        """
        # set to value
        value = 4
        self.sm.set_amplification(self.info_dict, value)
        self.assertTrue(
            torch.equal(self.sm.amplification, TorchUtils.format([value])))

        # set to default
        self.sm.set_amplification(self.info_dict, "default")
        self.assertTrue(
            torch.equal(
                self.sm.amplification,
                TorchUtils.format(
                    [self.info_dict["output_electrodes"]["amplification"]])))

    def test_set_output_clipping(self):
        """
        Test setting output clipping to default and new value.
        """
        # set to value
        value = np.array([10, 20])
        self.sm.set_output_clipping(self.info_dict, value)
        self.assertTrue(
            torch.equal(self.sm.output_clipping, TorchUtils.format(value)))

        # set to default
        self.sm.set_output_clipping(self.info_dict, "default")
        self.assertTrue(
            torch.equal(
                self.sm.get_voltage_ranges(),
                TorchUtils.format(
                    self.info_dict["output_electrodes"]["output_clipping"])))

    def test_set_noise(self):
        """
        Test setting the noise to gaussian or None.
        """
        # set to none
        self.sm.set_effects(self.info_dict)
        self.assertIsNone(self.sm.noise)

        # set to Gaussian
        noise_dict = {"noise_type": "gaussian", "variance": 1}
        self.sm.set_effects(self.info_dict, noise_configs=noise_dict)
        self.assertIsInstance(self.sm.noise, GaussianNoise)


if __name__ == "__main__":
    unittest.main()
