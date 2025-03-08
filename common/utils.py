from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
import io
from pathlib import PurePath
import string
import time
from typing import ClassVar, Literal
from django.db import models
from django.utils.deconstruct import deconstructible
from django.core.files.images import ImageFile
from PIL import Image, ImageOps
from typing import BinaryIO


@deconstructible
@dataclass
class FileUploadPathGenerator:

    base_path: PurePath
    name_prefix: str

    _name_prefix_range: ClassVar[tuple[Literal[2], Literal[16]]] = 2, 16


    def __post_init__(self) -> None:
        if self.base_path.is_absolute():
            raise ValueError(f"The base_path ({str(self.base_path)}) must be relative.")
        
        if not set(self.name_prefix).issubset(string.ascii_letters):
            raise ValueError(f"The name_prefix ({self.name_prefix}) can only contain ascii letters.")

        min_size, max_size = FileUploadPathGenerator._name_prefix_range
        if len(self.name_prefix) > max_size or len(self.name_prefix) < min_size:
            raise ValueError(f"The name_prefix ({self.name_prefix}) must be within {min_size} to {max_size} characters.")


    def __call__(self, instance: models.Model, filename_from_user: str) -> str:
        ext = PurePath(filename_from_user).suffix
        new_filename = f"{self.name_prefix}{FileUploadPathGenerator._get_timestamp()}{ext}"
        return str(self.base_path / new_filename)

    
    @staticmethod
    def _get_timestamp() -> str:
        return ''.join(str(time.time()).split('.'))


class ImageFormat(StrEnum):
    PNG = 'PNG'
    JPEG = 'JPEG'
    BMP = 'BMP'
    GIF = 'GIF'
    ICO = 'ICO'
    PDF = 'PDF'
    TIFF = 'TIFF'
    WEBP = 'WEBP'


_file_extensions_for_image_format: Mapping[str, tuple[str, ...]] = {
    'BLP': ('.blp',),
    'BMP': ('.bmp',),
    'BUFR': ('.bufr',),
    'CUR': ('.cur',),
    'DCX': ('.dcx',),
    'DDS': ('.dds',),
    'DIB': ('.dib',),
    'EPS': ('.ps', '.eps'),
    'FITS': ('.fit', '.fits'),
    'FLI': ('.fli', '.flc'),
    'FTEX': ('.ftc', '.ftu'),
    'GBR': ('.gbr',),
    'GIF': ('.gif',),
    'GRIB': ('.grib',),
    'HDF5': ('.h5', '.hdf'),
    'ICNS': ('.icns',),
    'ICO': ('.ico',),
    'IM': ('.im',),
    'IPTC': ('.iim',),
    'JPEG': ('.jfif', '.jpe', '.jpg', '.jpeg'),
    'JPEG2000': ('.jp2', '.j2k', '.jpc', '.jpf', '.jpx', '.j2c'),
    'MPEG': ('.mpg', '.mpeg'),
    'MPO': ('.mpo',),
    'MSP': ('.msp',),
    'PALM': ('.palm',),
    'PCD': ('.pcd',),
    'PCX': ('.pcx',),
    'PDF': ('.pdf',),
    'PIXAR': ('.pxr',),
    'PNG': ('.png', '.apng'),
    'PPM': ('.pbm', '.pgm', '.ppm', '.pnm', '.pfm'),
    'PSD': ('.psd',),
    'QOI': ('.qoi',),
    'SGI': ('.bw', '.rgb', '.rgba', '.sgi'),
    'SUN': ('.ras',),
    'TGA': ('.tga', '.icb', '.vda', '.vst'),
    'TIFF': ('.tif', '.tiff'),
    'WEBP': ('.webp',),
    'WMF': ('.wmf', '.emf'),
    'XBM': ('.xbm',),
    'XPM': ('.xpm',)
}


def get_file_extensions_for_image_format(image_format: ImageFormat) -> tuple[str, ...]:
    return _file_extensions_for_image_format[image_format]


def get_format_for_image_extension(image_extension: str) -> ImageFormat:
    for format, extensions in _file_extensions_for_image_format.items():
        if image_extension in extensions:
            return ImageFormat[format]
    else:
        raise ValueError(f"Image extension {image_extension} is not recognized.")


_compression_params = dict(
    # JPEG params
    quality=10,
    optimize=True,
    dpi=(72, 72),

    # PNG params
    compress_level=9,

    # WEBP params
    method=6
)
def compress_image_file(image_file: BinaryIO | ImageFile) -> io.BytesIO:
    in_memory_file = io.BytesIO()
    with Image.open(image_file) as img:
        img.save(in_memory_file, format=img.format, **_compression_params)
    return in_memory_file


def generate_thumbnail(image_file: BinaryIO | ImageFile, size: tuple[int, int]) -> io.BytesIO:
    in_memory_file = io.BytesIO()
    with Image.open(image_file) as img:
        ImageOps.pad(img, size, color='#ffffff').save(in_memory_file, format=img.format)
    return in_memory_file
