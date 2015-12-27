from setuptools import setup, find_packages


setup(
    name='opentracing',
    version='0.1.0',
    author='Yuri Shkuro',
    author_email='ys@uber.com',
    description='Opentracing API',
    packages=find_packages(exclude=['clay_tornado.test']),
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
