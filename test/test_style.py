from flake8.api import legacy as flake8
import unittest


class TestCodeFormat(unittest.TestCase):
    def test_code_format(self) -> None:
        """Test that we conform to PEP-8."""

        style_guide = flake8.get_style_guide(quiet=2, ignore=['E111', 'E114', 'E121', 'W191',
                                                              'E266', 'E402'])
        report = style_guide.check_files('..')
        errors = (len(report.get_statistics('F')) + len(report.get_statistics('E')) +
                  len(report.get_statistics('W')))
        self.assertEqual(errors, 0, 'Flake8 found {} violations'.format(errors))