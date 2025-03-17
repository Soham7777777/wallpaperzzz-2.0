from collections.abc import Mapping
from enum import StrEnum
import io
from django.core.files.images import ImageFile
from PIL import Image


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


def get_image_format_for_file_extension(file_extension: str) -> ImageFormat:
    for format, extensions in _file_extensions_for_image_format.items():
        if file_extension in extensions:
            return ImageFormat[format]
    else:
        raise ValueError(f"File extension {file_extension} is not recognized.")


def generate_webp_from_jpeg(image_file: ImageFile) -> ImageFile:
    in_memory_file = io.BytesIO()
    with Image.open(image_file) as img:
        if img.format != ImageFormat.JPEG:
            raise ValueError("The image must be in JPEG format.")
        img.save(
            in_memory_file,
            format=ImageFormat.WEBP,

            # webp compression params
            quality=20,
            alpha_quality=0,
            method=6,
        )
    return ImageFile(in_memory_file)
