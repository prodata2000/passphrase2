from setuptools import setup, find_packages

setup(
    name="flask-text-generator",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask",
        "Pillow"
        "gunicorn"
    ],
    entry_points={
        'console_scripts': [
            'flaskapp=wsgi.py:app.run'
        ]
    }
)
