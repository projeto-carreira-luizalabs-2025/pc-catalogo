from pydantic import BaseModel

_query_mapper = {
    "__ge": "$gte",
    "__gt": "$gt",
    "__le": "$lte",
    "__lt": "$lt",
}


class QueryModel(BaseModel):
    """
    Modelo para pesquisas.

    Atributos terminados com:

    - `__ge`: maior ou igual.
    - `__gt`: maior que.
    - `__le`: menor ou igual.
    - `__lt`: menor que.
    """

    def to_query_dict(self):
        query_dict = {}
        for key, value in self.model_dump(exclude_none=True).items():
            mapper = _query_mapper.get(key[-4:])
            if mapper is not None:
                if (current_key := key[:-4]) not in query_dict:
                    query_dict[current_key] = {}
                query_dict[current_key][mapper] = value
            else:
                query_dict[key] = value
        return query_dict
