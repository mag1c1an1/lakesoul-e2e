# SPDX-FileCopyrightText: LakeSoul Contributors
# 
# SPDX-License-Identifier: Apache-2.0
FROM dmetasoul/dev-all:0.1
COPY dist/e2etest-0.1.1-py3-none-any.whl /
COPY config.yaml /config.yaml
RUN pipx install e2etest-0.1.1-py3-none-any.whl --index-url https://pypi.tuna.tsinghua.edu.cn/simple
CMD ["e2etest", "--help"]
