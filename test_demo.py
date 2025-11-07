"""
🎓 Pytest 互动式演示

这个脚本会展示测试的实际运行过程
运行方式：python test_demo.py
"""

import sys
from colorama import init, Fore, Style

# 初始化 colorama（支持 Windows 彩色输出）
init()

def print_section(title):
    """打印章节标题"""
    print("\n" + "="*60)
    print(f"{Fore.CYAN}{Style.BRIGHT}{title}{Style.RESET_ALL}")
    print("="*60 + "\n")


def demo_1_basic_assert():
    """演示 1：基本断言"""
    print_section("演示 1: 基本断言 (Assert)")
    
    print(f"{Fore.YELLOW}代码:{Style.RESET_ALL}")
    print("  result = 1 + 1")
    print("  assert result == 2")
    print()
    
    # 实际执行
    result = 1 + 1
    try:
        assert result == 2
        print(f"{Fore.GREEN}✅ 断言通过！result = {result}{Style.RESET_ALL}")
    except AssertionError:
        print(f"{Fore.RED}❌ 断言失败！{Style.RESET_ALL}")
    
    print()
    input(f"{Fore.YELLOW}按 Enter 继续下一个演示...{Style.RESET_ALL}")


def demo_2_test_function():
    """演示 2：测试函数的执行"""
    print_section("演示 2: 测试我们的工具函数")
    
    print(f"{Fore.YELLOW}测试函数: is_valid_objectid(){Style.RESET_ALL}")
    print()
    
    from app.utils.helpers import is_valid_objectid
    
    # 测试有效的 ObjectId
    print(f"测试 1: is_valid_objectid('507f1f77bcf86cd799439011')")
    valid_id = "507f1f77bcf86cd799439011"
    result = is_valid_objectid(valid_id)
    print(f"  返回值: {result}")
    
    try:
        assert result is True
        print(f"  {Fore.GREEN}✅ 断言通过！{Style.RESET_ALL}")
    except AssertionError:
        print(f"  {Fore.RED}❌ 断言失败！{Style.RESET_ALL}")
    
    print()
    
    # 测试无效的 ObjectId
    print(f"测试 2: is_valid_objectid('invalid')")
    result = is_valid_objectid("invalid")
    print(f"  返回值: {result}")
    
    try:
        assert result is False
        print(f"  {Fore.GREEN}✅ 断言通过！{Style.RESET_ALL}")
    except AssertionError:
        print(f"  {Fore.RED}❌ 断言失败！{Style.RESET_ALL}")
    
    print()
    input(f"{Fore.YELLOW}按 Enter 继续下一个演示...{Style.RESET_ALL}")


def demo_3_test_models():
    """演示 3：测试响应模型"""
    print_section("演示 3: 测试响应模型")
    
    print(f"{Fore.YELLOW}测试函数: success_response(){Style.RESET_ALL}")
    print()
    
    from app.models.common import success_response
    
    # 创建响应
    print("代码:")
    print("  response = success_response(")
    print("      data={'user_id': '123'},")
    print("      message='User created'")
    print("  )")
    print()
    
    response = success_response(
        data={"user_id": "123"},
        message="User created"
    )
    
    print("返回的响应:")
    import json
    print(json.dumps(response, indent=2, ensure_ascii=False))
    print()
    
    # 验证响应
    print("验证:")
    tests = [
        ("response['success'] is True", response["success"] is True),
        ("response['data']['user_id'] == '123'", response["data"]["user_id"] == "123"),
        ("response['message'] == 'User created'", response["message"] == "User created"),
    ]
    
    for test_desc, test_result in tests:
        status = f"{Fore.GREEN}✅" if test_result else f"{Fore.RED}❌"
        print(f"  {status} {test_desc}{Style.RESET_ALL}")
    
    print()
    input(f"{Fore.YELLOW}按 Enter 继续下一个演示...{Style.RESET_ALL}")


def demo_4_test_pagination():
    """演示 4：测试分页"""
    print_section("演示 4: 测试分页功能")
    
    print(f"{Fore.YELLOW}测试类: PaginationParams{Style.RESET_ALL}")
    print()
    
    from app.models.common import PaginationParams
    
    # 创建分页参数
    print("创建分页参数:")
    print("  params = PaginationParams(page=2, per_page=10)")
    print()
    
    params = PaginationParams(page=2, per_page=10)
    
    print("属性值:")
    print(f"  page: {params.page}")
    print(f"  per_page: {params.per_page}")
    print(f"  skip: {params.skip}  (计算得出: (2-1) * 10 = 10)")
    print()
    
    print("验证:")
    tests = [
        ("params.page == 2", params.page == 2),
        ("params.per_page == 10", params.per_page == 10),
        ("params.skip == 10", params.skip == 10),
    ]
    
    for test_desc, test_result in tests:
        status = f"{Fore.GREEN}✅" if test_result else f"{Fore.RED}❌"
        print(f"  {status} {test_desc}{Style.RESET_ALL}")
    
    print()
    input(f"{Fore.YELLOW}按 Enter 继续下一个演示...{Style.RESET_ALL}")


def demo_5_test_order_number():
    """演示 5：测试订单编号生成"""
    print_section("演示 5: 测试订单编号生成")
    
    print(f"{Fore.YELLOW}测试函数: generate_order_number(){Style.RESET_ALL}")
    print()
    
    from app.utils.helpers import generate_order_number
    
    # 生成订单号
    print("生成两个订单号:")
    order_num1 = generate_order_number("ORD")
    order_num2 = generate_order_number("ORD")
    
    print(f"  订单号 1: {order_num1}")
    print(f"  订单号 2: {order_num2}")
    print()
    
    print("验证:")
    tests = [
        ("以 'ORD' 开头", order_num1.startswith("ORD")),
        ("长度为 23", len(order_num1) == 23),
        ("两个订单号不同", order_num1 != order_num2),
    ]
    
    for test_desc, test_result in tests:
        status = f"{Fore.GREEN}✅" if test_result else f"{Fore.RED}❌"
        print(f"  {status} {test_desc}{Style.RESET_ALL}")
    
    print()
    print(f"{Fore.CYAN}说明: 订单号格式 = ORD(3位) + 日期(8位) + 时间(6位) + 随机(6位) = 23位{Style.RESET_ALL}")
    
    print()
    input(f"{Fore.YELLOW}按 Enter 继续下一个演示...{Style.RESET_ALL}")


def demo_6_test_error_handler():
    """演示 6：测试错误处理"""
    print_section("演示 6: 测试错误处理")
    
    print(f"{Fore.YELLOW}测试类: NotFoundException{Style.RESET_ALL}")
    print()
    
    from app.middleware.error_handler import NotFoundException
    
    # 创建异常
    print("创建 NotFoundException:")
    print("  exc = NotFoundException(resource='User', resource_id='123')")
    print()
    
    exc = NotFoundException(resource="User", resource_id="123")
    
    print("异常属性:")
    print(f"  status_code: {exc.status_code}")
    print(f"  code: {exc.code}")
    print(f"  message: {exc.message}")
    print(f"  details: {exc.details}")
    print()
    
    print("验证:")
    tests = [
        ("status_code == 404", exc.status_code == 404),
        ("code == 'NOT_FOUND'", exc.code == "NOT_FOUND"),
        ("'User not found' in message", "User not found" in exc.message),
        ("details['id'] == '123'", exc.details["id"] == "123"),
    ]
    
    for test_desc, test_result in tests:
        status = f"{Fore.GREEN}✅" if test_result else f"{Fore.RED}❌"
        print(f"  {status} {test_desc}{Style.RESET_ALL}")
    
    print()
    input(f"{Fore.YELLOW}按 Enter 完成演示...{Style.RESET_ALL}")


def main():
    """主函数"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║                                                           ║")
    print("║          🧪 Pytest 互动式演示                              ║")
    print("║                                                           ║")
    print("║     这个演示会展示测试是如何实际运行的                      ║")
    print("║                                                           ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}\n")
    
    try:
        demo_1_basic_assert()
        demo_2_test_function()
        demo_3_test_models()
        demo_4_test_pagination()
        demo_5_test_order_number()
        demo_6_test_error_handler()
        
        print_section("✅ 演示完成！")
        print(f"{Fore.GREEN}恭喜！你已经看到了测试是如何工作的！{Style.RESET_ALL}")
        print()
        print(f"{Fore.YELLOW}下一步:{Style.RESET_ALL}")
        print("  1. 运行实际的 pytest 测试:")
        print(f"     {Fore.CYAN}pytest tests/test_day4_5.py -v{Style.RESET_ALL}")
        print()
        print("  2. 或使用快捷脚本:")
        print(f"     {Fore.CYAN}.\\run_tests.ps1{Style.RESET_ALL}")
        print()
        print("  3. 阅读完整指南:")
        print(f"     {Fore.CYAN}PYTEST_GUIDE.md{Style.RESET_ALL}")
        print()
        
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}演示被中断{Style.RESET_ALL}")
        sys.exit(0)
    except ImportError as e:
        print(f"\n{Fore.RED}❌ 错误: 无法导入模块{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}请确保虚拟环境已激活并安装了所有依赖{Style.RESET_ALL}")
        print(f"错误信息: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}❌ 发生错误: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

