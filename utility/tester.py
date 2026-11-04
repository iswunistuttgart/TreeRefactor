from abc import ABC, abstractmethod


class Tester(ABC):
    @abstractmethod
    def test_before(self) -> str:
        """Run tests and record which passed and which failed.

        Returns:
            str: A short summary of the test run.
        """

    @abstractmethod
    def test_changed(self) -> bool:
        """Run tests and check if the same tests pass and fail as recorded.

        Returns:
            bool: True if the test results have changed, False otherwise.
        """
        


class NoTester(Tester):
    """Used when no tests are configured: nothing is run and results never change."""

    def test_before(self) -> str:
        return "No tests configured, skipping tests"

    def test_changed(self) -> bool:
        return False
