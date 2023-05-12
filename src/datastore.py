from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List

from google.cloud import datastore
from google.cloud.datastore.entity import Entity
from google.cloud.datastore.key import Key

from src import travis

datastore_client = datastore.Client(project="pants-remoting-beta")


@dataclass(frozen=True)
class JobAttempt:
    travis_job_id: travis.JobId
    started_at: datetime

    @property
    def datastore_key(self) -> Key:
        return Key("travis_job", self.travis_job_id, project="pants-remoting-beta")

    def _get_prior_start_times(self) -> List[datetime]:
        result = datastore_client.get(self.datastore_key)
        return [] if result is None else result["prior_start_times"]

    def already_used(self) -> bool:
        return self.started_at in self._get_prior_start_times()

    def save_to_db(self) -> None:
        new_entry = Entity(self.datastore_key)
        new_entry.update({"prior_start_times": self._get_prior_start_times() + [self.started_at]})
        datastore_client.put(new_entry)
