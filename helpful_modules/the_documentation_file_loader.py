import json
class DocumentationException(Exception):
  def _raise(self):
    raise self
class DocumentationNotFound(DocumentationException):
  pass
class DocumentationFileNotFound(DocumentationNotFound):
  pass

class DocumentationFileLoader:
  def __init__(self):
    pass
  def _load_documentation_file(self):
    with open("docs/documentation.json", "r") as file:
      return json.loads("\n".join([str(item) for item in file]))

	

  def load_documentation_into_readable_files(self):
    dictToStoreFileContent = {}
    docs_json = self._load_documentation_file()
    for item in docs_json:
      dictToStoreFileContent[item["file_name"]] = "<!This file is dynamically generated from documentation.json. If you want to contribute/this is your fork, edit that instead :)>\n"
      if item["contains_legend"] == "true":
        dictToStoreFileContent[item["file_name"]] += """# Legend - global
        
*: Only useable by users with the Administrator (considering changing it to Manage Server) permission and global trusted users can use.

⚠: Only useable by global trusted users (such as /raise_error)

**: Not a bot/slash command (Documentation is here for purposes of me, and those who wish to fork my project/contribute with pull requests :))

***: This is a module/class. Cannot be called.

No Mark: This is a command without user restrictions"""
      item2 = item["contents"]
      for Item in item2:
        dictToStoreFileContent[item["file_name"]] += "\n" + "#" * Item["heading_level"] + " " +Item["title"] + "\n" + Item["contents"]
    
    for documentationFileName in dictToStoreFileContent.keys():
      with open(documentationFileName,"w") as file:
        file.write(dictToStoreFileContent[documentationFileName])
    return docs_json
  def get_documentation(self,documentationSource,documentationItem):
    _documentation = None
    documentation_from_json = self._load_documentation_file()
    for item in documentation_from_json:
      if item["file_name"] == documentationSource:
        _documentation = item
        break
    if _documentation == None:
      raise DocumentationFileNotFound(f"Documentation file {documentationSource} not found")
    for item2 in _documentation["contents"]:
      print(type(item2))
      if item2["title"] == documentationItem:
        return item2["contents"]
    raise DocumentationNotFound(f"Documentation for {documentationItem} not found")
    

  

