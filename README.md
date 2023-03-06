# zarr-tools

Convert nd2 to zarr

[![License](https://img.shields.io/pypi/l/zarr-tools.svg?color=green)](https://github.com/BaroudLab/zarr-tools/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/zarr-tools.svg?color=green)](https://pypi.org/project/zarr-tools)
[![Python Version](https://img.shields.io/pypi/pyversions/zarr-tools.svg?color=green)](https://python.org)
[![tests](https://github.com/BaroudLab/zarr-tools/workflows/tests/badge.svg)](https://github.com/BaroudLab/zarr-tools/actions)
[![codecov](https://codecov.io/gh/BaroudLab/zarr-tools/branch/main/graph/badge.svg)](https://codecov.io/gh/BaroudLab/zarr-tools)

## Installation

```pip install zarr-tools```

## Usage

### As command line 
``` python -m zarr-tools file.nd2 ```

This will produce the zarr dataset with default 5 steps of binning for xy dimensions.

### As python module

```python
import nd2
import zarr_tools

data = nd2.ND2File("input.nd2").to_dask()
zarr_tools.convert.to_zarr(
    data,
    channel_axis=1,
    path="output.zarr", 
    steps=4, 
    name=['BF','TRITC'], 
    colormap=['gray','green'],
    lut=((1000,30000),(440, 600)),
)
```

