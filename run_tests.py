import unittest

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.discover('.', pattern='test_app.py')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    
    if result.wasSuccessful():
        exit(0)
    else:
        exit(1)
