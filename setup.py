from setuptools import setup


setup(
    name='opentracing',
    version='2.0.0',
    author='The OpenTracing Authors',
    author_email='opentracing@googlegroups.com',
    description='OpenTracing API for Python. See documentation at http://opentracing.io',
    long_description='\n'+open('README.rst').read(),
    license='Apache License 2.0',
    url='https://github.com/opentracing/opentracing-python',
    keywords=['opentracing'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=['opentracing'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    extras_require={
        'tests': [
            'doubles',
            'flake8<3',  # see https://github.com/zheller/flake8-quotes/issues/29
            'flake8-quotes',
            'mock<1.1.0',
            'pytest>=2.7,<3',
            'pytest-cov',
            'pytest-mock',
            'Sphinx',
            'sphinx_rtd_theme',

            'six>=1.10.0,<2.0',
            'gevent==1.2',
            'tornado',
        ],
        ':python_version == "2.7"': ['futures'],
    },
)
