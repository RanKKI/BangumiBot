from pydantic import BaseModel
from .app import app as api
from bangumi.parser import Parser


class ParseTitle(BaseModel):
    name: str


@api.post("/parse")
async def get_pending(params: ParseTitle):
    ret = {}
    result = Parser.parse_bangumi_name(params.name)
    if result:
        ret["title"] = params.name
        ret["formatted"] = result.formatted
        ret.update(result.__dict__)
    return ret
