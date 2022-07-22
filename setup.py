import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="xdnlp",
    version="0.0.18",
    author="geb",
    author_email="853934146@qq.com",
    description="An efficient NLP tool.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mikuh/xdnlp",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_data={'': ['data/*.txt', "data/*.tsv"]},
    install_requires=['numpy', 'pandas', 'nltk'],
    python_requires='>=3.6',
)