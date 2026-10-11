"""驗收 `Brokery.get_accounts`：四家一律以 ACCOUNT_COLUMNS 返回戶口與資金，核對格式統一、只列真實且
已啟用的戶口、currency 欄有無真係填到，以及 acc_type / currency / broker 三個參數在非法或不支持時明確
報錯。

以腳本方式直接執行：
    python brokery/acceptance/run_get_accounts.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

import pandas as pd

from brokery import Brokery
from brokery.brokers.base import ACCOUNT_COLUMNS, ACC_CASH, ACC_MARGIN

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 240)

BROKERS = ("futu", "ib", "tiger", "webull")
MONEY = ACCOUNT_COLUMNS[5:]  # 前五欄為身份欄，其餘一律為金額


def frame_checks(name: str, frame: pd.DataFrame) -> list[tuple[str, bool, str]]:
    """統一格式：欄位齊全、金額一律為數值（無值為 NaN）、身份欄不為空。"""
    checks = [("欄位為 ACCOUNT_COLUMNS", list(frame.columns) == ACCOUNT_COLUMNS, str(list(frame.columns)))]
    checks.append(("金額欄皆為數值", all(pd.api.types.is_numeric_dtype(frame[c]) for c in MONEY),
                   "；".join(f"{c}={frame[c].dtype}" for c in MONEY[:3])))
    checks.append(("account_id 無空值", bool((frame["account_id"].astype(str).str.len() > 0).all()),
                   f"{len(frame)} 個戶口"))
    # currency 是金額的計價幣種，空白的話該行金額便無從解讀，故必須有值。
    checks.append(("currency 全部有值", bool((frame["currency"].astype(str).str.len() > 0).all()),
                   ",".join(sorted(set(frame["currency"])))) or "空")
    return checks


def main() -> dict:
    frames: dict[str, pd.DataFrame] = {}
    with Brokery() as b:
        for name in BROKERS:
            result = b.get_accounts(broker=name)
            print(f"\n===== {name} status={result['status']} message={result['message']}")
            if result["status"]:
                frames[name] = result["data"]
                print(result["data"][["source", "account_id", "acc_type", "status", "currency",
                                      "net_liquidation", "cash", "buying_power"]].to_string())

        # 參數邊界：非法的 acc_type、未啟用的券商、不支持的 acc_type、以及不存在於任何戶口的幣種。
        bad_type = b.get_accounts(acc_type="leveraged")
        unknown = b.get_accounts(broker="bogus")
        all_rows = b.get_accounts()

    checks: list[tuple[str, bool, str]] = []
    for name in BROKERS:
        frame = frames.get(name)
        if frame is None or frame.empty:
            checks.append((f"{name} 返回戶口", False, "status=False 或無戶口"))
            continue
        checks += [(f"{name}：{label}", passed, detail) for label, passed, detail in frame_checks(name, frame)]
        checks.append((f"{name} acc_type 有值",
                       bool((frame["acc_type"].astype(str).str.len() > 0).all()),
                       ",".join(sorted(set(frame["acc_type"])))))
        # 一律只列真實且已啟用的戶口：富途是四家中唯一會同時返回模擬與已停用戶口的接口，故以它驗證。
        if name == "futu":
            stale = frame.loc[frame["status"] != "ACTIVE", ["account_id", "status"]]
            checks.append(("futu 不返回模擬／已停用戶口", stale.empty, stale.to_string()))

    checks.append(("非法 acc_type 明確報錯", not bad_type["status"] and bad_type["message"].startswith("bad_acc_type"),
                   bad_type["message"]))
    checks.append(("未啟用的 broker 明確報錯", not unknown["status"] and unknown["message"].startswith("unknown_source"),
                   unknown["message"]))

    if frames:
        with Brokery() as b:
            for name, frame in frames.items():
                # 以實測到的幣種重新請求，必須仍取到同一戶口（指定幣種只是篩選，不是換算）。
                ccy = frame["currency"].iloc[0]
                same = b.get_accounts(broker=name, currency=ccy)
                checks.append((f"{name} 以實測幣種 {ccy} 篩選仍取到戶口",
                               same["status"] and not same["data"].empty
                               and set(same["data"]["currency"]) == {ccy},
                               same["message"]))
                # 該券商沒有這個幣種的戶口時必須明確返回沒有戶口，不能返回其他幣種的金額湊數。
                none = b.get_accounts(broker=name, currency="ZZZ")
                checks.append((f"{name} 不支持的幣種明確報錯",
                               not none["status"] and none["message"].startswith("no_account"), none["message"]))
                # acc_type 為返回欄位：按實測到的性質篩選，只能取到該性質的戶口。券商原樣返回的性質
                # （如 IB 個人戶口的 individual）不在可篩選的取值內，此时必須明確報錯。
                kind = frame["acc_type"].iloc[0]
                if kind in (ACC_CASH, ACC_MARGIN):
                    picked = b.get_accounts(broker=name, acc_type=kind)
                    checks.append((f"{name} 按 acc_type={kind} 篩選只取該性質",
                                   picked["status"] and not picked["data"].empty
                                   and set(picked["data"]["acc_type"]) == {kind}, picked["message"]))
                else:
                    rejected = b.get_accounts(broker=name, acc_type=kind)
                    checks.append((f"{name} 的 {kind} 不可作 acc_type 篩選（明確報錯）",
                                   not rejected["status"] and rejected["message"].startswith("bad_acc_type"),
                                   rejected["message"]))

        # 一次過查全部券商：個別券商失敗不影響其余，且同一戶口的同一幣種只留一列。
        combined = all_rows["data"]
        checks.append(("不指定 broker 時返回戶口", all_rows["status"] and not combined.empty, all_rows["message"]))
        if all_rows["status"]:
            keys = list(zip(combined["source"], combined["account_id"], combined["currency"]))
            checks.append(("同一戶口的同一幣種不重複", len(keys) == len(set(keys)), f"{len(keys)} 列"))
            got = set(combined["source"])
            checks.append(("返回的券商均在啟用清單內", got <= set(BROKERS), ",".join(sorted(got))))
            print(f"\n===== 全部券商（{len(combined)} 列）=====")
            print(combined[["source", "account_id", "acc_type", "currency"]].to_string())

    for label, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'} {label}（{detail}）")
    failed = [label for label, passed, _ in checks if not passed]
    if failed:
        return {"status": False,
                "data": next(iter(frames.values()), pd.DataFrame(columns=ACCOUNT_COLUMNS)),
                "message": "失敗：" + "；".join(failed)}
    summary = "，".join(f"{name} {len(frame)} 個戶口" for name, frame in frames.items())
    return {"status": True, "data": all_rows["data"],
            "message": f"{len(checks)} 項檢查全過：{len(BROKERS)} 家券商戶口（{summary}）"}


if __name__ == "__main__":
    raise SystemExit(0 if main()["status"] else 1)
