from setuptools import setup


setup(
    name='opentracing',
    version='2.0.1.dev0',
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
            'flake8<3',  # see https://github.com/zheller/flake8-quotes/issues/29
            'flake8-quotes',
            'mock<1.1.0',
            'pytest>=2.7,<3',
            'pytest-cov==2.6.0', # pytest-cov 2.6.1 depends on pytest>=3.6
            'pytest-mock',
            'Sphinx',
            'sphinx_rtd_theme',
            'six>=1.10.0,<2.0',
        ],
        'tornado': [
            'tornado<6',
        ],
        'gevent': [
            'gevent==1.2',
        ],
        ':python_version == "2.7"': ['futures'],
    },
)
