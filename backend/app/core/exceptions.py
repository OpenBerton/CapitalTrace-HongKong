class CCASSServiceError(Exception):
    """General CCASS 服務錯誤。"""


class CCASSParseError(CCASSServiceError):
    """無法解析 CCASS 回傳內容。"""


class CCASSNotFoundError(CCASSServiceError):
    """查無符合條件的 CCASS 股票資料。"""
