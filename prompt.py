# tools/prompt.py 
def get_tools_instruction(enable_tools: bool = True, mood: float = 0.0) -> str:
    tools_active = (enable_tools and mood >= 2.5)

    if tools_active:
        return """
- Kamu BISA menggunakan tools (weather, search) jika diperlukan untuk menjawab pertanyaan user.
- Panggil tools secara mandiri, jangan minta user memberikan informasi tambahan.
"""
    else:
        return """
- Informasi cuaca dan hasil pencarian akan DISEDIAKAN OTOMATIS oleh sistem jika diperlukan.
- Kamu TIDAK PERLU meminta atau mencari informasi apapun. Cukup jawab berdasarkan informasi yang sudah ada.
"""