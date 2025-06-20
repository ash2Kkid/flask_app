from setuptools import setup, find_packages

setup(
    name="flask-agent-zero-app",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask==2.3.3",
        "requests==2.32.3",
        "python-dotenv==1.0.1",
        "pytest==8.3.2"
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A Flask app integrated with Agent Zero",
    python_requires=">=3.9"
)