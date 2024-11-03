import json
from pathlib import Path

import datasets
import jsonlines
import pyarrow.compute as pc
import pyarrow.parquet as pq
import pytest

from lerobot.common.datasets.utils import EPISODES_PATH, INFO_PATH, STATS_PATH, TASKS_PATH


@pytest.fixture(scope="session")
def info_path(info):
    def _create_info_json_file(dir: Path, info_dict: dict = info) -> Path:
        fpath = dir / INFO_PATH
        fpath.parent.mkdir(parents=True, exist_ok=True)
        with open(fpath, "w") as f:
            json.dump(info_dict, f, indent=4, ensure_ascii=False)
        return fpath

    return _create_info_json_file


@pytest.fixture(scope="session")
def stats_path(stats):
    def _create_stats_json_file(dir: Path, stats_dict: dict = stats) -> Path:
        fpath = dir / STATS_PATH
        fpath.parent.mkdir(parents=True, exist_ok=True)
        with open(fpath, "w") as f:
            json.dump(stats_dict, f, indent=4, ensure_ascii=False)
        return fpath

    return _create_stats_json_file


@pytest.fixture(scope="session")
def tasks_path(tasks):
    def _create_tasks_jsonl_file(dir: Path, task_dicts: list = tasks) -> Path:
        fpath = dir / TASKS_PATH
        fpath.parent.mkdir(parents=True, exist_ok=True)
        with jsonlines.open(fpath, "w") as writer:
            writer.write_all(task_dicts)
        return fpath

    return _create_tasks_jsonl_file


@pytest.fixture(scope="session")
def episode_path(episodes):
    def _create_episodes_jsonl_file(dir: Path, episode_dicts: list = episodes) -> Path:
        fpath = dir / EPISODES_PATH
        fpath.parent.mkdir(parents=True, exist_ok=True)
        with jsonlines.open(fpath, "w") as writer:
            writer.write_all(episode_dicts)
        return fpath

    return _create_episodes_jsonl_file


@pytest.fixture(scope="session")
def single_episode_parquet_path(hf_dataset, info):
    def _create_single_episode_parquet(
        dir: Path, hf_ds: datasets.Dataset = hf_dataset, ep_idx: int = 0
    ) -> Path:
        data_path = info["data_path"]
        chunks_size = info["chunks_size"]
        ep_chunk = ep_idx // chunks_size
        fpath = dir / data_path.format(episode_chunk=ep_chunk, episode_index=ep_idx)
        fpath.parent.mkdir(parents=True, exist_ok=True)
        table = hf_ds.data.table
        ep_table = table.filter(pc.equal(table["episode_index"], ep_idx))
        pq.write_table(ep_table, fpath)
        return fpath

    return _create_single_episode_parquet


@pytest.fixture(scope="session")
def multi_episode_parquet_path(hf_dataset, info):
    def _create_multi_episode_parquet(dir: Path, hf_ds: datasets.Dataset = hf_dataset) -> Path:
        data_path = info["data_path"]
        chunks_size = info["chunks_size"]
        total_episodes = info["total_episodes"]
        for ep_idx in range(total_episodes):
            ep_chunk = ep_idx // chunks_size
            fpath = dir / data_path.format(episode_chunk=ep_chunk, episode_index=ep_idx)
            fpath.parent.mkdir(parents=True, exist_ok=True)
            table = hf_ds.data.table
            ep_table = table.filter(pc.equal(table["episode_index"], ep_idx))
            pq.write_table(ep_table, fpath)
        return dir / "data"

    return _create_multi_episode_parquet