from setuptools import setup


setup(
    name='opentracing',
    version='0.3.1',
    author='Yuri Shkuro',
    author_email='ys@uber.com',
    description='Opentracing API',
    packages=['opentracing'],
    include_package_data=True,
    platforms='any',
    install_requires=[
        'futures',
    ],
    extras_require={
        'tests': [
            'doubles',
            'flake8',
            'flake8-quotes',
            'mock<1.1.0',
            'pytest',
            'pytest-cov',
            'pytest-mock',
            'Sphinx',
            'sphinx_rtd_theme',
        ]
    },
)
