import numpy as np

from tdf_galaxy_tau.metrics.comparison import chi_square, reduced_chi_square, rmse
from tdf_galaxy_tau.metrics.information_criteria import aic, bic, model_parameter_count


def test_metrics_basic_outputs() -> None:
    obs = np.array([10.0, 11.0, 12.0])
    mod = np.array([10.0, 10.0, 10.0])
    err = np.array([1.0, 1.0, 1.0])
    chi2 = chi_square(obs, mod, err)
    assert rmse(obs, mod) > 0
    assert reduced_chi_square(chi2, 3, 0) > 0
    assert aic(chi2, 1) >= chi2
    assert bic(chi2, 3, 1) >= chi2


def test_baryonic_parameter_count_zero() -> None:
    assert model_parameter_count("baryonic_only") == 0
    assert model_parameter_count("nfw") == 2
    assert model_parameter_count("burkert") == 2
