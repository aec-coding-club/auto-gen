#!/usr/bin/env python

"""
gen-cards.py: Script to mass-generate identity cards & handouts using email
as the primary key to compile all student data, given
  - image source directory, with items labelled as {email}.png 
  - CSV with student data
"""

import traceback, os, textwrap, csv, glob
from PIL import Image, ImageFont, ImageDraw

__author__ = "Jayanta Pandit"
__version__ = "1.0.0"
__email__ = "jay.dnb@outlook.in"
__license__ = "GPL"
__date__ = "Nov 8, 2022"

import traceback, os, textwrap, csv, glob
from PIL import Image, ImageFont, ImageDraw

# colours
RED = '#cd2626'
BLACK = '#000000'

# fonts
HAMMERSMITH_35 = ImageFont.truetype(r'HammersmithOne-Regular.ttf', 35)
HAMMERSMITH_75 = ImageFont.truetype(r'HammersmithOne-Regular.ttf', 75)
HAMMERSMITH_50 = ImageFont.truetype(r'HammersmithOne-Regular.ttf', 50)
HAMMERSMITH_100 = ImageFont.truetype(r'HammersmithOne-Regular.ttf', 100)
FIRACODE_25 = ImageFont.truetype(r'FiraCode-VariableFont_wght.ttf', 25)
FIRACODE_30 = ImageFont.truetype(r'FiraCode-VariableFont_wght.ttf', 30)

# data sources relative to script's root
TEMPLATE_SIDE1 = 'side1.png'
TEMPLATE_SIDE2 = 'side2.png'
RESPONSE_DATA_CSV = 'responses.csv'
HEADSHOT_SRC_DIR = 'photos'
ICARD_OUTP_DIR = 'out'

# data row indices: X = Y, where X can be found at (zero-indexed) column Y from source csv
IDX_UNIQUE_ID = 0
IDX_NAME = 1
IDX_DEPARTMENT = 3
IDX_ADDRESS = 5
IDX_CURRENT_YEAR = 2
IDX_PHONE_NO = 6
IDX_EMAIL_ID = 7

BATCH_SERIAL_MAP = { '1st': '2026', '2nd': '2025', '3rd': '2024', '4th': '2023' }

# template field coordinates: (x, y)
COORD_HEADSHOT = (170, 280)
COORD_NAME_LINE_1 = (420, 320)
COORD_NAME_LINE_2 = (420, 400)
COORD_UNIQUE_ID = (420, 290)
COORD_DEPARTMENT = (125, 255)
COORD_PASSOUT = (510, 255)
COORD_PHONE_NO = (125, 340)
COORD_ADDRESS = (510, 340)


def add_corners_and_square(im):
    im = im.resize((200, 200))
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask) 
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    im.putalpha(mask)
    return im


def make(id: str, name: str, headshot: str, dept: str, addr: str, passout: str, phone: str, email: str):
    # ---------------------------------- SIDE1 ----------------------------------
    template1 = Image.open(TEMPLATE_SIDE1)
    
    # Adding headshot to the template1
    headshot = add_corners_and_square(Image.open(headshot))
    template1.paste(headshot, COORD_HEADSHOT, headshot)

    # Filling text fields in side1
    ImageDraw.Draw(template1).text(COORD_NAME_LINE_1, name.split(' ')[0].upper(), RED, HAMMERSMITH_75)
    ImageDraw.Draw(template1).text(COORD_NAME_LINE_2, ' '.join([ x.upper() for x in name.split(' ')[1:] ]), BLACK, HAMMERSMITH_50)
    ImageDraw.Draw(template1).text(COORD_UNIQUE_ID, id, BLACK, FIRACODE_25, stroke_width=1)
    
    # ---------------------------------- SIDE2 ----------------------------------
    template2 = Image.open(TEMPLATE_SIDE2)

    # Filling text fields in side2
    ImageDraw.Draw(template2).text(COORD_DEPARTMENT, dept.upper(), RED, FIRACODE_25, stroke_width=1)
    ImageDraw.Draw(template2).text(COORD_PASSOUT, passout, RED, FIRACODE_25, stroke_width=1)
    ImageDraw.Draw(template2).text(COORD_PHONE_NO, phone, RED, FIRACODE_25, stroke_width=1)
    ImageDraw.Draw(template2).text(COORD_ADDRESS, textwrap.fill(addr, 25), RED, FIRACODE_25, stroke_width=1)

    # Saving the front face inside './{ICARD_OUTP_DIR}/{email}'
    dir_name = '-'.join(id.split('/')) + '%' + email
    try:
        os.mkdir(os.path.join(os.getcwd(), ICARD_OUTP_DIR, dir_name))
    except FileExistsError:
        # ignore all FileExistsError exceptions caused by already existing directories
        pass

    # save side 1
    template1.save(f'./{ICARD_OUTP_DIR}/{dir_name}/1.png')
    # save side 2
    template2.save(f'./{ICARD_OUTP_DIR}/{dir_name}/2.png')


if __name__ == "__main__":
    try:
        os.mkdir(os.path.join(os.getcwd(), ICARD_OUTP_DIR))
    except FileExistsError:
        # ignore FileExistsError exception caused by already existing directory
        pass
    
    print()
    file = open(f'./{RESPONSE_DATA_CSV}')
    csvee = csv.reader(file)
    
    data = []
    for row in csvee:
        data.append(row)
    for datarow in data:
        try:
            # convert exotic formats[*.jpg *.webp *.jpeg] to PNG[*.png]
            try: image = Image.open(f'./{HEADSHOT_SRC_DIR}/{datarow[IDX_EMAIL_ID]}.jpg')
            except FileNotFoundError:
                try: image = Image.open(f'./{HEADSHOT_SRC_DIR}/{datarow[IDX_EMAIL_ID]}.webp')
                except FileNotFoundError:
                    try: image = Image.open(f'./{HEADSHOT_SRC_DIR}/{datarow[IDX_EMAIL_ID]}.jpeg')
                    # account for rogue file extension casing possibilities
                    except FileNotFoundError:
                        try: image = Image.open(f'./{HEADSHOT_SRC_DIR}/{datarow[IDX_EMAIL_ID]}.JPG')
                        except FileNotFoundError:
                            try: image = Image.open(f'./{HEADSHOT_SRC_DIR}/{datarow[IDX_EMAIL_ID]}.WEBP')
                            except FileNotFoundError:
                                try: image = Image.open(f'./{HEADSHOT_SRC_DIR}/{datarow[IDX_EMAIL_ID]}.JPEG')
                                except FileNotFoundError:
                                    try: image = Image.open(f'./{HEADSHOT_SRC_DIR}/{datarow[IDX_EMAIL_ID]}.PNG')
                                    except FileNotFoundError:
                                        # Look for any file that contains a matching substring.
                                        # If this fails, control to transfered to the terminal 
                                        # exception handler below. This increases time complexity
                                        # multifold and should be resorted to when all the above fail.
                                        image = Image.open(glob.glob((os.path.join(os.getcwd(), HEADSHOT_SRC_DIR, f'*{datarow[IDX_EMAIL_ID]}*')))[0])

            # saving as *.png
            image.save(f'./{HEADSHOT_SRC_DIR}/{datarow[IDX_EMAIL_ID]}.png')
            
            # generate
            print('\u001b[31m[Generating...]\u001b[30m \u001b[32m', datarow[IDX_UNIQUE_ID], '\u001b[32m')

            # accounting for 'BCA'
            grad_year = int(BATCH_SERIAL_MAP[datarow[IDX_CURRENT_YEAR]])
            if datarow[IDX_DEPARTMENT] == 'BCA':
                grad_year -= 1
            
            make(
                # Unique ID
                datarow[IDX_UNIQUE_ID],
                # Name
                datarow[IDX_NAME].strip().title(), 
                # Relative addr to headshot png
                f'./{HEADSHOT_SRC_DIR}/{datarow[IDX_EMAIL_ID].strip()}.png', 
                # Department
                datarow[IDX_DEPARTMENT],
                # Address line 1, line 2
                datarow[IDX_ADDRESS], 
                # Outgoing batch year
                str(grad_year),
                # Phone no.
                datarow[IDX_PHONE_NO],
                # Email ID
                datarow[IDX_EMAIL_ID]
            )
            print()
        except Exception as e:
            traceback.print_exc()
