# Maintaining the profile

## Public websites, EEA work, and writing

The profile is a portfolio, not just a public repository list. `portfolio.json` holds explicitly selected public websites and writing, including projects whose source code is private. Do not add private source links or operational details. These entries are preserved on every refresh.

The daily refresh also reads resource cards from https://hub.entethalliance.org/ and keeps their public destinations, titles, descriptions, current; editorial domain assignments keep the portfolio grouped by subject. A failed fetch or unrecognized hub layout stops the update and preserves the existing README. EEA standards and reports retain collective attribution.

Set `hide: true` on a repository ID in profile.json to omit an old project without changing or deleting its repository.

The profile refreshes daily and can also be refreshed from Actions → Refresh profile → Run workflow. GitHub may delay scheduled runs; schedules in inactive public repositories may be disabled after 60 days.

The generator reads every page of the public GitHub repositories endpoint, including forks. Private repositories are never listed. New projects appear automatically; renamed repositories use their current GitHub URL. Description and Website changes are picked up on the next refresh.

## Categories

Set a repository topic to `profile-zk`, `profile-housing`, `profile-tools`, `profile-learning`, or `profile-web` to select its category. These override all other rules. Add `profile-hide` to omit a public repository.

Otherwise the generator uses the curated category in profile.json, then regular topics, then keywords in the name and description. Unknown projects go under Web & personal projects so nothing disappears. The profile repository itself is excluded.

## Curated text and links

profile.json stores optional titles, descriptions, categories and demo URLs keyed by stable repository ID, so renames keep their curated text. Remove a description override to follow GitHub's description. Live Website fields are used unless a curated demo is set. Forks never automatically link to an upstream template website.

Use HTTPS demo URLs. The daily refresh updates metadata and links; it does not guarantee that externally hosted demos remain available.

## Local check

Run `python3 scripts/update_profile.py` with Python 3. The script has no third-party dependencies and fails without overwriting the README if GitHub cannot return a complete repository listing.

## Domain cards

The published portfolio combines repositories, EEA resources, and writing into six domain cards. Personal and EEA labels preserve attribution. Set `domain` on a repository override, curated project, EEA extra, writing entry, or hub_editorial entry to choose markets, privacy, operations, standards, housing, or tools. Existing profile topic categories still map into these domains. New hub resources default to intelligence and operations unless their title identifies another domain. Research links already present in the hub appear once.
