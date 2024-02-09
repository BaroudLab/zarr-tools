"""
Export data to zarr
"""

import os

import dask.array as da
import numpy as np
import zarr


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
    store = zarr.DirectoryStore(baseurl := path)
    grp = zarr.group(store)

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


def to_ome_zarr(
    dask_input: da.Array,
    path: str = None,
    steps=5,
    channel_axis=1,
    time_axis=None,
    dry_run=False,
    rechunk=(1, 1, 2000, 2000),
    axes=[
        {"name": "channel", "type": "channel"},
        {"name": "chip", "type": "space"},
        {"name": "y", "type": "space"},
        {"name": "x", "type": "space"},
    ],
    channels=[
        {
            "active": True,
            "color": "FFFFFF",
            "label": "BF",
            "window": {"end": 30000, "max": 64000, "min": 0, "start": 10000},
        },
        {
            "active": True,
            "color": "00FFFF",
            "label": "TRITC",
            "window": {"end": 600, "max": 64000, "min": 0, "start": 400},
        },
        {
            "active": False,
            "color": "0000FF",
            "label": "labels",
            "window": {"end": 500, "max": 501, "min": 0, "start": 0},
        },
    ],
):
    """
    Saves multiscale zarr dataset, returns the path.ome.zarr
    Time and channels should be first dimenstions (types: time, channel)
    """
    store = zarr.DirectoryStore(baseurl := path)
    grp = zarr.group(store)

    print(baseurl)
    datasets = []
    coord_scale = [1.0] * dask_input.ndim

    def get_scale(i):
        out = np.array(coord_scale)
        out[-2:] = 2**i
        return list(out)

    for i in range(steps):
        if i == 0:
            data = dask_input
        else:
            data = dask_input[..., ::2, ::2]

        try:
            data = data.rechunk(rechunk)
            print(data.chunksize, data.shape, data.npartitions)
            if dry_run:
                print(f"dry-run `to save to` {os.path.join(baseurl, str(i))}")
                continue

            data.to_zarr(ppp := os.path.join(baseurl, str(i)))
            print(f"saved {ppp}")
            datasets.append(
                {
                    "path": str(i),
                    "coordinateTransformations": [
                        {"scale": get_scale(i), "type": "scale"}
                    ],
                }
            )
            grp.attrs["multiscales"] = [
                {
                    "axes": axes,
                    "datasets": datasets,
                    "name": os.path.basename(path),
                    "version": "0.4",
                }
            ]

            dask_input = da.from_zarr(ppp)
        except Exception as e:
            print(e.args)
            raise e
    grp.attrs["omero"] = {"channels": channels}

    return baseurl
