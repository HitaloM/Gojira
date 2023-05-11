# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

ANILIST_API: str = "https://graphql.anilist.co"

ANIME_SEARCH: str = """
query($id: Int, $search: String, $page: Int = 1, $per_page: Int = 10) {
    Page(page: $page, perPage: $per_page) {
        pageInfo {
            total
            currentPage
            lastPage
            hasNextPage
        }
        media(id: $id, search: $search, type: ANIME, sort: POPULARITY_DESC) {
            id
            title {
                romaji
                english
                native
            }
            siteUrl
        }
    }
}
"""

MANGA_SEARCH: str = """
query($id: Int, $search: String, $page: Int = 1, $per_page: Int = 10) {
    Page(page: $page, perPage: $per_page) {
        pageInfo {
            total
            currentPage
            lastPage
            hasNextPage
        }
        media(id: $id, search: $search, type: MANGA, sort: POPULARITY_DESC) {
            id
            title {
                romaji
                english
                native
            }
            siteUrl
        }
    }
}
"""

ANIME_GET: str = """
query($id: Int) {
    Page(page: 1, perPage: 1) {
        media(id: $id, type: ANIME) {
            id
            title {
                romaji
                english
                native
            }
            episodes
            description
            format
            status
            duration
            genres
            studios {
                nodes {
                    name
                    isAnimationStudio
                }
            }
            startDate {
                year
                month
                day
            }
            endDate {
                year
                month
                day
            }
            season
            seasonYear
            source
            averageScore
            bannerImage
            coverImage {
                medium
                large
                extraLarge
            }
            relations {
                edges {
                    node {
                        id
                    }
                    relationType(version: 2)
                }
            }
        }
    }
}
"""


MANGA_GET: str = """
query($id: Int) {
    Page(page: 1, perPage: 1) {
        media(id: $id, type: MANGA) {
            id
            title {
                romaji
                english
                native
            }
            chapters
            volumes
            description
            format
            status
            genres
            startDate {
                year
                month
                day
            }
            endDate {
                year
                month
                day
            }
            source
            averageScore
            bannerImage
            coverImage {
                medium
                large
                extraLarge
            }
            relations {
                edges {
                    node {
                        id
                    }
                    relationType(version: 2)
                }
            }
        }
    }
}
"""


TRAILER_QUERY: str = """
query($id: Int, $media: MediaType) {
    Page(page: 1, perPage: 1) {
        media(id: $id, type: $media) {
            trailer {
                id
                site
                thumbnail
            }
            siteUrl
        }
    }
}
"""

DESCRIPTION_QUERY: str = """
query($id: Int, $media: MediaType) {
    Page(page: 1, perPage: 1) {
        media(id: $id, type: $media) {
            description
        }
    }
}
"""

CHARACTER_QUERY: str = """
query($id: Int, $media: MediaType) {
    Page(page: 1, perPage: 1) {
        media(id: $id, type: $media) {
            characters(sort: FAVOURITES_DESC) {
                edges {
                    node {
                        name {
                            first
                            full
                            native
                            last
                        }
                        id
                    }
                    role
                }
            }
        }
    }
}
"""

STAFF_QUERY: str = """
query($id: Int, $media: MediaType) {
    Page(page: 1, perPage: 1) {
        media(id: $id, type: $media) {
            staff(sort: FAVOURITES_DESC) {
                edges {
                    node {
                        name {
                            full
                        }
                        id
                    }
                    role
                }
            }
        }
    }
}
"""

AIRING_QUERY: str = """
query($id: Int, $media: MediaType) {
    Page(page: 1, perPage: 1) {
        media(id: $id, type: $media) {
            nextAiringEpisode {
                timeUntilAiring
                episode
            }
            externalLinks {
                id
                url
                site
                type
            }
            episodes
        }
    }
}
"""

STUDIOS_QUERY: str = """
query($id: Int, $media: MediaType) {
    Page(page: 1, perPage: 1) {
        media(id: $id, type: $media) {
            studios {
                nodes {
                    id
                    name
                    isAnimationStudio
                }
            }
        }
    }
}
"""

UPCOMING_QUERY: str = """
query($per_page: Int $media: MediaType) {
    Page(page: 1, perPage: $per_page) {
        media(type: $media, sort: POPULARITY_DESC, status: NOT_YET_RELEASED) {
            id
            title {
                romaji
                english
                native
            }
            siteUrl
        }
    }
}
"""

POPULAR_QUERY: str = """
query($media: MediaType) {
    Page(page: 1, perPage: 50) {
        media(type: $media, sort: POPULARITY_DESC) {
            id
            title {
                romaji
                english
                native
            }
            siteUrl
        }
    }
}
"""

CATEGORIE_QUERY: str = """
query($genre: String, $page: Int, $media: MediaType) {
    Page(page: $page, perPage: 50) {
        media(type: $media, genre: $genre, sort: POPULARITY_DESC) {
            id
            title {
                romaji
            }
        }
    }
}
"""
