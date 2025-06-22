FROM postgres:17-bullseye

COPY ./script/init.sh /docker-entrypoint-initdb.d/init.sh

# 環境設定
ENV TZ=Asia/Tokyo

# ポート開放
EXPOSE 15432