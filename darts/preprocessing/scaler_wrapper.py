"""
Scaler wrapper
--------------
"""
from darts.preprocessing.base_transformer import BaseTransformer
from darts.preprocessing.validator import Validator

from ..timeseries import TimeSeries
from ..logging import get_logger, raise_log
from sklearn.preprocessing import MinMaxScaler

logger = get_logger(__name__)


class ScalerWrapper(BaseTransformer[TimeSeries]):
    def __init__(self, scaler=MinMaxScaler(feature_range=(0, 1)), name="ScalerWrapper"):
        """
        Generic wrapper class for using transformers/scalers that implement `fit()`, `transform()` and
        `inverse_transform()` methods (typically from scikit-learn) on `TimeSeries`.

        Parameters
        ----------
        scaler
            The transformer/scaler to transform the data.
            It must provide the `fit()`, `transform()` and `inverse_transform()` methods.
            Default: `sklearn.preprocessing.MinMaxScaler(feature_range=(0, 1))`; this
            will scale all the values of a time series between 0 and 1.
        name
            A specific name for the transformer
        """
        super().__init__(
            fittable=True,
            invertible=True,
            validators=[Validator(lambda x: self._fit_called, 'fit() must be called before transform()')],
            name=name
        )

        if (not callable(getattr(scaler, "fit", None)) or not callable(getattr(scaler, "transform", None))
                or not callable(getattr(scaler, "inverse_transform", None))): # noqa W503
            raise_log(ValueError(
                      'The provided transformer object must have fit(), transform() and inverse_transform() methods'),
                      logger)

        self.transformer = scaler
        self.train_series = None
        self._fit_called = False

    def fit(self, series: TimeSeries) -> 'ScalerWrapper':
        """ Fits this transformer/scaler to the provided time series data

        Parameters
        ----------
        series
            The time series to fit the transformer on
        """
        self.transformer.fit(series.values().reshape((-1, series.width)))
        self.train_series = series
        self._fit_called = True
        return self

    def transform(self, series: TimeSeries, *args, **kwargs) -> TimeSeries:
        """
        Returns a new time series, transformed with this (fitted) transformer.
        This does not handle series with confidence intervals - the intervals are discarded.

        Parameters
        ----------
        series
            The time series to transform

        Returns
        -------
        TimeSeries
            A new time series, transformed with this (fitted) transformer.
        """
        assert self._fit_called, 'fit() must be called before transform()'
        return TimeSeries.from_times_and_values(series.time_index(),
                                                self.transformer.transform(series.values().
                                                                           reshape((-1, series.width))))

    def inverse_transform(self, series: TimeSeries, *args, **kwargs) -> TimeSeries:
        """
        Performs the inverse transformation on a time series

        Parameters
        ----------
        series
            The time series to inverse transform

        Returns
        -------
        TimeSeries
            The inverse transform
        """
        return TimeSeries.from_times_and_values(series.time_index(),
                                                self.transformer.inverse_transform(series.values().
                                                                                   reshape((-1, series.width))))
