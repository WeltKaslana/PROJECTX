from typing import AsyncIterator, Iterator
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
class CustomDocumentLoader (BaseLoader):
    """！逐⾏读取⽂件的⽂档加载器示例『"""
    def __init__(self,file_path: str) -> None:
        """使⽤⽂件路径初始化加载器
        参数：
        file_path：要加载的⽂件路径
        """
        self.file_path = file_path
    def lazy_load(self)-> Iterator[Document]:
        """逐⾏读取⽂件的惰性加载器
        
        当实现惰性加载⽅法时，你应该使⽤⽣成器
        ⼀次⽣成⼀个⽂档
        """
        # with open(self.file_path, "r", encoding="utf-8") as file:
        with open(self.file_path, "r") as file:
            line_number = 0
            content = file.read()  # 先读取全部内容验证
            if not content:
                print("文件为空！")
            file.seek(0)
            # for line in file:
            #     yield Document(
            #         page_content=line, 
            #         metadata={"line-number": line_number,"source": self.file_path}
            #     )
            #     line_number += 1
    # alazy_load 是可选的
    # 如果不实现它，将使⽤⼀个默认实现，该实现会委托给 lazy_load！
    async def alazy_load(
        self,
    ) -> AsyncIterator [Document]:#＜-- 不接受任何参数
        """逐⾏读取⽂件的异步惰性加载器"""
        import aiofiles
        async with aiofiles.open(self.file_path, encoding="utf-8") as f:
            line_number = 0
            async for line in f: 
                yield Document(
                    page_content=line, 
                    metadata={"line_number": line_number,"source": self.file_path},
                )
                Line_numberg += 1

# # 测试
# with open ("sun_test/meow.txt","w", encoding="utf-8") as f:
#     quality_content = "meow meow meow meow \n meow \n本子魔法喵 \n喵子魔法本 "
#     f.write(quality_content)
#     loader = CustomDocumentLoader("sun_test/meow.txt")
# ## 测试懒加载
# for doc in loader.lazy_load():
#     print("loading")
#     print (type (doc))
#     print (doc)
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