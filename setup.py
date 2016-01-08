from setuptools import setup


setup(
    name='opentracing',
    version='0.5.2.dev0',
    author='OpenTracing Authors',
    author_email='shkuro@gmail.com',
    description='OpenTracing API for Python. See documentation at http://opentracing.io',
    license='MIT',
    url='https://github.com/opentracing/api-python',
    download_url = 'https://github.com/opentracing/api-python/tarball/0.5.0',
    keywords=['opentracing'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
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
