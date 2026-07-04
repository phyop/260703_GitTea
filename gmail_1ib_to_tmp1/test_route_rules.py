from route_1ib_to_tmp1 import Message, is_cash_dividend_only, is_firstrade_login_notice


def test_cash_dividend_only_single_item():
    message = Message(
        message_id="m1",
        subject="Message Center Notification",
        text="""
MESSAGE NOTIFICATION(S):

Priority: NORMAL

1 Cash Dividend: BLOX@ARCA

BLOX@ARCA announced a cash dividend with an ex-dividend day.
""",
    )
    assert is_cash_dividend_only(message)


def test_cash_dividend_only_multiple_items():
    message = Message(
        message_id="m2",
        subject="Message Center Notification",
        text="""
MESSAGE NOTIFICATION(S):

1 Cash Dividend: TLT@NASDAQ
2 Cash Dividend: CMCSA@NASDAQ
""",
    )
    assert is_cash_dividend_only(message)


def test_pending_merger_is_not_moved():
    message = Message(
        message_id="m3",
        subject="Message Center Notification",
        text="""
MESSAGE NOTIFICATION(S):

1 Pending Merger: HOII@VALUE
2 Pending Merger: MSII@VALUE
""",
    )
    assert not is_cash_dividend_only(message)


def test_mixed_message_center_is_not_moved():
    message = Message(
        message_id="m4",
        subject="Message Center Notification",
        text="""
MESSAGE NOTIFICATION(S):

1 Cash Dividend: TLT@NASDAQ
2 Pending Merger: HOII@VALUE
""",
    )
    assert not is_cash_dividend_only(message)


def test_firstrade_login_notice():
    message = Message(
        message_id="m5",
        subject="Firstrade登入確認通知",
        text="尊敬的客戶，為了保障您的賬戶安全，我們系統顯示您登入過 firstrade.com。",
    )
    assert is_firstrade_login_notice(message)


def test_firstrade_non_login_notice_is_not_moved():
    message = Message(
        message_id="m6",
        subject="Firstrade 市場活動通知",
        text="Firstrade market newsletter.",
    )
    assert not is_firstrade_login_notice(message)


def main():
    tests = [
        test_cash_dividend_only_single_item,
        test_cash_dividend_only_multiple_items,
        test_pending_merger_is_not_moved,
        test_mixed_message_center_is_not_moved,
        test_firstrade_login_notice,
        test_firstrade_non_login_notice_is_not_moved,
    ]
    for test in tests:
        test()
    print(f"通過 {len(tests)} 個規則測試。")


if __name__ == "__main__":
    main()
