# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

ANILIST_API: str = "https://graphql.anilist.co"
"""The URL to the AniList GraphQL API."""

ANILIST_SEARCH: str = """
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
"""
ANIME_SEARCH: str = A GraphQL query string used to search for anime titles and retrieve
relevant information.

:param $id: An integer representing the unique ID of the anime.
:param $search: A string representing the search query for the anime title.
:param $page: (Optional) An integer representing the current page number of the search
results. Default is 1.
:param $per_page: (Optional) An integer representing the number of search results per
page. Default is 10.

The query returns the following information:
- pageInfo:
    - total: The total number of search results.
    - currentPage: The current page number of the search results.
    - lastPage: The last page number of the search results.
    - hasNextPage: A boolean indicating whether there is a next page of search results.
- media:
    - id: The unique ID of the anime.
    - title:
        - romaji: The anime title in romaji.
        - english: The anime title in English.
        - native: The anime title in its native language.
    - siteUrl: The URL to the anime's page on the source website.

Note: This query is designed for use with a GraphQL API.
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
"""
ANIME_GET: str = A GraphQL query string used to retrieve detailed information about an
anime title by its ID.

:param $id: An integer representing the unique ID of the anime.

The query returns the following information:
- media:
    - id: The unique ID of the anime.
    - title:
        - romaji: The anime title in romaji.
        - english: The anime title in English.
        - native: The anime title in its native language.
    - episodes: The number of episodes in the anime.
    - description: A brief description of the anime.
    - format: The format of the anime (e.g., TV, movie, OVA, etc.).
    - status: The current airing status of the anime (e.g., finished, airing, etc.).
    - duration: The duration of each episode in minutes.
    - genres: A list of genres associated with the anime.
    - studios:
        - nodes:
            - name: The name of the animation studio.
            - isAnimationStudio: A boolean indicating whether the studio is an animation
                studio.
    - startDate:
        - year: The year the anime started airing.
        - month: The month the anime started airing.
        - day: The day the anime started airing.
    - endDate:
        - year: The year the anime finished airing.
        - month: The month the anime finished airing.
        - day: The day the anime finished airing.
    - season: The season (e.g., winter, spring, summer, or fall) the anime aired.
    - seasonYear: The year of the season the anime aired.
    - source: The original source material of the anime (e.g., manga, light novel, etc.)
    - meanScore: The mean score of the anime.
    - averageScore: The average score of the anime.
    - relations:
        - edges:
            - node:
                - id: The unique ID of the related anime.
            - relationType(version: 2): The type of relation between the anime titles
                (e.g., sequel, prequel, etc.).

Note: This query is designed for use with a GraphQL API.
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
"""
A GraphQL query string to fetch the trailer information for a given media item.

This query takes two variables as input:
    - $id: Int - The unique identifier of the media item.
    - $media: MediaType - The type of media (e.g., ANIME, MANGA).

The query returns the following fields:
    - trailer:
        - id: The unique identifier of the trailer.
        - site: The website hosting the trailer.
        - thumbnail: The URL of the trailer thumbnail image.
    - siteUrl: The URL of the media item's page on the AniList website.

Note: This query is designed for use with a GraphQL API.
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
