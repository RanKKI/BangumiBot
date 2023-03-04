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
        ret["raw_title"] = params.name
        ret["formatted"] = result.formatted
        ret.update(result.__dict__)
    return ret


"""
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"name":"[星空字幕组][关于我在无意间被隔壁的天使变成废柴这件事 / Otonarino-tenshisama][07][繁日双语][1080P][WEBrip][MP4]（急招校对、后期） [297.08 MB] [复制磁连]"}' \
  http://localhost:8000/parse
"""
