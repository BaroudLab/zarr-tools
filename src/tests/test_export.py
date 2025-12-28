import json
import os
import shutil
from unittest.mock import MagicMock, Mock, patch

import dask.array as da
import numpy as np
import pytest

from zarr_tools import __main__, convert


def test_convert():

    data = np.zeros((15, 3, 2**12, 2**12), dtype="uint16")
    path = "test.zarr"
    convert.to_zarr(da.from_array(data), path=path, steps=3)
    for i in range(3):
        assert da.from_zarr(os.path.join(path, str(i))).shape[-1] == 2 ** (
            12 - i
        )

    shutil.rmtree(path)


def test_convert_dry_run():
    """Test dry_run mode in to_zarr"""
    data = np.zeros((2, 3, 128, 128), dtype="uint16")
    path = "test_dry_run.zarr"

    # Run with dry_run=True
    result = convert.to_zarr(
        da.from_array(data), path=path, steps=2, dry_run=True
    )

    # Verify the path is returned but nothing is saved
    assert result == path
    # Directory might be created but should be empty or minimal
    if os.path.exists(path):
        shutil.rmtree(path)


def test_convert_with_custom_channel_axis():
    """Test to_zarr with custom channel_axis"""
    data = np.zeros((2, 3, 128, 128), dtype="uint16")
    path = "test_custom_channel.zarr"

    result = convert.to_zarr(
        da.from_array(data), path=path, steps=2, channel_axis=0
    )

    assert result == path
    assert os.path.exists(path)

    shutil.rmtree(path)


def test_save_metadata():
    """Test save_metadata function"""
    output = "test_metadata.zarr"
    os.makedirs(output, exist_ok=True)

    # Create a mock ND2File object
    mock_nd2 = Mock()
    mock_nd2.custom_data = {
        "test_key": "test_value",
        "NDControlV1_0": {"existing": "data"},
    }

    meta_path = __main__.save_metadata(mock_nd2, output)

    assert os.path.exists(meta_path)
    assert meta_path == os.path.join(output, ".metadata")

    # Verify the metadata was written correctly
    with open(meta_path) as f:
        saved_meta = json.load(f)
        assert "test_key" in saved_meta
        assert saved_meta["test_key"] == "test_value"

    shutil.rmtree(output)


def test_save_metadata_type_error():
    """Test save_metadata with non-serializable data"""
    output = "test_metadata_error.zarr"
    os.makedirs(output, exist_ok=True)

    # Create a mock ND2File with non-serializable data
    mock_nd2 = Mock()
    mock_nd2.custom_data = {
        "non_serializable": lambda x: x  # Function cannot be JSON serialized
    }

    with pytest.raises(TypeError):
        __main__.save_metadata(mock_nd2, output)

    shutil.rmtree(output)


def test_get_lut():
    """Test get_lut function"""
    mock_nd2 = Mock()
    mock_nd2.sizes = {"C": 2}
    mock_nd2.custom_data = {
        "LUTDataV1_0": {
            "LutParam": {
                "CompLutParam": {
                    "00": {"MinSrc": [100], "MaxSrc": [1000]},
                    "01": {"MinSrc": [200], "MaxSrc": [2000]},
                }
            }
        }
    }

    lut = __main__.get_lut(mock_nd2)

    assert lut is not None
    assert len(lut) == 2
    assert lut[0] == [100, 1000]
    assert lut[1] == [200, 2000]


def test_get_lut_missing_data():
    """Test get_lut with missing LUT data"""
    mock_nd2 = Mock()
    mock_nd2.sizes = {"C": 2}
    mock_nd2.custom_data = {}

    lut = __main__.get_lut(mock_nd2)

    assert lut is None


@patch("zarr_tools.__main__.nd2.ND2File")
def test_main(mock_nd2_class):
    """Test main function"""
    # Create a mock ND2File instance
    mock_nd2_instance = MagicMock()
    mock_nd2_instance.sizes = {"C": 2, "Y": 128, "X": 128}
    mock_data = da.zeros((2, 128, 128), dtype="uint16")
    mock_nd2_instance.to_dask.return_value = mock_data
    mock_nd2_instance.custom_data = {
        "LUTDataV1_0": {
            "LutParam": {
                "CompLutParam": {
                    "00": {"MinSrc": [0], "MaxSrc": [100]},
                    "01": {"MinSrc": [0], "MaxSrc": [100]},
                }
            }
        }
    }

    mock_nd2_class.return_value = mock_nd2_instance

    # Create a temporary nd2 file path (doesn't need to exist due to mocking)
    nd2_path = "test_file.nd2"
    output_path = "test_output.zarr"

    with pytest.raises(SystemExit) as exc_info:
        __main__.main(nd2_path, output=output_path, steps=2, dry_run=True)

    assert exc_info.value.code == 0
    mock_nd2_class.assert_called_once_with(nd2_path)


@patch("zarr_tools.__main__.nd2.ND2File")
def test_main_no_channel_axis(mock_nd2_class):
    """Test main function without channel axis"""
    mock_nd2_instance = MagicMock()
    mock_nd2_instance.sizes = {"Y": 128, "X": 128}  # No 'C' dimension
    mock_data = da.zeros((128, 128), dtype="uint16")
    mock_nd2_instance.to_dask.return_value = mock_data
    mock_nd2_instance.custom_data = {}

    mock_nd2_class.return_value = mock_nd2_instance

    nd2_path = "test_file_no_channel.nd2"

    with pytest.raises(SystemExit) as exc_info:
        __main__.main(nd2_path, steps=2, dry_run=True)

    assert exc_info.value.code == 0


@patch("zarr_tools.__main__.nd2.ND2File")
@patch("zarr_tools.__main__.save_metadata")
def test_main_metadata_save_fails(mock_save_metadata, mock_nd2_class):
    """Test main function when metadata saving fails"""
    # Create a mock ND2File instance
    mock_nd2_instance = MagicMock()
    mock_nd2_instance.sizes = {"C": 2, "Y": 128, "X": 128}
    mock_data = da.zeros((2, 128, 128), dtype="uint16")
    mock_nd2_instance.to_dask.return_value = mock_data
    mock_nd2_instance.custom_data = {}

    mock_nd2_class.return_value = mock_nd2_instance

    # Make save_metadata raise an exception
    mock_save_metadata.side_effect = Exception("Metadata save failed")

    nd2_path = "test_file_metadata_fail.nd2"
    output_path = "test_output_metadata_fail.zarr"

    # The main function should catch the exception and exit normally
    with pytest.raises(SystemExit) as exc_info:
        __main__.main(nd2_path, output=output_path, steps=2, dry_run=True)

    assert exc_info.value.code == 0
    mock_save_metadata.assert_called_once()
