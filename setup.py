from setuptools import setup


setup(
    name='opentracing',
    version='0.4.0',
    author='Yuri Shkuro',
    author_email='ys@uber.com',
    description='Opentracing API',
    license='MIT',
    url='https://github.com/uber-common/opentracing-python',
    keywords=['opentracing'],
    classifiers=[
        'Development Status :: RFC',
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
