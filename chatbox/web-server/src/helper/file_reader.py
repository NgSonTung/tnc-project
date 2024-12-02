"""Simple reader that reads files of different formats from a directory."""
import logging
from typing import Callable, Dict, List, Optional, Type

from llama_index.readers.base import BaseReader
from src.helper.reader.pdf_reader import PDFReader
from src.helper.reader.csv_reader import CSVReader
from src.helper.reader.xls_reader import PandasExcelReader
from llama_index.readers.file.docs_reader import DocxReader
from llama_index.readers.file.epub_reader import EpubReader
from llama_index.readers.file.image_reader import ImageReader
from llama_index.readers.file.ipynb_reader import IPYNBReader
from llama_index.readers.file.markdown_reader import MarkdownReader
from llama_index.readers.file.mbox_reader import MboxReader
from llama_index.readers.file.slides_reader import PptxReader
from llama_index.readers.file.video_audio_reader import VideoAudioReader
from llama_index.schema import Document

DEFAULT_FILE_READER_CLS: Dict[str, Type[BaseReader]] = {
    ".pdf": PDFReader,
    ".docx": DocxReader,
    ".pptx": PptxReader,
    ".jpg": ImageReader,
    ".png": ImageReader,
    ".jpeg": ImageReader,
    ".mp3": VideoAudioReader,
    ".mp4": VideoAudioReader,
    ".csv": CSVReader,
    ".epub": EpubReader,
    ".md": MarkdownReader,
    ".mbox": MboxReader,
    ".ipynb": IPYNBReader,
    ".xls": PandasExcelReader,
    ".xlsx": PandasExcelReader,
}

logger = logging.getLogger(__name__)


class FileReader(BaseReader):
    """Simple directory reader.

    Load files from file directory.
    Automatically select the best file reader given file extensions.

    Args:
        input_dir (str): Path to the directory.
        input_files (List): List of file paths to read
            (Optional; overrides input_dir, exclude)
        exclude (List): glob of python file paths to exclude (Optional)
        exclude_hidden (bool): Whether to exclude hidden files (dotfiles).
        encoding (str): Encoding of the files.
            Default is utf-8.
        errors (str): how encoding and decoding errors are to be handled,
              see https://docs.python.org/3/library/functions.html#open
        recursive (bool): Whether to recursively search in subdirectories.
            False by default.
        filename_as_id (bool): Whether to use the filename as the document id.
            False by default.
        required_exts (Optional[List[str]]): List of required extensions.
            Default is None.
        file_extractor (Optional[Dict[str, BaseReader]]): A mapping of file
            extension to a BaseReader class that specifies how to convert that file
            to text. If not specified, use default from DEFAULT_FILE_READER_CLS.
        num_files_limit (Optional[int]): Maximum number of files to read.
            Default is None.
        file_metadata (Optional[Callable[str, Dict]]): A function that takes
            in a filename and returns a Dict of metadata for the Document.
            Default is None.
    """

    def __init__(
        self,
        exclude: Optional[List] = None,
        exclude_hidden: bool = True,
        errors: str = "ignore",
        recursive: bool = False,
        encoding: str = "utf-8",
        filename_as_id: bool = False,
        required_exts: Optional[List[str]] = None,
        file_extractor: Optional[Dict[str, BaseReader]] = None,
        num_files_limit: Optional[int] = None,
        file_metadata: Optional[Callable[[str], Dict]] = None,
    ) -> None:
        """Initialize with parameters."""
        super().__init__()

        self.errors = errors
        self.encoding = encoding

        self.exclude = exclude
        self.recursive = recursive
        self.exclude_hidden = exclude_hidden
        self.required_exts = required_exts
        self.num_files_limit = num_files_limit

        if file_extractor is not None:
            self.file_extractor = file_extractor
        else:
            self.file_extractor = {}

        self.supported_suffix = list(DEFAULT_FILE_READER_CLS.keys())
        self.file_metadata = file_metadata
        self.filename_as_id = filename_as_id

    def load_data(self, input_file, file_suffix, metadata, context_item=None, room=None):
        """Load data from the input directory.

        Returns:
            List[Document]: A list of documents.
        """
        documents = []

        # metadata = self.file_metadata(str(input_file))

        if (
            file_suffix in self.supported_suffix
            or file_suffix in self.file_extractor
        ):
            # use file readers
            if file_suffix not in self.file_extractor:
                # instantiate file reader if not already
                reader_cls = DEFAULT_FILE_READER_CLS[file_suffix]
                self.file_extractor[file_suffix] = reader_cls()
            reader = self.file_extractor[file_suffix]
            docs = reader.load_data(
                input_file, extra_info=metadata, context_item=context_item, room=room)
            documents = docs
        else:
            data = input_file.read().decode('utf-8')
            doc = Document(text=data, metadata=metadata or {})
            if self.filename_as_id:
                doc.id_ = str(input_file)

            documents.append(doc)

        return documents
