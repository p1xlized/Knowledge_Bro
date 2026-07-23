import trafilatura


def parse_link(url: str) -> str:
    downloaded = trafilatura.fetch_url(url)
    return trafilatura.extract(downloaded)


if __name__ == "__main__":
    print(
        parse_link(
            "https://www.theguardian.com/technology/2026/jul/23/eu-fines-google-for-competition-breaches-over-search-and-apps"
        )
    )
