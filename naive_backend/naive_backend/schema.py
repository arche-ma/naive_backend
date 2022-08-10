import graphene
from graphene_django import DjangoObjectType

from shop.models import Artist, Artwork


class ArtistType(DjangoObjectType):
    class Meta:
        model = Artist
        fields = ('id', 'name', 'date_of_birth')


class ArtworkType(DjangoObjectType):
    class Meta:
        model = Artwork
        fields = ('id', 'title', 'description',
                  'author')


class Query(graphene.ObjectType):
    all_artworks = graphene.List(ArtworkType)
    all_artists = graphene.List(ArtistType)

    def resolve_all_artworks(root, info):
        return Artwork.objects.select_related('author').all()

    def resolve_all_artists(root, info):
        return Artist.objects.all()


schema = graphene.Schema(query=Query)
