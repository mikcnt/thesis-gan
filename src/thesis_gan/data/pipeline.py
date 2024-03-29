from typing import List, Optional, Union

import numpy as np
import pandas as pd
from sklearn.exceptions import NotFittedError
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.utils.validation import check_is_fitted


def is_fitted(scaler: Union[MinMaxScaler, StandardScaler]) -> bool:
    try:
        check_is_fitted(scaler)
        return True
    except NotFittedError:
        return False


class Pipeline:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def preprocess(self, df: pd.DataFrame, targets: List[str]) -> np.ndarray:
        pass

    def inverse_transform(self, x: np.ndarray, x_last: Optional[np.ndarray]) -> np.ndarray:
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} (scaler={self.scaler})"


class ScalerPipeline(Pipeline):
    def __init__(self, scaler: Union[MinMaxScaler, StandardScaler]) -> None:
        super(ScalerPipeline, self).__init__()
        self.scaler = scaler

    def preprocess(self, df: pd.DataFrame, targets: List[str]) -> np.ndarray:
        df_targets = df[targets]

        if not is_fitted(self.scaler):
            self.scaler.fit(df_targets)

        return self.scaler.transform(df_targets)

    def inverse_transform(self, x: np.ndarray, x_last: Optional[np.ndarray] = None) -> np.ndarray:
        return self.scaler.inverse_transform(x)


class ReturnPipeline(Pipeline):
    def __init__(self, scaler: Union[MinMaxScaler, StandardScaler]) -> None:
        super(ReturnPipeline, self).__init__()
        self.scaler = scaler

    def preprocess(self, df: pd.DataFrame, targets: List[str]) -> np.ndarray:
        df_targets = df[targets]
        returns = df_targets.pct_change().fillna(0).to_numpy()

        if not is_fitted(self.scaler):
            self.scaler.fit(returns)

        return self.scaler.transform(returns)

    def inverse_transform(self, x: np.ndarray, x_last: np.ndarray) -> np.ndarray:
        returns = self.scaler.inverse_transform(x)
        return x_last * np.cumprod((1 + returns), axis=0)


class LogReturnPipeline(Pipeline):
    def __init__(self, scaler: Union[MinMaxScaler, StandardScaler]) -> None:
        super(LogReturnPipeline, self).__init__()
        self.scaler = scaler

    def preprocess(self, df: pd.DataFrame, targets: List[str]) -> np.ndarray:
        df_targets = df[targets]
        log_returns = np.log(df_targets / df_targets.shift(1)).fillna(0).to_numpy()

        if not is_fitted(self.scaler):
            self.scaler.fit(log_returns)

        return self.scaler.transform(log_returns)

    def inverse_transform(self, x: np.ndarray, x_last: np.ndarray) -> np.ndarray:
        log_returns = self.scaler.inverse_transform(x)
        return x_last * (np.cumprod(np.exp(log_returns), axis=0))
