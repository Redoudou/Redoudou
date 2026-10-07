"""Generate the public profile from live GitHub metadata. Standard library only."""
import html
import json
import os
from pathlib import Path
import urllib.request
from urllib.parse import urljoin
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
OWNER = 'Redoudou'
CATEGORIES = [
    ('zk', 'Zero-knowledge & Ethereum', ['zk', 'zkp', 'zero-knowledge', 'ethereum', 'defi', 'blockchain', 'web3', 'solidity'], '#6d28d9', '#a855f7'),
    ('housing', 'Housing & civic tech', ['housing', 'housing-affordability', 'civic-tech', 'government', 'rent'], '#0369a1', '#06b6d4'),
    ('tools', 'Everyday tools', ['tool', 'tools', 'utility', 'productivity', 'whatsapp', 'photography'], '#047857', '#14b8a6'),
    ('learning', 'Learning & experiments', ['education', 'learning', 'physics', 'experiment', 'game'], '#c2410c', '#f59e0b'),
    ('web', 'Web & personal projects', ['website', 'portfolio', 'blog', 'github-pages'], '#be185d', '#f472b6'),
]
# IDs survive repository renames. Only public project metadata belongs here.
OVERRIDES = {}

class HubParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cards, self.card, self.field = [], None, None
        self.section, self.parts = 'Resources', []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'h2':
            self.field, self.parts = 'section', []
        if tag == 'a' and 'card' in attrs.get('class', '').split():
            self.card = {'url': urljoin('https://hub.entethalliance.org/', attrs['href']), 'section': self.section}
        if self.card and tag in ('h3', 'p'):
            self.field, self.parts = ('title' if tag == 'h3' else 'description'), []

    def handle_data(self, data):
        if self.field:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if self.field and tag in ('h2', 'h3', 'p'):
            value = ' '.join(''.join(self.parts).split())
            if self.field == 'section':
                self.section = value
            elif self.card:
                self.card[self.field] = value
            self.field = None
        if tag == 'a' and self.card:
            if self.card.get('title') and safe_url(self.card['url']):
                self.cards.append(self.card)
            self.card = None

def hub_cards(source):
    parser = HubParser()
    parser.feed(source)
    if len(parser.cards) < 5:
        raise ValueError('Hub layout changed or response incomplete; refusing to erase portfolio')
    return parser.cards

def api_repos():
    repos = []
    for page in range(1, 100):
        request = urllib.request.Request(f'https://api.github.com/users/{OWNER}/repos?type=owner&per_page=100&page={page}', headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'Redoudou-profile'})
        token = os.environ.get('GH_TOKEN')
        if token:
            request.add_header('Authorization', f'Bearer {token}')
        with urllib.request.urlopen(request, timeout=30) as response:
            batch = json.load(response)
        repos.extend(batch)
        if len(batch) < 100:
            return repos
    raise RuntimeError('Pagination limit exceeded; refusing an incomplete update')

def category(repo, override):
    topics = set(repo.get('topics') or [])
    for key, _, _, _, _ in CATEGORIES:
        if f'profile-{key}' in topics:
            return key
    if override.get('category'):
        return override['category']
    for key, _, keywords, _, _ in CATEGORIES:
        if topics.intersection(keywords):
            return key
    words = (repo['name'] + ' ' + (repo.get('description') or '')).lower()
    for key, _, keywords, _, _ in CATEGORIES:
        if any(word in words for word in keywords):
            return key
    return 'web'

def safe_url(value):
    return value if value and value.startswith('https://') else None

def generate(repos, overrides, portfolio=None, hub=None):
    groups = {c[0]: [] for c in CATEGORIES}
    for repo in sorted(repos, key=lambda r: r['name'].lower()):
        if repo.get('private') or repo['name'].lower() == OWNER.lower() or 'profile-hide' in (repo.get('topics') or []):
            continue
        override = overrides.get(str(repo['id']), {})
        if override.get('hide'):
            continue
        key = category(repo, override)
        name = html.escape(override.get('title', repo['name']))
        url = safe_url(repo['html_url'])
        if not url:
            raise ValueError('Invalid repository URL')
        description = html.escape(override.get('description') or repo.get('description') or 'A project in progress. Explore the repository for details.')
        status = ' · Archived' if repo.get('archived') else (' · Fork' if repo.get('fork') else '')
        demo = safe_url(repo.get('homepage')) or safe_url(override.get('demo'))
        if repo.get('fork') and demo and not override.get('demo'):
            demo = None  # A template homepage may belong to its upstream author.
        if override.get('demo'):
            demo = safe_url(override['demo'])
        if demo == override.get('blocked_demo'):
            demo = None
        links = f'<a href="{html.escape(url, quote=True)}">Code →</a>'
        if demo:
            links += f' &nbsp;·&nbsp; <a href="{html.escape(demo, quote=True)}">Open project ↗</a>'
        groups[key].append(f'<p><strong><a href="{html.escape(url, quote=True)}">{name}</a></strong>{status}<br>{description}<br>{links}</p>')
    for project in (portfolio or {}).get('projects', []):
        url = safe_url(project.get('url'))
        label = project.get('label', 'Visit website ↗')
        link = f'<a href="{html.escape(url, quote=True)}">{html.escape(label)}</a>' if url else html.escape(label)
        groups[project['category']].insert(0, f'<p><strong>{html.escape(project["title"])}</strong><br>{html.escape(project["description"])}<br>{link}</p>')
    result = '''<!-- Generated by scripts/update_profile.py; see PROFILE.md for controls. -->
![Redwan — ideas into useful things](assets/banner.svg)

**Obsessed vibe coder.** I turn questions I can’t leave alone into working prototypes, public tools, and interactive explanations.

Zero-knowledge & privacy · Ethereum & institutions · Housing & civic tech · Everyday tools

Brooklyn · Executive Director, [Enterprise Ethereum Alliance](https://entethalliance.org/) · Previously ChainSafe

[Personal projects](#personal-projects) · [Built for the EEA](#built-for-the-eea) · [Writing & research](#writing--research) · [Blog & portfolio](https://helloredwan.me/) · [LinkedIn](https://www.linkedin.com/in/redwanmeslem/)

## Personal projects

'''
    cells = []
    for key, title, _, _, _ in CATEGORIES:
        entries = '\n'.join(groups[key]) or '<p>Exploring this area. Public projects will appear here automatically.</p>'
        cells.append(f'<td width="50%" valign="top"><img src="assets/{key}.svg" alt="{html.escape(title)}" width="420"><br>\n{entries}\n</td>')
    result += '<table>\n' + '\n'.join('<tr>\n' + '\n'.join(cells[i:i+2]) + '\n</tr>' for i in range(0, len(cells), 2)) + '\n</table>\n\n'
    if hub:
        result += '## Built for the EEA\n\nI built the websites and tools collected in the [EEA Resource Hub](https://hub.entethalliance.org/). The standards and working-group reports are collective EEA work; my contribution here is making the research, tools, and resources accessible on the web.\n\n'
        section = None
        for card in hub + (portfolio or {}).get('eea', []):
            if card['section'] != section:
                section = card['section']
                result += f'### {html.escape(section)}\n\n'
            title = card['title']
            if title == 'Institutional Requests & Requirements':
                title = 'EEA Prospector — RFI & RFP scanner'
            if title == 'Digital Asset Policy Monitor':
                title = 'Policy Friday — Digital Asset Policy Monitor'
            result += f'- **[{title}]({card["url"]})** — {html.escape(card["description"])}\n'
        result += '\n'
    result += '## Writing & research\n\n'
    for article in (portfolio or {}).get('writing', []):
        if not safe_url(article['url']):
            raise ValueError('Invalid article URL')
        result += f'- **[{article["title"]}]({article["url"]})** — {article["description"]}\n'
    result += '\n[More on my blog & portfolio →](https://helloredwan.me/) · [Speaking & media →](https://helloredwan.me/speaking-media.html)\n\n'
    result += '[Browse public code →](https://github.com/Redoudou?tab=repositories&type=public)\n\n<sub>Public repositories and the EEA Hub refresh daily. Curated public websites and writing remain featured even when their source code is private.</sub>\n'
    return result

def assets():
    (ROOT / 'assets').mkdir(exist_ok=True)
    for key, title, _, start, end in CATEGORIES:
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="840" height="112" viewBox="0 0 840 112"><defs><linearGradient id="g"><stop stop-color="{start}"/><stop offset="1" stop-color="{end}"/></linearGradient></defs><rect width="840" height="112" rx="16" fill="url(#g)"/><circle cx="780" cy="20" r="90" fill="white" opacity=".08"/><text x="30" y="69" fill="white" font-family="Arial,sans-serif" font-size="34" font-weight="700">{html.escape(title)}</text></svg>'
        (ROOT / 'assets' / f'{key}.svg').write_text(svg)
    (ROOT / 'assets/banner.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="240" viewBox="0 0 1200 240"><defs><linearGradient id="g"><stop stop-color="#312e81"/><stop offset=".55" stop-color="#6d28d9"/><stop offset="1" stop-color="#0891b2"/></linearGradient></defs><rect width="1200" height="240" rx="24" fill="url(#g)"/><circle cx="1080" cy="40" r="160" fill="white" opacity=".06"/><circle cx="1150" cy="210" r="170" fill="white" opacity=".06"/><text x="48" y="102" fill="white" font-family="Arial,sans-serif" font-size="58" font-weight="700">Hi, I’m Redwan.</text><text x="48" y="159" fill="#e0e7ff" font-family="Arial,sans-serif" font-size="28">Obsessed vibe coder. Ideas into useful things.</text><text x="48" y="207" fill="#c7d2fe" font-family="Arial,sans-serif" font-size="20">ZERO-KNOWLEDGE / ETHEREUM / TOOLS / EXPERIMENTS</text></svg>')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--fixture', type=Path)
    parser.add_argument('--hub-fixture', type=Path)
    args = parser.parse_args()
    repos = json.loads(args.fixture.read_text()) if args.fixture else api_repos()
    overrides = json.loads((ROOT / 'profile.json').read_text())
    portfolio = json.loads((ROOT / 'portfolio.json').read_text())
    if args.hub_fixture:
        hub_source = args.hub_fixture.read_text()
    else:
        with urllib.request.urlopen('https://hub.entethalliance.org/', timeout=30) as response:
            hub_source = response.read().decode('utf-8')
    readme = generate(repos, overrides, portfolio, hub_cards(hub_source))
    assets()
    (ROOT / 'README.md').write_text(readme)
