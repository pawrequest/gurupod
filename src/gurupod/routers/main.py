from __future__ import annotations as _annotations

from fastapi import APIRouter, Depends
from fastui import FastUI
from sqlmodel import Session

from gurupod.core.database import get_session
from gurupod.routers.eps import episode_list_view

router = APIRouter()


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def api_index(page: int = 1, guru_name: str | None = None, session: Session = Depends(get_session)):
    # language=markdown
    markdown = """\
This site provides a demo of [FastUI](https://github.com/pydantic/FastUI), the code for the demo
is [here](https://github.com/pydantic/FastUI/tree/main/demo).

The following components are demonstrated:

* `Markdown` — that's me :-)
* `Text`— example [here](/components#text)
* `Paragraph` — example [here](/components#paragraph)
* `PageTitle` — you'll see the title in the browser tab change when you navigate through the site
* `Heading` — example [here](/components#heading)
* `Code` — example [here](/components#code)
* `Button` — example [here](/components#button-and-modal)
* `Link` — example [here](/components#link-list)
* `LinkList` — example [here](/components#link-list)
* `Navbar` — see the top of this page
* `Footer` — see the bottom of this page
* `Modal` — static example [here](/components#button-and-modal), dynamic content example [here](/components#dynamic-modal)
* `ServerLoad` — see [dynamic modal example](/components#dynamic-modal) and [SSE example](/components#server-load-sse)
* `Image` - example [here](/components#image)
* `Iframe` - example [here](/components#iframe)
* `Video` - example [here](/components#video)
* `Table` — See [cities table](/table/cities) and [users table](/table/users)
* `Pagination` — See the bottom of the [cities table](/table/cities)
* `ModelForm` — See [forms](/forms/login)
"""
    # return fast_ui_default_page(c.Markdown(text=markdown))
    # return GoToEvent(url="/eps/")
    return episode_list_view(page, guru_name, session)


@router.get("/{path:path}", status_code=404)
async def api_404():
    # so we don't fall through to the index page
    return {"message": "Not Found"}
