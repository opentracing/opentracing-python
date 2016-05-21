from setuptools import setup


setup(
    name='opentracing',
    version='1.0rc4',
    author='Yuri Shkuro, The OpenTracing Authors',
    author_email='shkuro@gmail.com',
    description='OpenTracing API for Python. See documentation at http://opentracing.io',
    license='MIT',
    url='https://github.com/opentracing/opentracing-python',
    keywords=['opentracing'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=['opentracing'],
    include_package_data=True,
    zip_safe=False,
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
            'pytest>=2.7,<3',
            'pytest-cov',
            'pytest-mock',
            'Sphinx',
            'sphinx_rtd_theme'
        ]
    },
)
