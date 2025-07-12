# SPDX-FileCopyrightText: LakeSoul Contributors
#
# SPDX-License-Identifier: Apache-2.0


from e2etest.s3 import s3_delete_dir, s3_delete_jars, s3_upload_jars
from e2etest.vars import E2E_DATA_DIR


def test_s3():
    s3_delete_jars()
    s3_upload_jars()
    s3_delete_dir(E2E_DATA_DIR)
