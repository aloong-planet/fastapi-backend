from fastapi import Query
from sqlalchemy import asc, desc


class SortingParams:
    def __init__(
            self,
            sort_by: str = Query("id", description="Field to sort by"),
            order: str = Query("asc", description="Sort order ('asc' or 'desc')")
    ):
        self.sort_by = sort_by
        self.order = order

    def apply_sorting(self, query, model):
        """Apply sorting to the SQLAlchemy query based on model attributes."""
        if hasattr(model, self.sort_by):
            sort_field = getattr(model, self.sort_by)
            if self.order == "desc":
                query = query.order_by(desc(sort_field))
            else:
                query = query.order_by(asc(sort_field))
        return query
