import datetime

from fastapi import FastAPI
from pydantic import AnyUrl, BaseModel, models

app = FastAPI()


class Episode(BaseModel):
    title: str
    date: datetime.date
    url = AnyUrl
    notes: str
    links = models.ManyToManyField('Link', related_name='episode_links', blank=True)
    gurus = models.ManyToManyField('Guru', related_name='guru_episodes', blank=True)
    slug = models.SlugField(editable=False, unique=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("episode_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        self.url = self.url.lower()
        super().save(*args, **kwargs)


class Item(BaseModel):
    name: str
    tax: str
    price: str


@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get('/episode/{slug}')
async def read_episode(episode_slug: str):
    return {"item_id": item_id}


