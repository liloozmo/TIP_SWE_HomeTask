import os
from datetime import datetime
import unittest
from app.utils import get_current_time,ensure_output_directory

class TestUtils(unittest.TestCase):
    """
    This test class tests the two function in utils.py: get_current_time
    and _ensure_output_directory
    """
    def test_get_current_time(self):
        current_time = get_current_time() 
        self.assertIsInstance(current_time,str,"current time should be a string")

        #check if the format is correct and if not fail the test.
        try:
            datetime.strptime(current_time,"%d%m%Y_%H%M%S_%f")
        except ValueError:
            self.fail("get_current_time() returned a string in the wrong format")
    
    def test_ensure_output_directory(self):
        dummy_dir = "./tests/temporary_test_output" #Create dummy directory for the test output
        if os.path.exists(dummy_dir):  #Delete if exist
            os.rmdir(dummy_dir)
        ensure_output_directory(directory=dummy_dir)   # Call the funcion 
        self.assertTrue(os.path.exists(dummy_dir)) #Test if the dummy directory created after calling the function.

        os.rmdir(dummy_dir) # clean up.

if __name__ == "__main__":
    unittest.main()