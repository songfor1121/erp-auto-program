class OCRService:
    @staticmethod
    def process(file_path: str) -> str:
        # Phase 1: Mock OCR
        # This simulates extracting raw text from an image/PDF.
        # It's kept separate so we can plug in Google Cloud Document AI / Vision later.
        return """
        ABC Semiconductor
        Date: 2026-10-07
        Order No: SO-123456

        Item No | Spec | Qty | Unit Qty | Price | Amount | DC
        234b    | 10x20| 500 | 10       | 1200  | 570000 | 5%
        235b    | 20x30| 100 | 1        | 5000  | 500000 |
        """
