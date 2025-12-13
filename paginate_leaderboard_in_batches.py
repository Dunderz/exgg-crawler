# async def paginate_leaderboard_in_batches(context):
#     build_id = fetch_build_id(BUCKLER_BASE)

#     CONCURRENCY = 10
#     PAGES_PER_BATCH = 50

#     semaphore = asyncio.Semaphore(CONCURRENCY)

#     next_page = 1
#     done = False

#     while not done:
#         batch_pages = list(range(next_page, next_page + PAGES_PER_BATCH))
#         tasks = [
#             asyncio.create_task(fetch_page_with_limit(context, pn, build_id, semaphore))
#             for pn in batch_pages
#         ]

#         results = await asyncio.gather(*tasks, return_exceptions=True)

#         ok = []
#         for r in results:
#             if isinstance(r, Exception):
#                 print(f"[!] Batch page task failed: {r}")
#                 continue
#             ok.append(r)

#         ok.sort(key=lambda x: x[0])

#         first_empty_page = None
#         all_players = []

#         for page_number, players in ok:
#             if not players and first_empty_page is None:
#                 first_empty_page = page_number
#             if first_empty_page is None:
#                 all_players.extend(players)

#         if all_players:
#             print(f"[*] Uploading pages {batch_pages[0]}-{batch_pages[-1]} to Supabase... ({len(all_players)} rows)")
#             save_to_supabase(all_players)

#         if first_empty_page is not None:
#             print(f"Reached end of leaderboard at page {first_empty_page}.")
#             done = True
#         else:
#             next_page += PAGES_PER_BATCH