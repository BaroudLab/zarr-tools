"""
Export data to zarr
"""

import os

import dask.array as da
import zarr
from zarr.storage import LocalStore


def to_zarr(
    dask_input: da.Array,
    path: str = None,
    steps=3,
    channel_axis=1,
    dry_run=False,
    **kwargs,
):
    """
    Saves multiscale zarr dataset, returns the path.zarr
    """
    baseurl = path
    store = LocalStore(baseurl)
    grp = zarr.open_group(store, mode="a")

    print(baseurl)
    datasets = []
    for i in range(steps):
        if i == 0:
            data = dask_input
        else:
            data = dask_input[..., ::2, ::2]

        try:
            data = data.rechunk()
            print(data.chunksize, data.shape, data.npartitions)
            if dry_run:
                print(f"dry-run `to save to` {os.path.join(baseurl, str(i))}")
                continue

            data.to_zarr(ppp := os.path.join(baseurl, str(i)))
            print(f"saved {ppp}")
            datasets.append({"path": str(i)})
            grp.attrs["multiscales"] = {
                "multiscales": [
                    {
                        "datasets": datasets,
                        "title": os.path.basename(baseurl),
                        "type": "nd2",
                        "channel_axis": channel_axis,
                        "version": "0.1",
                        **kwargs,
                    },
                ]
            }
            dask_input = da.from_zarr(ppp)
        except Exception as e:
            print(e.args)
            raise e

    return baseurl
