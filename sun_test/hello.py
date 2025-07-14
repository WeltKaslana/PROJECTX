from langchain_community.document_loaders import UnstructuredExcelLoader
file_path = "meow.xlsx"
loader = UnstructuredExcelLoader(
    file_path,
    mode="elements",
    process_multiple_sheets=False
)

documents = loader.load()
print(f"Loaded {len(documents)} documents from {file_path}")

for doc in documents:
    print(f"Metadata: {doc.metadata}")
    print(f"Content: {doc.page_content[:500]}...")  # Print first 500 characters of content
    print("-" * 80)