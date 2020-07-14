from logging import Logger
from unittest import TestCase
from unittest.mock import patch
import json

from harmony.message import Message

from pymods.subset import subset_granule
from tests.utilities import contains


class TestSubset(TestCase):
    """ Test the module that performs subsetting on a single granule. """

    @classmethod
    def setUpClass(cls):
        cls.granule_url = 'https://harmony.earthdata.nasa.gov/bucket/africa'
        cls.message_content = {
            'sources': [{'collection': 'C1233860183-EEDTEST',
                         'variables': [{'id': 'V1234834148-EEDTEST',
                                        'name': 'alpha_var',
                                        'fullPath': 'alpha_var'}],
                         'granules': [{'id': 'G1233860471-EEDTEST',
                                       'url': cls.granule_url}]}]
        }
        cls.message = Message(json.dumps(cls.message_content))

    def setUp(self):
        self.logger = Logger('tests')

    @patch('pymods.subset.VarInfo')
    @patch('pymods.subset.util_download')
    def test_subset_granule(self, mock_util_download, mock_var_info):
        """ Ensure valid request does not raise exception,
            raise appropriate exception otherwise.
        """
        granule = self.message.granules[0]
        mock_util_download.return_value = 'africa_subset.nc4'

        # Note: return value below is a list, not a set, so the order can be
        # guaranteed in the assertions that the request to OPeNDAP was made
        # with all required variables.
        mock_var_info.return_value.get_required_variables.return_value = [
            '/alpha_var', '/blue_var'
        ]

        with self.subTest('Succesful calls to OPeNDAP'):
            output_path = subset_granule(granule, self.logger)
            mock_util_download.assert_called_once_with(
                f'{self.granule_url}.nc4?alpha_var,blue_var',
                contains('/tmp/tmp'),
                self.logger
            )
            self.assertIn('africa_subset.nc4', output_path)
