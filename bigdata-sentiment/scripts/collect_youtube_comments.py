"""
YouTube comment collector for Big Data & Analytics sentiment project.
Searches for brand-related videos, pulls comments, saves to JSON.
"""

import os
import json
import time
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()  # reads YOUTUBE_API_KEY from a local .env file

API_KEY = os.getenv("YOUTUBE_API_KEY")
if not API_KEY:
    raise ValueError("YOUTUBE_API_KEY not found. Create a .env file with YOUTUBE_API_KEY=your_key_here")

BRAND = "Apple"
SEARCH_QUERIES = [
    "iPhone review",
    "Apple Watch unboxing",
    "iPhone vs Samsung",
    "Apple controversy",
    "MacBook review 2026",
    "Apple new product reaction",
]

TARGET_COMMENT_COUNT = 500   # adjust as needed
VIDEOS_PER_QUERY = 5
COMMENTS_PER_VIDEO = 100     # max allowed per request page
OUTPUT_FILE = "apple_youtube_comments.json"

youtube = build("youtube", "v3", developerKey=API_KEY)


def search_videos(query, max_results=VIDEOS_PER_QUERY):
    """Return a list of video IDs matching a search query."""
    try:
        request = youtube.search().list(
            q=query,
            part="id,snippet",
            type="video",
            maxResults=max_results,
            order="relevance",
        )
        response = request.execute()
        return [
            {
                "videoId": item["id"]["videoId"],
                "videoTitle": item["snippet"]["title"],
            }
            for item in response.get("items", [])
        ]
    except HttpError as e:
        print(f"Search failed for query '{query}': {e}")
        return []


def get_comments(video_id, video_title, max_results=COMMENTS_PER_VIDEO):
    """Return a list of top-level comments for a given video."""
    comments = []
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_results,
            textFormat="plainText",
            order="relevance",
        )
        response = request.execute()
        for item in response.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "videoId": video_id,
                "videoTitle": video_title,
                "comment": snippet["textDisplay"],
                "author": snippet["authorDisplayName"],
                "likeCount": snippet["likeCount"],
                "publishedAt": snippet["publishedAt"],
            })
    except HttpError as e:
        # Comments disabled on this video, or another API-side issue — skip it
        print(f"Could not fetch comments for '{video_title}': {e}")
    return comments


def main():
    all_comments = []
    seen_video_ids = set()

    for query in SEARCH_QUERIES:
        if len(all_comments) >= TARGET_COMMENT_COUNT:
            break

        print(f"Searching: {query}")
        videos = search_videos(query)

        for video in videos:
            if video["videoId"] in seen_video_ids:
                continue
            seen_video_ids.add(video["videoId"])

            print(f"  Pulling comments from: {video['videoTitle']}")
            comments = get_comments(video["videoId"], video["videoTitle"])
            all_comments.extend(comments)
            print(f"  Collected {len(comments)} comments (total: {len(all_comments)})")

            time.sleep(0.5)  # small pause to be polite to the API

            if len(all_comments) >= TARGET_COMMENT_COUNT:
                break

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_comments, f, indent=2, ensure_ascii=False)

    print(f"\nDone. Saved {len(all_comments)} comments to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
