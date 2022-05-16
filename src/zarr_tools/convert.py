import zarr
import dask.array as da
import os
import nd2

def nd2_to_zarr(path_nd2, out=None, steps=6, dry_run=False):
    '''
    Converts nd2 to zarr, multiscale
    '''
    data = nd2.ND2File(path_nd2)
    print(sizes := data.sizes)
    channel_axis = list(sizes.keys()).index('C')
    out = (path_nd2.replace('.nd2', '.zarr') if out is None else path_nd2)
    dask_input = data.to_dask()
    _ = to_zarr(
        dask_input=dask_input,
        path=out,
        steps=steps,
        channel_axis=channel_axis,
        dry_run=dry_run
    )


def to_zarr(dask_input:da.Array, path:str=None, steps=3, channel_axis=1, dry_run=False, **kwargs):
    store = zarr.DirectoryStore(baseurl := path.replace('.nd2', '.zarr') if path is None else path)
    grp = zarr.group(store)
    
    print(baseurl)
    datasets = []
    for i in range(steps):
        if i==0:
            data = dask_input
        else:
            data = dask_input[...,::2,::2]

        try:
            data = data.rechunk()
            print(data.chunksize, data.shape)
            if dry_run:
                print(f'dry-run `to save to` {os.path.join(baseurl, str(i))}')
                continue
            
            data.to_zarr(ppp:=os.path.join(baseurl, str(i)))
            print(f'saved {ppp}')
            datasets.append({"path": str(i)})
            grp.attrs['multiscales'] = {
                "multiscales": [
                    {
                        "datasets": datasets,
                        "name": os.path.basename(baseurl),
                        "type": "nd2",
                        "channel_axis": channel_axis,
                        "version": "0.1",
                        **kwargs
                    },

                ]
            }
            dask_input = da.from_zarr(ppp)
        except Exception as e:
            print(e.args)
            raise e
        
    return baseurl
    

