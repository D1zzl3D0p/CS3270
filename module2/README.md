# Module 2

In this module we were tasked to:

Output additional descriptive data, in addition to creating a package, and
uploading the package to [pypi test server](https://test.pypi.org).

## Information

Here we are dealing with the Australian Weather data.

Use the following commands to install the package:

```bash
pip install setuptools wheel

pip install -i http://test.pypi.org my_first_package_8TyUNLepm1b
```

## Test Procedure

Simply import the module, and then run `test_functions()`

## Implementation

I ended up downloading the dataset direct from Kaggle, onto the host's computer,
and reading the data in using pandas, since the module is loaded onto the host's
computer, no manifest is required

### Methods to generate files

1. Ensure the following packages are installed: setuptools, wheel, twine
2. Run `python -m build` with the setup.py file in the folder
3. Upload to pypi using twine
