#!/usr/bin/env python3
import socket
import sys
from PIL import Image, ImageDraw, ImageFont
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send
from brother_ql.raster import BrotherQLRaster

# ----- ARGUMENTS -----
if len(sys.argv) != 2:
    print("Usage: python print_label.py <file_with_label_content>")
    sys.exit(1)

file_path = sys.argv[1]

# ----- READ LABEL DATA -----
with open(file_path) as f:
    content = f.read()

# Expecting content like:
# Serial: 1000000012345678
# Board: 000 (0)
# Printer IP: 10.9.8.219
serial = ''
board = ''
printer_ip = ''
part_no = ''
for line in content.splitlines():
    if line.lower().startswith('serial:'):
        serial = line.split(':',1)[1].strip()
    elif line.lower().startswith('board:'):
        board = line.split(':',1)[1].strip()
    elif line.lower().startswith('partno:'):
        part_no = line.split(':', 1)[1].strip()
    elif line.lower().startswith('printer ip:'):
        printer_ip = line.split(':',1)[1].strip()


# ----- CONFIG -----
PRINTER_MODEL = "QL-820NWB"

printer=f"{printer_ip}:9100"
# Label size in pixels (full printer width)
LABEL_WIDTH_PX = 306   # Must match printer expected width
LABEL_HEIGHT_PX = 991  # For 29x90 mm die-cut label at 300 dpi


backend = 'network'
# ----- CREATE LABEL IMAGE -----
img = Image.new("RGB", (991, 306), "white")
draw = ImageDraw.Draw(img)

# Load TrueType font
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)

# Text to print
text1 = f"Serial: {serial}"
text2 = f"Board: {board}"
text3 = f"PartNo: {part_no}"

# Draw centered text
draw.text((10, 70), text1, fill="black", font=font)
draw.text((10, 140), text2, fill="black", font=font)
draw.text((10, 210), text3, fill="black", font=font)

# ----- GENERATE RASTER DATA -----
qlr = BrotherQLRaster(PRINTER_MODEL)

label_images=[]
label_images.append(img)

instructions = convert(
        qlr=qlr,
        images=label_images,    #  Takes a list of file names or PIL objects.
        label='29x90',
        rotate='90',    # 'Auto', '0', '90', '270'
        threshold=70.0,    # Black and white threshold in percent.
        dither=False,
        compress=False,
        dpi_600=False,
        hq=True,    # False for low quality.
        cut=True
)

send(instructions=instructions, printer_identifier=printer, backend_identifier=backend, blocking=True)

print("Label sent to printer successfully!")
