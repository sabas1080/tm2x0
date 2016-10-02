from setuptools import setup, find_packages

#The test stuff is from https://fgimian.github.io/blog/2014/04/27/running-nose-tests-with-plugins-using-the-python-setuptools-test-command/
from setuptools.command.test import test as TestCommand

tests_require = ['nose',
                 'mock',
                 'coverage',
                 'pexpect',
                 'testfixtures']

# Inspired by the example at https://pytest.org/latest/goodpractises.html
class NoseTestCommand(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Run nose ensuring that argv simulates running nosetests directly
        import nose
        nose.run_exit(argv=['nosetests'])


setup(
    name="tm2x0",
    version="0.1",
    packages=find_packages(),
    install_requires=[],
    tests_require=tests_require,
    cmdclass={'test': NoseTestCommand},
    entry_points={
        'console_scripts': [
            'tm2x0-kicad-import = tm2x0.kicad_import:main',
            'tm2x0-describe = tm2x0.describe_cli:main',
        ],
    }
)
