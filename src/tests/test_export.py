from zarr_tools import convert, __main__
import numpy as np
import dask.array as da
import os
import shutil

def test_convert():

    data = np.zeros((15,3,2**12, 2**12), dtype="uint16")
    path = "test.zarr"
    convert.to_zarr(
        da.from_array(data),
        path = path,
        steps=3
    )
    for i in range(3):
        assert da.from_zarr(os.path.join(path, str(i))).shape[-1] == 2**(12-i)
    
    shutil.rmtree(path)