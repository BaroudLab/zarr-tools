from .convert import to_zarr
import fire
import nd2
import os

def main(nd2_path:str, output:str=None, channel_axis:int=1, steps:int=6, dry_run=False):
    data = (d := nd2.ND2File(nd2_path)).to_dask().rechunk()
    print(d.sizes)
    try:
        channel_axis = list(d.sizes.keys()).index('C')
    except ValueError:
        channel_axis = None

    if output is None:
        output = nd2_path.replace('.nd2', '.zarr')
    out = to_zarr(data, output, steps=steps, dry_run=dry_run, channel_axis=channel_axis, sizes=d.sizes)
    assert os.path.exists(out), "Failed..."
    exit(0)

if __name__=="__main__":
    fire.Fire(main)
