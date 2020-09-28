import unittest
import logging

from darts.preprocessing import transformer_from_ts_functions, transformer_from_values_functions
from darts.utils.timeseries_generation import constant_timeseries


class UtilsTestCase(unittest.TestCase):
    __test__ = True

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

    class FitCalled:
        def __init__(self):
            self._fit_called = False

        def __call__(self, *args, **kwargs):
            self._fit_called = True

    def test_inverse_called(self):
        # given
        ts = constant_timeseries(1, 10)
        other = constant_timeseries(2, 10)
        fit_check = self.FitCalled()
        transformer = transformer_from_ts_functions(transform=lambda x: x + other,
                                                    inverse_transform=lambda x: x + 2 * other,
                                                    fit=fit_check)

        # when
        inverse_fitted = transformer.fit(ts).inverse_transform(ts)

        # then
        self.assertSequenceEqual([[5]] * 10, inverse_fitted.values().tolist())
        self.assertTrue(fit_check._fit_called)

    def test_inverse_not_called(self):
        # given
        ts = constant_timeseries(1, 10)
        other = constant_timeseries(2, 10)
        fit_check = self.FitCalled()
        transformer = transformer_from_ts_functions(transform=lambda x: x + other,
                                                    inverse_transform=lambda x: x + 2 * other,
                                                    fit=fit_check)

        # when
        transformed = transformer.fit_transform(ts)

        # then
        self.assertSequenceEqual([[3]] * 10, transformed.values().tolist())
        self.assertTrue(fit_check._fit_called)

    def test_correct_properties_set(self):
        properties = {
            'invertible': 'inverse_transform',
            'fittable': 'fit'
        }

        def test_property(expected_false, expected_true, funcs):
            transformer = transformer_from_ts_functions(lambda x: x, **funcs)
            for name in expected_true:
                self.assertTrue(getattr(transformer, name))
            for name in expected_false:
                self.assertFalse(getattr(transformer, name))

        # when & then
        for prop, func_name in properties.items():
            funcs = {
                f_name: lambda x: x for f_name in properties.values()
            }
            funcs[func_name] = None
            expected_true = [p for p in properties.keys() if p != prop]
            expected_false = [prop]
            test_property(expected_false, expected_true, funcs)

    def test_inverse_called_values(self):
        # given
        ts = constant_timeseries(1, 10)
        other = constant_timeseries(2, 10).values()
        fit_check = self.FitCalled()
        transformer = transformer_from_values_functions(transform=lambda x: x + other,
                                                        inverse_transform=lambda x: x + 2 * other,
                                                        fit=fit_check)

        # when
        inverse_fitted = transformer.fit(ts).inverse_transform(ts)

        # then
        self.assertSequenceEqual([[5]] * 10, inverse_fitted.values().tolist())
        self.assertTrue(fit_check._fit_called)

    def test_inverse_not_called_values(self):
        # given
        ts = constant_timeseries(1, 10)
        other = constant_timeseries(2, 10).values()
        fit_check = self.FitCalled()
        transformer = transformer_from_values_functions(transform=lambda x: x + other,
                                                        inverse_transform=lambda x: x + 2 * other,
                                                        fit=fit_check)

        # when
        transformed = transformer.fit_transform(ts)

        # then
        self.assertSequenceEqual([[3]] * 10, transformed.values().tolist())
        self.assertTrue(fit_check._fit_called)

    def test_correct_properties_set_values(self):
        properties = {
            'invertible': 'inverse_transform',
            'fittable': 'fit'
        }

        def test_property(expected_false, expected_true, funcs):
            transformer = transformer_from_values_functions(lambda x: x, **funcs)
            for name in expected_true:
                self.assertTrue(getattr(transformer, name))
            for name in expected_false:
                self.assertFalse(getattr(transformer, name))

        # when & then
        for prop, func_name in properties.items():
            funcs = {
                f_name: lambda x: x for f_name in properties.values()
            }
            funcs[func_name] = None
            expected_true = [p for p in properties.keys() if p != prop]
            expected_false = [prop]
            test_property(expected_false, expected_true, funcs)
