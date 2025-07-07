# SPDX-FileCopyrightText: LakeSoul Contributors
# 
# SPDX-License-Identifier: Apache-2.0

from e2etest.core import E2E_DATA_DIR, s3_delete_dir, s3_delete_jars, s3_upload_jars


def test_s3():
    s3_delete_jars()
    s3_upload_jars()
    s3_delete_dir(E2E_DATA_DIR)