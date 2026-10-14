from engine import check_velocity, check_outlier, velocity_cache
from datetime import datetime, timedelta
import pytest


@pytest.fixture
def clear_velocity_cache():
    # Clear the velocity cache before each test
    velocity_cache.clear()


def test_check_outlier_normal_amount():
    # Test case 1: Amount is not an outlier
    history = [10, 12, 11, 13, 14]
    amount = 12
    assert check_outlier(history, amount) is False


def test_check_outlier_large_amount():
    # Test case 2: Amount is an outlier
    history = [10, 12, 11, 13, 14]
    amount = 30
    assert check_outlier(history, amount) is True


def test_check_outlier_empty_history():
    # Test case 3: Empty history
    history = []
    amount = 10
    assert check_outlier(history, amount) is False


def test_check_outlier_same_history():
    # Test case 4: All amounts in history are the same
    history = [100, 100, 100, 100, 100]
    amount = 100
    assert check_outlier(history, amount) is False


def test_check_velocity_with_single_transaction(clear_velocity_cache):

    # Simulate a single transaction
    user_id = 1
    current_time = datetime(2024, 6, 1, 12, 0, 0)

    # The first transaction should not trigger the velocity flag
    assert check_velocity(user_id, current_time) is False


def test_check_velocity_with_five_transactions(clear_velocity_cache):
    user_id = 1
    current_time = datetime(2024, 6, 1, 12, 0, 0)

    # Simulate five transactions within the last minute
    for i in range(4):
        check_velocity(user_id, current_time - timedelta(seconds=i * 10))

    # The fifth transaction should not trigger the velocity flag
    assert check_velocity(user_id, current_time) is False


def test_check_velocity_with_six_transactions(clear_velocity_cache):
    user_id = 1

    # Simulate six transactions within the last minute
    for i in range(5):
        current_time = datetime(2024, 6, 1, 12, 0, i)
        check_velocity(user_id, current_time)

    # The sixth transaction should trigger the velocity flag
    assert check_velocity(user_id, current_time) is True

