from __future__ import annotations

import dataclasses
import datetime
import typing as t

import numpy as np


PrecipitationType = str


@dataclasses.dataclass
class PredictionPoint(object):
    time_stamp: datetime.datetime
    temperature: float
    precipitation_type: PrecipitationType
    precipitation: float

    @classmethod
    def from_remote(cls, remote: t.Mapping[str, t.Any]) -> PredictionPoint:
        return cls(
            time_stamp = datetime.datetime.fromisoformat(remote['localTimeIso']),
            temperature = remote['temp'],
            precipitation_type = remote['precipType'],
            precipitation = remote['prec90'],
        )


@dataclasses.dataclass
class ForecastSlice(object):
    start_time: datetime.datetime
    end_time: datetime.datetime
    average_temperature: float
    total_precipitation: float
    precipitation_types: t.AbstractSet[PrecipitationType]

    @property
    def duration(self) -> datetime.timedelta:
        return self.end_time - self.start_time

    @property
    def precipitation_per_hour(self) -> float:
        return self.total_precipitation / (self.duration / datetime.timedelta(hours = 1))


@dataclasses.dataclass
class Forecast(object):
    points: t.Sequence[PredictionPoint]

    @classmethod
    def from_remote(cls, remote: t.Sequence[t.Mapping[str, t.Any]]) -> Forecast:
        return cls(
            points = [
                PredictionPoint.from_remote(point)
                for point in
                remote[:48]
            ]
        )

    @property
    def time_span(self) -> t.Tuple[datetime.datetime, datetime.datetime]:
        return self.points[0].time_stamp, self.points[-1].time_stamp

    def predictions_in_range(self, start: datetime.datetime, end: datetime.datetime) -> t.Iterator[PredictionPoint]:
        if start < self.points[0].time_stamp or end > self.points[-1].time_stamp:
            raise ValueError('Slice range not within forecast range')
        on = False
        for p in self.points:
            if not on:
                if p.time_stamp >= start:
                    on = True
            if on:
                if end < p.time_stamp:
                    break
                yield p

    def values_in_range(self, start: datetime.datetime, end: datetime.datetime) -> ForecastSlice:
        points = list(self.predictions_in_range(start, end))
        return ForecastSlice(
            start_time = points[0].time_stamp,
            end_time = points[-1].time_stamp,
            total_precipitation = sum(p.precipitation for p in points),
            average_temperature = np.mean([p.temperature for p in points]),
            precipitation_types = {p.precipitation_type for p in points},
        )
