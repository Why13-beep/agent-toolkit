# tools/exceptions.py
# Definisikan custom exception untuk tools jika diperlukan

class ToolError(Exception):
    pass

class NetworkError(ToolError):
    pass

class DataFetchError(ToolError):
    pass
