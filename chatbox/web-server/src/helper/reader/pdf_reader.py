"""Docs parser.

Contains parsers for docx, pdf files.

"""
from typing import Dict, List, Optional
from llama_index.readers.base import BaseReader
from llama_index.schema import Document
from src.routes.ws import progressUpdate

import io
import gevent


class PDFReader(BaseReader):
    """PDF parser."""

    def load_data(
        self, file, extra_info: Optional[Dict] = None, context_item=None, room=None
    ) -> List[Document]:
        """Parse file."""
        try:
            import pypdf
        except ImportError:
            raise ImportError(
                "pypdf is required to read PDF files: `pip install pypdf`"
            )
        # with open(file, "rb") as fp:
            # Create a PDF object

        fp = io.BufferedReader(file)
        pdf = pypdf.PdfReader(fp)

        # Get the number of pages in the PDF document
        num_pages = len(pdf.pages)

        # Iterate over every page
        docs = []

        fifty_percent = int(round(0.5 * num_pages))

        for page in range(num_pages):
            # Extract the text from the page
            page_text = pdf.pages[page].extract_text()
            page_label = pdf.page_labels[page]
            if num_pages >= 2:
                if page == fifty_percent:
                    progressUpdate(context_item=context_item.to_json(),
                                   progress=30, is_file=True, message='', room=room)

            metadata = {"page_label": page_label, "file_name": file.filename}
            if extra_info is not None:
                metadata.update(extra_info)

            docs.append(Document(text=page_text, metadata=metadata))
        return docs
