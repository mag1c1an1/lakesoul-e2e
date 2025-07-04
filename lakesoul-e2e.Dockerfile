# SPDX-FileCopyrightText: LakeSoul Contributors
# 
# SPDX-License-Identifier: Apache-2.0
FROM dmetasoul/dev-all:0.1
COPY dist/e2etest-0.1.0-py3-none-any.whl /
COPY config.yaml /config.yaml
RUN pipx install e2etest-0.1.0-py3-none-any.whl
CMD ["e2etest", "--help"]