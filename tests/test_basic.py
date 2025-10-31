"""
基礎 API 測試腳本

測試 FastAPI 應用的基本功能：
1. 根路由測試
2. 健康檢查測試
3. API 文檔訪問測試
"""

import requests
import sys
from typing import Dict, Any

# 配置
BASE_URL = "http://localhost:8000"
TIMEOUT = 5  # 請求超時時間（秒）


class Colors:
    """終端機顏色代碼"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_success(message: str):
    """印出成功訊息"""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")


def print_error(message: str):
    """印出錯誤訊息"""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")


def print_info(message: str):
    """印出資訊訊息"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")


def print_warning(message: str):
    """印出警告訊息"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")


def test_root() -> bool:
    """
    測試根路由
    
    Returns:
        bool: 測試是否通過
    """
    print(f"\n{Colors.BOLD}測試 1: 根路由 (GET /){Colors.RESET}")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        
        if response.status_code != 200:
            print_error(f"狀態碼錯誤: {response.status_code} (預期: 200)")
            return False
        
        data: Dict[str, Any] = response.json()
        
        # 檢查必要欄位
        required_fields = ["message", "project", "version", "docs", "health"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            print_error(f"缺少欄位: {', '.join(missing_fields)}")
            return False
        
        print_success("根路由測試通過")
        print_info(f"   專案名稱: {data['project']}")
        print_info(f"   版本: {data['version']}")
        print_info(f"   訊息: {data['message']}")
        return True
        
    except requests.exceptions.ConnectionError:
        print_error("無法連接到 API 服務器")
        print_warning("請確認 API 是否正在運行: uvicorn app.main:app --reload")
        return False
    except requests.exceptions.Timeout:
        print_error(f"請求超時（>{TIMEOUT}秒）")
        return False
    except Exception as e:
        print_error(f"發生錯誤: {str(e)}")
        return False


def test_health() -> bool:
    """
    測試健康檢查端點
    
    Returns:
        bool: 測試是否通過
    """
    print(f"\n{Colors.BOLD}測試 2: 健康檢查 (GET /health){Colors.RESET}")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        
        if response.status_code != 200:
            print_error(f"狀態碼錯誤: {response.status_code} (預期: 200)")
            return False
        
        data: Dict[str, Any] = response.json()
        
        # 檢查必要欄位
        if "status" not in data:
            print_error("回應中缺少 'status' 欄位")
            return False
        
        if data["status"] != "healthy":
            print_warning(f"服務狀態: {data['status']} (預期: healthy)")
        
        print_success("健康檢查測試通過")
        print_info(f"   狀態: {data.get('status', 'N/A')}")
        print_info(f"   服務: {data.get('service', 'N/A')}")
        print_info(f"   資料庫: {data.get('database', 'N/A')}")
        return True
        
    except requests.exceptions.ConnectionError:
        print_error("無法連接到 API 服務器")
        return False
    except requests.exceptions.Timeout:
        print_error(f"請求超時（>{TIMEOUT}秒）")
        return False
    except Exception as e:
        print_error(f"發生錯誤: {str(e)}")
        return False


def test_docs_access() -> bool:
    """
    測試 API 文檔訪問
    
    Returns:
        bool: 測試是否通過
    """
    print(f"\n{Colors.BOLD}測試 3: API 文檔訪問{Colors.RESET}")
    try:
        # 測試 Swagger UI
        response = requests.get(f"{BASE_URL}/docs", timeout=TIMEOUT)
        if response.status_code == 200:
            print_success("Swagger UI 可訪問")
            print_info(f"   URL: {BASE_URL}/docs")
        else:
            print_warning(f"Swagger UI 返回狀態碼: {response.status_code}")
        
        # 測試 OpenAPI JSON
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=TIMEOUT)
        if response.status_code == 200:
            print_success("OpenAPI 規範可訪問")
            openapi_data = response.json()
            print_info(f"   API 標題: {openapi_data.get('info', {}).get('title', 'N/A')}")
            print_info(f"   API 版本: {openapi_data.get('info', {}).get('version', 'N/A')}")
        else:
            print_warning(f"OpenAPI 規範返回狀態碼: {response.status_code}")
        
        return True
        
    except Exception as e:
        print_error(f"發生錯誤: {str(e)}")
        return False


def test_mongodb_connection() -> bool:
    """
    測試 MongoDB 連線（通過觀察啟動日誌）
    
    Returns:
        bool: 測試提示
    """
    print(f"\n{Colors.BOLD}測試 4: MongoDB 連線檢查{Colors.RESET}")
    print_info("請檢查 API 啟動日誌中是否有以下訊息：")
    print(f"   {Colors.GREEN}✅ 成功連接到 MongoDB 資料庫{Colors.RESET}")
    print_info("如果看到連線錯誤，請確認：")
    print("   1. MongoDB 服務是否正在運行")
    print("   2. .env 檔案中的 MONGODB_URL 是否正確")
    print("   3. 資料庫是否可訪問")
    return True


def run_all_tests():
    """執行所有測試"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{'  電商 API 基礎測試套件':^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
    print_info(f"目標 API: {BASE_URL}")
    
    results = []
    
    # 執行測試
    results.append(("根路由測試", test_root()))
    results.append(("健康檢查測試", test_health()))
    results.append(("API 文檔測試", test_docs_access()))
    results.append(("MongoDB 連線檢查", test_mongodb_connection()))
    
    # 統計結果
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}測試結果總結{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}通過{Colors.RESET}" if result else f"{Colors.RED}失敗{Colors.RESET}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{Colors.BOLD}總計: {passed}/{total} 測試通過{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 恭喜！所有測試都通過了！{Colors.RESET}")
        print_info("你的 API 已經準備好進入下一階段的開發")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  有 {total - passed} 個測試未通過{Colors.RESET}")
        print_info("請檢查錯誤訊息並修正問題")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(run_all_tests())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}測試被用戶中斷{Colors.RESET}")
        sys.exit(1)

