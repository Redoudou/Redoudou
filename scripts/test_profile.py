import unittest
from update_profile import category, generate, hub_cards

class ProfileTests(unittest.TestCase):
    def test_explicit_topic_overrides_curated_category(self):
        self.assertEqual(category({'name':'new', 'topics':['profile-zk']}, {'category':'tools'}), 'zk')

    def test_unknown_repo_has_a_home(self):
        self.assertEqual(category({'name':'new-project'}, {}), 'web')

    def test_visibility_rename_and_escaping(self):
        repos = [
            {'id':1, 'name':'renamed', 'html_url':'https://github.com/Redoudou/renamed', 'description':'<script> & stuff'},
            {'id':2, 'name':'secret', 'private':True},
            {'id':3, 'name':'hidden', 'topics':['profile-hide']},
        ]
        result = generate(repos, {'1':{'category':'tools'}})
        self.assertIn('https://github.com/Redoudou/renamed', result)
        self.assertIn('&lt;script&gt; &amp; stuff', result)
        self.assertNotIn('secret', result)
        self.assertNotIn('hidden', result)

    def test_upstream_homepage_not_promoted(self):
        repo = {'id':1, 'name':'fork', 'fork':True, 'html_url':'https://github.com/Redoudou/fork', 'homepage':'https://upstream.example'}
        self.assertNotIn('https://upstream.example', generate([repo], {}))

    def test_curated_public_site_survives_private_repository(self):
        result = generate([{'id':2, 'name':'private-source', 'private':True}], {}, {'projects':[{'category':'zk','title':'Public demo','description':'Prototype','url':'https://demo.example'}]})
        self.assertIn('https://demo.example', result)
        self.assertNotIn('private-source', result)

    def test_retired_repository_stays_hidden(self):
        result = generate([{'id':1,'name':'old-project'}], {'1':{'hide':True}})
        self.assertNotIn('old-project', result)

    def test_hub_relative_links_and_grouping(self):
        source = '<h2>Research</h2>' + ''.join(f'<a class="card" href="/project-{i}/"><h3>Project {i}</h3><p>Public tool</p></a>' for i in range(5))
        cards = hub_cards(source)
        self.assertEqual(cards[0]['url'], 'https://hub.entethalliance.org/project-0/')
        self.assertEqual(cards[0]['section'], 'Research')
        with self.assertRaises(ValueError):
            hub_cards('<html>Unavailable</html>')

    def test_domains_combine_sources_without_duplicate_research(self):
        url = 'https://demo.example/research'
        result = generate(
            [{'id':1,'name':'green-light','html_url':'https://github.com/Redoudou/green-light'}],
            {'1':{'category':'zk','title':'Green Light'}},
            {'writing':[{'title':'Research duplicate','url':url,'description':'Writing'}]},
            [{'title':'Investor Eligibility','url':url,'section':'Research','description':'Reusable checks'}])
        privacy = result.split('alt="Privacy &amp; identity"')[1].split('</td>')[0]
        self.assertIn('Green Light', privacy)
        self.assertIn('Investor Eligibility', privacy)
        self.assertIn('Personal · Code', privacy)
        self.assertIn('EEA ·', privacy)
        self.assertNotIn('Research duplicate', result)
        self.assertNotIn('—', result)

if __name__ == '__main__':
    unittest.main()
