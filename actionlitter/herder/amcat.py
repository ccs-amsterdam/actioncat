from amcat4py import AmcatClient
from typing import Optional, List

def request_documents(index: str, ids: List[str], token: str):
    amcat = AmcatClient(token["host"])
    if amcat.login_required():
        amcat.token = token
    docs = list()
    for i in ids:
        docs = docs + [amcat.get_document('state_of_the_union', i)]
    return docs
