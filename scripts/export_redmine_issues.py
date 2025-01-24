import requests
import csv

# Redmineの設定
API_KEY = "YOUR_API_KEY"  # RedmineのAPIキーを入力
REDMINE_URL = "https://YOUR_REDMINE_URL"  # 例: https://redmine.example.com

# チケットを取得するクエリパラメータ
params_assigned = {
    "status_id": "*",  # すべてのステータス
    "assigned_to_id": "me",  # 自分が担当しているチケット
    "limit": 100,  # 取得する最大件数（調整可能）
}

params_reported = {
    "status_id": "*",  # すべてのステータス
    "author_id": "me",  # 自分が報告（作成）したチケット
    "limit": 100,  # 取得する最大件数
}

# APIキーをヘッダーに設定
headers = {"X-Redmine-API-Key": API_KEY}

# 自分がアサインされたチケットの取得
response_assigned = requests.get(
    f"{REDMINE_URL}/issues.json", headers=headers, params=params_assigned
)

# 自分が作成したチケットの取得
response_reported = requests.get(
    f"{REDMINE_URL}/issues.json", headers=headers, params=params_reported
)

# チケットリストの取得処理
issues = []

if response_assigned.status_code == 200 and response_reported.status_code == 200:
    assigned_issues = response_assigned.json().get("issues", [])
    reported_issues = response_reported.json().get("issues", [])

    # アサイン＋報告したチケットを統合（重複を防ぐためにセットを使用）
    unique_issues = {
        issue["id"]: issue for issue in assigned_issues + reported_issues
    }.values()
    issues.extend(unique_issues)

    # CSVファイルの作成
    with open(
        "redmine_my_assigned_and_reported_tickets.csv",
        mode="w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)

        # CSVヘッダー行
        writer.writerow(
            [
                "チケットID",
                "タイトル",
                "ステータス",
                "優先度",
                "作成日",
                "担当者",
                "作成者",
                "チケットURL",
            ]
        )

        # チケット情報の書き込み
        for issue in issues:
            issue_id = issue["id"]
            issue_url = f"{REDMINE_URL}/issues/{issue_id}"

            writer.writerow(
                [
                    issue_id,
                    issue["subject"],
                    issue["status"]["name"],
                    issue["priority"]["name"],
                    issue["created_on"][:10],  # YYYY-MM-DD形式に変換
                    issue.get("assigned_to", {}).get("name", "未割当"),
                    issue["author"]["name"],
                    issue_url,
                ]
            )

    print("CSVファイル 'redmine_my_assigned_and_reported_tickets.csv' を作成しました。")

else:
    print(f"Error: {response_assigned.status_code} - {response_assigned.text}")
    print(f"Error: {response_reported.status_code} - {response_reported.text}")
