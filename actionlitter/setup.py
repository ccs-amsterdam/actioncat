try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='actionlitter',
    install_requires=[
        "requests",
        "json",
        "amcat4py"
        "fastapi",
        "subprocess"
    ]
)
