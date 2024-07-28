import os
import season
from season.lib.static.config import base as BaseConfig

from glob import glob 
from langchain.document_loaders import PyPDFLoader, UnstructuredHTMLLoader, UnstructuredExcelLoader, UnstructuredPowerPointLoader, Docx2txtLoader, TextLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
import hashlib

from langchain_openai import ChatOpenAI
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough


class Config(BaseConfig):
    DEFAULT_VALUES = {
        'display_log': (bool, False),
        'basepath': (str, ""),
        'path': (str, "src"),
        'coderead': (None, ".py .md .ts .css .scss .sql".split(" "))
    }

class Model:
    def __init__(self, **kwargs):
        self.PATH_ROOT = wiz.project.fs().abspath()
        self.config = Config(kwargs)

    def fs(self, *args):
        return season.util.filesystem(os.path.join(self.PATH_ROOT, *args))

    def __call__(self, **kwargs):
        self.setConfig(**kwargs)
        
        config = self.config
        parseFile = self.parseFile
        path = config['path']

        pages = []
        if config['basepath'] is not None:
            fs = self.fs(config['basepath'])
        else:
            fs = self.fs()

        if fs.isdir(path):
            files = fs.files(path, recursive=True)
            idx = 0
            size = len(files)
            
            for f in files:
                idx += 1
                if fs.isdir(f): 
                    continue
                
                res = parseFile(fs.abspath(f), f"{idx}/{size}")

                if res is not None:
                    pages += res
        else : 
            pages = parseFile(path, "1/1")
            
        self.display(f'pages:{len(pages)}')

        return pages

    def retriever(self):
        openai_key = wiz.server.config.ide.openai_key
        openai_model = wiz.server.config.ide.openai_model

        llm = ChatOpenAI(
            model=openai_model,
            temperature=0,
            max_tokens=4096,
            api_key=openai_key)

        docs = self()
        retriever = None
        if len(docs) > 0:
            bm25 = BM25Retriever.from_documents(docs)
            retriever = MultiQueryRetriever.from_llm(retriever=bm25, llm=llm)
        return retriever

    def setConfig(self, **kwargs):
        for key in kwargs:
            self.config[key] = kwargs[key]

    def display(self, *args):
        if self.config.display_log:
            print(*args)

    def parseFile(self, f, idx=0):
        config = self.config

        ext = os.path.splitext(f)[-1]
        try:
            if ext in ['.csv']:
                self.display(f"[{idx}] read csv:", f)
                loader = CSVLoader(file_path=f)
                return loader.load()
            
            if ext in ['.doc', '.docx']:
                self.display(f"[{idx}] read doc:", f)
                loader = Docx2txtLoader(file_path=f)
                return loader.load()

            if ext in ['.ppt', '.pptx']:
                self.display(f"[{idx}] read ppt:", f)
                loader = UnstructuredPowerPointLoader(f)
                return loader.load()

            if ext in ['.xls', '.xlsx']:
                self.display(f"[{idx}] read excel:", f)
                loader = UnstructuredExcelLoader(f)
                return loader.load()

            if ext == '.pdf':
                self.display(f"[{idx}] read pdf:", f)
                loader = PyPDFLoader(f)
                return loader.load_and_split()

            if ext in ['.txt'] + config['coderead']:
                self.display(f"[{idx}] read txt:", f)
                loader = TextLoader(f)
                return loader.load()

            if ext == '.html':
                self.display(f"[{idx}] read html:", f)
                loader = UnstructuredHTMLLoader(f)
                return loader.load()

        except Exception as e:
            self.display(f"[{idx}] error:", f, str(e))
            return None

        self.display(f"[{idx}] unreaded:", f)
        return None
