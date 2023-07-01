# DQT-Parser

We utilized the [Manipulated-Image-Dataset](https://github.com/allinonee/Manipulated-Image-Dataset.git) to insert metadata artifacts into the Reference DB, specific to each editing tool. We provide a simple code that parses the metadata (exif, dqt) and inserts it into the database, enabling the identification of the last source. This is meant to demonstrate the ability to determine manipulation and trace the ultimate source through metadata. By referencing this code and principle, it contributes to research in image manipulation detection and related studies.

### Reference DB
- A database that contains exif, dqt, and filename signature information for images edited using various editing tools.
- Used as a reference to determine the manipulation and editing source of specific images.

### Insertion_ExifDQT.py
- Code that enables the insertion of metadata artifacts, specific to each editing tool, into the Reference DB.
- Exif data is parsed using exiftool, extracting the necessary parts, while dqt is parsed based on its signature (0xFFDB).

### Insertion_Signature.py
- Code that directly inserts Filename Signatures, specific to each editing tool, into the Reference DB.

### LastSourceChecker.py
- Code that utilizes the Reference DB to verify the manipulation and editing source of a particular image
