import subprocess

# Danh sách các thư viện cần cài đặt
libraries = [
    'fastapi', 'pypdf', 'tiktoken', 'wikipedia', 'torch', 'transformers', 'sentence-transformers', 
    'beautifulsoup4', 'requests', 'python-dotenv', 'schedule', 'unstructured', 'unidecode', 'httpx', 
    'pypdf', 'rapidocr-onnxruntime', 'arxiv', 'ipython', 'aspose-pdf', 'aiofiles', 
    'google-api-python-client', 'google-auth-httplib2', 'google-auth-oauthlib', 
    'mysql-connector-python', 'serpapi', 
    'langchain', 'langchain-openai', 'langchain-chroma', 'langchain-qdrant', 'langchain-community', 
    'langchain-core', 'langchainhub', 'langgraph', 'langchain-anthropic', 'langchain_huggingface', 
    'langsmith', 'langchain_cohere', 'qdrant-client', 'faiss-cpu', 'neo4j', 
    'markdown', 'markdownify', 'markdown-crawler', 'PyPDF2', 'pymupdf', 
    'unstructured[all-docs]', 'pydantic', 'lxml', 'pdf2image', 'spacy', 'pyvi', 
    'flashrank', 'cohere', 'pycryptodome', 'pyairtable', 'gspread', 'llama-cpp-python' ,'selenium' , 'webdriver-manager'
]

# Danh sách lưu các thư viện không cài đặt được
failed_packages = []

# Hàm cài đặt thư viện với pip
def install_package(package):
    try:
        print(f"Cài đặt thư viện {package}...")
        subprocess.check_call(['pip', 'install', package])
        print(f"Thư viện {package} đã được cài đặt thành công.\n")
    except subprocess.CalledProcessError:
        print(f"Lỗi khi cài đặt thư viện {package}. Bỏ qua và tiếp tục cài đặt các thư viện khác.\n")
        failed_packages.append(package)

# Lặp qua từng thư viện và cài đặt
for lib in libraries:
    install_package(lib)

# Kiểm tra và in kết quả sau khi hoàn tất
if failed_packages:
    print("Các thư viện sau đây không thể cài đặt được:", ", ".join(failed_packages))
else:
    print("Tất cả các thư viện đã được cài đặt thành công.")
