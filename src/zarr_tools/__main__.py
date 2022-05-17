from .convert import to_zarr
import fire
import json
import nd2
import os

def main(nd2_path:str, output:str=None, channel_axis:int=1, steps:int=5, dry_run=False):
    data = (d := nd2.ND2File(nd2_path)).to_dask().rechunk()
    print(d.sizes)

    try:
        channel_axis = list(d.sizes.keys()).index('C')
    except ValueError:
        channel_axis = None

    if output is None:
        output = nd2_path.replace('.nd2', '.zarr')

        
    out = to_zarr(
        data, 
        output, 
        steps=steps, 
        dry_run=dry_run, 
        channel_axis=channel_axis, 
        sizes=d.sizes,
        lut=get_lut(d))
    
    assert os.path.exists(out), "Saving zarr failed..."
    
    try:
        meta_path = save_metadata(d, output)
        print(f'Saved metadata to {meta_path}')
    except Exception as e:
        print(f'Saving metadata Failed due to {e}')
        
    exit(0)

def save_metadata(data:nd2.ND2File, output:str):
    try:
        meta = data.custom_data
        meta['NDControlV1_0'] = {}
        with open(meta_path:=os.path.join(output, '.metadata'), 'w') as f:
            json.dump(meta, f, indent=4)
    except TypeError as e:
        raise e
    return meta_path

def get_lut(data:nd2.ND2File):
    try:
        meta = data.custom_data
        return \
        [
            [
                meta['LUTDataV1_0']['LutParam']['CompLutParam'][f'{ch:02d}'][lim][0] \
                for lim in ['MinSrc','MaxSrc']
            ] for ch in range(data.sizes['C'])
        ]
    except Exception as e:
        print(f'Unable to get LUT due to {e}')
        return None

if __name__=="__main__":
    fire.Fire(main)
