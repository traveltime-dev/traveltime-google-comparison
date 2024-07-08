import pandas as pd
from traveltime_google_comparison.analysis import *


def test_calculate_differences_calculate_absolute_and_relative_differences():
    data = {
        Fields.TRAVEL_TIME[GOOGLE_API]: [100, 200, 300],
        Fields.TRAVEL_TIME[TRAVELTIME_API]: [90, 210, 290]
    }
    df = pd.DataFrame(data)
    result_df = calculate_differences(df)

    assert result_df[ABSOLUTE_ERROR].tolist() == [10, 10, 10]
    assert result_df[RELATIVE_ERROR].tolist() == [10.0, 5.0, 10.0 / 3]


def test_calculate_differences_survives_division_by_zero():
    data = {
        Fields.TRAVEL_TIME[GOOGLE_API]: [0, 200, 300],
        Fields.TRAVEL_TIME[TRAVELTIME_API]: [90, 210, 290]
    }
    df = pd.DataFrame(data)
    result_df = calculate_differences(df)

    assert result_df[ABSOLUTE_ERROR].tolist() == [90, 10, 10]
    assert result_df[RELATIVE_ERROR].tolist() == [float('inf'), 5.0, 10.0 / 3]


odd_data = {
    ABSOLUTE_ERROR: [10, 20, 30, 40, 50],
    RELATIVE_ERROR: [5.0, 10.0, 15.0, 20.0, 25.0]
}
odd_df = pd.DataFrame(odd_data)


def test_calculate_quantiles_return_exact_element_for_quantile_which_provides_an_exact_division():
    # Test 1: Basic Quantile Test

    result = calculate_quantiles(odd_df, 0.5)

    assert isinstance(result, QuantileErrorResult)
    assert result.absolute_error == 30
    assert result.relative_error == 15

    assert calculate_quantiles(odd_df, 0.25) == QuantileErrorResult(20, 10)
    assert calculate_quantiles(odd_df, 0.75) == QuantileErrorResult(40, 20)

    assert calculate_quantiles(odd_df, 0.0) == QuantileErrorResult(10, 5)
    assert calculate_quantiles(odd_df, 1.0) == QuantileErrorResult(50, 25)


def test_calculate_quantiles_return_next_element_for_quantile_which_does_not_provide_an_exact_division():
    even_data = {
        ABSOLUTE_ERROR: [10, 20, 30, 40],
        RELATIVE_ERROR: [5.0, 10.0, 15.0, 20.0]
    }
    even_df = pd.DataFrame(even_data)

    assert calculate_quantiles(odd_df, 0.01) == QuantileErrorResult(20, 10)
    assert calculate_quantiles(even_df, 0.5) == QuantileErrorResult(30, 15)
    assert calculate_quantiles(odd_df, 0.99) == QuantileErrorResult(50, 25)


def test_calculate_quantiles_for_unsorted_list():
    random_order_data = {
        ABSOLUTE_ERROR: [40, 10, 30, 50, 20],
        RELATIVE_ERROR: [25.0, 20.0, 10.0, 15.0, 5.0]
    }
    random_order_df = pd.DataFrame(random_order_data)
    assert calculate_quantiles(random_order_df, 0.25) == QuantileErrorResult(20, 10)
    assert calculate_quantiles(random_order_df, 0.75) == QuantileErrorResult(40, 20)
