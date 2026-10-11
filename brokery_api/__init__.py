"""brokery_api：以 FastAPI 把 Brokery 的統一輸出映射為 HTTP 與 WebSocket，並提供網頁控制台。

只作映射與展示，不含任何券商邏輯：所有取數仍由 brokery.core.Brokery 完成，返回的欄位與錯誤口徑
與直接呼叫 Python 時完全一致。
"""
