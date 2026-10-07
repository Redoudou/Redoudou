import unittest
from update_profile import category, generate

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

if __name__ == '__main__':
    unittest.main()
