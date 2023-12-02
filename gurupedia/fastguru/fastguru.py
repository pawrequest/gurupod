import datetime

from pydantic import AnyUrl, BaseModel

from static.resource import ALL_EPISODE_URLS
from fastapi import FastAPI

app = FastAPI()


class Episode(BaseModel):
    title: str
    date: datetime.date
    url = AnyUrl
    notes :str
    links = models.ManyToManyField(Link)
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



@app.get('bulk-import')
async def bulk_import():
    fails = []
    eps_to_add = episodes_to_add()
    for episode_url in eps_to_add:
        episode_url = episode_url.lower()
        print(f'episode importer : {episode_url=}')

        if Episode.objects.filter(url=episode_url).exists():
            print(f'API ERROR Episode already exists {episode_url}')

        try:
            response = requests.get(episode_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            links_dict = show_links_from_soup(soup)
            episode_links = get_or_create_links(links_dict)
            episode = Episode.objects.create(
                url=episode_url,
                title=soup.select_one(".episode-title").text,
                notes=show_notes_from_soup(soup),
                date=parse(soup.select_one(".publish-date").text),
            )
            episode.links.set(episode_links)
            print(f'Episode imported : {episode.title} {episode.date}')
        except Exception as e:
            fails.append(episode_url)
            print(e)
            continue
        else:
            return Response({'fails': fails}, status=status.HTTP_201_CREATED)

def episodes_to_add():
    all_episodes = set(ALL_EPISODE_URLS)
    print(f'{len(all_episodes)=}')

    existing = set()
    print(f'{len(existing)=}')

    return all_episodes - existing
