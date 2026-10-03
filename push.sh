#!/usr/bin/env bash
# 一键推送到 astrnox/gamespace
# 用法：
#   GITHUB_PAT=ghp_xxx ./push.sh
# 或
#   ./push.sh            # 交互式读取（不 echo）

set -euo pipefail
cd "$(dirname "$0")"

if [ -z "${GITHUB_PAT:-}" ]; then
  read -rsp "粘贴 GitHub PAT（gamespace 仓库 write 权限）: " GITHUB_PAT
  echo
fi

AUTH=$(printf 'x-access-token:%s' "$GITHUB_PAT" | base64 -w0)

if [ -z "$(git remote get-url origin 2>/dev/null || true)" ]; then
  git remote add origin "https://github.com/astrnox/gamespace.git"
fi

git -c "http.https://github.com/.extraheader=Authorization: Basic $AUTH" \
    push -u origin main

unset GITHUB_PAT AUTH
echo "推送完成： https://github.com/astrnox/gamespace"
