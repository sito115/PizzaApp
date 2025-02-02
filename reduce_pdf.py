from pathlib import Path
from spire.pdf import *
from spire.pdf.common import *
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

IS_OVERWRITE = False
QUALITY = 60

ROOT = Path(r"C:\Thomas\Jobs\Geomecon")

INPUT_FOLDER = ROOT.joinpath('Literatur')
OUTPUT_FOLDER = ROOT.joinpath('Literatur_shrinked')

for file in INPUT_FOLDER.rglob('*.pdf'):
    relative_path = file.relative_to(INPUT_FOLDER)
    output_path = OUTPUT_FOLDER.joinpath(relative_path)

    if not IS_OVERWRITE:
        if output_path.exists():
            logging.info(f"Skipping {file.relative_to(ROOT)}")
            continue

    logging.info('Compressing ' + str(file.relative_to(ROOT)))
    compressor = PdfCompressor(str(file))
    compression_options = compressor.OptimizationOptions
    compression_options.SetImageQuality(ImageQuality.Medium)
    # compression_options.SetIsCompressFonts(True)
    # compression_options.SetResizeImages(True)
    compression_options.SetIsCompressImage(True)
    # compression_options.SetIsCompressContents(True)
    compressor.CompressToFile(str(output_path))


    logging.info(f"Created {output_path.relative_to(ROOT)}")
    logging.info(f"Old size: {file.stat().st_size / 1024 / 1024:.2f} MB")
    logging.info(f"New size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
