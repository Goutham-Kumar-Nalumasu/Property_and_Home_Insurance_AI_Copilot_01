from typing import Any, Dict, List, Optional

import pandas as pd

from app.config import settings


class DamageEstimator:
    def __init__(self, csv_file=settings.REPAIR_COST_FILE):
        self.csv_file = csv_file
        self.df = self._load()

    def _load(self) -> pd.DataFrame:
        if not self.csv_file.exists():
            return pd.DataFrame()

        df = pd.read_csv(self.csv_file)
        df.columns = [col.strip().replace("\\_", "_") for col in df.columns]
        return df

    def reload(self) -> None:
        self.df = self._load()

    @staticmethod
    def _contains(series: pd.Series, value: Optional[str]) -> pd.Series:
        if not value:
            return pd.Series([True] * len(series), index=series.index)

        return series.astype(str).str.lower().str.contains(value.lower(), na=False)

    def estimate(
        self,
        damage_type: str,
        property_size_category: Optional[str] = None,
        peril_category: Optional[str] = None,
        affected_component: Optional[str] = None,
        top_n: int = 5,
    ) -> Dict[str, Any]:
        if self.df.empty:
            return {
                "found": False,
                "message": "Repair cost table was not found or is empty.",
                "matches": [],
            }

        filtered = self.df.copy()

        filtered = filtered[
            self._contains(filtered["damage_type"], damage_type)
        ]

        if property_size_category:
            filtered = filtered[
                self._contains(filtered["property_size_category"], property_size_category)
            ]

        if peril_category:
            filtered = filtered[
                self._contains(filtered["peril_category"], peril_category)
            ]

        if affected_component:
            filtered = filtered[
                self._contains(filtered["affected_component"], affected_component)
            ]

        if filtered.empty:
            return {
                "found": False,
                "message": "No matching repair-cost records found. Try a broader damage description.",
                "matches": [],
            }

        records: List[Dict[str, Any]] = (
            filtered.head(top_n)
            .fillna("")
            .to_dict(orient="records")
        )

        return {
            "found": True,
            "message": f"Found {len(records)} matching repair estimate record(s).",
            "matches": records,
        }


damage_estimator = DamageEstimator()