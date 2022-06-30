# zarr-tools

Convert nd2 to zarr

## Installation

```pip install git+https://gitlab.pasteur.fr/aaristov/zarr-tools.git```

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

