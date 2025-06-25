from pathlib import Path

import pytest

@pytest.fixture(scope="module")
def root_dir_path() -> Path:
  """
  ルートディレクトリパスを取得する。

  Returns
  ----------
  Path ルートディレクトリパス
  """
  root_dir_path = Path(__file__).resolve().parent.parent.parent
  return root_dir_path