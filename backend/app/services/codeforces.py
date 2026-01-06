import httpx

CF_USER_API = "https://codeforces.com/api/user.info"


async def fetch_cf_user(handle: str) -> dict | None:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            CF_USER_API,
            params={"handles": handle},
        )

    data = r.json()
    if data["status"] != "OK":
        return None

    return data["result"][0]
