# Maintaining the profile

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
